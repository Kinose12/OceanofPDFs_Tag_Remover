# Quick Start Guide

Get up and running with OceanofPDFs Tag Remover & Renamer in 5 minutes.

## 📋 Prerequisites

- **Python 3.10 or higher** installed on your system
- Basic familiarity with command line/terminal

### Check Python Version

```bash
python --version
```

If you see `Python 3.10.x` or higher, you're good to go!

---

## 🚀 Installation (3 Steps)

### Step 1: Install Required Libraries

Open your terminal/command prompt and run:

```bash
pip install pymupdf tqdm
```

**Optional (Windows only)** - For full timestamp preservation:
```bash
pip install pywin32
```

### Step 2: Download the Script

**Option A: Clone the repository**
```bash
git clone https://github.com/yourusername/oceanofpdfs-remover.git
cd oceanofpdfs-remover
```

**Option B: Direct download**
1. Download `oceanofpdfs_remover_+_renamer.py` from this repository
2. Save it to a convenient location (e.g., `C:\scripts\` or `~/scripts/`)

### Step 3: Verify Installation

Navigate to the script directory and run:

```bash
python oceanofpdfs_remover_+_renamer.py
```

You should see the usage message. If you get an error, check that Python and the required libraries are installed correctly.

---

## 🎯 Basic Usage

### Test Run (Dry Run)

**Always start with a dry run to preview changes without modifying files!**

```bash
python oceanofpdfs_remover_+_renamer.py "C:\Users\YourName\Documents\Books" --dry-run
```

This will:
- Show you what would be changed
- List files that would be cleaned
- Show proposed renames
- **Not modify any files**

### Process a Single Folder

Once you're comfortable with the preview:

```bash
python oceanofpdfs_remover_+_renamer.py "C:\Users\YourName\Documents\Books"
```

### Process Multiple Locations

```bash
python oceanofpdfs_remover_+_renamer.py "C:\Books" "D:\Library" "E:\eBooks"
```

---

## 💡 Common Scenarios

### Scenario 1: I just want to remove the watermarks, not rename files

```bash
python oceanofpdfs_remover_+_renamer.py "C:\Books" --no-rename
```

### Scenario 2: I need fast processing and don't care about the progress bar

```bash
python oceanofpdfs_remover_+_renamer.py "C:\Books" --no-progress
```

### Scenario 3: Only remove clickable links (fastest mode)

```bash
python oceanofpdfs_remover_+_renamer.py "C:\Books" --links-only
```

### Scenario 4: Process entire drive

```bash
python oceanofpdfs_remover_+_renamer.py "C:\" --no-progress
```

**Note:** Processing entire drives can take hours depending on size!

---

## 📊 Understanding the Output

### During Processing

```
Scanning for PDFs...
Scanning: C:\Users\YourName\Documents\Books\Fiction | PDFs: 1,234
✓ Scan complete: 1,234 PDFs found

Processing PDFs: 100%|████████████| 1234/1234 [00:15<00:00, 82.27file/s]

♻️ Cleaned: The_Great_Gatsby.pdf (hits=12) & Renamed -> F. Scott Fitzgerald - The Great Gatsby.pdf
ℹ️ Renamed: 1984_ (Z-Library).pdf -> 1984.pdf
```

### Icon Legend

| Icon | Meaning |
|------|---------|
| ♻️ | File cleaned (watermarks removed) |
| ℹ️ | File renamed |
| ‼️ | Processing failed |
| 🏳️ | Dry run (preview only) |

### Final Summary

```
DONE: 1234 processed | 156 cleaned | 203 renamed | 2 failed
```

- **processed**: Total PDFs examined
- **cleaned**: Files with watermarks removed
- **renamed**: Files with normalized names
- **failed**: Files that couldn't be processed

---

## ⚠️ Important Tips

### Before You Start

1. ✅ **Always run with `--dry-run` first** to preview changes
2. ✅ **Have backups** of important documents
3. ✅ **Close any PDFs** you're viewing before processing
4. ✅ **Check available disk space** (script creates temporary files)

### Common Mistakes

❌ **Don't** process files while they're open in a PDF reader  
✅ **Do** close all PDFs before running the script

❌ **Don't** run on entire drives without testing first  
✅ **Do** test on a small folder with `--dry-run`

❌ **Don't** interrupt the process in the middle  
✅ **Do** wait for completion or use Ctrl+C to safely cancel

---

## 🔧 Troubleshooting

### "No module named 'fitz'" error

**Solution:** Install PyMuPDF
```bash
pip install pymupdf
```

### Progress bar not showing

**Solution:** Install tqdm
```bash
pip install tqdm
```

Or use the script without progress bars:
```bash
python oceanofpdfs_remover_+_renamer.py "C:\Books" --no-progress
```

### "Permission denied" errors

**Solutions:**
1. Close any open PDF viewers
2. Run terminal/cmd as administrator (Windows)
3. Check file permissions
4. Disable cloud sync temporarily (OneDrive, Dropbox, etc.)

### "Path not found" error

**Solutions:**
1. Use quotes around paths with spaces: `"C:\My Books"`
2. Check that the path exists
3. Use forward slashes on all platforms: `C:/Books`

### Script is very slow

**Solutions:**
1. Use `--links-only` for faster processing (text removal is slower)
2. Use `--no-progress` to skip initial scanning
3. Process smaller folders instead of entire drives
4. Exclude cloud-synced folders if not needed

---

## 🎓 Next Steps

### Customize Your Workflow

Create a batch file (Windows) or shell script (macOS/Linux) for your common tasks:

**Windows (clean_books.bat):**
```batch
@echo off
python oceanofpdfs_remover_+_renamer.py "C:\Users\%USERNAME%\Documents\Books" --no-progress
pause
```

**macOS/Linux (clean_books.sh):**
```bash
#!/bin/bash
python oceanofpdfs_remover_+_renamer.py "$HOME/Documents/Books" --no-progress
```

### Learn More

- Read the full [README.md](README.md) for detailed documentation
- Check [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute
- Review [CHANGELOG.md](CHANGELOG.md) for version history

---

## ❓ Need Help?

1. Check the [README](README.md) for detailed documentation
2. Look through [existing issues](https://github.com/yourusername/oceanofpdfs-remover/issues)
3. Create a new issue with:
   - Your Python version
   - Operating system
   - Complete error message
   - Command you ran

---

**Happy cleaning! 📚✨**
