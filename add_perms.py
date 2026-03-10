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


# 2. Upgrade Android SDK versions (Min, Target, and Compile)
gradle_path = 'android/app/build.gradle'

if os.path.exists(gradle_path):
    with open(gradle_path, 'r') as f:
        gradle_content = f.read()

    # Set Min SDK to 21 (required by the record library)
    gradle_content = re.sub(
        r'minSdkVersion\s+\d+',
        'minSdkVersion 21',
        gradle_content
    )

    # Set Compile & Target SDK to 34
    gradle_content = re.sub(
        r'compileSdkVersion\s+\d+',
        'compileSdkVersion 34',
        gradle_content
    )
    gradle_content = re.sub(
        r'targetSdkVersion\s+\d+',
        'targetSdkVersion 34',
        gradle_content
    )

    with open(gradle_path, 'w') as f:
        f.write(gradle_content)

    print("SDK versions upgraded (Min: 21, Target: 34).")
