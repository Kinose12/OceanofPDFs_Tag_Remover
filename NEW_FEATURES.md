# New Features Guide (v2.1)

Quick reference for the enhanced features in version 2.1.

---

## 🎮 CTRL-Q Scan Abort

**What it does**: Press CTRL-Q during the scanning phase to stop searching for more PDFs and start processing the ones already found.

**When to use**:
- You have huge drives and want to start processing sooner
- You see enough PDFs found and don't want to wait
- You want to test on a subset before processing everything

**Example**:
```bash
python oceanofpdfs_remover_+_renamer_v2.py "C:\" --log "C:\logs"
# During scanning, press CTRL-Q when you've found enough files
```

**Output**:
```
Scanning for PDFs...
Press CTRL-Q to abort scan and process files found so far

Scanning: C:\Users\Tedy\Documents\Books | PDFs: 1,234
# Press CTRL-Q here
⚠️  CTRL-Q detected! Aborting scan, will process files found so far...
✓ Scan aborted: 1,234 PDFs found

Processing PDFs: 100%|████████████| 1234/1234 [00:15<00:00]
```

**Requirements**: Optional `keyboard` package
```bash
pip install keyboard
```

---

## 📋 Logging with Resume

**What it does**: Saves detailed logs of all processing and automatically skips files that were already processed.

**When to use**:
- Processing large batches that might get interrupted
- Want to track what was changed
- Running multiple passes on the same directories
- Debugging issues

**Usage**:
```bash
python oceanofpdfs_remover_+_renamer_v2.py "C:\Books" --log "C:\logs\pdf_processing"
```

**What gets logged**:
1. **Event Log** (`oceanofpdfs_log_YYYYMMDD_HHMMSS.jsonl`):
   - Every file processed with timestamp
   - What happened (cleaned, renamed, failed, etc.)
   - Details about changes made
   
2. **Resume File** (`processed_files.json`):
   - List of all successfully processed files
   - Used to skip files on subsequent runs

**Log Format** (JSONL - one JSON object per line):
```json
{"timestamp": "2025-02-01T10:30:45.123456", "event": "cleaned", "file": "C:\\Books\\file.pdf", "details": {"text_hits": 12, "link_hits": 3, "renamed": true, "new_name": "Author - Title.pdf"}}
{"timestamp": "2025-02-01T10:30:46.234567", "event": "ocr", "file": "C:\\Books\\file2.pdf", "details": {"success": true}}
{"timestamp": "2025-02-01T10:30:47.345678", "event": "failed", "file": "C:\\Books\\broken.pdf", "details": {"error": "Corrupted file structure", "stage": "cleaning"}}
```

**Resume Example**:
```bash
# First run - processes all files
python oceanofpdfs_remover_+_renamer_v2.py "C:\Books" --log "C:\logs"

# Gets interrupted after processing 500 files...

# Second run - automatically skips the 500 already processed
python oceanofpdfs_remover_+_renamer_v2.py "C:\Books" --log "C:\logs"
```

**Output**:
```
✓ Logging enabled: C:\logs\oceanofpdfs_log_20250201_103045.jsonl
✓ Resume file: C:\logs\processed_files.json
ℹ️  Loaded 500 previously processed files (will skip)

⏭️  Skipped (already processed): file1.pdf
⏭️  Skipped (already processed): file2.pdf
♻️ Cleaned: file3.pdf (hits=8)
```

---

## 🔍 OCR Processing

**What it does**: Makes PDFs searchable by performing OCR (Optical Character Recognition) on scanned or image-based PDFs.

**When to use**:
- Preparing PDFs for NotebookLM (it searches text)
- Building a searchable library
- PDFs are scanned images without text layer

**Usage**:
```bash
python oceanofpdfs_remover_+_renamer_v2.py "C:\Books" --ocrmypdf
```

**Smart Features**:
- ✅ Automatically detects if PDF already has text
- ✅ Skips OCR if PDF is already searchable
- ✅ Only OCRs image-based pages
- ✅ Preserves timestamps
- ✅ Uses optimized settings for speed

**Requirements**: 
```bash
pip install ocrmypdf
```

**Output**:
```
♻️ Cleaned: document.pdf (hits=5)
🔍 OCR processed: document.pdf
ℹ️ Renamed: old_name.pdf -> Author - Title.pdf
```

**Combined with logging**:
```bash
python oceanofpdfs_remover_+_renamer_v2.py "C:\Books" --log "C:\logs" --ocrmypdf
```

The log will show which files were OCR'd:
```json
{"timestamp": "2025-02-01T10:30:45", "event": "ocr", "file": "C:\\Books\\scanned.pdf", "details": {"success": true}}
```

