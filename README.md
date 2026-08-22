# Document Perspective Scanner

A lightweight application for straightening photographed or scanned documents. Select the four corners of a page and the app applies a perspective transform to produce a flat, rectangular image.

## Features

- Open PNG, JPEG, BMP, TIFF, and WebP images
- Drag and drop an image onto the app window
- Rotate an image left or right before processing
- Select corners in any order and drag markers for precise adjustment
- Preview the perspective-corrected result
- Save the result as PNG, JPEG, or TIFF
- Preserve the original source image

## Requirements

- Windows 10 or later
- Python 3.10 or newer
- Tkinter (included with standard Python installations from [python.org](https://www.python.org/))

The Python packages used by the app are listed in [`requirements.txt`](requirements.txt): NumPy, OpenCV, Pillow, and tkinterdnd2.

## Installation

Clone the repository and open a terminal in its directory:

```powershell
git clone https://github.com/acrimu/DocScanner.git
cd DocScanner
```

Creating a virtual environment is recommended:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Running the app

Double-click `run_app.bat`, or run the application from PowerShell:

```powershell
python doc_scanner.py
```

The batch launcher automatically uses `.venv\Scripts\python.exe` when that virtual environment exists. Otherwise, it looks for the Python launcher (`py`) and then `python` on `PATH`.

## Usage

1. Drag an image onto the application window, or select **Open image**.
2. Use **Rotate left** or **Rotate right** if the page is not upright.
3. Click the four corners of the document in any order.
4. Drag the yellow corner markers to refine the selection.
5. Select **Extract page** to correct the perspective.
6. Preview the result and select **Save result**.

## How it works

The app orders the selected points around the page, calculates the target dimensions from the opposing edges, and uses OpenCV to compute and apply a perspective transform. The processed image remains in memory until you choose where to save it.

## Troubleshooting

### Python was not found

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
|-- requirements.txt  # Python dependencies
|-- LICENSE
`-- README.md
```

## License

This project is licensed under the terms of the [MIT License](LICENSE).
