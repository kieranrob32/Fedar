import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from typing import Optional


class tab_bar:
    def __init__(self, main_window):
        self.main_window = main_window
        self.container = self.create_tab_bar()
    
    def create_tab_bar(self) -> Gtk.Box:
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        container.add_css_class('fedar-tab-container')
        
        tab_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        tab_box.add_css_class('fedar-tab-bar')
        tab_box.set_margin_start(20)
        tab_box.set_margin_end(20)
        tab_box.set_margin_top(8)
        tab_box.set_margin_bottom(8)
        container.append(tab_box)
        
        self.search_button = self._create_tab_button(
            'system-search-symbolic', 'Search', 'search'
        )
        self.search_button.set_active(True)
        tab_box.append(self.search_button)
        
        self.updates_button = self._create_tab_button(
            'system-software-update-symbolic', 'System Updates', 'updates'
        )
        self.updates_button.set_group(self.search_button)
        tab_box.append(self.updates_button)
        
        self.installed_button = self._create_tab_button(
            'package-x-generic-symbolic', 'Installed', 'installed'
        )
        self.installed_button.set_group(self.search_button)
        tab_box.append(self.installed_button)
        
        self.settings_button = self._create_tab_button(
            'emblem-system-symbolic', 'Settings', 'settings'
        )
        self.settings_button.set_group(self.search_button)
        tab_box.append(self.settings_button)
        
        return container
    
    def _create_tab_button(self, icon_name: str, label: str, tab_name: str) -> Gtk.ToggleButton:
        button = Gtk.ToggleButton()
        button.add_css_class('fedar-tab-button')
        
        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        content.set_margin_start(10)
        content.set_margin_end(10)
        content.set_margin_top(7)
        content.set_margin_bottom(7)
        
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(14)
        content.append(icon)
        
        label_widget = Gtk.Label(label=label)
        label_widget.add_css_class('title-4')
        content.append(label_widget)
        
        button.set_child(content)
        button.connect('clicked', lambda b: self.main_window.switch_to_tab(tab_name))
        
        return button
    
    def set_active(self, tab_name: str) -> None:
        buttons = {
            'search': self.search_button,
            'updates': self.updates_button,
            'installed': self.installed_button,
            'settings': self.settings_button
        }
        
        for name, button in buttons.items():
            button.set_active(name == tab_name)
