# Tesseract OCR Installation Guide

## What is Tesseract?

Tesseract is an OCR (Optical Character Recognition) engine that extracts text from images. It's required for the Image Upload feature.

## 🪟 Windows Installation (Recommended)

### Step 1: Download Tesseract

1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest installer: `tesseract-ocr-w64-setup-5.3.3.20231005.exe` (or latest version)
3. Or direct link: https://digi.bib.uni-mannheim.de/tesseract/

### Step 2: Install Tesseract

1. **Run the installer** (tesseract-ocr-w64-setup-*.exe)
2. **Important**: During installation, note the installation path
   - Default: `C:\Program Files\Tesseract-OCR`
3. **Check "Add to PATH"** option if available
4. Complete the installation

### Step 3: Add to PATH (if not done automatically)

1. **Open System Environment Variables**:
   - Press `Win + R`
   - Type: `sysdm.cpl`
   - Press Enter

2. **Edit PATH**:
   - Click "Environment Variables"
   - Under "System variables", find "Path"
   - Click "Edit"
   - Click "New"
   - Add: `C:\Program Files\Tesseract-OCR`
   - Click "OK" on all windows

3. **Verify Installation**:
   - Open a NEW Command Prompt (important!)
   - Type: `tesseract --version`
   - You should see version information

### Step 4: Install Python Package

```bash
pip install pytesseract
```

### Step 5: Configure Python (if needed)

If Python can't find Tesseract, add this to your code:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## 🐧 Linux Installation

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
pip install pytesseract
```

### Fedora/RHEL:
```bash
sudo dnf install tesseract
pip install pytesseract
```

## 🍎 macOS Installation

### Using Homebrew:
```bash
brew install tesseract
pip install pytesseract
```

## ✅ Verify Installation

### Test in Command Prompt/Terminal:
```bash
tesseract --version
```

Expected output:
```
tesseract 5.3.3
 leptonica-1.83.1
  libgif 5.2.1 : libjpeg 8d (libjpeg-turbo 2.1.5.1) : libpng 1.6.40 : libtiff 4.5.1 : zlib 1.2.13 : libwebp 1.3.2 : libopenjp2 2.5.0
```

### Test in Python:
```python
import pytesseract
from PIL import Image

# Test if tesseract is accessible
print(pytesseract.get_tesseract_version())

# Test OCR on an image
img = Image.open('test_image.png')
text = pytesseract.image_to_string(img)
print(text)
```

## 🔧 Troubleshooting

### Issue 1: "tesseract is not installed or it's not in your PATH"

**Solution**:
1. Verify Tesseract is installed: `tesseract --version`
2. If not found, add to PATH (see Step 3 above)
3. **Restart your terminal/IDE** after adding to PATH
4. **Restart the Flask server**

### Issue 2: Python can't find Tesseract

**Solution**: Set the path explicitly in your code:

```python
import pytesseract

# Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Linux/Mac
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
```

### Issue 3: "Failed to load library"

**Solution**: Install Visual C++ Redistributable:
- Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Install and restart

### Issue 4: Poor OCR quality

**Solutions**:
1. Use higher resolution images
2. Ensure good contrast (black text on white background)
3. Use clear, readable fonts
4. Preprocess images (convert to grayscale, increase contrast)

## 📦 Alternative: Use Without Tesseract

If you don't want to install Tesseract, the system will still work for:
- ✅ Text Analysis (direct text input)
- ✅ File Upload (CSV/TXT files)
- ❌ Image Upload (requires Tesseract)

The system will show a friendly error message if you try to upload images without Tesseract installed.

## 🚀 Quick Start After Installation

1. **Restart your terminal/command prompt**
2. **Restart the Flask server**:
   ```bash
   python src/api/app_enhanced.py
   ```
3. **Test image upload** at http://localhost:5000
4. **Upload a test image** with text

## 📝 Test Images

Create a simple test image:
1. Open Paint or any image editor
2. Write some text: "This is a test message"
3. Save as PNG or JPG
4. Upload to the system

## ✅ Success Indicators

You'll know it's working when:
- ✅ `tesseract --version` shows version info
- ✅ No error when uploading images
- ✅ Extracted text appears in results
- ✅ Server logs show "Image prediction successful"

## 📞 Still Having Issues?

1. **Check PATH**: `echo %PATH%` (Windows) or `echo $PATH` (Linux/Mac)
2. **Check installation**: `where tesseract` (Windows) or `which tesseract` (Linux/Mac)
3. **Restart everything**: Terminal, IDE, Flask server
4. **Try explicit path**: Set `tesseract_cmd` in Python code

---

**Installation time**: ~5 minutes
**Difficulty**: Easy
**Required**: Only for Image Upload feature

After installation, refresh your browser and try uploading an image with text!
