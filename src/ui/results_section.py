import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from src.core.config import CSS_TITLE_4, CSS_DIM_LABEL


def create_results_section():
    results_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
    results_box.set_margin_top(24)
    results_box.set_visible(False)
    results_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    results_header.set_margin_bottom(4)
    results_box.append(results_header)
    results_title = Gtk.Label(label='Results')
    results_title.set_css_classes([CSS_TITLE_4])
    results_title.set_xalign(0)
    results_title.set_hexpand(True)
    results_header.append(results_title)
    status_label = Gtk.Label()
    status_label.add_css_class(CSS_DIM_LABEL)
    results_header.append(status_label)
    scrolled = Gtk.ScrolledWindow()
    scrolled.set_vexpand(True)
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled.set_max_content_height(600)
    results_box.append(scrolled)
    results_list = Gtk.ListBox()
    results_list.set_selection_mode(Gtk.SelectionMode.NONE)
    results_list.add_css_class('boxed-list')
    scrolled.set_child(results_list)
    spinner = Gtk.Spinner()
    spinner.set_size_request(32, 32)
    spinner.set_halign(Gtk.Align.CENTER)
    spinner.set_margin_top(50)
    spinner.set_visible(False)
    results_box.append(spinner)
    empty_state = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
    empty_state.set_halign(Gtk.Align.CENTER)
    empty_state.set_margin_top(80)
    empty_state.set_visible(False)
    results_box.append(empty_state)
    return {
        'container': results_box,
        'status_label': status_label,
        'results_list': results_list,
        'spinner': spinner,
        'empty_state': empty_state
    }
