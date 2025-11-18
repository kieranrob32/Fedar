import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from src.core.config import ROW_PADDING, ICON_PACKAGE, ICON_CHEVRON, CSS_TITLE_4, CSS_DIM_LABEL


def create_package_row(pkg):
    row = Gtk.ListBoxRow()
    row._package_name = pkg['name']
    
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    box.set_margin_start(ROW_PADDING)
    box.set_margin_end(ROW_PADDING)
    box.set_margin_top(10)
    box.set_margin_bottom(10)
    row.set_child(box)
    
    icon = Gtk.Image.new_from_icon_name(ICON_PACKAGE)
    icon.set_pixel_size(28)
    box.append(icon)
    
    info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    info_box.set_hexpand(True)
    box.append(info_box)
    
    name_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    name_row.set_hexpand(True)
    info_box.append(name_row)
    
    display_name = pkg.get('display_name', pkg['name'])
    name = Gtk.Label(label=display_name)
    name.set_css_classes([CSS_TITLE_4])
    name.set_xalign(0)
    name.set_hexpand(True)
    name_row.append(name)
    
    if pkg.get('installed', False):
        badge = Gtk.Label(label='Installed')
        badge.add_css_class('dim-label')
        badge.add_css_class('caption')
        badge.set_margin_start(8)
        name_row.append(badge)
    
    if pkg.get('summary'):
        summary = Gtk.Label(label=pkg['summary'])
        summary.add_css_class(CSS_DIM_LABEL)
        summary.set_xalign(0)
        summary.set_wrap(True)
        summary.set_max_width_chars(70)
        summary.set_lines(1)
        summary.set_ellipsize(3)
        info_box.append(summary)
    
    chevron = Gtk.Image.new_from_icon_name(ICON_CHEVRON)
    chevron.add_css_class(CSS_DIM_LABEL)
    chevron.set_pixel_size(14)
    box.append(chevron)
    
    return row
