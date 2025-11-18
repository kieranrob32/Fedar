import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from src.core.config import CARD_PADDING, ICON_SEARCH


def create_search_card(entry, callback, placeholder='Search for packages...', show_button=True):
    clamp = Adw.Clamp()
    clamp.set_maximum_size(650)
    
    card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    card.add_css_class('card')
    clamp.set_child(card)
    
    container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    container.set_margin_start(CARD_PADDING)
    container.set_margin_end(CARD_PADDING)
    container.set_margin_top(CARD_PADDING)
    container.set_margin_bottom(CARD_PADDING)
    card.append(container)
    
    icon = Gtk.Image.new_from_icon_name(ICON_SEARCH)
    icon.set_pixel_size(20)
    icon.add_css_class('dim-label')
    container.append(icon)
    
    entry.set_placeholder_text(placeholder)
    entry.set_hexpand(True)
    if callback:
        entry.connect('activate', callback)
    container.append(entry)
    
    if show_button and callback:
        button = Gtk.Button(label='Search')
        button.set_css_classes(['suggested-action', 'pill'])
        button.set_size_request(90, 38)
        button.connect('clicked', callback)
        container.append(button)
    
    return clamp
