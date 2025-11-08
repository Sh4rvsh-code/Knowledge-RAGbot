# ⚠️ IMPORTANT: packages.txt Format

## The Issue

Streamlit Cloud's `packages.txt` file **CANNOT contain comments**!

### ❌ Wrong (will cause deployment failure):
```txt
# This is a comment
libmupdf-dev  # inline comment also fails
mupdf
```

### ✅ Correct:
```txt
libmupdf-dev
mupdf
libmagic1
build-essential
```

## Why This Happens

- `packages.txt` is passed directly to `apt-get install`
- apt-get treats `#` as a package name, not a comment
- This causes "Unable to locate package #" errors

## Current packages.txt Content

```txt
libmupdf-dev
mupdf
mupdf-tools
libmagic1
build-essential
```

## What These Packages Do

- **libmupdf-dev, mupdf, mupdf-tools**: Required for PyMuPDF (PDF processing)
- **libmagic1**: Required for python-magic (file type detection)
- **build-essential**: Compilers and build tools for better performance

## If You Need to Add Packages

Just add package names, one per line:

```txt
libmupdf-dev
mupdf
mupdf-tools
libmagic1
build-essential
your-new-package
```

**No comments, no blank lines at the start!**

## Fixed!

The error has been fixed and pushed to GitHub. Streamlit Cloud will automatically redeploy.

Wait 2-3 minutes and check your app again!
