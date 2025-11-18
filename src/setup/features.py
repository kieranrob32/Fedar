import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from src.core.config import CONTENT_MARGIN, CSS_TITLE_2, CSS_DIM_LABEL


class FeaturesPage:
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
        self._add_features(main_box)
        self._add_read_more_button(main_box)
        self._add_continue_button(main_box)
        
        return container
    
    def _add_header(self, parent):
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        header_box.set_halign(Gtk.Align.CENTER)
        header_box.set_margin_bottom(8)
        parent.append(header_box)
        
        icon = Gtk.Image.new_from_icon_name('system-search-symbolic')
        icon.set_pixel_size(64)
        icon.set_margin_bottom(8)
        header_box.append(icon)
        
        title = Gtk.Label(label='Getting Started')
        title.set_css_classes([CSS_TITLE_2])
        title.set_halign(Gtk.Align.CENTER)
        header_box.append(title)
        
        subtitle = Gtk.Label(label='Discover what makes Fedar powerful and easy to use')
        subtitle.add_css_class(CSS_DIM_LABEL)
        subtitle.set_halign(Gtk.Align.CENTER)
        subtitle.set_wrap(True)
        subtitle.set_justify(Gtk.Justification.CENTER)
        subtitle.set_max_width_chars(50)
        header_box.append(subtitle)
    
    def _add_features(self, parent):
        features_group = Adw.PreferencesGroup()
        features_group.set_title('Key Features')
        features_group.set_description('Everything you need to manage packages')
        parent.append(features_group)
        
        features = [
            ('system-search-symbolic', 'Search Packages', 'Find any package from DNF repositories instantly'),
            ('document-install-symbolic', 'One-Click Install', 'Install packages with a single click, no terminal needed'),
            ('folder-documents-symbolic', 'Manage Installed', 'View and uninstall your installed packages easily'),
            ('preferences-system-symbolic', 'Smart Caching', 'Faster searches with intelligent result caching')
        ]
        
        for icon_name, title, desc in features:
            row = Adw.ActionRow()
            row.set_title(title)
            row.set_subtitle(desc)
            
            icon = Gtk.Image.new_from_icon_name(icon_name)
            icon.set_pixel_size(24)
            row.add_prefix(icon)
            
            features_group.add(row)
    
    def _add_read_more_button(self, parent):
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        button_box.set_margin_top(16)
        button_box.set_halign(Gtk.Align.CENTER)
        parent.append(button_box)
        
        read_more_btn = Gtk.Button(label='Read More')
        read_more_btn.set_halign(Gtk.Align.CENTER)
        read_more_btn.connect('clicked', self._on_read_more)
        button_box.append(read_more_btn)
    
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
    
    def _on_read_more(self, button):
        self.main_window.show_features_details_page()
    
    def _on_continue(self, button):
        self.main_window.show_finish_page()
