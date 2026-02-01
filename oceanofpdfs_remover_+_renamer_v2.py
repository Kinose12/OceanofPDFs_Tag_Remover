"""
OceanofPDFs Tag Remover & Renamer (Enhanced Edition)
------------------------------------------------
A utility to redact watermarks, normalize filenames, OCR PDFs, and upload to NotebookLM.

Enhanced Features:
- Press CTRL-Q during scanning to abort and process files found so far
- Logging with resume capability (skip already processed files)
- Optional OCR processing with ocrmypdf
- Optional NotebookLM upload integration

Author: Theodore Eich
License: MIT
Repository: https://github.com/yourusername/oceanofpdfs-remover
Python Version: 3.10+
"""

import os
import sys
import re
import shutil
import time
import json
import threading
from pathlib import Path
from datetime import datetime
import fitz  # PyMuPDF

# Attempt to load optional dependencies
try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    keyboard = None

# ANSI Color Codes
RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

# Silence MuPDF internal console spam
fitz.TOOLS.mupdf_display_errors(False)
fitz.TOOLS.mupdf_display_warnings(False)

# Configuration Constants
PHRASE = "OceanofPDFs.com"
URI_MATCH = "OceanofPDFs.com"
PREFIX = "_OceanofPDFs.com_"
ZLIB_SUFFIX = "_ (Z-Library)"
TEXT_PATTERN = re.compile(r"(?i)o\s*c\s*e\s*a\s*n\s*o\s*f\s*p\s*d\s*f\s*\.\s*c\s*o\s*m")

# Cloud-synced folder patterns
CLOUD_PATTERNS = [
    "onedrive", "dropbox", "google drive", "crossdevice", 
    "icloud", "box sync", "sync", "cloud"
]

# Global flag for scan abort
ABORT_SCAN = False

def is_cloud_path(path: Path) -> bool:
    """Check if path is in a cloud-synced folder."""
    path_str = str(path).lower()
    return any(pattern in path_str for pattern in CLOUD_PATTERNS)

# ============================================================================
# LOGGING SYSTEM
# ============================================================================

class ProcessLogger:
    """Handles logging and resume functionality."""
    
    def __init__(self, log_dir: Path = None):
        """
        Initialize logger.
        
        Args:
            log_dir: Directory to store log files. If None, logging is disabled.
        """
        self.log_dir = log_dir
        self.log_file = None
        self.processed_files = set()
        
        if self.log_dir:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = self.log_dir / f"oceanofpdfs_log_{timestamp}.jsonl"
            self.resume_file = self.log_dir / "processed_files.json"
            self._load_processed_files()
    
    def _load_processed_files(self):
        """Load previously processed files from resume file."""
        if self.resume_file and self.resume_file.exists():
            try:
                with open(self.resume_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_files = set(data.get('processed', []))
                print(f"{CYAN}ℹ️  Loaded {len(self.processed_files)} previously processed files (will skip){RESET}")
            except Exception as e:
                print(f"{YELLOW}⚠️  Could not load resume file: {e}{RESET}")
    
    def is_processed(self, pdf_path: Path) -> bool:
        """Check if file was already processed."""
        return str(pdf_path.absolute()) in self.processed_files
    
    def log_event(self, event_type: str, pdf_path: Path, details: dict = None):
        """
        Log an event to the log file.
        
        Args:
            event_type: Type of event (cleaned, renamed, failed, skipped, ocr, upload)
            pdf_path: Path to the PDF file
            details: Additional details about the event
        """
        if not self.log_file:
            return
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event': event_type,
            'file': str(pdf_path.absolute()),
            'details': details or {}
        }
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            print(f"{YELLOW}⚠️  Logging error: {e}{RESET}")
    
    def mark_processed(self, pdf_path: Path):
        """Mark a file as processed and update resume file."""
        file_str = str(pdf_path.absolute())
        self.processed_files.add(file_str)
        
        if self.resume_file:
            try:
                with open(self.resume_file, 'w', encoding='utf-8') as f:
                    json.dump({'processed': list(self.processed_files)}, f, indent=2)
            except Exception as e:
                print(f"{YELLOW}⚠️  Could not update resume file: {e}{RESET}")

# ============================================================================
# KEYBOARD INTERRUPT HANDLER
# ============================================================================

