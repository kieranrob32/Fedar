import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk
from typing import Optional, Any, Dict, List

from src.handlers.dnf_handler import search_packages
from src.utils import run_in_thread
from src.cache import cache
from src.core.config import (
    CONTENT_MARGIN, CONTENT_SPACING,
    CSS_TITLE_2, CSS_DIM_LABEL, ICON_SEARCH,
    MAX_SEARCH_RESULTS
)
from src.ui.search_card import create_search_card
from src.ui.results_section import create_results_section
from src.widgets.package_row import create_package_row
from src.core.logger import logger


class SearchPage:
    def __init__(self, main_window: Any) -> None:
        self.main_window = main_window
        self.search_thread: Optional[Any] = None
        self.page = self._build_page()
    
    def _build_page(self) -> Gtk.Box:
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        container.append(scroll)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=CONTENT_SPACING)
        content.set_margin_start(CONTENT_MARGIN)
        content.set_margin_end(CONTENT_MARGIN)
        content.set_margin_top(60)
        content.set_margin_bottom(60)
        scroll.set_child(content)
        
        self._add_hero_section(content)
        self._add_search_section(content)
        self._add_results_section(content)
        
        key_controller = Gtk.EventControllerKey()
        key_controller.connect('key-pressed', self._on_key_press)
        container.add_controller(key_controller)
        
        return container
    
    def _add_hero_section(self, parent: Gtk.Box) -> None:
        clamp = Adw.Clamp()
        clamp.set_maximum_size(700)
        parent.append(clamp)
        
        hero = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        clamp.set_child(hero)
        
        title = Gtk.Label(label='Discover Packages')
        title.set_css_classes([CSS_TITLE_2])
        title.set_margin_bottom(8)
        hero.append(title)
        
        subtitle = Gtk.Label(label='Search and install packages from DNF repositories with ease')
        subtitle.add_css_class(CSS_DIM_LABEL)
        subtitle.set_margin_bottom(32)
        hero.append(subtitle)
    
    def _add_search_section(self, parent: Gtk.Box) -> None:
        self.search_entry = Gtk.Entry()
        search_card = create_search_card(self.search_entry, self._on_search)
        parent.append(search_card)
    
    def _add_results_section(self, parent: Gtk.Box) -> None:
        results = create_results_section()
        self.results_container = results['container']
        self.status_label = results['status_label']
        self.results_list = results['results_list']
        self.spinner = results['spinner']
        self.empty_state = results['empty_state']
        
        self.results_list.connect('row-activated', self._on_row_click)
        
        empty_icon = Gtk.Image.new_from_icon_name(ICON_SEARCH)
        empty_icon.set_pixel_size(56)
        empty_icon.add_css_class(CSS_DIM_LABEL)
        empty_icon.set_opacity(0.4)
        self.empty_state.append(empty_icon)
        
        empty_label = Gtk.Label(label='Enter a package name to search')
        empty_label.add_css_class(CSS_DIM_LABEL)
        empty_label.set_margin_top(12)
        self.empty_state.append(empty_label)
        
        parent.append(self.results_container)
    
    def _on_row_click(self, listbox: Gtk.ListBox, row: Gtk.ListBoxRow) -> None:
        package_name = getattr(row, '_package_name', None)
        if package_name:
            logger.debug(f"Opening package detail for: {package_name}")
            self.main_window.show_package_detail(package_name)
    
    def _on_key_press(self, controller: Gtk.EventControllerKey, keyval: int, keycode: int, state: Gdk.ModifierType) -> bool:
        if keyval == Gdk.KEY_f and state & Gdk.ModifierType.CONTROL_MASK:
            self.search_entry.grab_focus()
            return True
        return False
    
    def _on_search(self, widget: Gtk.Widget) -> None:
        query = self.search_entry.get_text().strip()
        if not query:
            return
        
        if self.search_thread and self.search_thread.is_alive():
            return
        
        cached = cache.get(query.lower())
        if cached is not None:
            self.results_container.set_visible(True)
            self._display_results(cached, query)
            return
        
        self._start_search(query)
    
    def _start_search(self, query: str) -> None:
        logger.debug(f"Starting search for: {query}")
        self.results_container.set_visible(True)
        self.status_label.set_text('Searching...')
        self.spinner.set_visible(True)
        self.spinner.start()
        self.empty_state.set_visible(False)
        
        self._clear_results()
        
        def search() -> List[Dict[str, Any]]:
            try:
                packages = search_packages(query)
                if len(packages) > MAX_SEARCH_RESULTS:
                    packages = packages[:MAX_SEARCH_RESULTS]
                cache.set(query.lower(), packages)
                return packages
            except Exception as e:
                logger.error(f"Search failed: {e}")
                raise Exception(str(e))
        
        self.search_thread = run_in_thread(
            search,
            callback=lambda packages: self._display_results(packages, query),
            error_callback=self._on_error
        )
    
    def _clear_results(self) -> None:
        while self.results_list.get_first_child():
            self.results_list.remove(self.results_list.get_first_child())
    
    def _display_results(self, packages: List[Dict[str, Any]], query: str) -> None:
        self.spinner.stop()
        self.spinner.set_visible(False)
        
        if not packages:
            self.status_label.set_text(f'No packages found for "{query}"')
            self.empty_state.set_visible(True)
            return
        
        self.status_label.set_text(f'Found {len(packages)} packages')
        self.empty_state.set_visible(False)
        
        for pkg in packages:
            row = create_package_row(pkg)
            self.results_list.append(row)
    
    def _on_error(self, error_msg: str) -> None:
        logger.error(f"Search error: {error_msg}")
        self.spinner.stop()
        self.spinner.set_visible(False)
        self.status_label.set_text(f'Error: {error_msg}')
        self.empty_state.set_visible(True)
