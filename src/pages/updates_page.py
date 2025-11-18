import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, GLib, Adw
from typing import List, Dict, Any, Optional

from src.handlers.dnf_handler import check_updates, update_system
from src.utils import run_in_thread
from src.handlers.notifications import show_success_notification, show_error_notification
from src.core.config import (
    CONTENT_MARGIN, CONTENT_SPACING,
    ICON_PACKAGE,
    CSS_DIM_LABEL, CSS_TITLE_3
)
from src.widgets.package_row import create_package_row
from src.core.logger import logger


class UpdatesPage:
    def __init__(self, main_window):
        self.main_window = main_window
        self.all_updates: List[Dict[str, Any]] = []
        self.progress_timeout: Optional[int] = None
        self.page = self._build_page()
        self._check_updates()
    
    def _build_page(self) -> Adw.ToastOverlay:
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=CONTENT_SPACING)
        content_box.set_margin_start(CONTENT_MARGIN)
        content_box.set_margin_end(CONTENT_MARGIN)
        content_box.set_margin_top(32)
        content_box.set_margin_bottom(32)
        main_box.append(content_box)
        
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        header_box.set_margin_bottom(20)
        content_box.append(header_box)
        
        title_label = Gtk.Label(label='System Updates')
        title_label.set_css_classes([CSS_TITLE_3])
        title_label.set_xalign(0)
        title_label.set_hexpand(True)
        header_box.append(title_label)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header_box.append(button_box)
        
        self.update_all_btn = Gtk.Button(label='Update System')
        self.update_all_btn.set_css_classes(['suggested-action'])
        self.update_all_btn.connect('clicked', self._on_update_system)
        button_box.append(self.update_all_btn)
        
        refresh_btn = Gtk.Button.new_from_icon_name('view-refresh-symbolic')
        refresh_btn.set_tooltip_text('Check for updates')
        refresh_btn.connect('clicked', self._on_refresh)
        button_box.append(refresh_btn)
        
        self.status_label = Gtk.Label()
        self.status_label.add_css_class(CSS_DIM_LABEL)
        self.status_label.set_xalign(0)
        self.status_label.set_margin_bottom(16)
        content_box.append(self.status_label)
        
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_visible(False)
        self.progress_bar.set_margin_bottom(16)
        content_box.append(self.progress_bar)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        content_box.append(scrolled)
        
        self.updates_list = Gtk.ListBox()
        self.updates_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.updates_list.add_css_class('boxed-list')
        self.updates_list.connect('row-activated', self._on_row_activated)
        scrolled.set_child(self.updates_list)
        
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
        
        empty_icon = Gtk.Image.new_from_icon_name('emblem-ok-symbolic')
        empty_icon.set_pixel_size(40)
        empty_icon.add_css_class(CSS_DIM_LABEL)
        self.empty_state.append(empty_icon)
        
        empty_label = Gtk.Label(label='All packages are up to date')
        empty_label.add_css_class(CSS_DIM_LABEL)
        self.empty_state.append(empty_label)
        
        self.toast_overlay = Adw.ToastOverlay()
        self.toast_overlay.set_child(main_box)
        
        return self.toast_overlay
    
    def _check_updates(self) -> None:
        
        logger.debug("Checking for updates")
        
        def do_check():
            try:
                return check_updates()
            except Exception as e:
                raise Exception(str(e))
        
        run_in_thread(
            do_check,
            callback=self._update_display,
            error_callback=self._show_error
        )
    
    def _update_display(self, updates: List[Dict[str, Any]]) -> None:
        
        logger.info(f"Displaying {len(updates)} available updates")
        
        self.spinner.stop()
        self.spinner.set_visible(False)
        self.all_updates = updates
        
        while self.updates_list.get_first_child():
            self.updates_list.remove(self.updates_list.get_first_child())
        
        if not updates:
            self.status_label.set_text('No updates available')
            self.empty_state.set_visible(True)
            self.update_all_btn.set_sensitive(False)
            return
        
        self.empty_state.set_visible(False)
        self.update_all_btn.set_sensitive(True)
        self.status_label.set_text(f'{len(updates)} package{"s" if len(updates) != 1 else ""} can be updated')
        
        for update in updates:
            row = self._create_update_row(update)
            self.updates_list.append(row)
    
    def _create_update_row(self, update: Dict[str, Any]) -> Gtk.ListBoxRow:
        
        row = Gtk.ListBoxRow()
        row._package_name = update['name']
        
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_margin_start(16)
        box.set_margin_end(16)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        
        icon = Gtk.Image.new_from_icon_name(ICON_PACKAGE)
        icon.set_pixel_size(24)
        box.append(icon)
        
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        text_box.set_hexpand(True)
        
        name_label = Gtk.Label(label=update['display_name'])
        name_label.set_css_classes(['title-4'])
        name_label.set_xalign(0)
        name_label.set_wrap(True)
        text_box.append(name_label)
        
        version_info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        if update.get('current_version'):
            current_label = Gtk.Label(label=f"Current: {update['current_version']}")
            current_label.add_css_class(CSS_DIM_LABEL)
            current_label.set_xalign(0)
            version_info.append(current_label)
        
        if update.get('available_version'):
            arrow = Gtk.Label(label='→')
            arrow.add_css_class(CSS_DIM_LABEL)
            version_info.append(arrow)
            
            available_label = Gtk.Label(label=f"Available: {update['available_version']}")
            available_label.add_css_class(CSS_DIM_LABEL)
            available_label.set_xalign(0)
            version_info.append(available_label)
        
        text_box.append(version_info)
        
        if update.get('summary'):
            summary_label = Gtk.Label(label=update['summary'])
            summary_label.add_css_class(CSS_DIM_LABEL)
            summary_label.set_xalign(0)
            summary_label.set_wrap(True)
            summary_label.set_max_width_chars(60)
            summary_label.set_lines(1)
            text_box.append(summary_label)
        
        box.append(text_box)
        
        chevron = Gtk.Image.new_from_icon_name('go-next-symbolic')
        chevron.set_pixel_size(16)
        chevron.set_opacity(0.5)
        box.append(chevron)
        
        row.set_child(box)
        return row
    
    def _on_row_activated(self, listbox: Gtk.ListBox, row: Gtk.ListBoxRow) -> None:
        
        package_name = getattr(row, '_package_name', None)
        if package_name:
            logger.debug(f"Opening update detail for: {package_name}")
            self.main_window.show_package_detail(package_name)
    
    def _on_refresh(self, button: Gtk.Button) -> None:
        
        logger.debug("Refreshing updates")
        self.spinner.set_visible(True)
        self.spinner.start()
        self.empty_state.set_visible(False)
        self.status_label.set_text('Checking for updates...')
        self._check_updates()
    
    def _on_update_system(self, button: Gtk.Button) -> None:
        
        if self.all_updates:
            dialog = Adw.MessageDialog(
                heading='Update System',
                body=f'Update all {len(self.all_updates)} available packages? This requires administrator privileges and may take some time.',
                transient_for=self.main_window
            )
            dialog.add_response('cancel', 'Cancel')
            dialog.add_response('update', 'Update')
            dialog.set_response_appearance('update', Adw.ResponseAppearance.SUGGESTED)
            dialog.connect('response', self._on_update_response)
            dialog.present()
        else:
            show_error_notification(
                self.toast_overlay,
                'No updates available'
            )
    
    def _on_update_response(self, dialog: Adw.MessageDialog, response: str) -> None:
        
        if response == 'update':
            self._start_system_update()
        dialog.destroy()
    
    def _start_system_update(self) -> None:
        
        logger.info("Starting system update")
        
        self.update_all_btn.set_sensitive(False)
        self.update_all_btn.set_label('Updating...')
        self.progress_bar.set_visible(True)
        self.progress_bar.pulse()
        
        def pulse_progress():
            self.progress_bar.pulse()
            return True
        
        self.progress_timeout = GLib.timeout_add(50, pulse_progress)
        
        def do_update():
            return update_system()
        
        run_in_thread(
            do_update,
            callback=lambda result: self._update_complete(result[0], result[1]),
            error_callback=lambda e: self._update_complete(False, str(e))
        )
    
    def _update_complete(self, success: bool, message: str) -> None:
        
        if self.progress_timeout:
            GLib.source_remove(self.progress_timeout)
            self.progress_timeout = None
        
        self.progress_bar.set_visible(False)
        self.update_all_btn.set_sensitive(True)
        self.update_all_btn.set_label('Update System')
        
        if success:
            logger.info("System update completed successfully")
            show_success_notification(
                self.toast_overlay,
                'System updated successfully'
            )
            self._check_updates()
            if hasattr(self.main_window, 'load_installed_packages'):
                self.main_window.load_installed_packages()
        else:
            logger.error(f"System update failed: {message}")
            show_error_notification(
                self.toast_overlay,
                f'Update failed: {message[:80] if message else "Unknown error"}'
            )
    
    def _show_error(self, error_msg: str) -> None:
        
        logger.error(f"Error checking updates: {error_msg}")
        self.spinner.stop()
        self.spinner.set_visible(False)
        self.empty_state.set_visible(True)
        
        while self.empty_state.get_first_child():
            self.empty_state.remove(self.empty_state.get_first_child())
        
        error_icon = Gtk.Image.new_from_icon_name('dialog-error-symbolic')
        error_icon.set_pixel_size(40)
        error_icon.add_css_class(CSS_DIM_LABEL)
        self.empty_state.append(error_icon)
        
        error_label = Gtk.Label(label=f'Error: {error_msg}')
        error_label.add_css_class(CSS_DIM_LABEL)
        self.empty_state.append(error_label)
        
        self.status_label.set_text('Failed to check for updates')
