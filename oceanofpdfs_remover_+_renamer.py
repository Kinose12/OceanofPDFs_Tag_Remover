"""
OceanofPDFs Tag Remover & Renamer (Color Edition)
------------------------------------------------
A utility to redact watermarks and normalize filenames for ebook libraries.

This script performs two main functions:
1. Content Cleanup: Removes "OceanofPDFs.com" text and hyperlinks from PDFs
2. Filename Normalization: Renames files to human-readable formats

Author: Theodore Eich
License: MIT
Repository: https://github.com/yourusername/oceanofpdfs-remover
Python Version: 3.10+

Key Features:
- Dual processing modes (standard with progress bar, streaming for immediate processing)
- Cloud-sync awareness (detects and defers OneDrive, Dropbox, etc.)
- Full timestamp preservation (access, modification, and creation times)
- Atomic file operations (no partial overwrites)
- Comprehensive error handling and reporting
"""

import os
import sys
import re
import shutil
import time
from pathlib import Path
import fitz  # PyMuPDF - PDF manipulation library

# Attempt to load tqdm for progress bars (optional dependency)
try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

# ============================================================================
# ANSI COLOR CODES FOR TERMINAL OUTPUT
# ============================================================================
# These codes enable colored console output for better readability
# They work on most modern terminals (Windows 10+, macOS, Linux)
RED = "\033[91m"      # Error messages, failures
GREEN = "\033[92m"    # Success messages, cleaned files
BLUE = "\033[94m"     # Information, renamed files
CYAN = "\033[96m"     # Headers, mode labels
YELLOW = "\033[93m"   # Warnings, counts
RESET = "\033[0m"     # Reset to default color

# ============================================================================
# MUPDF CONFIGURATION
# ============================================================================
# Suppress MuPDF's internal error and warning messages to console
# Many PDFs have minor structural issues that don't affect our processing
# but generate noise. We handle errors ourselves at a higher level.
fitz.TOOLS.mupdf_display_errors(False)
fitz.TOOLS.mupdf_display_warnings(False)

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================
# Target phrase to remove from PDFs (case-insensitive with spacing variations)
PHRASE = "OceanofPDFs.com"

# URI pattern for hyperlink matching
URI_MATCH = "OceanofPDFs.com"

# Common filename prefix pattern to clean
# Example: "_OceanofPDFs.com_Book_Title_-_Author.pdf"
PREFIX = "_OceanofPDFs.com_"

# Z-Library suffix pattern to remove
# Example: "Book_Title_ (Z-Library).pdf"
ZLIB_SUFFIX = "_ (Z-Library)"

# Regex pattern to catch "OceanofPDFs.com" with variable spacing
# Matches: "OceanofPDFs.com", "O c e a n o f P D F s . c o m", etc.
# (?i) makes it case-insensitive
# \s* allows zero or more whitespace characters between each letter
TEXT_PATTERN = re.compile(r"(?i)o\s*c\s*e\s*a\s*n\s*o\s*f\s*p\s*d\s*f\s*\.\s*c\s*o\s*m")

# ============================================================================
# CLOUD-SYNC DETECTION
# ============================================================================
# List of folder name patterns that indicate cloud-synced directories
# Files in these folders are processed last to avoid timeout errors
CLOUD_PATTERNS = [
    "onedrive",           # Microsoft OneDrive
    "dropbox",            # Dropbox
    "google drive",       # Google Drive
    "crossdevice",        # Samsung/cross-device sync
    "icloud",             # Apple iCloud
    "box sync",           # Box.com
    "sync",               # Generic sync folders
    "cloud"               # Generic cloud folders
]

def is_cloud_path(path: Path) -> bool:
    """
    Determine if a file path is within a cloud-synced folder.
    
    Cloud-synced folders often have timeout issues during file operations
    because the cloud service may be uploading/syncing the file. By detecting
    these paths, we can process them last or apply retry logic.
    
    Args:
        path: Path object to check
        
    Returns:
        True if path contains any cloud pattern, False otherwise
        
    Examples:
        >>> is_cloud_path(Path("C:/Users/John/OneDrive/Books/file.pdf"))
        True
        >>> is_cloud_path(Path("C:/Users/John/Documents/file.pdf"))
        False
    """
    path_str = str(path).lower()
    return any(pattern in path_str for pattern in CLOUD_PATTERNS)

# ============================================================================
# PDF DISCOVERY FUNCTIONS
# ============================================================================

