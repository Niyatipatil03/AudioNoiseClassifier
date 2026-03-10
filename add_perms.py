import os

path = 'android/app/src/main/AndroidManifest.xml'
print("Adding permissions to:", path)

with open(path, 'r') as f:
    content = f.read()

# Real XML tags (not HTML escaped)
perms = """
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.INTERNET" />
"""

# Insert permissions ONLY if they are not already present
if '<uses-permission' not in content:
    new_content = content.replace('<application', perms + '    <application')
    with open(path, 'w') as f:
        f.write(new_content)

    print("Permissions added successfully.")
else:
    print("Permissions already exist.")
