from gi.repository import Gtk, Gdk


def load_styles():
    css_provider = Gtk.CssProvider()
    css = b"""
    .fedar-tab-button {
        border-radius: 8px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .fedar-tab-button:active {
        transform: scale(0.98);
    }
    """
    css_provider.load_from_data(css, len(css))
    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(),
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