def collect_pdfs_streaming(target: Path, callback=None):
    """
    Generator that yields PDF files as they're discovered (streaming mode).
    
    This function is used when --no-progress flag is set. It yields PDFs
    one at a time as they're found, allowing immediate processing without
    waiting to count all files first.
    
    Args:
        target: Path to file or directory to search
        callback: Optional function to call with current directory being scanned
        
    Yields:
        Path objects for each PDF file found
        
    Examples:
        >>> for pdf in collect_pdfs_streaming(Path("C:/Books")):
        ...     process_pdf(pdf)
    """
    # If target is a single file, yield it if it's a PDF
    if target.is_file() and target.suffix.lower() == ".pdf":
        yield target
        return
    
    # If target is a directory, walk through it recursively
    if target.is_dir():
        for root, dirs, files in os.walk(target):
            current_path = Path(root)
            
            # Notify callback of current directory (for progress display)
            if callback:
                callback(current_path)
            
            # Yield each PDF file found in this directory
            for file in files:
                if file.lower().endswith('.pdf'):
                    yield current_path / file

def collect_pdfs_all(targets: list[Path], show_progress=True) -> tuple[list[Path], list[Path]]:
    """
    Collect all PDF files from multiple targets, separating cloud-synced ones.
    
    This function is used in standard mode (with progress bar). It scans all
    directories first to get an accurate count, then separates local files
    from cloud-synced files for optimized processing order.
    
    Args:
        targets: List of Path objects (files or directories) to search
        show_progress: If True, display real-time scanning progress
        
    Returns:
        Tuple of (local_pdfs, cloud_pdfs) where each is a list of Path objects
        
    Notes:
        - Shows live updates of current folder being scanned
        - Displays running count of PDFs found
        - Progress updates on a single line (no spam)
        
    Examples:
        >>> local, cloud = collect_pdfs_all([Path("C:/Books"), Path("D:/Library")])
        >>> print(f"Found {len(local)} local and {len(cloud)} cloud PDFs")
    """
    local_pdfs = []   # Files NOT in cloud-synced folders
    cloud_pdfs = []   # Files IN cloud-synced folders
    total_found = 0
    
    if show_progress:
        print(f"{CYAN}Scanning for PDFs...{RESET}")
    
    # Process each target path provided by user
    for target in targets:
        # Handle single file targets
        if target.is_file() and target.suffix.lower() == ".pdf":
            if is_cloud_path(target):
                cloud_pdfs.append(target)
            else:
                local_pdfs.append(target)
            total_found += 1
            
            if show_progress:
                # Update count on same line (\r returns cursor to start)
                print(f"\r{YELLOW}PDFs found: {total_found}{RESET}", end='', flush=True)
            continue
        
        # Handle directory targets (recursive walk)
        if target.is_dir():
            for root, dirs, files in os.walk(target):
                current_path = Path(root)
                
                if show_progress:
                    # Format path for display (truncate if too long)
                    display_path = str(current_path)
                    if len(display_path) > 80:
                        # Show last 77 chars with "..." prefix
                        display_path = "..." + display_path[-77:]
                    
                    # Update single line with folder path and count
                    # \r returns to start, end='' prevents newline, flush=True forces immediate display
                    print(f"\r{CYAN}Scanning:{RESET} {display_path:<80}", end='', flush=True)
                    print(f"\r{CYAN}Scanning:{RESET} {display_path:<80} | {YELLOW}PDFs: {total_found}{RESET}", end='', flush=True)
                
                # Check each file in current directory
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_path = current_path / file
                        
                        # Categorize as local or cloud
                        if is_cloud_path(pdf_path):
                            cloud_pdfs.append(pdf_path)
                        else:
                            local_pdfs.append(pdf_path)
                        
                        total_found += 1
    
    if show_progress:
        # Clear the scanning line and show completion message
        # Extra spaces clear any leftover text from previous updates
        print(f"\r{GREEN}✓ Scan complete: {total_found} PDFs found{RESET}" + " " * 60)
        
        # Inform user about cloud files if any were found
        if cloud_pdfs:
            print(f"{YELLOW}ℹ️  {len(cloud_pdfs)} cloud-synced files will be processed last{RESET}")
    
    return local_pdfs, cloud_pdfs

# ============================================================================
# TIMESTAMP PRESERVATION FUNCTIONS
# ============================================================================

