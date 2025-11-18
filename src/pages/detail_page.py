import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, GLib, Adw

from src.handlers.dnf_handler import get_package_info, install_package, uninstall_package
from src.utils import run_in_thread
from src.handlers.notifications import show_success_notification, show_error_notification
from src.core.config import ICON_PACKAGE, ICON_ERROR, CSS_TITLE_3, CSS_DIM_LABEL
from src.cache import cache


class PackageDetailPage(Gtk.Box):
    def __init__(self, package_name, nav_view, main_window):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.package_name = package_name
        self.nav_view = nav_view
        self.main_window = main_window
        self.package_info = None
        self.progress_timeout = None
        
        self._build_ui()
        self._load_package_info()
    
    def _build_ui(self):
        self.toast_overlay = Adw.ToastOverlay()
        self.append(self.toast_overlay)
        
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.toast_overlay.set_child(content_box)
        
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(True)
        content_box.append(header)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        content_box.append(scrolled)
        
        scroll_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        scroll_content.set_margin_start(36)
        scroll_content.set_margin_end(36)
        scroll_content.set_margin_top(32)
        scroll_content.set_margin_bottom(32)
        scrolled.set_child(scroll_content)
        
        self.spinner = Gtk.Spinner()
        self.spinner.set_size_request(36, 36)
        self.spinner.set_halign(Gtk.Align.CENTER)
        self.spinner.set_margin_top(50)
        self.spinner.start()
        scroll_content.append(self.spinner)
        
        self.info_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.info_container.set_visible(False)
        scroll_content.append(self.info_container)
        
        self._build_header()
        self._build_details()
        self._build_description()
    
    def _build_header(self):
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        self.info_container.append(header_box)
        
        icon = Gtk.Image.new_from_icon_name(ICON_PACKAGE)
        icon.set_pixel_size(36)
        header_box.append(icon)
        
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        title_box.set_hexpand(True)
        header_box.append(title_box)
        
        self.name_label = Gtk.Label()
        self.name_label.set_css_classes([CSS_TITLE_3])
        self.name_label.set_xalign(0)
        self.name_label.set_wrap(True)
        title_box.append(self.name_label)
        
        self.summary_label = Gtk.Label()
        self.summary_label.add_css_class(CSS_DIM_LABEL)
        self.summary_label.set_xalign(0)
        self.summary_label.set_wrap(True)
        title_box.append(self.summary_label)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        button_box.set_valign(Gtk.Align.CENTER)
        header_box.append(button_box)
        
        install_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        button_box.append(install_box)
        
        self.install_button = Gtk.Button(label='Install')
        self.install_button.set_css_classes(['suggested-action', 'pill'])
        self.install_button.set_size_request(100, 34)
        self.install_button.connect('clicked', self._on_install_clicked)
        install_box.append(self.install_button)
        
        self.install_progress = Gtk.ProgressBar()
        self.install_progress.set_visible(False)
        self.install_progress.set_size_request(100, 4)
        install_box.append(self.install_progress)
        
        uninstall_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        button_box.append(uninstall_box)
        
        self.uninstall_button = Gtk.Button(label='Uninstall')
        self.uninstall_button.set_css_classes(['destructive-action', 'pill'])
        self.uninstall_button.set_size_request(100, 34)
        self.uninstall_button.set_visible(False)
        self.uninstall_button.connect('clicked', self._on_uninstall_clicked)
        uninstall_box.append(self.uninstall_button)
        
        self.uninstall_progress = Gtk.ProgressBar()
        self.uninstall_progress.set_visible(False)
        self.uninstall_progress.set_size_request(100, 4)
        uninstall_box.append(self.uninstall_progress)
    
    def _build_details(self):
        details_group = Adw.PreferencesGroup()
        details_group.set_title('Package Information')
        details_group.set_margin_bottom(8)
        
        self.version_row = Adw.ActionRow(title='Version')
        details_group.add(self.version_row)
        
        self.arch_row = Adw.ActionRow(title='Architecture')
        details_group.add(self.arch_row)
        
        self.size_row = Adw.ActionRow(title='Size')
        details_group.add(self.size_row)
        
        self.repo_row = Adw.ActionRow(title='Repository')
        details_group.add(self.repo_row)
        
        self.license_row = Adw.ActionRow(title='License')
        details_group.add(self.license_row)
        
        self.url_row = Adw.ActionRow(title='Website')
        details_group.add(self.url_row)
        
        self.info_container.append(details_group)
    
    def _build_description(self):
        desc_group = Adw.PreferencesGroup()
        desc_group.set_title('Description')
        
        desc_box = Gtk.Box()
        desc_box.set_margin_start(16)
        desc_box.set_margin_end(16)
        desc_box.set_margin_top(10)
        desc_box.set_margin_bottom(10)
        
        self.desc_label = Gtk.Label()
        self.desc_label.set_xalign(0)
        self.desc_label.set_wrap(True)
        self.desc_label.set_selectable(True)
        desc_box.append(self.desc_label)
        
        desc_group.add(desc_box)
        self.info_container.append(desc_group)
    
    def _load_package_info(self):
        def do_load():
            try:
                return get_package_info(self.package_name)
            except Exception as e:
                raise Exception(str(e))
        
        run_in_thread(
            do_load,
            callback=self._update_info,
            error_callback=self._show_error
        )
    
    def _update_info(self, info):
        self.package_info = info
        self.spinner.stop()
        self.spinner.set_visible(False)
        self.info_container.set_visible(True)
        
        self.name_label.set_text(info.get('name', self.package_name))
        self.summary_label.set_text(info.get('summary', 'No summary available'))
        
        if info.get('installed', False):
            self.install_button.set_visible(False)
            self.uninstall_button.set_visible(True)
        else:
            self.install_button.set_visible(True)
            self.uninstall_button.set_visible(False)
        
        version = info.get('version') or 'Unknown'
        release = info.get('release') or ''
        if release and release != 'Unknown':
            version = f"{version}-{release}"
        self.version_row.set_subtitle(version)
        self.arch_row.set_subtitle(info.get('architecture') or 'Unknown')
        self.size_row.set_subtitle(info.get('size') or 'Unknown')
        self.repo_row.set_subtitle(info.get('repository') or 'Unknown')
        self.license_row.set_subtitle(info.get('license') or 'Unknown')
        
        url = info.get('url') or ''
        if url and url != 'Unknown':
            self.url_row.set_subtitle(url)
        else:
            self.url_row.set_visible(False)
        
        desc = info.get('description') or 'No description available.'
        self.desc_label.set_text(desc)
    
    def _show_error(self, error_msg):
        self.spinner.stop()
        self.spinner.set_visible(False)
        
        error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        error_box.set_halign(Gtk.Align.CENTER)
        error_box.set_margin_top(40)
        
        error_icon = Gtk.Image.new_from_icon_name(ICON_ERROR)
        error_icon.set_pixel_size(36)
        error_box.append(error_icon)
        
        error_label = Gtk.Label(label=f'Error: {error_msg}')
        error_label.add_css_class(CSS_DIM_LABEL)
        error_label.set_wrap(True)
        error_box.append(error_label)
        
        self.info_container.append(error_box)
        self.info_container.set_visible(True)
    
    def _on_install_clicked(self, button):
        if not self.package_info:
            return
        
        dialog = Adw.MessageDialog(
            heading='Install Package',
            body=f'Install {self.package_name}? This requires administrator privileges.',
            transient_for=self.main_window
        )
        dialog.add_response('cancel', 'Cancel')
        dialog.add_response('install', 'Install')
        dialog.set_response_appearance('install', Adw.ResponseAppearance.SUGGESTED)
        dialog.connect('response', self._on_install_response)
        dialog.present()
    
    def _on_install_response(self, dialog, response):
        if response == 'install':
            self._start_install()
        dialog.destroy()
    
    def _start_install(self):
        self.install_button.set_sensitive(False)
        self.install_button.set_label('Installing...')
        self.install_progress.set_visible(True)
        self.install_progress.pulse()
        
        def pulse_progress():
            self.install_progress.pulse()
            return True
        
        self.progress_timeout = GLib.timeout_add(50, pulse_progress)
        
        def do_install():
            return install_package(self.package_name)
        
        run_in_thread(
            do_install,
            callback=lambda result: self._install_complete(result[0], result[1]),
            error_callback=lambda e: self._install_complete(False, str(e))
        )
    
    def _install_complete(self, success, message):
        if self.progress_timeout:
            GLib.source_remove(self.progress_timeout)
            self.progress_timeout = None
        
        self.install_progress.set_visible(False)
        self.install_button.set_sensitive(True)
        self.install_button.set_label('Install')
        
        if success:
            show_success_notification(
                self.toast_overlay,
                f'{self.package_name} installed successfully'
            )
            self.install_button.set_visible(False)
            self.uninstall_button.set_visible(True)
            self._load_package_info()
            
            if hasattr(self.main_window, 'load_installed_packages'):
                self.main_window.load_installed_packages()
            
            cache.clear()
        else:
            show_error_notification(
                self.toast_overlay,
                f'Failed to install {self.package_name}: {message[:80] if message else "Unknown error"}'
            )
    
    def _on_uninstall_clicked(self, button):
        if not self.package_info:
            return
        
        dialog = Adw.MessageDialog(
            heading='Uninstall Package',
            body=f'Uninstall {self.package_name}? This requires administrator privileges.',
            transient_for=self.main_window
        )
        dialog.add_response('cancel', 'Cancel')
        dialog.add_response('uninstall', 'Uninstall')
        dialog.set_response_appearance('uninstall', Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect('response', self._on_uninstall_response)
        dialog.present()
    
    def _on_uninstall_response(self, dialog, response):
        if response == 'uninstall':
            self._start_uninstall()
        dialog.destroy()
    
    def _start_uninstall(self):
        self.uninstall_button.set_sensitive(False)
        self.uninstall_button.set_label('Uninstalling...')
        self.uninstall_progress.set_visible(True)
        self.uninstall_progress.pulse()
        
        def pulse_progress():
            self.uninstall_progress.pulse()
            return True
        
        self.progress_timeout = GLib.timeout_add(50, pulse_progress)
        
        def do_uninstall():
            return uninstall_package(self.package_name)
        
        run_in_thread(
            do_uninstall,
            callback=lambda result: self._uninstall_complete(result[0], result[1]),
            error_callback=lambda e: self._uninstall_complete(False, str(e))
        )
    
    def _uninstall_complete(self, success, message):
        if self.progress_timeout:
            GLib.source_remove(self.progress_timeout)
            self.progress_timeout = None
        
        self.uninstall_progress.set_visible(False)
        self.uninstall_button.set_sensitive(True)
        self.uninstall_button.set_label('Uninstall')
        
        if success:
            show_success_notification(
                self.toast_overlay,
                f'{self.package_name} uninstalled successfully'
            )
            self.uninstall_button.set_visible(False)
            self.install_button.set_visible(True)
            self._load_package_info()
            
            if hasattr(self.main_window, 'load_installed_packages'):
                self.main_window.load_installed_packages()
            
            cache.clear()
        else:
            show_error_notification(
                self.toast_overlay,
                f'Failed to uninstall {self.package_name}: {message[:80] if message else "Unknown error"}'
            )


package_detail_page = PackageDetailPage
