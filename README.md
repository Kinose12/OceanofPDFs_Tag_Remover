# OceanofPDFs Tag Remover & Renamer

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

A high-performance Python utility for cleaning PDF libraries by removing OceanofPDFs.com watermarks and normalizing filenames. Designed to handle large collections (10,000+ files) efficiently with smart processing modes and cloud-sync awareness.

---

## ✨ Features

### 🧹 Content Cleanup
- **Text Removal**: Detects and removes all variations of "OceanofPDFs.com" watermarks
  - Handles spaced variants: `O c e a n o f P D F s . c o m`
  - Case-insensitive pattern matching
  - White-out redaction preserves document structure
- **Link Removal**: Deletes hyperlink annotations pointing to OceanofPDFs.com
  - Removes blue underline artifacts
  - Cleans clickable watermarks
- **Two-Pass Optimization**: 
  1. Fast link removal on all pages
  2. Text redaction only when watermarks detected
- **Malformed PDF Handling**: Processes broken PDFs safely with comprehensive error handling

### 📝 Filename Normalization

Automatically renames PDFs following consistent, human-readable patterns:

#### Pattern Recognition

**Rule 1: Prefix cleanup and author-title reordering**
```
_OceanofPDFs.com_The_Great_Gatsby_-_F._Scott_Fitzgerald.pdf
→ F. Scott Fitzgerald - The Great Gatsby.pdf
```

**Rule 2: Z-Library suffix removal**
```
The_Great_Gatsby_ (Z-Library).pdf
→ The Great Gatsby.pdf
```

**Rule 3: Underscore normalization**
```
Book___Title___With____Underscores.pdf
→ Book Title With Underscores.pdf
```

#### Additional Filename Features
- ✅ Invalid Windows characters removed (`\ / : * ? " < > |`)
- ✅ Automatic collision detection with incremental naming
  - `Book.pdf` → `Book (1).pdf` → `Book (2).pdf`
- ✅ Whitespace normalization
- ✅ Optional: Disable renaming with `--no-rename` flag

---

## 🚀 Installation

### Prerequisites
- **Python 3.10 or higher**
- **Operating System**: Windows, macOS, or Linux

### Step 1: Install Python Dependencies

```bash
pip install pymupdf tqdm
```

**Optional (Windows only)**: For full creation date preservation:
```bash
pip install pywin32
```

### Step 2: Download the Script

Clone this repository:
```bash
git clone https://github.com/yourusername/oceanofpdfs-remover.git
cd oceanofpdfs-remover
```

Or download `oceanofpdfs_remover_+_renamer.py` directly.

---

## 📖 Usage

### Basic Commands

**Process a single PDF:**
```bash
python oceanofpdfs_remover_+_renamer.py "C:\Books\example.pdf"
```

**Process entire directory recursively:**
```bash
python oceanofpdfs_remover_+_renamer.py "C:\Books"
```

**Process multiple drives/directories:**
```bash
python oceanofpdfs_remover_+_renamer.py "C:\Books" "D:\Library" "E:\Ebooks"
```

### Command-Line Flags

| Flag | Description |
|------|-------------|
| `--dry-run` | Preview changes without modifying files. Shows what would be cleaned/renamed. |
| `--links-only` | Remove only hyperlinks (fastest mode). Skips text redaction. |
| `--no-rename` | Disable all filename changes. Only clean PDF content. |
| `--no-progress` | Disable progress bar and enable streaming mode. Process files as found. |

### Advanced Examples

**Dry run to preview changes:**
```bash
python oceanofpdfs_remover_+_renamer.py "C:\Books" --dry-run
```

**Fast mode (links only, no renaming):**
```bash
python oceanofpdfs_remover_+_renamer.py "C:\Books" --links-only --no-rename
```

**Streaming mode for immediate processing:**
```bash
python oceanofpdfs_remover_+_renamer.py "C:\Books" --no-progress
```

**Process multiple drives without progress bar:**
```bash
python oceanofpdfs_remover_+_renamer.py C:\ D:\ E:\ --no-progress
```

---

## 🎯 Processing Modes

### Standard Mode (Default)
- Scans all directories first to count total PDFs
- Shows real-time scanning progress with current folder path
- Displays accurate progress bar during processing
- Processes local files first, cloud-synced files last
- **Best for**: Large libraries where you want to see total progress

**Example Output:**
```
Scanning for PDFs...
Scanning: C:\Users\YourName\Documents\Books | PDFs: 1,234
✓ Scan complete: 1,234 PDFs found
ℹ️  45 cloud-synced files will be processed last

Processing PDFs: 100%|████████████████████| 1234/1234 [00:15<00:00, 82.27file/s]

DONE: 1234 processed | 156 cleaned | 203 renamed | 2 failed
```

### Streaming Mode (`--no-progress`)
- Processes PDFs immediately as they're discovered
- No initial scan delay
- Shows folder changes in real-time
- **Best for**: Quick processing, CI/CD pipelines, or when total count doesn't matter

