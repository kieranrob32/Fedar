import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk
from typing import Optional

from src.tab_bar import tab_bar
from src.pages.search_page import SearchPage
from src.pages.updates_page import UpdatesPage
from src.pages.installed_page import InstalledPage
from src.pages.settings_page import SettingsPage
from src.pages.detail_page import PackageDetailPage
from src.setup.welcome import WelcomePage
from src.setup.features import FeaturesPage
from src.setup.features_details import FeaturesDetailsPage
from src.setup.finish import FinishPage
from src.core.config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from src.core.logger import logger
from src.preferences import is_first_run, get_pref


class FedarWindow(Adw.ApplicationWindow):
    def __init__(self, app: Adw.Application) -> None:
        super().__init__(application=app, title='Fedar')
        logger.debug("Initializing FedarWindow")
        
        try:
            self.set_default_size(WINDOW_WIDTH, WINDOW_HEIGHT)
            self.set_size_request(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
            self.set_decorated(True)
            self.set_resizable(True)
            
            self._apply_theme()
            
            self.nav_view = Adw.NavigationView()
            self.set_content(self.nav_view)
            
            key_controller = Gtk.EventControllerKey()
            key_controller.connect('key-pressed', self._on_key_press)
            self.add_controller(key_controller)
            
            if is_first_run():
                logger.info("First run detected, showing welcome page")
                self._show_welcome()
            else:
                logger.debug("Showing main application")
                self._show_main_app()
            
            logger.debug("FedarWindow initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize window: {e}")
            raise
    
    def _apply_theme(self) -> None:
        try:
            style_manager = Adw.StyleManager.get_default()
            dark_mode = get_pref('dark_mode', 'true') == 'true'
            
            if dark_mode:
                style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
                logger.debug("Applied dark theme")
            else:
                style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
                logger.debug("Applied light theme")
        except Exception as e:
            logger.warning(f"Failed to apply theme: {e}")
    
    def _show_welcome(self) -> None:
        try:
            logger.debug("Creating welcome page")
            welcome = WelcomePage(self)
            nav_page = Adw.NavigationPage(child=welcome.page, title='Welcome')
            self.nav_view.push(nav_page)
            logger.debug("Welcome page displayed")
        except Exception as e:
            logger.error(f"Failed to show welcome page: {e}")
            raise
    
    def _show_main_app(self) -> None:
        try:
            logger.debug("Creating main application page")
            main_page = self._create_main_page()
            nav_page = Adw.NavigationPage(child=main_page, title='Fedar')
            self.nav_view.push(nav_page)
            logger.debug("Main application displayed")
        except Exception as e:
            logger.error(f"Failed to show main app: {e}")
            raise
    
    def show_features_page(self) -> None:
        try:
            logger.debug("Showing features page")
            features = FeaturesPage(self)
            nav_page = Adw.NavigationPage(child=features.page, title='Getting Started')
            self.nav_view.push(nav_page)
        except Exception as e:
            logger.error(f"Failed to show features page: {e}")
            raise
    
    def show_features_details_page(self) -> None:
        try:
            logger.debug("Showing features details page")
            details = FeaturesDetailsPage(self)
            nav_page = Adw.NavigationPage(child=details.page, title='More Information')
            self.nav_view.push(nav_page)
        except Exception as e:
            logger.error(f"Failed to show features details page: {e}")
            raise
    
    def show_finish_page(self) -> None:
        try:
            logger.debug("Showing finish page")
            self.nav_view.pop()
            finish = FinishPage(self)
            nav_page = Adw.NavigationPage(child=finish.page, title='Ready')
            self.nav_view.push(nav_page)
        except Exception as e:
            logger.error(f"Failed to show finish page: {e}")
            raise
    
    def show_main_application(self) -> None:
        try:
            logger.info("Completing setup, showing main application")
            self.nav_view.pop()
            self._show_main_app()
        except Exception as e:
            logger.error(f"Failed to show main application: {e}")
            raise
    
    def _create_main_page(self) -> Gtk.Box:
        try:
            logger.debug("Building main page components")
            container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            
            header = Adw.HeaderBar()
            header.set_show_end_title_buttons(True)
            header.set_title_widget(Gtk.Label(label='Fedar'))
            container.append(header)
            
            self.tab_bar = tab_bar(self)
            container.append(self.tab_bar.container)
            
            self.view_stack = Adw.ViewStack()
            
            logger.debug("Initializing search page")
            self.search_page_obj = SearchPage(self)
            self.view_stack.add_titled(self.search_page_obj.page, 'search', 'Search')
            
            logger.debug("Initializing updates page")
            self.updates_page_obj = UpdatesPage(self)
            self.view_stack.add_titled(self.updates_page_obj.page, 'updates', 'System Updates')
            
            logger.debug("Initializing installed page")
            self.installed_page_obj = InstalledPage(self)
            self.view_stack.add_titled(self.installed_page_obj.page, 'installed', 'Installed')
            
            logger.debug("Initializing settings page")
            self.settings_page_obj = SettingsPage(self)
            self.view_stack.add_titled(self.settings_page_obj.page, 'settings', 'Settings')
            
            container.append(self.view_stack)
            logger.debug("Main page created successfully")
            return container
        except Exception as e:
            logger.error(f"Failed to create main page: {e}")
            raise
    
    def switch_to_tab(self, tab_name: str) -> None:
        try:
            logger.debug(f"Switching to tab: {tab_name}")
            valid_tabs = ['search', 'updates', 'installed', 'settings']
            
            if tab_name in valid_tabs:
                self.view_stack.set_visible_child_name(tab_name)
                self.tab_bar.set_active(tab_name)
            else:
                logger.warning(f"Unknown tab name: {tab_name}")
        except Exception as e:
            logger.error(f"Failed to switch tab: {e}")
    
    def show_package_detail(self, package_name: str) -> None:
        try:
            logger.debug(f"Showing package detail for: {package_name}")
            detail_page = PackageDetailPage(package_name, self.nav_view, self)
            nav_page = Adw.NavigationPage(child=detail_page, title=package_name)
            self.nav_view.push(nav_page)
        except Exception as e:
            logger.error(f"Failed to show package detail for {package_name}: {e}")
            raise
    
    def load_installed_packages(self) -> None:
        try:
            if hasattr(self, 'installed_page_obj'):
                logger.debug("Reloading installed packages")
                self.installed_page_obj.load_installed_packages()
        except Exception as e:
            logger.error(f"Failed to load installed packages: {e}")
    
    def refresh_updates(self) -> None:
        try:
            if hasattr(self, 'updates_page_obj'):
                logger.debug("Refreshing updates")
                self.updates_page_obj._check_updates()
        except Exception as e:
            logger.error(f"Failed to refresh updates: {e}")
    
    def _on_key_press(self, controller: Gtk.EventControllerKey, keyval: int, keycode: int, state: Gdk.ModifierType) -> bool:
        if keyval == Gdk.KEY_Escape:
            try:
                logger.debug("Escape key pressed, navigating back")
                self.nav_view.pop()
                return True
            except Exception as e:
                logger.debug(f"Could not navigate back: {e}")
        return False
