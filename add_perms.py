import os
import re

# 1) Add Microphone & Internet permissions to AndroidManifest.xml
manifest_path = 'android/app/src/main/AndroidManifest.xml'
if os.path.exists(manifest_path):
    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Use real XML tags (not HTML-escaped)
    perm_mic = '<uses-permission android:name="android.permission.RECORD_AUDIO" />'
    perm_net = '<uses-permission android:name="android.permission.INTERNET" />'

    # Insert permissions only if not already present
    needs_mic = 'android.permission.RECORD_AUDIO' not in content
    needs_net = 'android.permission.INTERNET' not in content

    if needs_mic or needs_net:
        insert_block = ''
        if needs_mic:
            insert_block += f'    {perm_mic}\n'
        if needs_net:
            insert_block += f'    {perm_net}\n'

        # Insert before the <application ...> tag
        if '<application' in content:
            new_content = content.replace('<application', f'{insert_block}    <application', 1)
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("AndroidManifest.xml: permissions added.")
        else:
            print("WARNING: <application> tag not found. Skipped permission injection.")
    else:
        print("AndroidManifest.xml: permissions already present.")
else:
    print("WARNING: AndroidManifest.xml not found; skipping permission changes.")

# 2) Force local.properties (overrides Flutter defaults)
props_path = 'android/local.properties'
os.makedirs(os.path.dirname(props_path), exist_ok=True)
with open(props_path, 'a', encoding='utf-8') as f:
    # Use minSdkVersion 26 to satisfy audio recording/TFLite combos
    f.write("\nflutter.minSdkVersion=26\n")
    f.write("flutter.targetSdkVersion=34\n")
    f.write("flutter.compileSdkVersion=34\n")
print("local.properties: forced min/target/compile SDK (26 / 34 / 34).")

# 3) Patch android/app/build.gradle to enforce SDK versions
gradle_path = 'android/app/build.gradle'
if os.path.exists(gradle_path):
    with open(gradle_path, 'r', encoding='utf-8') as f:
        gradle_content = f.read()

    # Handle both Groovy and potential Kotlin DSL-like patterns
    # Replace minSdkVersion/minSdk
    gradle_content = re.sub(r'minSdkVersion\s+\d+', 'minSdkVersion 26', gradle_content)
    gradle_content = re.sub(r'minSdk\s*=\s*\d+', 'minSdk = 26', gradle_content)

    # Replace target and compile versions with 34
    gradle_content = re.sub(r'targetSdkVersion\s+\d+', 'targetSdkVersion 34', gradle_content)
    gradle_content = re.sub(r'targetSdk\s*=\s*\d+', 'targetSdk = 34', gradle_content)
    gradle_content = re.sub(r'compileSdkVersion\s+\d+', 'compileSdkVersion 34', gradle_content)
    gradle_content = re.sub(r'compileSdk\s*=\s*\d+', 'compileSdk = 34', gradle_content)

    with open(gradle_path, 'w', encoding='utf-8') as f:
        f.write(gradle_content)
    print("build.gradle: SDK versions enforced (min=26, target=34, compile=34).")
else:
    print("WARNING: android/app/build.gradle not found; skipping Gradle patch.")
