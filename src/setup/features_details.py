import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from src.core.config import CONTENT_MARGIN, CSS_TITLE_2, CSS_DIM_LABEL


class FeaturesDetailsPage:
    def __init__(self, main_window):
        self.main_window = main_window
        self.page = self._build_page()
    
    def _build_page(self):
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(True)
        container.append(header)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        container.append(scroll)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=40)
        content.set_margin_start(CONTENT_MARGIN)
        content.set_margin_end(CONTENT_MARGIN)
        content.set_margin_top(60)
        content.set_margin_bottom(60)
        scroll.set_child(content)
        
        clamp = Adw.Clamp()
        clamp.set_maximum_size(700)
        content.append(clamp)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=32)
        clamp.set_child(main_box)
        
        self._add_header(main_box)
        self._add_shortcuts(main_box)
        self._add_tips(main_box)
        
        return container
    
    def _add_header(self, parent):
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        header_box.set_halign(Gtk.Align.CENTER)
        header_box.set_margin_bottom(8)
        parent.append(header_box)
        
        title = Gtk.Label(label='More Information')
        title.set_css_classes([CSS_TITLE_2])
        title.set_halign(Gtk.Align.CENTER)
        header_box.append(title)
        
        subtitle = Gtk.Label(label='Learn more about using Fedar effectively')
        subtitle.add_css_class(CSS_DIM_LABEL)
        subtitle.set_halign(Gtk.Align.CENTER)
        subtitle.set_wrap(True)
        subtitle.set_justify(Gtk.Justification.CENTER)
        subtitle.set_max_width_chars(50)
        header_box.append(subtitle)
    
    def _add_shortcuts(self, parent):
        shortcuts_group = Adw.PreferencesGroup()
        shortcuts_group.set_title('Keyboard Shortcuts')
        shortcuts_group.set_description('Speed up your workflow')
        parent.append(shortcuts_group)
        
        shortcuts = [
            ('keyboard-symbolic', 'Ctrl+F', 'Focus the search bar instantly'),
            ('go-previous-symbolic', 'Esc', 'Go back or close detail pages')
        ]
        
        for icon_name, key, desc in shortcuts:
            row = Adw.ActionRow()
            row.set_title(key)
            row.set_subtitle(desc)
            
            icon = Gtk.Image.new_from_icon_name(icon_name)
            icon.set_pixel_size(24)
            row.add_prefix(icon)
            
            shortcuts_group.add(row)
    
    def _add_tips(self, parent):
        tips_group = Adw.PreferencesGroup()
        tips_group.set_title('Tips')
        tips_group.set_description('Get the most out of Fedar')
        parent.append(tips_group)
        
        tips = [
            ('dialog-information-symbolic', 'Search Tips', 'Use partial names to find packages quickly'),
            ('emblem-ok-symbolic', 'Installed Badge', 'Look for the "Installed" badge in search results'),
            ('view-refresh-symbolic', 'Cache Management', 'Clear cache in Settings if results seem outdated')
        ]
        
        for icon_name, title, desc in tips:
            row = Adw.ActionRow()
            row.set_title(title)
            row.set_subtitle(desc)
            
            icon = Gtk.Image.new_from_icon_name(icon_name)
            icon.set_pixel_size(24)
            row.add_prefix(icon)
            
            tips_group.add(row)