def setup_abort_handler():
    """Setup CTRL-Q handler to abort scanning."""
    global ABORT_SCAN
    
    if not KEYBOARD_AVAILABLE:
        return
    
    def on_abort():
        global ABORT_SCAN
        ABORT_SCAN = True
        print(f"\n{YELLOW}⚠️  CTRL-Q detected! Aborting scan, will process files found so far...{RESET}")
    
    try:
        keyboard.add_hotkey('ctrl+q', on_abort)
    except Exception:
        # Silently fail if keyboard hook setup fails
        pass

# ============================================================================
# OCR FUNCTIONALITY
# ============================================================================

def ocr_pdf(pdf_path: Path, log_func=print) -> bool:
    """
    Perform OCR on a PDF using ocrmypdf.
    
    Args:
        pdf_path: Path to PDF file
        log_func: Function for logging output
        
    Returns:
        True if OCR was successful, False otherwise
    """
    try:
        import ocrmypdf
        
        # Check if PDF already has text (skip if already OCR'd)
        doc = fitz.open(pdf_path)
        has_text = False
        for page in doc:
            if page.get_text().strip():
                has_text = True
                break
        doc.close()
        
        if has_text:
            # Already has text, skip OCR
            return True
        
        # Create temp file for OCR output
        temp_output = pdf_path.with_suffix('.ocr.pdf')
        
        # Run OCR with basic settings
        ocrmypdf.ocr(
            pdf_path,
            temp_output,
            skip_text=True,  # Skip pages that already have text
            optimize=1,      # Light optimization
            output_type='pdf',  # Standard PDF, not PDF/A
            force_ocr=False,  # Don't redo existing OCR
            quiet=True,
            progress_bar=False
        )
        
        # Get timestamps before replacement
        atime, mtime, ctime = get_file_times(pdf_path)
        
        # Replace original with OCR'd version
        shutil.move(temp_output, pdf_path)
        
        # Restore timestamps
        restore_times(pdf_path, atime, mtime, ctime)
        
        return True
        
    except ImportError:
        log_func(f"{RED}⚠️  ocrmypdf not installed. Install with: pip install ocrmypdf{RESET}")
        return False
    except Exception as e:
        log_func(f"{YELLOW}⚠️  OCR failed for {pdf_path.name}: {str(e)}{RESET}")
        if temp_output.exists():
            temp_output.unlink()
        return False

# ============================================================================
# NOTEBOOKLM INTEGRATION
# ============================================================================

def upload_to_notebooklm(pdf_path: Path, notebook_name: str, log_func=print) -> bool:
    """
    Upload a PDF to NotebookLM notebook.
    
    Note: As of Feb 2025, NotebookLM does not have a public API.
    This function is a placeholder for future API integration or
    can be customized with unofficial methods.
    
    Args:
        pdf_path: Path to PDF file
        notebook_name: Name of the NotebookLM notebook
        log_func: Function for logging output
        
    Returns:
        True if upload successful, False otherwise
    """
    try:
        # TODO: Implement NotebookLM API integration when available
        # Current options:
        # 1. Wait for official API (recommended)
        # 2. Use browser automation (selenium/playwright)
        # 3. Use unofficial API if available
        
        log_func(f"{YELLOW}ℹ️  NotebookLM API not yet available. File prepared: {pdf_path.name}{RESET}")
        log_func(f"{CYAN}   Please manually upload to notebook: {notebook_name}{RESET}")
        
        # For now, we could copy files to a staging directory
        staging_dir = Path.home() / "notebooklm_staging" / notebook_name
        staging_dir.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(pdf_path, staging_dir / pdf_path.name)
        log_func(f"{GREEN}   ✓ Copied to staging: {staging_dir}{RESET}")
        
        return True
        
    except Exception as e:
        log_func(f"{RED}⚠️  NotebookLM staging failed: {str(e)}{RESET}")
        return False

# ============================================================================
# PDF DISCOVERY FUNCTIONS
# ============================================================================

def collect_pdfs_streaming(target: Path, callback=None):
    """Generator that yields PDF files as they're discovered."""
    global ABORT_SCAN
    
    if target.is_file() and target.suffix.lower() == ".pdf":
        yield target
        return
    
    if target.is_dir():
        for root, dirs, files in os.walk(target):
            if ABORT_SCAN:
                break
                
            current_path = Path(root)
            if callback:
                callback(current_path)
            
            for file in files:
                if ABORT_SCAN:
                    break
                if file.lower().endswith('.pdf'):
                    yield current_path / file

