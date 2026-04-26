from utils.helpers import t as tr

def get_text():
    return tr("brain_devguide_text")

BRAIN_DEVGUIDE_TEXT_EN = """How to create a tool for OHUN Launcher

1. FOLDER STRUCTURE:
tools/
└── your_tool/
    ├── main.py
    └── meta.json

2. META.JSON:
{
    "name": "Your Tool",
    "icon": ">>",
    "color": "#2277ff",
    "version": "1.0",
    "author": "YourName",
    "description": "What does your tool do"
}

3. MAIN.PY (minimal):
def open_ui():
    # your Kivy UI here
    pass

4. TOOL API (optional):
from tool_api import get_tool_dir, save_tool_data, load_tool_data, notify

- get_tool_dir(__file__)       → your tool folder path
- save_tool_data(__file__, 'data.json', {...})
- load_tool_data(__file__, 'data.json', default={})
- notify("message")            → status bar message

5. RULES:
- Tool must not crash the launcher
- All errors must be caught inside the tool
- UI opens via open_ui() function only"""