def restore_times(path: Path, atime, mtime, ctime):
    """
    Restore file access, modification, and creation timestamps.
    
    Preserving timestamps is important because:
    - Users may sort by date modified to find recent additions
    - Creation date preserves original download/creation information
    - Access time tracking can be useful for library management
    
    Args:
        path: Path to file whose timestamps should be restored
        atime: Access time (seconds since epoch)
        mtime: Modification time (seconds since epoch)
        ctime: Creation time (seconds since epoch, Windows only)
        
    Notes:
        - On Windows, uses pywin32 if available for true creation time
        - On Unix systems, ctime is metadata change time (can't be preserved)
        - Fails silently if permissions don't allow timestamp changes
        
    Platform Differences:
        Windows: atime, mtime, and ctime (creation) all preserved
        macOS/Linux: atime and mtime preserved, ctime is metadata change time
    """
    if atime is None or mtime is None:
        return
    
    try:
        # Restore access and modification times (works on all platforms)
        os.utime(path, (atime, mtime))
        
        # On Windows, restore creation time using pywin32 if available
        if sys.platform == 'win32' and ctime is not None:
            try:
                import pywintypes
                import win32file
                import win32con
                from datetime import datetime
                
                # Open file handle with write permission
                handle = win32file.CreateFile(
                    str(path),
                    win32con.GENERIC_WRITE,
                    win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                    None,
                    win32con.OPEN_EXISTING,
                    win32con.FILE_ATTRIBUTE_NORMAL,
                    None
                )
                
                # Set creation time (first parameter)
                # None for access and modification times (already set with os.utime)
                win32file.SetFileTime(handle, pywintypes.Time(ctime), None, None)
                win32file.CloseHandle(handle)
            except Exception:
                # Silently fail if pywin32 not available
                # File is still usable, just without creation time preservation
                pass
    except Exception:
        # Fail silently - some filesystems or permissions may prevent this
        pass

def get_file_times(path: Path):
    """
    Retrieve all file timestamps (access, modification, creation).
    
    Args:
        path: Path to file to query
        
    Returns:
        Tuple of (atime, mtime, ctime) as floats (seconds since epoch)
        Returns (None, None, None) if file cannot be accessed
        
    Notes:
        - On Windows: ctime is actual creation time
        - On Unix: ctime is last metadata change time (not creation)
        
    Examples:
        >>> atime, mtime, ctime = get_file_times(Path("document.pdf"))
        >>> print(f"Last modified: {datetime.fromtimestamp(mtime)}")
    """
    try:
        st = path.stat()
        atime = st.st_atime
        mtime = st.st_mtime
        
        # Platform-specific handling of ctime
        # Windows: ctime = creation time
        # Unix: ctime = metadata change time (use mtime as fallback)
        ctime = st.st_ctime if sys.platform == 'win32' else st.st_mtime
        
        return atime, mtime, ctime
    except Exception:
        # File may not exist or we lack permissions
        return None, None, None

# ============================================================================
# PDF CONTENT MANIPULATION FUNCTIONS
# ============================================================================

def remove_links(page) -> int:
    """
    Find and delete hyperlink annotations pointing to target URI.
    
    PDF hyperlinks are stored as annotations (not embedded in text).
    These annotations create blue underlined text that's clickable.
    Even after removing the text, the clickable link may remain.
    
    Args:
        page: PyMuPDF page object to process
        
    Returns:
        Number of links removed from this page
        
    How it works:
        1. Iterate through all link annotations on the page
        2. Check if the link URI contains our target domain
        3. Delete matching links using page.delete_link()
        
    Examples:
        >>> doc = fitz.open("file.pdf")
        >>> removed = remove_links(doc[0])
        >>> print(f"Removed {removed} links from first page")
    """
    removed = 0
    
    # Get all link annotations on this page
    for link in page.get_links():
        uri = link.get("uri", "")
        
        # Check if this link points to our target domain (case-insensitive)
        if uri and URI_MATCH in uri.lower():
            page.delete_link(link)
            removed += 1
    
    return removed

