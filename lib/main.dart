import 'dart:convert';
      import 'package:flutter/material.dart';
      import 'package:http/http.dart' as http;
      import 'package:record/record.dart';
      import 'package:path_provider/path_provider.dart';
      import 'package:permission_handler/permission_handler.dart';
     
      void main() => runApp(const AudioApp());
     
     class AudioApp extends StatelessWidget {
       const AudioApp({super.key});
       @override
       Widget build(BuildContext context) {
         return MaterialApp(
           debugShowCheckedModeBanner: false,
           theme: ThemeData(useMaterial3: true, colorSchemeSeed: Colors.blue),
           home: const AudioPredictor(),
         );
       }
     }
    
     class AudioPredictor extends StatefulWidget {
       const AudioPredictor({super.key});
       @override
       State<AudioPredictor> createState() => _AudioPredictorState();
     }
    
     class _AudioPredictorState extends State<AudioPredictor> {
       final record = AudioRecorder();
       bool isRecording = false;
       bool isProcessing = false;
       String resultText = "Ready to analyze noise";
       Color statusColor = Colors.blueGrey;
    
       // Using your PC's IP address
       final String baseUrl = "http://10.3.17.101:8000";
    
       Future<void> startRecording() async {
         final status = await Permission.microphone.request();
         if (status != PermissionStatus.granted) {
           setState(() => resultText = "Microphone permission denied");
           return;
         }
    
         final directory = await getTemporaryDirectory();
         final path = '${directory.path}/test_audio.wav';
    
         await record.start(const RecordConfig(encoder: AudioEncoder.wav), path: path);
         setState(() {
           isRecording = true;
           resultText = "Recording audio...";
           statusColor = Colors.red;
         });
       }
    
       Future<void> stopAndUpload() async {
         final path = await record.stop();
         setState(() => isRecording = false);
         if (path == null) return;
         uploadAudio(path);
       }
    
       Future<void> uploadAudio(String path) async {
         setState(() {
           isProcessing = true;
           resultText = "Sending to AI Server...";
           statusColor = Colors.orange;
         });
    
         try {
           var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/predict'));
           request.files.add(await http.MultipartFile.fromPath('file', path));
    
           var streamedResponse = await request.send();
           var response = await http.Response.fromStream(streamedResponse);
    
           if (response.statusCode == 200) {
             final data = jsonDecode(response.body);
             setState(() {
               final res = data['result'];
               resultText = "FINAL RESULT: $res\n"
                            "Noise Ratio: ${(data['noise_ratio'] * 100).toStringAsFixed(1)}%\n"
                            "Confidence: ${(data['confidence'] * 100).toStringAsFixed(1)}%";
               statusColor = res == "OK" ? Colors.green : Colors.red;
             });
           } else {
             setState(() {
               resultText = "Server Error: ${response.statusCode}";
               statusColor = Colors.black;
             });
           }
         } catch (e) {
           setState(() {
             resultText = "Connection Error!\nCheck if PC is running backend\nand phone is on same Wi-Fi.";
             statusColor = Colors.black;
           });
         } finally {
           setState(() => isProcessing = false);
         }
      }
   
      @override
      Widget build(BuildContext context) {
        return Scaffold(
          appBar: AppBar(title: const Text("Noise AI Classifier"), centerTitle: true),
          body: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(isRecording ? Icons.mic : Icons.multitrack_audio, size: 80, color: statusColor),
                const SizedBox(height: 20),
                Container(
                  padding: const EdgeInsets.all(20),
                  margin: const EdgeInsets.symmetric(horizontal: 30),
                  decoration: BoxDecoration(
                    color: statusColor.withOpacity(0.1),
                    border: Border.all(color: statusColor),
                    borderRadius: BorderRadius.circular(15),
                  ),
                  child: Text(resultText, textAlign: TextAlign.center,
                              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: statusColor)),
                ),
                const SizedBox(height: 40),
                if (isProcessing)
                  const CircularProgressIndicator()
                else
                  FloatingActionButton.large(
                    onPressed: isRecording ? stopAndUpload : startRecording,
                    backgroundColor: isRecording ? Colors.red : Colors.blue,
                    child: Icon(isRecording ? Icons.stop : Icons.mic, color: Colors.white, size: 40),
                  ),
              ],
            ),
          ),
        );
      }
    }
