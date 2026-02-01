# Contributing to OceanofPDFs Tag Remover & Renamer

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

1. **Clear Title**: Briefly describe the problem
2. **Environment Details**:
   - Python version (`python --version`)
   - Operating system and version
   - PyMuPDF version (`pip show pymupdf`)
3. **Steps to Reproduce**: Exact commands and inputs that trigger the bug
4. **Expected Behavior**: What should happen
5. **Actual Behavior**: What actually happens
6. **Error Messages**: Complete error output if applicable
7. **Sample Files**: If possible, provide a minimal example PDF (ensure no copyrighted content)

### Suggesting Features

Feature requests are welcome! Please create an issue with:

1. **Use Case**: Describe the problem you're trying to solve
2. **Proposed Solution**: How you envision the feature working
3. **Alternatives Considered**: Other approaches you've thought about
4. **Impact**: Who would benefit from this feature

### Pull Requests

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/oceanofpdfs-remover.git
   cd oceanofpdfs-remover
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
   or
   ```bash
   git checkout -b bugfix/issue-number-description
   ```

3. **Make Your Changes**
   - Follow the coding style (see below)
   - Add comments for complex logic
   - Update documentation if needed

4. **Test Your Changes**
   ```bash
   # Run dry-run tests
   python oceanofpdfs_remover_+_renamer.py "test_pdfs/" --dry-run
   
   # Test all modes
   python oceanofpdfs_remover_+_renamer.py "test_pdfs/" --links-only --dry-run
   python oceanofpdfs_remover_+_renamer.py "test_pdfs/" --no-rename --dry-run
   python oceanofpdfs_remover_+_renamer.py "test_pdfs/" --no-progress --dry-run
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```
   
   Commit message format:
   - `feat: Add new feature`
   - `fix: Fix bug in timestamp preservation`
   - `docs: Update README with new examples`
   - `refactor: Improve error handling logic`
   - `test: Add tests for cloud file detection`

6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Provide a clear description of changes
   - Reference any related issues

## 📝 Coding Style

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these specifics:

- **Indentation**: 4 spaces (no tabs)
- **Line Length**: Maximum 100 characters (120 for comments)
- **Naming Conventions**:
  - Functions/variables: `snake_case`
  - Constants: `UPPER_CASE`
  - Classes: `PascalCase`
- **Docstrings**: Use triple quotes for all functions
  ```python
  def process_pdf(pdf_path: Path, links_only=False, dry_run=False):
      """Handles the core cleaning logic and returns results.
      
      Args:
          pdf_path: Path to the PDF file to process
          links_only: If True, only remove hyperlinks
          dry_run: If True, simulate changes without modifying files
          
      Returns:
          Tuple of (changed, text_hits, link_hits, error_str)
      """
  ```

### Code Organization

- **Imports**: Group in order:
  1. Standard library
  2. Third-party packages
  3. Local modules
  
- **Constants**: Define at module level after imports

- **Functions**: Organize logically:
  1. Utility functions
  2. Core processing functions
  3. Main entry point

### Comments

- **Inline Comments**: Explain *why*, not *what*
  ```python
  # Good
  # Retry for cloud-synced files which may timeout
  for attempt in range(retries):
  
  # Bad
  # Loop 3 times
  for attempt in range(retries):
  ```

- **Complex Logic**: Add block comments before complex sections
  ```python
  # Two-pass optimization: remove links first (fast), then redact text
  # only on pages where watermarks are detected (slower but thorough)
  ```

## 🧪 Testing Guidelines

### Manual Testing Checklist

Before submitting a PR, verify:

- [ ] Script runs without errors on sample PDFs
- [ ] `--dry-run` mode shows accurate preview
- [ ] `--links-only` mode completes faster
- [ ] `--no-rename` prevents filename changes
- [ ] `--no-progress` provides streaming output
- [ ] Timestamps are preserved (check with file properties)
- [ ] Cloud files are handled gracefully
- [ ] Error messages are clear and helpful
- [ ] Works on Windows (if available)
- [ ] Works on macOS/Linux (if available)

### Test Cases to Consider

1. **Empty directory**: Should complete without errors
2. **Single PDF**: Should process and report correctly
3. **Mixed files**: PDFs and non-PDFs in same directory
4. **Nested directories**: Deep folder structures
5. **Filename collisions**: Files with same target name
6. **Special characters**: Filenames with unicode, spaces, etc.
7. **Malformed PDFs**: Corrupted or incomplete files
8. **Large files**: PDFs over 100MB
9. **Cloud-synced folders**: OneDrive, Dropbox, etc.
10. **Read-only files**: Files with restricted permissions

## 🐛 Debugging Tips

### Enable Verbose Output

For debugging, you can temporarily enable MuPDF warnings:
```python
# In the script, comment out these lines:
# fitz.TOOLS.mupdf_display_errors(False)
# fitz.TOOLS.mupdf_display_warnings(False)
```

### Add Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Then use throughout code:
logger.debug(f"Processing: {pdf_path}")
```

## 📚 Resources

- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [Python Path Library](https://docs.python.org/3/library/pathlib.html)
- [ANSI Color Codes](https://en.wikipedia.org/wiki/ANSI_escape_code#Colors)
- [Regex Pattern Testing](https://regex101.com/)

## 🎯 Priority Areas for Contribution

Current priorities (check issues for details):

1. **Cross-platform Testing**: Verify behavior on different OS versions
2. **Performance Optimization**: Speed improvements for large libraries
3. **Error Recovery**: Better handling of edge cases
4. **Documentation**: Examples, tutorials, troubleshooting guides
5. **Unit Tests**: Automated testing framework

## 📧 Questions?

If you have questions about contributing:

1. Check existing [Issues](https://github.com/yourusername/oceanofpdfs-remover/issues)
2. Create a new issue with the "question" label
3. Be specific and include context

## ⚖️ Code of Conduct

- Be respectful and constructive
- Focus on the code, not the person
- Accept feedback gracefully
- Help others learn and grow

Thank you for making this project better! 🙏