def page_might_contain_phrase(page) -> bool:
    """
    Fast preliminary check if page contains target text.
    
    This is an optimization to avoid expensive redaction operations on
    clean pages. We do a quick text search before the slower redaction.
    
    Args:
        page: PyMuPDF page object to check
        
    Returns:
        True if target phrase (or variants) found, False otherwise
        
    Performance:
        - Quick text extraction: ~0.001s per page
        - Full redaction: ~0.01-0.1s per page
        - This pre-check can speed up processing by 10-100x on clean PDFs
        
    Examples:
        >>> if page_might_contain_phrase(page):
        ...     hits = redact_phrase(page)  # Only redact if phrase found
    """
    # Extract all text from page as plain string
    t = page.get_text("text")
    
    # Use regex to search for phrase with spacing variations
    return bool(t and TEXT_PATTERN.search(t))

def redact_phrase(page) -> int:
    """
    Identify target text spans and apply white-out redaction.
    
    This function performs the actual watermark removal by:
    1. Extracting detailed text layout information (dict format)
    2. Finding text spans that match our target pattern
    3. Adding redaction annotations (white rectangles) over those spans
    4. Applying the redactions to permanently remove the text
    
    Args:
        page: PyMuPDF page object to redact
        
    Returns:
        Number of text spans redacted on this page
        
    How Redaction Works:
        - add_redact_annot() marks areas for redaction (reversible)
        - apply_redactions() makes the changes permanent (irreversible)
        - fill=(1,1,1) creates white fill color (RGB: 1.0, 1.0, 1.0)
        - images=PDF_REDACT_IMAGE_NONE preserves images (only text redacted)
        
    Text Dictionary Structure:
        {
            "blocks": [
                {
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "OceanofPDFs.com",
                                    "bbox": [x0, y0, x1, y1],  # Bounding box
                                    ...
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
    Examples:
        >>> hits = redact_phrase(page)
        >>> if hits > 0:
        ...     print(f"Redacted {hits} watermark instances")
    """
    hits = 0
    
    # Extract text with detailed layout information
    # "dict" format provides character-level positioning
    data = page.get_text("dict")
    
    # Navigate the nested structure: blocks -> lines -> spans
    for block in data.get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                txt = span.get("text", "")
                
                # Check if this text span matches our pattern
                if txt and TEXT_PATTERN.search(txt):
                    # Create white rectangle over this text span
                    # bbox is [x0, y0, x1, y1] defining the rectangle
                    page.add_redact_annot(
                        fitz.Rect(span["bbox"]),  # Area to redact
                        fill=(1, 1, 1)            # White color (RGB)
                    )
                    hits += 1
    
    # Apply all redactions if any were added
    if hits:
        page.apply_redactions(
            images=fitz.PDF_REDACT_IMAGE_NONE  # Don't touch images
        )
    
    return hits

def process_pdf(pdf_path: Path, links_only=False, dry_run=False):
    """
    Core PDF cleaning logic with atomic file replacement.
    
    This is the main workhorse function that:
    1. Opens the PDF
    2. Removes hyperlinks from all pages
    3. Optionally removes watermark text
    4. Saves to temporary file
    5. Atomically replaces original
    6. Restores timestamps
    
    Args:
        pdf_path: Path to PDF file to process
        links_only: If True, skip text redaction (faster)
        dry_run: If True, don't save changes (preview mode)
        
    Returns:
        Tuple of (changed, text_hits, link_hits, error_str)
        - changed: True if any modifications were made
        - text_hits: Number of text spans redacted
        - link_hits: Number of links removed
        - error_str: Error message if processing failed, None otherwise
        
    Atomic Replacement Strategy:
        1. Create temp file: original.pdf.tmp
        2. Apply all modifications to temp file
        3. If successful, move temp -> original (atomic on most filesystems)
        4. If failed, delete temp file (original unchanged)
        
    This ensures we never have a partially-modified PDF.
    
    Error Handling:
        - Any exception during processing is caught
        - Original file is never touched if processing fails
        - Temp file is cleaned up automatically
        - Error details returned in tuple for reporting
        
    Examples:
        >>> changed, text, links, err = process_pdf(Path("book.pdf"))
        >>> if err:
        ...     print(f"Failed: {err}")
        >>> elif changed:
        ...     print(f"Cleaned: {text+links} hits")
    """
    # Create temporary file path (same location, .tmp extension)
    temp = pdf_path.with_suffix(pdf_path.suffix + ".tmp")
    text_hits = link_hits = 0

    # Capture current timestamps before opening file
    atime, mtime, ctime = get_file_times(pdf_path)

    try:
        # Open PDF (this loads it into memory)
        doc = fitz.open(pdf_path)
        
        # PASS 1: Remove hyperlinks (fast, applies to all pages)
        for page in doc:
            link_hits += remove_links(page)

        # PASS 2: Remove text watermarks (slower, only where needed)
        if not links_only:
            for page in doc:
                # Quick check before expensive redaction
                if page_might_contain_phrase(page):
                    text_hits += redact_phrase(page)

        # Determine if we made any changes
        changed = (text_hits + link_hits) > 0

        # Dry run mode: just report what would change, don't save
        if dry_run:
            doc.close()
            return True, text_hits, link_hits, None

        # Save to temp file if changes were made
        if changed:
            doc.save(
                temp,
                garbage=4,    # Garbage collection level (remove unused objects)
                deflate=True, # Compress streams
                clean=True    # Clean up structure
            )
        
        # Close the document (releases file handle)
        doc.close()

        # If no changes, just clean up and return
        if not changed:
            if temp.exists():
                temp.unlink()
            return False, 0, 0, None

        # Atomically replace original with modified version
        # shutil.move is atomic on most filesystems when source and dest are on same drive
        shutil.move(temp, pdf_path)
        
        # Restore original timestamps
        restore_times(pdf_path, atime, mtime, ctime)
        
        return True, text_hits, link_hits, None

    except Exception as e:
        # Clean up temp file if it exists
        if temp.exists():
            temp.unlink()
        
        # Return error information
        # -1 for hit counts indicates processing failed
        return False, -1, -1, str(e)

