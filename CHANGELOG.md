# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-02-01

### Added
- **CTRL-Q Abort Feature**: Press CTRL-Q during scanning to abort and process files found so far
  - Requires optional `keyboard` package
  - Shows helpful prompt during scan: "Press CTRL-Q to abort scan and process files found so far"
  - Gracefully stops scanning and proceeds to processing
  
- **Logging System with Resume Capability**: 
  - `--log <directory>` flag enables comprehensive logging
  - Creates JSONL log files with timestamps and event details
  - Maintains `processed_files.json` for resume functionality
  - Automatically skips previously processed files on subsequent runs
  - Perfect for large batches and interrupted processing
  
- **OCR Integration**:
  - `--ocrmypdf` flag enables OCR processing
  - Automatically detects if PDF already has text (skips if searchable)
  - Uses optimized ocrmypdf settings for speed
  - Preserves timestamps after OCR
  - Makes PDFs searchable for tools like NotebookLM
  
- **NotebookLM Preparation**:
  - `--notebooklm <notebook_name>` flag prepares PDFs for upload
  - Copies files to staging directory: `~/notebooklm_staging/<notebook_name>/`
  - Maintains timestamps during copy
  - Ready for manual upload (NotebookLM API not yet available)
  - Logs upload events for tracking

### Changed
- Enhanced help message with all new flags and examples
- Improved error messages for missing flag values
- Log output now includes OCR and upload status
- Summary statistics now show skipped, OCR'd, and uploaded counts

### Technical
- Added `ProcessLogger` class for comprehensive logging
- Added `ocr_pdf()` function with smart text detection
- Added `upload_to_notebooklm()` function (staging mode)
- Global `ABORT_SCAN` flag for keyboard interrupt handling
- Enhanced `process_single_pdf()` to support all new features

## [2.0.0] - 2025-02-01

### Added
- **Real-time Scanning Feedback**: Live updates showing current folder path and PDF count during scanning
- **Dual Processing Modes**: 
  - Standard mode with progress bar (default)
  - Streaming mode with `--no-progress` flag for immediate processing
- **Cloud-Sync Intelligence**: Automatic detection and deferred processing of cloud-synced folders
- **Retry Logic**: 3 automatic retries for cloud timeout errors
- **Full Timestamp Preservation**: Now preserves creation date (ctime) on Windows with pywin32
- **Multi-path Support**: Process multiple directories/drives in a single command
- **Improved Error Handling**: Separate handling for rename failures vs processing failures

### Changed
- **Eliminated Startup Lag**: Scanning feedback now appears immediately
- **Optimized Cloud File Handling**: Cloud-synced files processed last to prevent blocking
- **Better Console Output**: Single-line updating progress during scan (no spam)
- **Enhanced Error Reporting**: More detailed error context and grouping

### Fixed
- Timestamps not preserved correctly (atime, mtime, ctime all now preserved)
- Long delay before console output appears
- Cloud-synced file timeout errors causing script to crash
- Progress bar not showing accurate totals

## [1.0.0] - 2024-12-XX

### Added
- Initial release
- OceanofPDFs.com text watermark removal with regex pattern matching
- Hyperlink annotation removal
- Automatic filename normalization:
  - `_OceanofPDFs.com_` prefix removal
  - Z-Library suffix removal
  - Author-title reordering
  - Underscore to space conversion
- Command-line flags: `--dry-run`, `--links-only`, `--no-rename`
- Progress bar with tqdm
- Recursive directory processing
- Collision-safe renaming with automatic incrementing
- Error grouping and reporting
- ANSI color-coded console output
- Timestamp preservation (atime, mtime)

### Technical Details
- Built with PyMuPDF (fitz) for PDF manipulation
- Two-pass optimization (links first, then text redaction)
- Atomic file replacement with temporary files
- Support for malformed PDFs with error suppression
