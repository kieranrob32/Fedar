import os
from gi.repository import GLib


PREF_DIR = os.path.join(GLib.get_user_config_dir(), 'fedar')
PREF_FILE = os.path.join(PREF_DIR, 'preferences.ini')


def _ensure_dir():
    os.makedirs(PREF_DIR, exist_ok=True)


def get_pref(key, default=None):
    _ensure_dir()
    if not os.path.exists(PREF_FILE):
        return default
    
    try:
        with open(PREF_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    if k.strip() == key:
                        return v.strip()
    except:
        pass
    
    return default


def set_pref(key, value):
    _ensure_dir()
    prefs = {}
    
    if os.path.exists(PREF_FILE):
        try:
            with open(PREF_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        k, v = line.split('=', 1)
                        prefs[k.strip()] = v.strip()
        except:
            pass
    
    prefs[key] = str(value)
    
    try:
        with open(PREF_FILE, 'w') as f:
            for k, v in prefs.items():
                f.write(f'{k}={v}\n')
    except:
        pass


def is_first_run():
    if not os.path.exists(PREF_FILE):
        return True
    return get_pref('first_run', 'true') == 'true'


def set_first_run_complete():
    set_pref('first_run', 'false')

