import os
import re

# 1. Add Microphone & Internet Permissions
manifest_path = 'android/app/src/main/AndroidManifest.xml'

if os.path.exists(manifest_path):
    with open(manifest_path, 'r') as f:
        content = f.read()

    perms = """
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.INTERNET" />
    """

    # Only add if missing
    if '<uses-permission' not in content:
        new_content = content.replace(
            '<application',
            perms + '    <application'
        )
        with open(manifest_path, 'w') as f:
            f.write(new_content)

    print("Permissions added.")


# 2. Force local.properties (Flutter uses this to override SDK versions)
props_path = 'android/local.properties'

with open(props_path, 'a') as f:
    f.write("\nflutter.minSdkVersion=21\n")
    f.write("flutter.targetSdkVersion=34\n")
    f.write("flutter.compileSdkVersion=34\n")

print("local.properties forced to version 21/34.")


# 3. Force SDK versions inside android/app/build.gradle
gradle_path = 'android/app/build.gradle'

if os.path.exists(gradle_path):
    with open(gradle_path, 'r') as f:
        gradle_content = f.read()

    # Replace any minSdkVersion or minSdk syntax
    gradle_content = re.sub(
        r'minSdkVersion\s+.*',
        'minSdkVersion 21',
        gradle_content
    )
    gradle_content = re.sub(
        r'minSdk\s*=\s*.*',
        'minSdk = 21',
        gradle_content
    )

    # Replace target and compile versions
    gradle_content = re.sub(
        r'targetSdkVersion\s+.*',
        'targetSdkVersion 34',
        gradle_content
    )
    gradle_content = re.sub(
        r'targetSdk\s*=\s*.*',
        'targetSdk = 34',
        gradle_content
    )
    gradle_content = re.sub(
        r'compileSdkVersion\s+.*',
        'compileSdkVersion 34',
        gradle_content
    )
    gradle_content = re.sub(
        r'compileSdk\s*=\s*.*',
        'compileSdk = 34',
        gradle_content
    )

    with open(gradle_path, 'w') as f:
        f.write(gradle_content)

    print("build.gradle forced to SDK versions 21/34.")
