# Directory Organiser

A PySide6-based GUI application for scanning and organizing directories according to custom rules. Perfect for validating asset naming conventions, file formats, and structure in game development or other structured environments.

## Features

- **Recursive directory scanning** — Walk through all subdirectories and check every file
- **Multiple scanning modes** — "Game-ready" and "Source" asset validation
- **Flexible naming rules** — Prefix/suffix checking, regex pattern matching, banned words detection
- **Image validation** — Power-of-two dimensions and resolution limits
- **Issue tracking** — Table view of all found issues with details
- **Quick fixes** — Rename, move, delete, or ignore files directly from the UI
- **State persistence** — Automatically saves and restores your last session
- **Dark/Light theme support** — Fusion-based UI with custom styling

## Requirements

- Python 3.8+
- PySide6
- Pillow (PIL)
- PyYAML

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Jelena04/directory_organiser.git
cd directory_organiser
```

2. Install dependencies:
```bash
pip install PySide6 Pillow PyYAML
```

3. Run the application:
```bash
python main.py
```

## Usage

### Basic Workflow

1. **Select a directory to scan** — Click "Browse" or paste a path directly
2. **Choose a config file** — Select your rules configuration (YAML format)
3. **Pick a scanning mode:**
   - *Game-ready assets* — Validates prefixes, suffixes, folders, and image specs
   - *Source assets* — Validates naming patterns and banned words
4. **Click "Scan"** — The app will scan and display any issues found
5. **Fix issues** using the action buttons:
   - **Rename** — Change filename to match naming rules
   - **Move** — Relocate file to correct folder based on prefix
   - **Delete** — Permanently delete the file
   - **Ignore** — Skip this issue without action
   - **Open in Explorer** — View file in Windows Explorer

### Config File Format

Create a YAML file to define your validation rules:

```yaml
game_ready:
  folders:
    M_: Materials
    SKM_: Meshes/Skeletal
    SM_: Meshes
    T_: Textures
  naming:
    prefixes:
      material: M_
      static_mesh: SM_
      texture: T_
    suffixes:
      base_color: _BC
      normal: _N
      roughness: _R
  textures:
    max_resolution: 512
    require_power_of_two: true
  allowed_formats:
    - .png
    - .tga
    - .fbx
  max_file_size_mb: 50

source:
  naming:
    pattern: '^[a-z0-9]+(_[a-z0-9]+)*_v\d{2}$'  # Regex pattern
    banned_words:
      - final
      - new
      - copy
      - test
  allowed_formats:
    - .blend
    - .ma
    - .psd
  max_file_size_mb: 100
```

See `my_config.yaml` for a complete example.

## Architecture

The application is split into three main components:

**`main.py`**
Entry point. Initializes the PySide6 application and main window.

**`scanner_func.py`**
Core scanning and file manipulation logic:
- `Scanner` class — Loads config, performs directory scanning, validates files
- `Issue` class — Data model representing a single issue

**`scanner_ui.py`**
User interface:
- `MainWindow` class — Builds and manages the GUI, handles user interactions

## Validation Rules

### Game-Ready Mode

| Rule | Description |
|------|-------------|
| File Format | File extension must be in `allowed_formats` |
| Prefix | Filename must start with a configured prefix |
| Suffix | Filename must end with a configured suffix |
| Folder Location | File must be in the correct subfolder for its prefix |
| File Size | File must not exceed `max_file_size_mb` |
| Image Dimensions | For images: must be power-of-two and within `max_resolution` |

### Source Mode

| Rule | Description |
|------|-------------|
| File Format | File extension must be in `allowed_formats` |
| Naming | Filename must match the regex pattern and not contain `banned_words` |
| File Size | File must not exceed `max_file_size_mb` |

## UI State

The application saves your session to `ui_state.json`:

- Selected directory and config file paths
- Issue list with full details
- Scan statistics (files scanned, issues found/solved)
- Selected scanning mode

This is automatically loaded when you restart the app.
