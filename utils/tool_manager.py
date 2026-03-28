# utils/tool_manager.py
# Faol toollarni boshqaradi

_active_tools = {}  # {"ToolNomi": {"widget": ..., "popup": ...}}


def register(name, widget, popup):
    """Tool ochilganda ro'yxatga qo'shadi."""
    _active_tools[name] = {"widget": widget, "popup": popup}


def unregister(name):
    """Tool yopilganda ro'yxatdan o'chiradi."""
    _active_tools.pop(name, None)


def is_active(name):
    """Tool hozir ochiqmi?"""
    return name in _active_tools


def get_active():
    """Barcha faol toollar ro'yxati."""
    return dict(_active_tools)


def focus(name):
    """Orqa fondagi toolni oldinga chiqaradi."""
    tool = _active_tools.get(name)
    if tool and tool.get("popup"):
        tool["popup"].open()
        return True
    return False


def close(name):
    """Toolni to'liq yopadi."""
    tool = _active_tools.get(name)
    if tool and tool.get("popup"):
        tool["popup"].dismiss()
    unregister(name)