# ============================================================================
# FILENAME MANIPULATION FUNCTIONS
# ============================================================================

def sanitize(s: str) -> str:
    """
    Remove illegal Windows filename characters.
    
    Windows prohibits these characters in filenames:
    \ / : * ? " < > |
    
    Args:
        s: String to sanitize
        
    Returns:
        Cleaned string with illegal characters removed and whitespace trimmed
        
    Examples:
        >>> sanitize('Book: The "Great" Novel')
        'Book The Great Novel'
        >>> sanitize('  File/Path\\Name  ')
        'File Path Name'
    """
    # Replace illegal characters with empty string
    cleaned = re.sub(r'[\\/:*?"<>|]', "", s)
    
    # Remove leading/trailing whitespace
    return cleaned.strip()

def unique_path(p: Path) -> Path:
    """
    Handle filename collisions by adding incremental suffix.
    
    If the target filename already exists, this function finds a unique
    name by appending (1), (2), (3), etc. before the extension.
    
    Args:
        p: Desired Path object
        
    Returns:
        Path object that doesn't exist (either original or with suffix)
        
    Examples:
        >>> unique_path(Path("document.pdf"))  # If doesn't exist
        Path("document.pdf")
        >>> unique_path(Path("document.pdf"))  # If exists
        Path("document (1).pdf")
        >>> unique_path(Path("document.pdf"))  # If (1) also exists
        Path("document (2).pdf")
    """
    # If path doesn't exist, we can use it as-is
    if not p.exists():
        return p
    
    # Try incrementing numbers until we find one that doesn't exist
    i = 1
    while True:
        # with_stem() replaces the filename (without extension)
        cand = p.with_stem(f"{p.stem} ({i})")
        if not cand.exists():
            return cand
        i += 1

