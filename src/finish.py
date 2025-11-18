import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from src.config import CONTENT_MARGIN, CSS_TITLE_2, CSS_DIM_LABEL


class FinishPage:
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
        self._add_donate_section(main_box)
        self._add_begin_button(main_box)
        
        return container
    
    def _add_header(self, parent):
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        header_box.set_halign(Gtk.Align.CENTER)
        header_box.set_margin_bottom(8)
        parent.append(header_box)
        
        icon = Gtk.Image.new_from_icon_name('object-select-symbolic')
        icon.set_pixel_size(64)
        icon.set_margin_bottom(8)
        header_box.append(icon)
        
        title = Gtk.Label(label='All Set!')
        title.set_css_classes([CSS_TITLE_2])
        title.set_halign(Gtk.Align.CENTER)
        header_box.append(title)
        
        message = Gtk.Label(label='Fedar is ready to use. If you find it helpful, consider supporting the project.')
        message.add_css_class(CSS_DIM_LABEL)
        message.set_halign(Gtk.Align.CENTER)
        message.set_wrap(True)
        message.set_justify(Gtk.Justification.CENTER)
        message.set_max_width_chars(50)
        header_box.append(message)
    
    def _add_donate_section(self, parent):
        prefs_page = Adw.PreferencesPage()
        parent.append(prefs_page)
        
        donate_group = Adw.PreferencesGroup()
        donate_group.set_title('Support Fedar')
        donate_group.set_description('Help us continue development and improvement')
        prefs_page.add(donate_group)
        
        donate_row = Adw.ActionRow()
        donate_row.set_title('Donate')
        donate_row.set_subtitle('Support the development of Fedar')
        donate_btn = Gtk.Button(label='Donate')
        donate_btn.set_css_classes(['suggested-action'])
        donate_btn.set_valign(Gtk.Align.CENTER)
        donate_btn.connect('clicked', self._on_donate)
        donate_row.add_suffix(donate_btn)
        donate_group.add(donate_row)
    
    def _add_begin_button(self, parent):
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        button_box.set_margin_top(24)
        parent.append(button_box)
        
        begin_btn = Gtk.Button(label='Begin')
        begin_btn.set_css_classes(['suggested-action', 'pill'])
        begin_btn.set_size_request(220, 44)
        begin_btn.set_halign(Gtk.Align.CENTER)
        begin_btn.connect('clicked', self._on_begin)
        button_box.append(begin_btn)
    
    def _on_donate(self, button):
        uri = 'https://fedarproject.xyz/donate'
        launcher = Gtk.UriLauncher.new(uri)
        launcher.launch(self.main_window, None, None, None)
    
    def _on_begin(self, button):
        self.main_window.show_main_application()
