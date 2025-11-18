import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, GLib, Adw

from src.handlers.dnf_handler import get_installed_packages
from src.utils import run_in_thread, debounce
from src.core.config import (
    CONTENT_MARGIN, CONTENT_SPACING,
    ICON_PACKAGE,
    CSS_DIM_LABEL, CSS_TITLE_3,
    SEARCH_DEBOUNCE_MS
)
from src.ui.search_card import create_search_card
from src.widgets.package_row import create_package_row


class InstalledPage:
    def __init__(self, main_window):
        self.main_window = main_window
        self.all_installed_packages = []
        self.page = self.create_page()
        self.load_installed_packages()
    
    def create_page(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=CONTENT_SPACING)
        content_box.set_margin_start(CONTENT_MARGIN)
        content_box.set_margin_end(CONTENT_MARGIN)
        content_box.set_margin_top(32)
        content_box.set_margin_bottom(32)
        main_box.append(content_box)
        title_label = Gtk.Label(label='Installed Packages')
        title_label.set_css_classes([CSS_TITLE_3])
        title_label.set_xalign(0)
        title_label.set_margin_bottom(20)
        content_box.append(title_label)
        self.search_entry = Gtk.Entry()
        self.search_entry.connect('changed', self.on_search_debounced)
        search_card = create_search_card(
            self.search_entry, 
            None, 
            placeholder='Search installed packages...',
            show_button=False
        )
        search_card.set_margin_bottom(16)
        content_box.append(search_card)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        content_box.append(scrolled)
        self.packages_list = Gtk.ListBox()
        self.packages_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.packages_list.add_css_class('boxed-list')
        self.packages_list.connect('row-activated', self.on_row_activated)
        scrolled.set_child(self.packages_list)
        self.spinner = Gtk.Spinner()
        self.spinner.set_size_request(32, 32)
        self.spinner.set_halign(Gtk.Align.CENTER)
        self.spinner.set_margin_top(50)
        self.spinner.set_visible(True)
        self.spinner.start()
        content_box.append(self.spinner)
        self.empty_state = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.empty_state.set_halign(Gtk.Align.CENTER)
        self.empty_state.set_margin_top(80)
        self.empty_state.set_visible(False)
        content_box.append(self.empty_state)
        empty_icon = Gtk.Image.new_from_icon_name(ICON_PACKAGE)
        empty_icon.set_pixel_size(40)
        empty_icon.add_css_class(CSS_DIM_LABEL)
        self.empty_state.append(empty_icon)
        empty_label = Gtk.Label(label='No packages found')
        empty_label.add_css_class(CSS_DIM_LABEL)
        self.empty_state.append(empty_label)
        return main_box
    
    def load_installed_packages(self):
        def do_load():
            try:
                return get_installed_packages()
            except Exception as e:
                raise Exception(str(e))
        run_in_thread(
            do_load,
            callback=self.update_packages,
            error_callback=self.show_error
        )
    
    def update_packages(self, packages):
        self.spinner.stop()
        self.spinner.set_visible(False)
        self.all_installed_packages = packages
        self.filter_packages()
    
    @debounce(SEARCH_DEBOUNCE_MS)
    def on_search_debounced(self, entry):
        self.filter_packages()
    
    def on_search(self, entry):
        pass
    
    def filter_packages(self):
        while self.packages_list.get_first_child():
            self.packages_list.remove(self.packages_list.get_first_child())
        query = self.search_entry.get_text().strip().lower()
        if query:
            filtered = [pkg for pkg in self.all_installed_packages 
                       if query in pkg['name'].lower() or 
                       (pkg.get('summary') and query in pkg['summary'].lower())]
        else:
            filtered = self.all_installed_packages
        if not filtered:
            self.empty_state.set_visible(True)
            return
        self.empty_state.set_visible(False)
        rows = [create_package_row(pkg) for pkg in filtered]
        for row in rows:
            self.packages_list.append(row)
    
    def on_row_activated(self, listbox, row):
        package_name = getattr(row, '_package_name', None)
        if package_name:
            self.main_window.show_package_detail(package_name)
    
    def show_error(self, error_msg):
        self.spinner.stop()
        self.spinner.set_visible(False)
        self.empty_state.set_visible(True)
        error_label = Gtk.Label(label=f'Error: {error_msg}')
        error_label.add_css_class('error')
        self.empty_state.append(error_label)
