import 'dart:io';
import 'package:flutter/material.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:tflite_flutter/tflite_flutter.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart' as p;
import 'package:intl/intl.dart';

void main() => runApp(const OfflineAudioApp());

class OfflineAudioApp extends StatelessWidget {
  const OfflineAudioApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(useMaterial3: true, colorSchemeSeed: Colors.deepPurple),
      home: const MainNavigation(),
    );
  }
}

// --- MAIN NAVIGATION WITH TABS ---
class MainNavigation extends StatefulWidget {
  const MainNavigation({super.key});

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _selectedIndex = 0;

  final List<Widget> _screens = [
    const OfflinePredictor(),
    const HistoryDashboard(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.mic), label: "Inspect"),
          BottomNavigationBarItem(icon: Icon(Icons.dashboard), label: "History"),
        ],
      ),
    );
  }
}

// --- DATABASE HELPER ---
class DatabaseHelper {
  static Future<Database> getDatabase() async {
    final dbPath = await getDatabasesPath();
    return openDatabase(
      p.join(dbPath, 'inspection_history.db'),
      onCreate: (db, version) {
        return db.execute(
          'CREATE TABLE recordings(id INTEGER PRIMARY KEY AUTOINCREMENT, result TEXT, confidence TEXT, timestamp TEXT, filePath TEXT)',
        );
      },
      version: 1,
    );
  }

  static Future<void> saveResult(String result, String confidence, String filePath) async {
    final db = await getDatabase();
    await db.insert('recordings', {
      'result': result,
      'confidence': confidence,
      'timestamp': DateFormat('dd-MM-yyyy HH:mm').format(DateTime.now()),
      'filePath': filePath,
    });
  }

  static Future<List<Map<String, dynamic>>> getHistory() async {
    final db = await getDatabase();
    return db.query('recordings', orderBy: 'id DESC');
  }
}

// --- PREDICTOR SCREEN ---
class OfflinePredictor extends StatefulWidget {
  const OfflinePredictor({super.key});

  @override
  State<OfflinePredictor> createState() => _OfflinePredictorState();
}

class _OfflinePredictorState extends State<OfflinePredictor> {
  final record = AudioRecorder();
  Interpreter? _interpreter;

  bool isRecording = false;
  bool isProcessing = false;

  String resultText = "Offline AI Ready\nHold button to record";
  Color statusColor = Colors.deepPurple;

  @override
  void initState() {
    super.initState();
    _loadModel();
  }

  Future<void> _loadModel() async {
    try {
      _interpreter = await Interpreter.fromAsset('model.tflite');
    } catch (e) {
      setState(() => resultText = "Error loading AI model: $e");
    }
  }

  Future<void> startRecording() async {
    final status = await Permission.microphone.request();
    if (status != PermissionStatus.granted) return;

    final directory = await getApplicationDocumentsDirectory();
    final path = '${directory.path}/rec_${DateTime.now().millisecondsSinceEpoch}.wav';

    await record.start(
      const RecordConfig(encoder: AudioEncoder.wav, sampleRate: 22050),
      path: path,
    );

    setState(() {
      isRecording = true;
      resultText = "Listening for noise...";
      statusColor = Colors.red;
    });
  }

  Future<void> stopAndAnalyze() async {
    final path = await record.stop();
    setState(() => isRecording = false);

    if (path == null || _interpreter == null) return;

    _runInference(path);
  }

  Future<void> _runInference(String path) async {
    setState(() {
      isProcessing = true;
      resultText = "AI is thinking...";
    });

    try {
      var input = List.generate(
        1,
        (i) => List.generate(
          1,
          (j) => List.generate(
            128,
            (k) => List.filled(64, 0.0),
          ),
        ),
      );

      var output = List.filled(2, 0.0).reshape([1, 2]);

      _interpreter!.run(input, output);

      String finalResult = output[0][1] > output[0][0] ? "NOT OK" : "OK";
      String conf = "${(output[0].reduce((a, b) => a > b ? a : b) * 100).toStringAsFixed(1)}%";

      await DatabaseHelper.saveResult(finalResult, conf, path);

      setState(() {
        resultText = "RESULT: $finalResult\nConfidence: $conf";
        statusColor = finalResult == "OK" ? Colors.green : Colors.red;
      });
    } catch (e) {
      setState(() => resultText = "Processing Error: $e");
    } finally {
      setState(() => isProcessing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Noise AI Inspect"), centerTitle: true),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              isRecording ? Icons.settings_voice : Icons.offline_bolt,
              size: 100,
              color: statusColor,
            ),
            const SizedBox(height: 30),
            Container(
              padding: const EdgeInsets.all(25),
              margin: const EdgeInsets.symmetric(horizontal: 30),
              decoration: BoxDecoration(
                color: statusColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: statusColor, width: 2),
              ),
              child: Text(
                resultText,
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: statusColor),
              ),
            ),
            const SizedBox(height: 50),
            if (isProcessing)
              const CircularProgressIndicator()
            else
              GestureDetector(
                onLongPress: startRecording,
                onLongPressUp: stopAndAnalyze,
                child: FloatingActionButton.large(
                  onPressed: () {},
                  backgroundColor: isRecording ? Colors.red : Colors.deepPurple,
                  child: Icon(
                    isRecording ? Icons.stop : Icons.mic,
                    size: 50,
                    color: Colors.white,
                  ),
                ),
              ),
            const SizedBox(height: 10),
            Text(
              isRecording ? "RELEASE TO ANALYZE" : "HOLD TO RECORD",
              style: TextStyle(color: Colors.grey[600], fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }
}

// --- HISTORY DASHBOARD SCREEN ---
class HistoryDashboard extends StatefulWidget {
  const HistoryDashboard({super.key});

  @override
  State<HistoryDashboard> createState() => _HistoryDashboardState();
}

class _HistoryDashboardState extends State<HistoryDashboard> {
  List<Map<String, dynamic>> _history = [];

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    final data = await DatabaseHelper.getHistory();
    setState(() => _history = data);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Inspection Dashboard"), centerTitle: true),
      body: _history.isEmpty
          ? const Center(child: Text("No inspections recorded yet."))
          : ListView.builder(
              itemCount: _history.length,
              itemBuilder: (context, index) {
                final item = _history[index];
                final isOk = item['result'] == "OK";

                return Card(
                  margin: const EdgeInsets.symmetric(horizontal: 15, vertical: 8),
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor: isOk ? Colors.green : Colors.red,
                      child: Icon(isOk ? Icons.check : Icons.close, color: Colors.white),
                    ),
                    title: Text(
                      "Result: ${item['result']}",
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text(
                      "Date: ${item['timestamp']}\nConfidence: ${item['confidence']}",
                    ),
                    trailing: const Icon(Icons.chevron_right),
                  ),
                );
              },
            ),
    );
  }
}
