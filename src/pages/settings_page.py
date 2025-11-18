import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio

from src.core.config import CONTENT_MARGIN, CONTENT_SPACING, CSS_TITLE_3, CSS_DIM_LABEL
from src.preferences import get_pref, set_pref


class SettingsPage:
    def __init__(self, main_window):
        self.main_window = main_window
        self.page = self._build_page()
    
    def _build_page(self):
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        container.append(scroll)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=CONTENT_SPACING)
        content.set_margin_start(CONTENT_MARGIN)
        content.set_margin_end(CONTENT_MARGIN)
        content.set_margin_top(32)
        content.set_margin_bottom(32)
        scroll.set_child(content)
        
        title = Gtk.Label(label='Settings')
        title.set_css_classes([CSS_TITLE_3])
        title.set_xalign(0)
        title.set_margin_bottom(24)
        content.append(title)
        
        prefs_page = Adw.PreferencesPage()
        prefs_page.set_margin_start(0)
        prefs_page.set_margin_end(0)
        content.append(prefs_page)
        
        self._add_appearance_group(prefs_page)
        self._add_behavior_group(prefs_page)
        self._add_support_group(prefs_page)
        self._add_about_group(prefs_page)
        
        return container
    
    def _add_appearance_group(self, parent):
        group = Adw.PreferencesGroup()
        group.set_title('Appearance')
        group.set_description('Customize the appearance of Fedar')
        parent.add(group)
        
        dark_mode_row = Adw.ActionRow()
        dark_mode_row.set_title('Dark Mode')
        dark_mode_row.set_subtitle('Use dark theme for the application')
        dark_switch = Gtk.Switch()
        dark_switch.set_active(get_pref('dark_mode', 'true') == 'true')
        dark_switch.set_valign(Gtk.Align.CENTER)
        dark_switch.connect('notify::active', self._on_dark_mode_toggle)
        dark_mode_row.add_suffix(dark_switch)
        group.add(dark_mode_row)
    
    def _add_behavior_group(self, parent):
        group = Adw.PreferencesGroup()
        group.set_title('Behavior')
        group.set_description('Configure application behavior')
        parent.add(group)
        
        cache_row = Adw.ActionRow()
        cache_row.set_title('Enable Caching')
        cache_row.set_subtitle('Cache search results for faster performance')
        cache_switch = Gtk.Switch()
        cache_switch.set_active(get_pref('enable_cache', 'true') == 'true')
        cache_switch.set_valign(Gtk.Align.CENTER)
        cache_switch.connect('notify::active', self._on_cache_toggle)
        cache_row.add_suffix(cache_switch)
        group.add(cache_row)
        
        clear_cache_row = Adw.ActionRow()
        clear_cache_row.set_title('Clear Cache')
        clear_cache_row.set_subtitle('Clear cached search results')
        clear_btn = Gtk.Button(label='Clear')
        clear_btn.set_valign(Gtk.Align.CENTER)
        clear_btn.connect('clicked', self._on_clear_cache)
        clear_cache_row.add_suffix(clear_btn)
        group.add(clear_cache_row)
    
    def _add_support_group(self, parent):
        group = Adw.PreferencesGroup()
        group.set_title('Support')
        group.set_description('Support the development of Fedar')
        parent.add(group)
        
        donate_row = Adw.ActionRow()
        donate_row.set_title('Donate')
        donate_row.set_subtitle('Help support Fedar development')
        donate_btn = Gtk.Button(label='Donate')
        donate_btn.set_valign(Gtk.Align.CENTER)
        donate_btn.set_css_classes(['suggested-action'])
        donate_btn.connect('clicked', self._on_donate)
        donate_row.add_suffix(donate_btn)
        group.add(donate_row)
    
    def _add_about_group(self, parent):
        group = Adw.PreferencesGroup()
        group.set_title('About')
        group.set_description('Information about Fedar')
        parent.add(group)
        
        version_row = Adw.ActionRow()
        version_row.set_title('Version')
        version_row.set_subtitle('1.0.0')
        group.add(version_row)
        
        desc_row = Adw.ActionRow()
        desc_row.set_title('Description')
        desc_row.set_subtitle('A simple DNF package manager with a modern GTK interface')
        group.add(desc_row)
    
    def _on_dark_mode_toggle(self, switch, param):
        style_manager = Adw.StyleManager.get_default()
        if switch.get_active():
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
            set_pref('dark_mode', 'true')
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
            set_pref('dark_mode', 'false')
    
    def _on_cache_toggle(self, switch, param):
        enabled = 'true' if switch.get_active() else 'false'
        set_pref('enable_cache', enabled)
        from src.cache import cache
        cache.enabled = switch.get_active()
    
    def _on_clear_cache(self, button):
        from src.cache import cache
        cache.clear()
        dialog = Adw.MessageDialog(
            heading='Cache Cleared',
            body='All cached search results have been cleared.',
            transient_for=self.main_window
        )
        dialog.add_response('ok', 'OK')
        dialog.set_response_appearance('ok', Adw.ResponseAppearance.SUGGESTED)
        dialog.connect('response', lambda d, r: d.destroy())
        dialog.present()
    
    def _on_donate(self, button):
        uri = 'https://fedarproject.xyz/donate'
        launcher = Gtk.UriLauncher.new(uri)
        launcher.launch(self.main_window, None, None, None)


settings_page = SettingsPage
