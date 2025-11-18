# Fedar

A modern GTK4 package manager for Fedora. Search, install, and manage DNF packages without touching the terminal.

**Status:** Alpha

## Screenshots
<img width="951" height="801" alt="image" src="https://github.com/user-attachments/assets/2fd576cd-35ae-4f7e-833a-bfb9c39e9fc8" />
<img width="946" height="792" alt="image" src="https://github.com/user-attachments/assets/94f6356d-b669-47e5-a53f-0ca52e27a001" />



## What is this?

Fedar is a graphical frontend for DNF that makes package management on Fedora actually pleasant. Instead of memorizing `dnf search` commands or dealing with terminal output, you get a clean interface that follows GNOME design guidelines.


## Requirements

- Fedora Linux (or any distro with DNF)
- Python 3.10+
- GTK4 and Libadwaita

### Installing dependencies

On Fedora:

```bash
sudo dnf install python3-gobject python3-libadwaita gtk4-devel libadwaita-devel
```

## Installation

Clone the repo and run:

```bash
git clone https://github.com/kieranrob32/fedar.git
cd fedar
python3 main.py
```

Or make it executable:

```bash
chmod +x main.py
./main.py
```

## How it works

Fedar uses DNF's Python API to search repositories and manage packages. All operations run in background threads to keep the UI responsive. Search results are cached for 5 minutes to avoid redundant queries.

The UI is built with GTK4 and Libadwaita, so it automatically matches your system theme and follows GNOME HIG.

## Contributing

This is still in alpha, so expect bugs. If you find something broken or have ideas for improvements, open an issue or send a PR.

## Donate

If you find Fedar useful, consider supporting development:

**[Donate at fedarproject.xyz/donate](https://fedarproject.xyz/donate)**

## License

MIT
