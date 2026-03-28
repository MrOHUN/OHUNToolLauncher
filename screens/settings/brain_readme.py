from utils.helpers import t as tr

def get_text():
    return tr("brain_readme_text")

BRAIN_README_TEXT_EN = """OHUN Tool Launcher — What is it?

A plugin-based tool launcher for Android.
Main app knows nothing — it just launches tools.
Each tool is independent and lives in its own folder.

How it works:
1. App loads tools/ folder
2. Each tool has main.py + meta.json
3. Tool communicates via tool_api.py only

Technologies:
- Python + Kivy
- Pydroid 3 (Android)
- GitHub (tool/theme/lang store)
- Buildozer (v1.0 — coming soon)

Current version: v0.9"""