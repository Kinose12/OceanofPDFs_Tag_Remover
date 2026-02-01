# Installation Guide

Complete installation instructions for OceanofPDFs Tag Remover & Renamer v2.1

---

## 📋 System Requirements

- **Python**: 3.10 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Disk Space**: ~500MB for dependencies (varies by features installed)
- **RAM**: 2GB minimum, 4GB recommended for large batches

---

## 🚀 Quick Install (Basic Features)

For basic watermark removal and renaming:

```bash
pip install pymupdf tqdm
```

Download the script:
```bash
# Option 1: Clone repository
git clone https://github.com/yourusername/oceanofpdfs-remover.git
cd oceanofpdfs-remover

# Option 2: Direct download
# Download oceanofpdfs_remover_+_renamer_v2.py
```

Test it:
```bash
python oceanofpdfs_remover_+_renamer_v2.py --help
```

---

## 🎯 Feature-Specific Installation

### CTRL-Q Scan Abort

**Package**: `keyboard`

```bash
pip install keyboard
```

**Platform Notes**:
- **Windows**: Works out of the box
- **Linux**: Requires root/sudo OR add your user to input group:
  ```bash
  sudo usermod -a -G input $USER
  # Log out and back in
  ```
- **macOS**: Requires accessibility permissions (will prompt on first use)

**Troubleshooting**:
If you get permission errors on Linux:
```bash
# Run with sudo (not recommended for regular use)
sudo python oceanofpdfs_remover_+_renamer_v2.py "path" --log "log_path"

# OR grant your user access (recommended):
sudo chmod +r /dev/input/*
```

---

### OCR Functionality

**Package**: `ocrmypdf`

**Windows**:
```bash
# Install Tesseract OCR first
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# During installation, note the install path (e.g., C:\Program Files\Tesseract-OCR)

# Add Tesseract to PATH (in PowerShell as Administrator):
$env:PATH += ";C:\Program Files\Tesseract-OCR"
setx PATH "$env:PATH" /M

# Install Python package
pip install ocrmypdf
```

**macOS**:
```bash
# Install Tesseract via Homebrew
brew install tesseract

# Install Python package
pip install ocrmypdf
```

**Linux (Ubuntu/Debian)**:
```bash
# Install Tesseract and dependencies
sudo apt-get update
sudo apt-get install tesseract-ocr ocrmypdf

# Or just the Python package (will pull dependencies):
pip install ocrmypdf
```

**Verify Installation**:
```bash
ocrmypdf --version
# Should output: ocrmypdf 15.x.x
```

**Additional Languages** (optional):
```bash
# Windows: Download language packs from Tesseract installer
# macOS:
brew install tesseract-lang

# Linux:
sudo apt-get install tesseract-ocr-spa  # Spanish
sudo apt-get install tesseract-ocr-fra  # French
sudo apt-get install tesseract-ocr-deu  # German
```

---

### Windows Timestamp Preservation

**Package**: `pywin32`

**Windows Only**:
```bash
pip install pywin32
```

**Verify Installation**:
```python
# Open Python interpreter
python
>>> import win32file
>>> # If no error, it's installed correctly
```

**macOS/Linux**: Not needed (timestamp preservation works natively)

---

## 📦 Complete Installation (All Features)

Install everything in one go:

```bash
# Core dependencies
pip install pymupdf tqdm

# All optional features
pip install keyboard ocrmypdf

# Windows only
pip install pywin32
```

**Or use requirements file**:
```bash
# Download requirements_v2.txt
pip install -r requirements_v2.txt
```

---

## 🐍 Virtual Environment (Recommended)

Keep dependencies isolated:

### Windows:
```bash
# Create virtual environment
python -m venv oceanofpdfs_env

# Activate
oceanofpdfs_env\Scripts\activate

# Install dependencies
pip install pymupdf tqdm keyboard ocrmypdf pywin32

# When done, deactivate
deactivate
```