def collect_pdfs_all(targets: list[Path], show_progress=True) -> tuple[list[Path], list[Path]]:
    """Collect all PDF files from multiple targets, separating cloud-synced ones."""
    global ABORT_SCAN
    local_pdfs = []
    cloud_pdfs = []
    total_found = 0
    
    if show_progress:
        print(f"{CYAN}Scanning for PDFs...{RESET}")
        if KEYBOARD_AVAILABLE:
            print(f"{MAGENTA}Press CTRL-Q to abort scan and process files found so far{RESET}\n")
    
    for target in targets:
        if ABORT_SCAN:
            break
            
        if target.is_file() and target.suffix.lower() == ".pdf":
            if is_cloud_path(target):
                cloud_pdfs.append(target)
            else:
                local_pdfs.append(target)
            total_found += 1
            if show_progress:
                print(f"\r{YELLOW}PDFs found: {total_found}{RESET}", end='', flush=True)
            continue
        
        if target.is_dir():
            for root, dirs, files in os.walk(target):
                if ABORT_SCAN:
                    break
                    
                current_path = Path(root)
                
                if show_progress:
                    display_path = str(current_path)
                    if len(display_path) > 70:
                        display_path = "..." + display_path[-67:]
                    print(f"\r{CYAN}Scanning:{RESET} {display_path:<70} | {YELLOW}PDFs: {total_found}{RESET}", end='', flush=True)
                
                for file in files:
                    if ABORT_SCAN:
                        break
                    if file.lower().endswith('.pdf'):
                        pdf_path = current_path / file
                        if is_cloud_path(pdf_path):
                            cloud_pdfs.append(pdf_path)
                        else:
                            local_pdfs.append(pdf_path)
                        total_found += 1
    
    if show_progress:
        status = "aborted" if ABORT_SCAN else "complete"
        print(f"\r{GREEN}✓ Scan {status}: {total_found} PDFs found{RESET}" + " " * 60)
        if cloud_pdfs:
            print(f"{YELLOW}ℹ️  {len(cloud_pdfs)} cloud-synced files will be processed last{RESET}")
    
    return local_pdfs, cloud_pdfs

# ============================================================================
# TIMESTAMP PRESERVATION FUNCTIONS
# ============================================================================

def restore_times(path: Path, atime, mtime, ctime):
    """Restore file access, modification, and creation timestamps."""
    if atime is None or mtime is None:
        return
    try:
        os.utime(path, (atime, mtime))
        
        if sys.platform == 'win32' and ctime is not None:
            try:
                import pywintypes
                import win32file
                import win32con
                
                handle = win32file.CreateFile(
                    str(path),
                    win32con.GENERIC_WRITE,
                    win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                    None,
                    win32con.OPEN_EXISTING,
                    win32con.FILE_ATTRIBUTE_NORMAL,
                    None
                )
                win32file.SetFileTime(handle, pywintypes.Time(ctime), None, None)
                win32file.CloseHandle(handle)
            except Exception:
                pass
    except Exception:
        pass

def get_file_times(path: Path):
    """Retrieve all file timestamps."""
    try:
        st = path.stat()
        atime = st.st_atime
        mtime = st.st_mtime
        ctime = st.st_ctime if sys.platform == 'win32' else st.st_mtime
        return atime, mtime, ctime
    except Exception:
        return None, None, None

# ============================================================================
# PDF CONTENT MANIPULATION FUNCTIONS
# ============================================================================

def remove_links(page) -> int:
    """Find and delete hyperlink annotations pointing to target URI."""
    removed = 0
    for link in page.get_links():
        uri = link.get("uri", "")
        if uri and URI_MATCH in uri.lower():
            page.delete_link(link)
            removed += 1
    return removed

def page_might_contain_phrase(page) -> bool:
    """Fast preliminary check if page contains target text."""
    t = page.get_text("text")
    return bool(t and TEXT_PATTERN.search(t))

def redact_phrase(page) -> int:
    """Identify target text spans and apply white-out redaction."""
    hits = 0
    data = page.get_text("dict")
    for block in data.get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                txt = span.get("text", "")
                if txt and TEXT_PATTERN.search(txt):
                    page.add_redact_annot(fitz.Rect(span["bbox"]), fill=(1, 1, 1))
                    hits += 1
    if hits:
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    return hits

