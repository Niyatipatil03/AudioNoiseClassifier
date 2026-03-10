    1 import os
    2 import re
    3
    4 # 1. Add Microphone & Internet Permissions
    5 manifest_path = 'android/app/src/main/AndroidManifest.xml'
    6 if os.path.exists(manifest_path):
    7     with open(manifest_path, 'r') as f:
    8         content = f.read()
    9     perms = """
   10     <uses-permission android:name="android.permission.RECORD_AUDIO" />
   11     <uses-permission android:name="android.permission.INTERNET" />
   12     """
   13     if '<uses-permission' not in content:
   14         new_content = content.replace('<application', perms + '    <application')
   15         with open(manifest_path, 'w') as f:
   16             f.write(new_content)
   17     print("Permissions added.")
   18
   19 # 2. Force local.properties (This is where Flutter usually hides the version)
   20 props_path = 'android/local.properties'
   21 with open(props_path, 'a') as f:
   22     f.write("\nflutter.minSdkVersion=21\n")
   23     f.write("flutter.targetSdkVersion=34\n")
   24     f.write("flutter.compileSdkVersion=34\n")
   25 print("local.properties forced to version 21.")
   26
   27 # 3. Force build.gradle (Both old and new syntax)
   28 gradle_path = 'android/app/build.gradle'
   29 if os.path.exists(gradle_path):
   30     with open(gradle_path, 'r') as f:
   31         gradle_content = f.read()
   32
   33     # Replace any mention of minSdkVersion/minSdk with 21
   34     gradle_content = re.sub(r'minSdkVersion\s+.*', 'minSdkVersion 21', gradle_content)
   35     gradle_content = re.sub(r'minSdk\s*=\s*.*', 'minSdk = 21', gradle_content)
   36
   37     # Replace target and compile versions with 34
   38     gradle_content = re.sub(r'targetSdkVersion\s+.*', 'targetSdkVersion 34', gradle_content)
   39     gradle_content = re.sub(r'targetSdk\s*=\s*.*', 'targetSdk = 34', gradle_content)
   40     gradle_content = re.sub(r'compileSdkVersion\s+.*', 'compileSdkVersion 34', gradle_content)
   41     gradle_content = re.sub(r'compileSdk\s*=\s*.*', 'compileSdk = 34', gradle_content)
   42
   43     with open(gradle_path, 'w') as f:
   44         f.write(gradle_content)
   45     print("build.gradle forced to version 21.")
