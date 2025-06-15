import os

# Constants
ASSETS_FOLDER = "assets"
HUMAN_IMAGE_PATH = os.path.join(ASSETS_FOLDER, "human.png")
BLUEYBOT_IMAGE_PATH = os.path.join(ASSETS_FOLDER, "blueybot.png")

# Check if the assets folder and images exist
print(f"Assets folder exists: {os.path.exists(ASSETS_FOLDER)}")
print(f"Assets folder absolute path: {os.path.abspath(ASSETS_FOLDER)}")

if os.path.exists(HUMAN_IMAGE_PATH):
    print(f"Human image found at: {os.path.abspath(HUMAN_IMAGE_PATH)}")
    print(f"Human image size: {os.path.getsize(HUMAN_IMAGE_PATH)} bytes")
else:
    print(f"Human image NOT found at: {os.path.abspath(HUMAN_IMAGE_PATH)}")

if os.path.exists(BLUEYBOT_IMAGE_PATH):
    print(f"Blueybot image found at: {os.path.abspath(BLUEYBOT_IMAGE_PATH)}")
    print(f"Blueybot image size: {os.path.getsize(BLUEYBOT_IMAGE_PATH)} bytes")
else:
    print(f"Blueybot image NOT found at: {os.path.abspath(BLUEYBOT_IMAGE_PATH)}")

# List all files in the assets folder
print("\nFiles in assets folder:")
for file in os.listdir(ASSETS_FOLDER):
    file_path = os.path.join(ASSETS_FOLDER, file)
    print(f"- {file} ({os.path.getsize(file_path)} bytes)")