def compute_rename(pdf_path: Path):
    """
    Calculate new filename based on pattern matching rules.
    
    This function implements the filename normalization logic:
    
    Rule 1: Remove Z-Library suffix
        "Book_ (Z-Library).pdf" -> "Book.pdf"
    
    Rule 2: Reformat OceanofPDFs prefix pattern
        "_OceanofPDFs.com_Title_-_Author.pdf" -> "Author - Title.pdf"
    
    Rule 3: Normalize underscores and whitespace
        "Book___Title__Name.pdf" -> "Book Title Name.pdf"
    
    Args:
        pdf_path: Current Path of the PDF file
        
    Returns:
        New Path object if rename is needed, None if file is already clean
        
    Notes:
        - Rules are applied in order
        - Returns None if no changes needed (already has clean name)
        - Automatically handles collisions with unique_path()
        
    Examples:
        >>> compute_rename(Path("_OceanofPDFs.com_Gatsby_-_Fitzgerald.pdf"))
        Path("Fitzgerald - Gatsby.pdf")
        >>> compute_rename(Path("already_clean.pdf"))
        None
    """
    # Start with current filename (without extension)
    name = pdf_path.stem

    # RULE 1: Remove Z-Library suffix if present
    # Example: "Book_ (Z-Library)" -> "Book"
    if name.endswith(ZLIB_SUFFIX):
        name = name[: -len(ZLIB_SUFFIX)]

    # RULE 2: Reformat OceanofPDFs pattern
    # Example: "_OceanofPDFs.com_Book_Title_-_Author_Name"
    #       -> "Author Name - Book Title"
    if name.startswith(PREFIX):
        # Remove the prefix
        remainder = name[len(PREFIX):]
        
        # Split on "_-_" separator (title and author separator)
        parts = remainder.split("_-_", 1)
        
        if len(parts) == 2:
            title, author = parts
            # Clean each part and reorder
            title = sanitize(title)
            author = sanitize(author)
            name = f"{author} - {title}"

    # RULE 3: Normalize underscores and whitespace
    # Replace multiple underscores with single space
    name = re.sub(r"_+", " ", name)
    
    # Replace multiple spaces with single space
    name = re.sub(r"\s+", " ", name)
    
    # Trim leading/trailing whitespace
    name = name.strip()

    # Create new path with cleaned name
    new_path = pdf_path.with_name(name + pdf_path.suffix)
    
    # Check if name actually changed
    if new_path == pdf_path:
        return None  # No rename needed
    
    # Handle potential collisions
    return unique_path(new_path)

def rename_if_needed(pdf_path: Path, dry_run=False, retries=3):
    """
    Execute file renaming with retry logic for cloud-synced files.
    
    This function:
    1. Calculates new filename using compute_rename()
    2. Preserves timestamps before rename
    3. Attempts rename with automatic retries
    4. Restores timestamps after rename
    
    Args:
        pdf_path: Current Path of the file
        dry_run: If True, only simulate rename (don't actually do it)
        retries: Number of retry attempts for cloud timeout errors
        
    Returns:
        Tuple of (did_rename, new_path)
        - did_rename: True if file was (or would be) renamed
        - new_path: New Path object (same as old if no rename)
        
    Retry Logic:
        Cloud-synced folders (OneDrive, Dropbox, etc.) can timeout during
        rename operations. This function automatically retries 3 times with
        1-second delays between attempts.
        
    Errors:
        - Raises exception if rename fails after all retries
        - OSError with "cloud operation" or "time-out" triggers retry
        - Other errors are raised immediately
        
    Examples:
        >>> did_rename, new_path = rename_if_needed(Path("old_name.pdf"))
        >>> if did_rename:
        ...     print(f"Renamed to: {new_path.name}")
    """
    # Calculate what the new name should be
    new_path = compute_rename(pdf_path)
    
    # If no rename needed, return early
    if not new_path:
        return False, pdf_path

    # Capture timestamps before rename
    atime, mtime, ctime = get_file_times(pdf_path)

    # Dry run: just report what would happen
    if dry_run:
        return True, new_path

    # Attempt rename with retry logic for cloud files
    for attempt in range(retries):
        try:
            # Perform the actual rename
            pdf_path.rename(new_path)
            
            # Restore timestamps on the renamed file
            restore_times(new_path, atime, mtime, ctime)
            
            return True, new_path
            
        except OSError as e:
            # Check if this is a cloud timeout error
            error_msg = str(e).lower()
            is_cloud_error = "cloud operation" in error_msg or "time-out" in error_msg
            
            if is_cloud_error and attempt < retries - 1:
                # Wait before retry
                time.sleep(1)
                continue  # Try again
            
            # Either not a cloud error, or we've exhausted retries
            raise  # Re-raise the exception
    
    # Should never reach here, but just in case
    return False, pdf_path

# ============================================================================
# SINGLE PDF PROCESSING FUNCTION
# ============================================================================