**Example Output:**
```
Starting streaming processing...

Processing folder: C:\Users\YourName\Documents\Books
♻️ Cleaned: The_Great_Gatsby.pdf (hits=12) & Renamed -> F. Scott Fitzgerald - The Great Gatsby.pdf
ℹ️ Renamed: 1984_ (Z-Library).pdf -> 1984.pdf

Processing folder: C:\Users\YourName\Documents\Books\Classics
♻️ Cleaned: Pride_and_Prejudice.pdf (hits=8)

DONE: 1234 processed | 156 cleaned | 203 renamed | 2 failed
```

---

## 🔒 Safety Features

### Data Protection
- ✅ **Atomic Replacement**: Original files only replaced after successful processing
- ✅ **Automatic Cleanup**: Temporary files deleted automatically on failure
- ✅ **Timestamp Preservation**: Maintains original access, modification, and creation dates
- ✅ **No Partial Overwrites**: Failed operations never corrupt original files
- ✅ **Collision Prevention**: Automatic unique naming prevents file overwrites

### Cloud-Sync Intelligence
- ✅ **Cloud Detection**: Identifies OneDrive, Dropbox, Google Drive, iCloud, etc.
- ✅ **Deferred Processing**: Cloud files processed last to avoid blocking
- ✅ **Retry Logic**: 3 automatic retries for cloud timeout errors
- ✅ **Graceful Degradation**: Non-cloud files complete even if cloud files fail

### Privacy & Security
- ✅ **No Network Access**: 100% offline operation
- ✅ **No Telemetry**: Zero data collection or phone-home behavior
- ✅ **No Metadata Scraping**: Only reads text/links, never tracks reading habits

---

## 📊 Output & Reporting

### Summary Statistics
At completion, the script provides:
- Total PDFs processed
- Number cleaned (watermarks removed)
- Number renamed
- Number failed with error grouping

### Error Handling
- **Grouped Errors**: Similar failures grouped for easy diagnosis
- **Detailed Messages**: Full error context for debugging
- **Non-Fatal**: Individual failures don't stop batch processing
- **Common Errors**: Broken PDFs, corrupted object streams, invalid colorspaces

**Example Error Report:**
```
DONE: 1234 processed | 156 cleaned | 203 renamed | 3 failed

Failure summary:

Failed to open file 'corrupted.pdf'.
  - corrupted.pdf
  - broken_structure.pdf

[WinError 426] The cloud operation was not completed before the time-out period expired
  - onedrive_syncing.pdf
```

---

## ⚡ Performance Notes

### Optimization Strategies
- **Pattern Pre-filtering**: Fast text search before expensive redaction
- **Page-level Processing**: Skip clean pages entirely
- **Smart Defaults**: Balance speed vs. thoroughness
- **Batch Operations**: Process multiple files without reloading libraries

### Benchmark Performance
- **Large Libraries**: Tested on 10,000+ PDF collections
- **Speed**: ~50-100 files/second in `--links-only` mode
- **Thoroughness**: ~10-30 files/second in full cleaning mode
- **Memory**: Minimal footprint, processes one file at a time

### Tips for Maximum Speed
1. Use `--links-only` if you only need link removal
2. Use `--no-progress` for slightly faster processing
3. Process local drives before network/cloud drives
4. Exclude temporary or download folders if not needed

---

## 🛠️ Technical Details

### Dependencies
- **PyMuPDF (fitz)**: PDF parsing and manipulation
- **tqdm**: Progress bar visualization (optional)
- **pywin32**: Windows creation date preservation (optional, Windows only)

### File Timestamp Handling
The script preserves three timestamp types:

| Timestamp | Windows | macOS/Linux | Preserved |
|-----------|---------|-------------|-----------|
| Access Time (atime) | ✅ | ✅ | Always |
| Modification Time (mtime) | ✅ | ✅ | Always |
| Creation Time (ctime) | ✅ | ⚠️* | With pywin32 |

*On Unix systems, `ctime` is metadata change time, not creation time.

### Temporary File Strategy
1. Create `.tmp` file with same name + `.tmp` extension
2. Apply all modifications to temp file
3. Atomic move from temp → original on success
4. Cleanup temp file on any failure

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
```bash
git clone https://github.com/yourusername/oceanofpdfs-remover.git
cd oceanofpdfs-remover
pip install -r requirements.txt
```

### Running Tests
```bash
# Dry run on test directory
python oceanofpdfs_remover_+_renamer.py "test_pdfs/" --dry-run
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This tool is for personal library management only. Users are responsible for ensuring they have the right to modify their PDF files. Always maintain backups of important documents.

---

## 🙏 Acknowledgments

- Built with [PyMuPDF](https://pymupdf.readthedocs.io/) for robust PDF processing
- Progress bars powered by [tqdm](https://github.com/tqdm/tqdm)
- Inspired by the need for clean, organized digital libraries

---

## 📧 Support

If you encounter issues or have questions:
1. Check the [Issues](https://github.com/yourusername/oceanofpdfs-remover/issues) page
2. Create a new issue with:
   - Python version (`python --version`)
   - Operating system
   - Error message (if applicable)
   - Command used

---

**Made with ❤️ for book lovers who value clean libraries**
