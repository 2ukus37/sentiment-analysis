# Tesseract OCR Installation - Complete Guide

## 🎯 Quick Summary

**Issue**: "tesseract is not installed or it's not in your PATH"

**Solution**: Install Tesseract OCR to enable image text extraction

**Time Required**: ~5 minutes

**Difficulty**: Easy

## 🚀 Quick Install (Windows)

### Option 1: Use the Helper Script (Easiest)
```bash
install_tesseract.bat
```

This script will:
1. Check if Tesseract is installed
2. Open the download page
3. Install Python package
4. Verify installation

### Option 2: Manual Installation

1. **Download Tesseract**:
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download: `tesseract-ocr-w64-setup-5.3.3.20231005.exe`

2. **Install**:
   - Run the installer
   - Note the path: `C:\Program Files\Tesseract-OCR`
   - Check "Add to PATH" if available

3. **Add to PATH** (if not automatic):
   - Press `Win + R`
   - Type: `sysdm.cpl`
   - Environment Variables → Path → Edit → New
   - Add: `C:\Program Files\Tesseract-OCR`
   - Click OK

4. **Install Python Package**:
   ```bash
   pip install pytesseract
   ```

5. **Restart**:
   - Close and reopen Command Prompt
   - Restart Flask server

6. **Verify**:
   ```bash
   tesseract --version
   ```

## 🐧 Linux Installation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install tesseract-ocr
pip install pytesseract

# Fedora/RHEL
sudo dnf install tesseract
pip install pytesseract

# Verify
tesseract --version
```

## 🍎 macOS Installation

```bash
# Using Homebrew
brew install tesseract
pip install pytesseract

# Verify
tesseract --version
```

## ✅ Verification Steps

### 1. Check Tesseract Installation
```bash
tesseract --version
```

Expected output:
```
tesseract 5.3.3
 leptonica-1.83.1
  ...
```

### 2. Check Python Package
```bash
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

### 3. Test in Application
1. Start the server: `.\start_enhanced_api.bat`
2. Go to: http://localhost:5000
3. Click "Image OCR" tab
4. Upload an image with text
5. Should see extracted text!

## 🔧 Troubleshooting

### Issue 1: "tesseract is not in your PATH"

**Solution**:
1. Add Tesseract to PATH (see manual installation step 3)
2. **Important**: Open a NEW command prompt
3. Restart Flask server
4. Try again

### Issue 2: Python can't find Tesseract

The system now automatically tries these paths:
- `C:\Program Files\Tesseract-OCR\tesseract.exe` (Windows)
- `/usr/bin/tesseract` (Linux)
- `/usr/local/bin/tesseract` (Mac)

If still not working, check `src/services/image_service.py`

### Issue 3: "Failed to load library"

**Solution**: Install Visual C++ Redistributable
- Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Install and restart

## 📝 What Features Require Tesseract?

### ✅ Works WITHOUT Tesseract:
- Text Analysis (direct text input)
- File Upload (CSV/TXT files)
- Batch Processing
- All ML predictions

### ❌ Requires Tesseract:
- Image Upload with OCR
- Screenshot text extraction
- Meme text analysis

## 🎨 Improved Error Messages

The system now shows helpful error messages:

**Before Tesseract Installation**:
```
❌ OCR Feature Not Available

Tesseract OCR is not installed or not found in PATH.

To enable image text extraction:
1. Install Tesseract OCR:
   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   Linux: sudo apt install tesseract-ocr
   Mac: brew install tesseract

2. Install Python package: pip install pytesseract

3. Restart the server

See INSTALL_TESSERACT_GUIDE.md for detailed instructions.
```

**After Installation**:
```
✅ Image analyzed successfully!
Extracted text: "Your text here..."
Confidence: 95.2%
```

## 📚 Documentation Files

I've created these helpful files:

1. **INSTALL_TESSERACT_GUIDE.md** - Detailed installation guide
2. **install_tesseract.bat** - Windows installation helper script
3. **TESSERACT_INSTALLATION_SUMMARY.md** - This file

## 🧪 Test After Installation

### Create a Test Image:
1. Open Paint
2. Write: "This is a test message for OCR"
3. Save as `test_ocr.png`
4. Upload to the system

### Expected Result:
- ✅ Text extracted: "This is a test message for OCR"
- ✅ Prediction shown (Hate Speech / Non-Hate)
- ✅ Confidence score displayed

## 💡 Pro Tips

1. **High Quality Images**: Use clear, high-resolution images for best results
2. **Good Contrast**: Black text on white background works best
3. **Readable Fonts**: Avoid fancy/decorative fonts
4. **Straight Text**: Rotated or skewed text may not work well

## 🚀 After Installation

1. **Restart Command Prompt** (important!)
2. **Restart Flask Server**:
   ```bash
   # Stop server (Ctrl+C)
   # Start again
   .\start_enhanced_api.bat
   ```
3. **Refresh Browser** (Ctrl+F5)
4. **Test Image Upload**

## ✅ Success Checklist

- [ ] Tesseract installed
- [ ] Added to PATH
- [ ] Python package installed (`pip install pytesseract`)
- [ ] Command prompt restarted
- [ ] Flask server restarted
- [ ] `tesseract --version` works
- [ ] Image upload works in browser

## 📞 Still Having Issues?

1. **Check the logs**: `logs/api_enhanced_*.log`
2. **Check browser console**: F12 → Console tab
3. **Verify PATH**: `echo %PATH%` (should include Tesseract)
4. **Try explicit path**: Edit `src/services/image_service.py`

## 🎉 Benefits After Installation

- ✅ Extract text from screenshots
- ✅ Analyze memes and images
- ✅ Detect cyberbullying in visual content
- ✅ Complete feature set enabled

---

**Installation Status**: Follow the steps above to install Tesseract

**Estimated Time**: 5-10 minutes

**Next Step**: Run `install_tesseract.bat` or follow manual installation

After installation, you'll have full access to all features including image text extraction!