---

## ☁️ NotebookLM Preparation

**What it does**: Prepares PDFs for upload to Google NotebookLM by copying them to a staging directory.

**Why staging**: NotebookLM doesn't have a public API yet (as of Feb 2025), so the script stages files for manual upload.

**Usage**:
```bash
python oceanofpdfs_remover_+_renamer_v2.py "C:\Books" --notebooklm "My Research Project"
```

**What happens**:
1. Processes PDFs normally (clean + rename)
2. Copies each processed PDF to staging directory
3. Maintains timestamps
4. Groups by notebook name

**Staging Directory**:
```
C:\Users\Tedy\notebooklm_staging\
  └── My Research Project\
      ├── Author1 - Book1.pdf
      ├── Author2 - Book2.pdf
      └── Author3 - Book3.pdf
```

**Output**:
```
♻️ Cleaned: book.pdf (hits=8) & Renamed -> Author - Title.pdf
ℹ️  NotebookLM API not yet available. File prepared: Author - Title.pdf
   Please manually upload to notebook: My Research Project
   ✓ Copied to staging: C:\Users\Tedy\notebooklm_staging\My Research Project
```

**Full Workflow** (Clean → OCR → Prepare for NotebookLM):
```bash
python oceanofpdfs_remover_+_renamer_v2.py "C:\Books" \
  --log "C:\logs" \
  --ocrmypdf \
  --notebooklm "Research: AI Papers"
```

This will:
1. ✅ Remove watermarks
2. ✅ Rename files properly
3. ✅ Make PDFs searchable (OCR)
4. ✅ Stage for NotebookLM upload
5. ✅ Log everything for resume capability

---

## 🎯 Complete Examples

### Example 1: Resume Long-Running Job
```bash
# Start processing entire drive
python oceanofpdfs_remover_+_renamer_v2.py "D:\" --log "C:\logs\drive_d"

# Computer crashes or you press CTRL-C...

# Resume where you left off (skips already processed files)
python oceanofpdfs_remover_+_renamer_v2.py "D:\" --log "C:\logs\drive_d"
```

### Example 2: Quick Abort Test
```bash
# Start scanning huge directory
python oceanofpdfs_remover_+_renamer_v2.py "C:\" --log "C:\logs"

# During scan, press CTRL-Q when you see enough files (e.g., 100 PDFs found)
# Script stops scanning and processes those 100 files immediately
```

### Example 3: Prepare Library for NotebookLM
```bash
# Clean, OCR, and prepare all PDFs for NotebookLM
python oceanofpdfs_remover_+_renamer_v2.py "C:\Research" \
  --log "C:\logs\research" \
  --ocrmypdf \
  --notebooklm "PhD Research"

# Then manually upload files from:
# C:\Users\Tedy\notebooklm_staging\PhD Research\
```

### Example 4: Incremental Daily Processing
```bash
# Day 1: Process downloads folder
python oceanofpdfs_remover_+_renamer_v2.py "C:\Downloads" --log "C:\logs\daily"

# Day 2: Process again (skips yesterday's files, only processes new ones)
python oceanofpdfs_remover_+_renamer_v2.py "C:\Downloads" --log "C:\logs\daily"

# Day 3: Same command, only new files processed
python oceanofpdfs_remover_+_renamer_v2.py "C:\Downloads" --log "C:\logs\daily"
```

---

## 📊 Summary Statistics

With all features enabled, you'll see comprehensive stats:

```
DONE: 1234 processed | 156 cleaned | 203 renamed | 2 failed
  ↳ 50 skipped (already processed)
  ↳ 89 OCR processed
  ↳ 145 uploaded to NotebookLM

📋 Log file saved: C:\logs\oceanofpdfs_log_20250201_103045.jsonl
📋 Resume file: C:\logs\processed_files.json
```

---

## 🛠️ Optional Dependencies

Install only what you need:

```bash
# Basic functionality (required)
pip install pymupdf tqdm

# CTRL-Q abort feature
pip install keyboard

# OCR functionality
pip install ocrmypdf

# Windows timestamp preservation
pip install pywin32
```

Or install everything:
```bash
pip install pymupdf tqdm keyboard ocrmypdf pywin32
```

---

## 💡 Pro Tips

1. **Always use --log** for large batches - you'll thank yourself later
2. **Test with --dry-run first** before enabling OCR (OCR is slow)
3. **Use CTRL-Q** to test on a small subset before committing to full scan
4. **Combine with --no-progress** for maximum speed when you don't need visual feedback
5. **Check log files** if something seems wrong - they contain all the details

---

**Questions or issues?** Check the main [README.md](README.md) or create an issue on GitHub!
