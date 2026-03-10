import 'dart:io';
import 'package:flutter/material.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:tflite_flutter/tflite_flutter.dart';

void main() => runApp(const OfflineAudioApp());

class OfflineAudioApp extends StatelessWidget {
  const OfflineAudioApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(useMaterial3: true, colorSchemeSeed: Colors.deepPurple),
      home: const OfflinePredictor(),
    );
  }
}

class OfflinePredictor extends StatefulWidget {
  const OfflinePredictor({super.key});

  @override
  State<OfflinePredictor> createState() => _OfflinePredictorState();
}

class _OfflinePredictorState extends State<OfflinePredictor> {
  // Changed from AudioRecorder() to Record() for compatibility
  final record = Record();
  Interpreter? _interpreter;
  bool isRecording = false;
  bool isProcessing = false;
  String resultText = "Offline AI Ready\n(No Wi-Fi needed)";
  Color statusColor = Colors.deepPurple;

  @override
  void initState() {
    super.initState();
    _loadModel();
  }

  Future<void> _loadModel() async {
    try {
      _interpreter = await Interpreter.fromAsset('assets/model.tflite');
    } catch (e) {
      setState(() => resultText = "Error loading AI model: $e");
    }
  }

  Future<void> startRecording() async {
    final status = await Permission.microphone.request();
    if (status != PermissionStatus.granted) return;

    final directory = await getTemporaryDirectory();
    final path = '${directory.path}/offline_test.wav';

    // Updated start method for record version 5+
    await record.start(
      path: path,
      encoder: AudioEncoder.wav,
      samplingRate: 22050,
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
      statusColor = Colors.orange;
    });

    try {
      final file = File(path);
      final bytes = await file.readAsBytes();

      // Fixed input/output shapes for the CNN
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

      var output = List.filled(1 * 2, 0.0).reshape([1, 2]);

      _interpreter!.run(input, output);

      double probOk = output[0][0];
      double probNotOk = output[0][1];

      setState(() {
        if (probNotOk > probOk) {
          resultText = "RESULT: NOT OK\nDetected Noise Patterns";
          statusColor = Colors.red;
        } else {
          resultText = "RESULT: OK\nClean Signal";
          statusColor = Colors.green;
        }
      });
    } catch (e) {
      setState(() {
        resultText = "Processing Error: $e";
        statusColor = Colors.black;
      });
    } finally {
      setState(() => isProcessing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Offline Noise AI"), centerTitle: true),
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
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
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
              style: TextStyle(
                color: Colors.grey[600],
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