def process_single_pdf(pdf, dry_run, links_only, no_rename, log_func):
    """
    Process a single PDF file (clean content and optionally rename).
    
    This is a wrapper function that combines PDF content cleaning and
    filename normalization into a single operation. It's called for each
    PDF in the batch processing loop.
    
    Args:
        pdf: Path object of the PDF to process
        dry_run: If True, simulate changes without modifying files
        links_only: If True, only remove links (skip text redaction)
        no_rename: If True, skip filename normalization
        log_func: Function to call for logging (e.g., print or tqdm.write)
        
    Returns:
        Dictionary with keys:
        - 'cleaned': 1 if PDF was cleaned, 0 otherwise
        - 'renamed': 1 if PDF was renamed, 0 otherwise
        - 'failed': 1 if processing failed, 0 otherwise
        - 'error': Error message (if failed)
        - 'filename': Original filename (if failed)
        
    This function is designed to be called in a loop over many PDFs,
    accumulating statistics for the final summary report.
    
    Examples:
        >>> stats = process_single_pdf(
        ...     Path("book.pdf"),
        ...     dry_run=False,
        ...     links_only=False,
        ...     no_rename=False,
        ...     log_func=print
        ... )
        >>> total_cleaned += stats['cleaned']
    """
    original_name = pdf.name
    
    # STEP 1: Clean PDF content (remove watermarks and links)
    changed, text_hits, link_hits, err = process_pdf(pdf, links_only, dry_run)

    # Handle processing failure
    if err:
        log_func(f"{RED}‼️ Failed: {original_name} | {err}{RESET}")
        return {'failed': 1, 'error': err, 'filename': pdf.name}

    # STEP 2: Rename file if needed and not disabled
    did_rename = False
    new_path = pdf
    
    if not no_rename:
        try:
            did_rename, new_path = rename_if_needed(pdf, dry_run)
        except Exception as e:
            # Rename failure is separate from processing failure
            log_func(f"{RED}‼️ Rename failed: {original_name} | {str(e)}{RESET}")
            return {'failed': 1, 'error': str(e), 'filename': pdf.name}

    # Initialize result counters
    result = {'cleaned': 0, 'renamed': 0, 'failed': 0}
    
    if did_rename:
        result['renamed'] = 1

    # Set icons based on dry run mode
    # In dry run, use flag icon; in actual mode, use descriptive icons
    fail_icon = "🏳️" if dry_run else "‼️"
    clean_icon = "🏳️" if dry_run else "♻️"
    rename_icon = "🏳️" if dry_run else "ℹ️"

    # Log the result with appropriate message
    if changed:
        result['cleaned'] = 1
        status = "Would clean" if dry_run else "Cleaned"
        rename_str = f" & Renamed -> {new_path.name}" if did_rename else ""
        log_func(f"{GREEN}{clean_icon} {status}: {original_name} (hits={text_hits+link_hits}){rename_str}{RESET}")
    elif did_rename:
        status = "Would rename" if dry_run else "Renamed"
        log_func(f"{BLUE}{rename_icon} {status}: {original_name} -> {new_path.name}{RESET}")

    return result

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """
    Main CLI entry point and orchestration function.
    
    This function:
    1. Parses command-line arguments
    2. Validates input paths
    3. Chooses processing mode (standard vs streaming)
    4. Orchestrates PDF processing
    5. Displays summary statistics
    6. Reports errors
    
    Command-Line Usage:
        python script.py <path1> [path2 ...] [--dry-run] [--links-only] [--no-rename] [--no-progress]
        
    Arguments:
        paths: One or more file or directory paths
        --dry-run: Preview changes without modifying files
        --links-only: Remove only hyperlinks (fastest)
        --no-rename: Skip filename normalization
        --no-progress: Use streaming mode (process as found, no progress bar)
        
    Processing Modes:
        Standard Mode (default):
        - Scans all paths first
        - Shows total count and progress bar
        - Processes local files first, cloud files last
        
        Streaming Mode (--no-progress):
        - Processes files immediately as found
        - No initial scan delay
        - Shows folder changes in real-time
        
    Return Codes:
        0: Success (all files processed)
        1: Invalid arguments or no paths provided
        2: Some files failed to process
        
    Examples:
        >>> sys.argv = ['script.py', 'C:/Books', '--dry-run']
        >>> sys.exit(main())
    """
    # Check if user provided any arguments
    if len(sys.argv) < 2:
        print('Usage: python oceanofpdfs_remover.py "<path>" [paths...] [--dry-run] [--links-only] [--no-rename] [--no-progress]')
        return 1

    # Parse command-line arguments (separate paths from flags)
    paths = []
    args = set()
    
    for arg in sys.argv[1:]:
        if arg.startswith('--'):
            # It's a flag
            args.add(arg)
        else:
            # It's a path - strip quotes and expand ~ to home directory
            p = Path(arg.strip('"\'').strip()).expanduser()
            if p.exists():
                paths.append(p)
            else:
                print(f"{RED}Error: Path not found: {p}{RESET}")

    # Validate that at least one valid path was provided
    if not paths:
        print(f"{RED}Error: No valid paths provided{RESET}")
        return 1

    # Extract flag states
    dry_run = "--dry-run" in args
    links_only = "--links-only" in args
    no_rename = "--no-rename" in args
    no_progress = "--no-progress" in args

    # Initialize statistics counters
    errors = {}      # {error_message: [filenames]}
    cleaned = 0      # Count of PDFs cleaned
    renamed = 0      # Count of PDFs renamed
    failed = 0       # Count of PDFs that failed

    def log(msg):
        """
        Smart logging function that works with or without tqdm.
        
        When using tqdm progress bar, we need to use tqdm.write() to prevent
        the progress bar from being overwritten. In streaming mode or when
        tqdm is not available, we use regular print().
        """
        if no_progress or not tqdm:
            print(msg)
        else:
            tqdm.write(msg)

    # ========================================================================
    # PROCESSING MODE SELECTION
    # ========================================================================
    
    if no_progress or not tqdm:
        # ====================================================================
        # STREAMING MODE: Process files as they're discovered
        # ====================================================================
        # This mode is faster to start but doesn't show total progress
        
        print(f"{CYAN}Starting streaming processing...{RESET}\n")
        
        processed = 0
        current_folder = None
        
        # Process each target path
        for target in paths:
            # Stream PDFs from this target
            for pdf in collect_pdfs_streaming(target, callback=lambda p: None):
                # Show folder change for context
                folder = pdf.parent
                if folder != current_folder:
                    current_folder = folder
                    folder_str = str(folder)
                    
                    # Truncate long paths
                    if len(folder_str) > 80:
                        folder_str = "..." + folder_str[-77:]
                    
                    print(f"\n{CYAN}Processing folder:{RESET} {folder_str}")
                
                # Process this PDF
                result = process_single_pdf(pdf, dry_run, links_only, no_rename, log)
                
                # Update statistics
                processed += 1
                if 'failed' in result:
                    failed += result['failed']
                    if 'error' in result:
                        errors.setdefault(result['error'], []).append(result['filename'])
                else:
                    cleaned += result.get('cleaned', 0)
                    renamed += result.get('renamed', 0)
        
        total_processed = processed
        
    else:
        # ====================================================================
        # STANDARD MODE: Collect all PDFs first, then process with progress bar
        # ====================================================================
        # This mode shows accurate progress but has initial scan delay
        
        local_pdfs, cloud_pdfs = collect_pdfs_all(paths, show_progress=True)
        all_pdfs = local_pdfs + cloud_pdfs
        
        # Inform user about processing order
        if cloud_pdfs:
            print(f"\n{CYAN}Processing local files first, cloud-synced files last...{RESET}\n")
        
        # Create progress bar
        iterator = tqdm(all_pdfs, desc="Processing PDFs", unit="file")
        
        # Process each PDF with progress bar
        for pdf in iterator:
            result = process_single_pdf(pdf, dry_run, links_only, no_rename, log)
            
            # Update statistics
            if 'failed' in result:
                failed += result['failed']
                if 'error' in result:
                    errors.setdefault(result['error'], []).append(result['filename'])
            else:
                cleaned += result.get('cleaned', 0)
                renamed += result.get('renamed', 0)
        
        total_processed = len(all_pdfs)

    # ========================================================================
    # FINAL SUMMARY REPORT
    # ========================================================================
    
    mode_label = f"{CYAN}DRY RUN{RESET}" if dry_run else f"{CYAN}DONE{RESET}"
    print(f"\n{mode_label}: {total_processed} processed | {cleaned} cleaned | {renamed} renamed | {failed} failed")

    # Display error summary if any failures occurred
    if errors:
        print(f"\n{RED}Failure summary:{RESET}")
        
        # Group errors by error message
        for reason, files in errors.items():
            print(f"\n{reason}")
            
            # Show first 10 files with this error
            for f in files[:10]:
                print(f"  - {f}")
            
            # If more than 10, show count of remaining
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more")

    # Return appropriate exit code
    return 0 if not failed else 2

# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """
    Script entry point with keyboard interrupt handling.
    
    This block only runs when the script is executed directly (not imported).
    It wraps main() with a try-except to handle Ctrl+C gracefully.
    """
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        # User pressed Ctrl+C - exit gracefully
        print(f"\n{RED}Process interrupted.{RESET}")
        sys.exit(1)