def process_pdf(pdf_path: Path, links_only=False, dry_run=False):
    """Core PDF cleaning logic with atomic file replacement."""
    temp = pdf_path.with_suffix(pdf_path.suffix + ".tmp")
    text_hits = link_hits = 0
    atime, mtime, ctime = get_file_times(pdf_path)

    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            link_hits += remove_links(page)

        if not links_only:
            for page in doc:
                if page_might_contain_phrase(page):
                    text_hits += redact_phrase(page)

        changed = (text_hits + link_hits) > 0

        if dry_run:
            doc.close()
            return True, text_hits, link_hits, None

        if changed:
            doc.save(temp, garbage=4, deflate=True, clean=True)
        doc.close()

        if not changed:
            if temp.exists():
                temp.unlink()
            return False, 0, 0, None

        shutil.move(temp, pdf_path)
        restore_times(pdf_path, atime, mtime, ctime)
        return True, text_hits, link_hits, None

    except Exception as e:
        if temp.exists():
            temp.unlink()
        return False, -1, -1, str(e)

# ============================================================================
# FILENAME MANIPULATION FUNCTIONS
# ============================================================================

def sanitize(s: str) -> str:
    """Remove illegal Windows filename characters."""
    return re.sub(r'[\\/:*?"<>|]', "", s).strip()

def unique_path(p: Path) -> Path:
    """Handle filename collisions by adding incremental suffix."""
    if not p.exists():
        return p
    i = 1
    while True:
        cand = p.with_stem(f"{p.stem} ({i})")
        if not cand.exists():
            return cand
        i += 1