### macOS/Linux:
```bash
# Create virtual environment
python3 -m venv oceanofpdfs_env

# Activate
source oceanofpdfs_env/bin/activate

# Install dependencies
pip install pymupdf tqdm keyboard ocrmypdf

# When done, deactivate
deactivate
```

---

## ✅ Verification

Test each feature:

### 1. Basic Functionality
```bash
python oceanofpdfs_remover_+_renamer_v2.py --help
# Should show usage information
```

### 2. Progress Bar (tqdm)
```bash
python oceanofpdfs_remover_+_renamer_v2.py "test_folder" --dry-run
# Should show progress bar during processing
```

### 3. CTRL-Q Abort (keyboard)
```bash
python -c "import keyboard; print('✓ keyboard installed')"
# Should print: ✓ keyboard installed
```

### 4. OCR (ocrmypdf)
```bash
ocrmypdf --version
# Should show version number
```

### 5. Timestamp Preservation (pywin32 - Windows only)
```bash
python -c "import win32file; print('✓ pywin32 installed')"
# Should print: ✓ pywin32 installed
```

---

## 🔧 Troubleshooting

### "No module named 'fitz'"
**Solution**: Install PyMuPDF
```bash
pip install pymupdf
```

### "No module named 'tqdm'"
**Solution**: Install tqdm or use `--no-progress` flag
```bash
pip install tqdm
# OR run without progress bar:
python oceanofpdfs_remover_+_renamer_v2.py "path" --no-progress
```

### "keyboard requires root access" (Linux)
**Solution**: Add user to input group
```bash
sudo usermod -a -G input $USER
# Log out and log back in
```

### "tesseract is not installed or it's not in your PATH"
**Windows**:
- Reinstall Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- Add to PATH: `C:\Program Files\Tesseract-OCR`

**macOS**:
```bash
brew install tesseract
```

**Linux**:
```bash
sudo apt-get install tesseract-ocr
```

### "ImportError: DLL load failed" (Windows pywin32)
**Solution**: Reinstall with post-install script
```bash
pip uninstall pywin32
pip install pywin32
python Scripts/pywin32_postinstall.py -install
```

### OCR is very slow
**Solutions**:
1. OCR only scanned documents (script auto-detects and skips text PDFs)
2. Use faster Tesseract settings (already optimized in script)
3. Process in smaller batches
4. Use `--links-only` if OCR not needed

### Permission denied errors
**Windows**: Run Command Prompt or PowerShell as Administrator
**macOS/Linux**: Check file permissions
```bash
chmod +x oceanofpdfs_remover_+_renamer_v2.py
```

---

## 🔄 Updating

### Update the script:
```bash
# If using git
cd oceanofpdfs-remover
git pull

# If downloaded directly
# Download latest version and replace old file
```

### Update dependencies:
```bash
pip install --upgrade pymupdf tqdm keyboard ocrmypdf pywin32
```

---

## 🗑️ Uninstallation

### Remove virtual environment:
```bash
# Windows
rmdir /s oceanofpdfs_env

# macOS/Linux
rm -rf oceanofpdfs_env
```

### Remove global packages:
```bash
pip uninstall pymupdf tqdm keyboard ocrmypdf pywin32
```

### Remove Tesseract (if installed):

**Windows**: 
- Uninstall via Windows Settings > Apps

**macOS**:
```bash
brew uninstall tesseract tesseract-lang
```

**Linux**:
```bash
sudo apt-get remove tesseract-ocr ocrmypdf
```

---

## 📚 Next Steps

After installation:

1. Read [QUICKSTART.md](QUICKSTART.md) for basic usage
2. Check [NEW_FEATURES.md](NEW_FEATURES.md) for v2.1 features
3. Review [README.md](README.md) for comprehensive documentation
4. Run a `--dry-run` on a test folder to verify everything works

---

## 🆘 Still Having Issues?

1. Check Python version: `python --version` (must be 3.10+)
2. Check pip version: `pip --version`
3. Try upgrading pip: `python -m pip install --upgrade pip`
4. Create an issue on GitHub with:
   - Your Python version
   - Operating system
   - Complete error message
   - Output of `pip list`

---

**Happy processing! 🎉**
