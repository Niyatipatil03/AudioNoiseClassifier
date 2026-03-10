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


# 2. Force Upgrade Android SDK versions (Min, Target, and Compile)
gradle_path = 'android/app/build.gradle'

if os.path.exists(gradle_path):
    with open(gradle_path, 'r') as f:
        gradle_content = f.read()

    # Handles cases like: 'minSdkVersion 16' or 'minSdkVersion flutter.minSdkVersion'
    gradle_content = re.sub(
        r'minSdkVersion\s+\S+',
        'minSdkVersion 21',
        gradle_content
    )
    gradle_content = re.sub(
        r'compileSdkVersion\s+\S+',
        'compileSdkVersion 34',
        gradle_content
    )
    gradle_content = re.sub(
        r'targetSdkVersion\s+\S+',
        'targetSdkVersion 34',
        gradle_content
    )

    # Also handle new Gradle DSL syntax:
    # minSdk = 21, targetSdk = 34, compileSdk = 34
    gradle_content = re.sub(
        r'minSdk\s*=\s*\S+',
        'minSdk = 21',
        gradle_content
    )
    gradle_content = re.sub(
        r'targetSdk\s*=\s*\S+',
        'targetSdk = 34',
        gradle_content
    )
    gradle_content = re.sub(
        r'compileSdk\s*=\s*\S+',
        'compileSdk = 34',
        gradle_content
    )

    with open(gradle_path, 'w') as f:
        f.write(gradle_content)

    print("SDK versions updated (Min=21, Target=34, Compile=34).")