def compute_rename(pdf_path: Path):
    """Calculate new filename based on pattern matching rules."""
    name = pdf_path.stem

    if name.endswith(ZLIB_SUFFIX):
        name = name[: -len(ZLIB_SUFFIX)]

    if name.startswith(PREFIX):
        remainder = name[len(PREFIX):]
        parts = remainder.split("_-_", 1)
        if len(parts) == 2:
            title, author = map(sanitize, parts)
            name = f"{author} - {title}"

    name = re.sub(r"_+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()

    new_path = pdf_path.with_name(name + pdf_path.suffix)
    return unique_path(new_path) if new_path != pdf_path else None

def rename_if_needed(pdf_path: Path, dry_run=False, retries=3):
    """Execute file renaming with retry logic for cloud-synced files."""
    new_path = compute_rename(pdf_path)
    if not new_path:
        return False, pdf_path

    atime, mtime, ctime = get_file_times(pdf_path)

    if dry_run:
        return True, new_path

    for attempt in range(retries):
        try:
            pdf_path.rename(new_path)
            restore_times(new_path, atime, mtime, ctime)
            return True, new_path
        except OSError as e:
            if "cloud operation" in str(e).lower() or "time-out" in str(e).lower():
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
            raise
    
    return False, pdf_path

# ============================================================================
# SINGLE PDF PROCESSING FUNCTION
# ============================================================================

def process_single_pdf(pdf, dry_run, links_only, no_rename, enable_ocr, notebooklm_notebook, logger, log_func):
    """Process a single PDF file with all enabled features."""
    original_name = pdf.name
    
    # Check if already processed (resume functionality)
    if logger and logger.is_processed(pdf):
        log_func(f"{BLUE}⏭️  Skipped (already processed): {original_name}{RESET}")
        logger.log_event('skipped', pdf, {'reason': 'already_processed'})
        return {'skipped': 1}
    
    # Clean PDF content
    changed, text_hits, link_hits, err = process_pdf(pdf, links_only, dry_run)

    if err:
        log_func(f"{RED}‼️ Failed: {original_name} | {err}{RESET}")
        if logger:
            logger.log_event('failed', pdf, {'error': err, 'stage': 'cleaning'})
        return {'failed': 1, 'error': err, 'filename': pdf.name}

    # Rename file if needed
    did_rename = False
    new_path = pdf
    
    if not no_rename:
        try:
            did_rename, new_path = rename_if_needed(pdf, dry_run)
        except Exception as e:
            log_func(f"{RED}‼️ Rename failed: {original_name} | {str(e)}{RESET}")
            if logger:
                logger.log_event('failed', new_path, {'error': str(e), 'stage': 'renaming'})
            return {'failed': 1, 'error': str(e), 'filename': pdf.name}

    result = {'cleaned': 0, 'renamed': 0, 'failed': 0, 'ocr': 0, 'uploaded': 0}
    
    if did_rename:
        result['renamed'] = 1

    # Set icons based on dry run mode
    fail_icon = "🏳️" if dry_run else "‼️"
    clean_icon = "🏳️" if dry_run else "♻️"
    rename_icon = "🏳️" if dry_run else "ℹ️"
    ocr_icon = "🏳️" if dry_run else "🔍"
    upload_icon = "🏳️" if dry_run else "☁️"

    # Log cleaning/renaming results
    if changed:
        result['cleaned'] = 1
        status = "Would clean" if dry_run else "Cleaned"
        rename_str = f" & Renamed -> {new_path.name}" if did_rename else ""
        log_func(f"{GREEN}{clean_icon} {status}: {original_name} (hits={text_hits+link_hits}){rename_str}{RESET}")
        if logger:
            logger.log_event('cleaned', new_path, {
                'original_name': original_name,
                'text_hits': text_hits,
                'link_hits': link_hits,
                'renamed': did_rename,
                'new_name': new_path.name if did_rename else None
            })
    elif did_rename:
        status = "Would rename" if dry_run else "Renamed"
        log_func(f"{BLUE}{rename_icon} {status}: {original_name} -> {new_path.name}{RESET}")
        if logger:
            logger.log_event('renamed', new_path, {
                'original_name': original_name,
                'new_name': new_path.name
            })
    
    # Perform OCR if enabled
    if enable_ocr and not dry_run:
        if ocr_pdf(new_path, log_func):
            result['ocr'] = 1
            log_func(f"{CYAN}{ocr_icon} OCR processed: {new_path.name}{RESET}")
            if logger:
                logger.log_event('ocr', new_path, {'success': True})
        else:
            if logger:
                logger.log_event('ocr', new_path, {'success': False})
    
    # Upload to NotebookLM if enabled
    if notebooklm_notebook and not dry_run:
        if upload_to_notebooklm(new_path, notebooklm_notebook, log_func):
            result['uploaded'] = 1
            if logger:
                logger.log_event('upload', new_path, {
                    'notebook': notebooklm_notebook,
                    'success': True
                })
        else:
            if logger:
                logger.log_event('upload', new_path, {
                    'notebook': notebooklm_notebook,
                    'success': False
                })
    
    # Mark as processed
    if logger and not dry_run:
        logger.mark_processed(new_path)

    return result

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main CLI entry point and orchestration function."""
    if len(sys.argv) < 2:
        print('Usage: python oceanofpdfs_remover.py "<path>" [paths...] [options]')
        print('\nOptions:')
        print('  --dry-run              Preview changes without modifying files')
        print('  --links-only           Remove only hyperlinks (fastest)')
        print('  --no-rename            Skip filename normalization')
        print('  --no-progress          Disable progress bar (streaming mode)')
        print('  --log <directory>      Enable logging and resume to specified directory')
        print('  --ocrmypdf             Perform OCR on PDFs (requires ocrmypdf package)')
        print('  --notebooklm <name>    Upload PDFs to NotebookLM notebook')
        print('\nExample:')
        print('  python oceanofpdfs_remover.py "C:\\Books" --log "C:\\logs\\pdfs" --ocrmypdf')
        return 1

    # Parse command-line arguments
    paths = []
    args = {}
    i = 1
    
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg.startswith('--'):
            # Handle flags with values
            if arg in ['--log', '--notebooklm']:
                if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('--'):
                    args[arg] = sys.argv[i + 1]
                    i += 2
                    continue
                else:
                    print(f"{RED}Error: {arg} requires a value{RESET}")
                    return 1
            else:
                # Boolean flags
                args[arg] = True
                i += 1
        else:
            # It's a path
            p = Path(arg.strip('"\'').strip()).expanduser()
            if p.exists():
                paths.append(p)
            else:
                print(f"{RED}Error: Path not found: {p}{RESET}")
            i += 1

    if not paths:
        print(f"{RED}Error: No valid paths provided{RESET}")
        return 1

    # Extract settings
    dry_run = '--dry-run' in args
    links_only = '--links-only' in args
    no_rename = '--no-rename' in args
    no_progress = '--no-progress' in args
    log_dir = Path(args.get('--log')) if '--log' in args else None
    enable_ocr = '--ocrmypdf' in args
    notebooklm_notebook = args.get('--notebooklm')

    # Initialize logger
    logger = ProcessLogger(log_dir) if log_dir else None
    if logger:
        print(f"{GREEN}✓ Logging enabled: {logger.log_file}{RESET}")
        print(f"{GREEN}✓ Resume file: {logger.resume_file}{RESET}\n")

    # Setup keyboard abort handler
    setup_abort_handler()

    # Initialize statistics
    errors = {}
    cleaned = renamed = failed = skipped = ocr_count = uploaded = 0

    def log(msg):
        """Smart logging function."""
        if no_progress or not tqdm:
            print(msg)
        else:
            tqdm.write(msg)

    # Process based on mode
    if no_progress or not tqdm:
        # Streaming mode
        print(f"{CYAN}Starting streaming processing...{RESET}\n")
        
        processed = 0
        current_folder = None
        
        for target in paths:
            for pdf in collect_pdfs_streaming(target, callback=lambda p: None):
                folder = pdf.parent
                if folder != current_folder:
                    current_folder = folder
                    folder_str = str(folder)
                    if len(folder_str) > 80:
                        folder_str = "..." + folder_str[-77:]
                    print(f"\n{CYAN}Processing folder:{RESET} {folder_str}")
                
                result = process_single_pdf(
                    pdf, dry_run, links_only, no_rename, 
                    enable_ocr, notebooklm_notebook, logger, log
                )
                
                processed += 1
                if 'failed' in result:
                    failed += result['failed']
                    if 'error' in result:
                        errors.setdefault(result['error'], []).append(result['filename'])
                elif 'skipped' in result:
                    skipped += result['skipped']
                else:
                    cleaned += result.get('cleaned', 0)
                    renamed += result.get('renamed', 0)
                    ocr_count += result.get('ocr', 0)
                    uploaded += result.get('uploaded', 0)
        
        total_processed = processed
        
    else:
        # Standard mode with progress bar
        local_pdfs, cloud_pdfs = collect_pdfs_all(paths, show_progress=True)
        all_pdfs = local_pdfs + cloud_pdfs
        
        if cloud_pdfs:
            print(f"\n{CYAN}Processing local files first, cloud-synced files last...{RESET}\n")
        
        iterator = tqdm(all_pdfs, desc="Processing PDFs", unit="file")
        
        for pdf in iterator:
            result = process_single_pdf(
                pdf, dry_run, links_only, no_rename,
                enable_ocr, notebooklm_notebook, logger, log
            )
            
            if 'failed' in result:
                failed += result['failed']
                if 'error' in result:
                    errors.setdefault(result['error'], []).append(result['filename'])
            elif 'skipped' in result:
                skipped += result['skipped']
            else:
                cleaned += result.get('cleaned', 0)
                renamed += result.get('renamed', 0)
                ocr_count += result.get('ocr', 0)
                uploaded += result.get('uploaded', 0)
        
        total_processed = len(all_pdfs)

    # Final summary
    mode_label = f"{CYAN}DRY RUN{RESET}" if dry_run else f"{CYAN}DONE{RESET}"
    print(f"\n{mode_label}: {total_processed} processed | {cleaned} cleaned | {renamed} renamed | {failed} failed")
    
    if skipped > 0:
        print(f"  {BLUE}↳ {skipped} skipped (already processed){RESET}")
    if ocr_count > 0:
        print(f"  {CYAN}↳ {ocr_count} OCR processed{RESET}")
    if uploaded > 0:
        print(f"  {MAGENTA}↳ {uploaded} uploaded to NotebookLM{RESET}")

    # Error summary
    if errors:
        print(f"\n{RED}Failure summary:{RESET}")
        for reason, files in errors.items():
            print(f"\n{reason}")
            for f in files[:10]:
                print(f"  - {f}")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more")

    # Log file location reminder
    if logger:
        print(f"\n{GREEN}📋 Log file saved: {logger.log_file}{RESET}")
        print(f"{GREEN}📋 Resume file: {logger.resume_file}{RESET}")

    return 0 if not failed else 2

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{RED}Process interrupted.{RESET}")
        sys.exit(1)
