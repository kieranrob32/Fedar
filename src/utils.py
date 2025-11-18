import threading
import re
from gi.repository import GLib


def run_in_thread(func, callback=None, error_callback=None):
    def wrapper():
        try:
            result = func()
            if callback:
                GLib.idle_add(callback, result)
        except Exception as e:
            if error_callback:
                GLib.idle_add(error_callback, str(e))
    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()
    return thread


def debounce(wait_ms):
    def decorator(func):
        timer_ids = {}
        def debounced(self, *args, **kwargs):
            instance_id = id(self)
            if instance_id in timer_ids:
                GLib.source_remove(timer_ids[instance_id])
            timer_ids[instance_id] = GLib.timeout_add(
                wait_ms, 
                lambda: func(self, *args, **kwargs) or False
            )
            return timer_ids[instance_id]
        return debounced
    return decorator


def clean_package_name(name):
    if not name:
        return name
    arch_patterns = [
        r'\.x86_64$',
        r'\.noarch$',
        r'\.aarch64$',
        r'\.armv7hl$',
        r'\.i686$',
        r'\.ppc64le$',
        r'\.s390x$',
        r'\.riscv64$',
    ]
    cleaned = name
    for pattern in arch_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    return cleaned
