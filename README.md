# Document Perspective Scanner

A lightweight cross-platform desktop application for straightening photographed or scanned documents. Select the four corners of a page and the app applies a perspective transform to produce a flat, rectangular image.

## Features

- Open PNG, JPEG, BMP, TIFF, and WebP images
- Drag and drop an image onto the app window
- Rotate an image left or right before processing
- Select corners in any order and drag markers for precise adjustment
- Use the live magnifier and crosshair for precise corner placement
- Preview the perspective-corrected result
- Save the result as PNG, JPEG, or TIFF
- Preserve the original source image

## Requirements

- Python 3.10 or newer
- Tkinter (included with standard Python installations on Windows and macOS; it may need to be installed separately on Linux)

The Python packages used by the app are listed in [`requirements.txt`](requirements.txt): NumPy, OpenCV, Pillow, and tkinterdnd2.

## Installation

Clone the repository and open a terminal in its directory:

```powershell
git clone https://github.com/acrimu/DocScanner.git
cd DocScanner
```

Creating a virtual environment is recommended.

### Windows (PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Linux and macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Debian or Ubuntu, install Tkinter separately if it is unavailable:

```bash
sudo apt install python3-tk
```

## Running the app

Run the application on any supported platform with:

```bash
python doc_scanner.py
```

On systems where Python 3 is exposed as `python3`, use `python3 doc_scanner.py` instead.

Windows users can also double-click [`run_app.bat`](run_app.bat). The batch launcher automatically uses `.venv\Scripts\python.exe` when that virtual environment exists. Otherwise, it looks for the Python launcher (`py`) and then `python` on `PATH`.

Linux and macOS users can run [`run_app.sh`](run_app.sh) from a terminal. It automatically uses `.venv/bin/python` when that virtual environment exists; otherwise, it looks for `python3` and then `python` on `PATH`:

```bash
./run_app.sh
```

### Build a macOS app

On a Mac, run the build script from the project directory:

```bash
./build_mac_app.sh
```

The script creates an isolated `.build-venv`, installs the requirements and PyInstaller, and builds `dist/Document Perspective Scanner.app`. Open it with:

```bash
open "dist/Document Perspective Scanner.app"
```

Build on macOS for the processor architecture you intend to support. Apps shared with other people may need to be signed and notarized to avoid Gatekeeper warnings.

### Build a Windows app

On Windows, double-click [`build_windows_app.bat`](build_windows_app.bat) or run it from Command Prompt in the project directory. It creates an isolated `.build-venv`, installs the requirements and PyInstaller, and builds:

```text
dist\Document Perspective Scanner\Document Perspective Scanner.exe
```

Build on Windows for the processor architecture you intend to support. Share the entire `Document Perspective Scanner` folder inside `dist`, not just the `.exe`, because PyInstaller's default build includes supporting files alongside it.

### Build a Linux app

On Linux, install Tkinter if needed (on Debian or Ubuntu: `sudo apt install python3-tk`) and run:

```bash
./build_linux_app.sh
```

The script creates an isolated `.build-venv-linux`, installs the requirements and PyInstaller, and builds `dist/Document Perspective Scanner/Document Perspective Scanner`. Share the entire `Document Perspective Scanner` folder inside `dist`, not just the executable, because PyInstaller's default build includes supporting files alongside it.

Build on Linux for the distribution and processor architecture you intend to support. PyInstaller does not bundle all system libraries, so the built app may also require system libraries available on the target Linux distribution.

## Usage

1. Drag an image onto the application window, or select **Open image**.
2. Use **Rotate left** or **Rotate right** if the page is not upright.
3. Click the four corners of the document in any order.
4. Use the magnified inset and crosshair while placing or dragging the yellow corner markers.
5. Select **Extract page** to correct the perspective.
6. Preview the result and select **Save result**.

## How it works

The app orders the selected points around the page, calculates the target dimensions from the opposing edges, and uses OpenCV to compute and apply a perspective transform. The processed image remains in memory until you choose where to save it.

## Troubleshooting

### Python was not found on Windows

Install Python 3 from [python.org](https://www.python.org/downloads/). During installation, enable **Add Python to PATH**, then run `run_app.bat` again.

### A Python module is missing

Install all project dependencies with the same Python interpreter used to run the app:

```powershell
python -m pip install -r requirements.txt
```

### Drag and drop is unavailable

The app still works through **Open image** if `tkinterdnd2` cannot be loaded. Reinstall the dependencies to restore drag-and-drop support.

## Project structure

```text
DocScanner/
|-- doc_scanner.py    # GUI and perspective-correction logic
|-- run_app.bat       # Windows launcher
|-- run_app.sh        # Linux and macOS launcher
|-- build_mac_app.sh  # macOS app builder
|-- build_windows_app.bat # Windows app builder
|-- build_linux_app.sh # Linux app builder
|-- requirements.txt  # Python dependencies
|-- LICENSE
`-- README.md
```

## License

This project is licensed under the terms of the [MIT License](LICENSE).
