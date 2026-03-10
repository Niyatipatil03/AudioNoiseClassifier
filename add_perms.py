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

    # Add permissions only if missing
    if '<uses-permission' not in content:
        new_content = content.replace(
            '<application',
            perms + '    <application'
        )
        with open(manifest_path, 'w') as f:
            f.write(new_content)

    print("Permissions added.")


# 2. Force local.properties (Flutter often overrides build.gradle values)
props_path = 'android/local.properties'

if os.path.exists(props_path):
    with open(props_path, 'a') as f:
        f.write("\nflutter.minSdkVersion=26\n")
        f.write("flutter.targetSdkVersion=34\n")
        f.write("flutter.compileSdkVersion=34\n")

    print("local.properties forced to version 26/34.")


# 3. Force build.gradle (both old and new syntax)
gradle_path = 'android/app/build.gradle'

if os.path.exists(gradle_path):
    with open(gradle_path, 'r') as f:
        gradle_content = f.read()

    # Replace minSdkVersion/minSdk with 26
    gradle_content = re.sub(
        r'minSdkVersion\s+.*',
        'minSdkVersion 26',
        gradle_content
    )
    gradle_content = re.sub(
        r'minSdk\s*=\s*.*',
        'minSdk = 26',
        gradle_content
    )

    # Replace target and compile versions with 34
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

    print("build.gradle forced to SDK versions 26/34.")
