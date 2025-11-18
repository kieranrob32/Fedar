import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw


def show_toast(overlay, message, timeout=3):
    toast = Adw.Toast.new(message)
    toast.set_timeout(timeout)
    overlay.add_toast(toast)


def show_success_notification(overlay, message):
    toast = Adw.Toast.new(message)
    toast.set_timeout(4)
    overlay.add_toast(toast)


def show_error_notification(overlay, message):
    toast = Adw.Toast.new(f'Error: {message[:100]}')
    toast.set_timeout(5)
    overlay.add_toast(toast)
