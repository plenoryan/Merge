# MergeApp

A standalone Windows executable for merging and processing PDFs.

## Features
- **Modern UI** built with Tkinter (clean, responsive window).
- Integrated PDF utilities (compress, add images, remove signatures, verify PDF/A).
- **LGPD compliance**: privacy notice on first run and a menu option to delete all stored data.
- **Icon customization**: users can replace `custom_icon.ico` in `%APPDATA%/MergeApp`.
- **Auto‑update**: checks the `plenaryan/merge` GitHub repository for newer releases and prompts the user to update.
- **Single‑file executable** (`MergeApp.exe`) – no external dependencies required.

## Installation
1. Download `MergeApp.exe` from the repository releases.
2. Run the file; it will create a config folder in `%APPDATA%\MergeApp`.
3. (Optional) Replace `custom_icon.ico` in that folder to change the window icon.

## Usage
- Launch the app.
- Use the **File** menu to access the PDF utilities.
- Choose **Check for Updates** to fetch the latest version.
- Choose **Delete Data (LGPD)** to clear any stored information.

## Development
The source lives in the `DevLatest` folder. To rebuild:
```powershell
# Re‑install dependencies if needed
python -m pip install pyinstaller
# Build
python -m PyInstaller --onefile --windowed --icon=icone\icone.ico --add-data "src/pdf_utils;pdf_utils" launcher.py
```
The resulting executable will be in `dist/launcher.exe`.

## License
MIT – see the LICENSE file in the repository.
