import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from src.core.config import CONTENT_MARGIN, CSS_TITLE_2, CSS_DIM_LABEL
from src.preferences import set_pref


class WelcomePage:
    def __init__(self, main_window):
        self.main_window = main_window
        self.page = self._build_page()
    
    def _build_page(self):
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(True)
        container.append(header)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=40)
        content.set_margin_start(CONTENT_MARGIN)
        content.set_margin_end(CONTENT_MARGIN)
        content.set_margin_top(60)
        content.set_margin_bottom(60)
        content.set_vexpand(True)
        container.append(content)
        
        clamp = Adw.Clamp()
        clamp.set_maximum_size(700)
        content.append(clamp)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=32)
        clamp.set_child(main_box)
        
        self._add_header(main_box)
        self._add_settings(main_box)
        self._add_continue_button(main_box)
        
        return container
    
    def _add_header(self, parent):
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        header_box.set_halign(Gtk.Align.CENTER)
        header_box.set_margin_bottom(8)
        parent.append(header_box)
        
        icon = Gtk.Image.new_from_icon_name('package-x-generic-symbolic')
        icon.set_pixel_size(64)
        icon.set_margin_bottom(8)
        header_box.append(icon)
        
        title = Gtk.Label(label='Welcome to Fedar')
        title.set_css_classes([CSS_TITLE_2])
        title.set_halign(Gtk.Align.CENTER)
        header_box.append(title)
        
        subtitle = Gtk.Label(label='A modern package manager for DNF. Configure your preferences below.')
        subtitle.add_css_class(CSS_DIM_LABEL)
        subtitle.set_halign(Gtk.Align.CENTER)
        subtitle.set_wrap(True)
        subtitle.set_justify(Gtk.Justification.CENTER)
        subtitle.set_max_width_chars(50)
        header_box.append(subtitle)
    
    def _add_settings(self, parent):
        prefs_group = Adw.PreferencesGroup()
        prefs_group.set_title('Preferences')
        prefs_group.set_description('Customize Fedar to your liking')
        parent.append(prefs_group)
        
        dark_mode_row = Adw.ActionRow()
        dark_mode_row.set_title('Dark Mode')
        dark_mode_row.set_subtitle('Use dark theme for the application')
        dark_switch = Gtk.Switch()
        dark_switch.set_active(True)
        dark_switch.set_valign(Gtk.Align.CENTER)
        dark_switch.connect('notify::active', self._on_dark_mode_toggle)
        dark_mode_row.add_suffix(dark_switch)
        prefs_group.add(dark_mode_row)
        
        auto_cache_row = Adw.ActionRow()
        auto_cache_row.set_title('Enable Caching')
        auto_cache_row.set_subtitle('Cache search results for faster performance')
        cache_switch = Gtk.Switch()
        cache_switch.set_active(True)
        cache_switch.set_valign(Gtk.Align.CENTER)
        cache_switch.connect('notify::active', self._on_cache_toggle)
        auto_cache_row.add_suffix(cache_switch)
        prefs_group.add(auto_cache_row)
    
    def _add_continue_button(self, parent):
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        button_box.set_margin_top(24)
        parent.append(button_box)
        
        continue_btn = Gtk.Button(label='Continue')
        continue_btn.set_css_classes(['suggested-action', 'pill'])
        continue_btn.set_size_request(220, 44)
        continue_btn.set_halign(Gtk.Align.CENTER)
        continue_btn.connect('clicked', self._on_continue)
        button_box.append(continue_btn)
    
    def _on_dark_mode_toggle(self, switch, param):
        style_manager = Adw.StyleManager.get_default()
        if switch.get_active():
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
            set_pref('dark_mode', 'true')
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
            set_pref('dark_mode', 'false')
    
    def _on_cache_toggle(self, switch, param):
        set_pref('enable_cache', 'true' if switch.get_active() else 'false')
    
    def _on_continue(self, button):
        self.main_window.show_features_page()
