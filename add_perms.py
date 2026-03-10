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

    # Add permissions only if they don't exist
    if '<uses-permission' not in content:
        new_content = content.replace(
            '<application',
            perms + '    <application'
        )
        with open(manifest_path, 'w') as f:
            f.write(new_content)

    print("Permissions added.")

# 2. Upgrade Android SDK version to 34
gradle_path = 'android/app/build.gradle'

if os.path.exists(gradle_path):
    with open(gradle_path, 'r') as f:
        gradle_content = f.read()

    # Replace any compileSdkVersion or targetSdkVersion with 34
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

    print("SDK version upgraded to 34.")
