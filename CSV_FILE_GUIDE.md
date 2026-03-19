# CSV File Upload Guide

## Error: "Buffer overflow caught - possible malformed input file"

This error occurs when your CSV file has formatting issues that prevent pandas from parsing it correctly.

## ✅ Solution Applied

The system now has **multiple fallback strategies**:

1. **Try UTF-8 encoding** with bad line skipping
2. **Try Latin-1 encoding** with bad line skipping
3. **Try CP1252 encoding** with bad line skipping
4. **Try Python engine** (slower but more forgiving)
5. **Fallback to plain text** - reads file line by line

If all strategies fail, you'll get a helpful error message with instructions.

## 📝 How to Fix Your CSV File

### Option 1: Use Simple Format (Recommended)

Create a CSV with just one column named "text":

```csv
text
You are stupid and worthless
I hate you so much
This is a nice day
Everyone loves you
```

### Option 2: Fix Existing CSV

1. **Open in Excel or Google Sheets**
2. **Check for issues**:
   - All rows should have the same number of columns
   - Text with commas should be in quotes: `"Hello, world"`
   - No special characters that break formatting
3. **Save As**:
   - File → Save As
   - Choose "CSV UTF-8 (Comma delimited)"
   - Save

### Option 3: Use TXT File Instead

If CSV keeps failing, use a simple text file:

```
You are stupid and worthless
I hate you so much
This is a nice day
Everyone loves you
```

Save as `yourfile.txt` and upload that instead!

## 🔍 Common CSV Issues

### Issue 1: Inconsistent Columns
```csv
text,label
Hello world,0
This has,three,columns  ❌ WRONG - 3 columns instead of 2
```

**Fix**: Ensure all rows have the same number of columns

### Issue 2: Unquoted Commas
```csv
text
Hello, world  ❌ WRONG - comma breaks parsing
```

**Fix**: Quote text with commas
```csv
text
"Hello, world"  ✅ CORRECT
```

### Issue 3: Special Characters
```csv
text
Text with "quotes" inside  ❌ WRONG
```

**Fix**: Escape quotes
```csv
text
"Text with ""quotes"" inside"  ✅ CORRECT
```

### Issue 4: Mixed Line Endings
- Windows uses `\r\n`
- Unix/Mac uses `\n`
- Mixed line endings can cause issues

**Fix**: Save file with consistent line endings (UTF-8 encoding handles this)

## 🧪 Test Files Provided

I've created test files for you:

1. **test_upload.txt** - Simple text file (always works)
   ```
   You are stupid and worthless
   I hate you so much
   This is a nice day
   ```

2. **test_upload.csv** - Simple CSV file
   ```csv
   text
   You are stupid and worthless
   I hate you so much
   This is a nice day
   ```

Try uploading these first to verify the system works!

## 💡 Pro Tips

1. **Start Simple**: Use a text file first to test
2. **One Column**: CSV with just "text" column is easiest
3. **UTF-8 Encoding**: Always save as UTF-8
4. **Test Small**: Try with 5-10 rows first
5. **Check Format**: Open in Notepad to see raw format

## 🚀 What Happens Now

When you upload a CSV file, the system:

1. **Tries 6 different parsing strategies**
2. **Logs which strategy worked** (check server logs)
3. **Falls back to plain text** if CSV parsing fails
4. **Gives helpful error messages** if nothing works

## 📊 Supported Formats

### CSV Format
```csv
text
Your text here
Another text here
```

Or with multiple columns:
```csv
id,text,label
1,Your text here,0
2,Another text here,1
```

### TXT Format
```
Your text here
Another text here
More text here
```

One text per line, no headers needed!

## ❓ Still Having Issues?

If you're still getting errors:

1. **Check the browser console** (F12) for detailed error messages
2. **Check server logs** in `logs/api_enhanced_*.log`
3. **Try the test files** provided (`test_upload.txt` or `test_upload.csv`)
4. **Convert to TXT**: Save your data as a simple text file instead

## ✅ Success Indicators

You'll know it worked when you see:
- ✅ "Success: X texts processed" in server logs
- ✅ A table showing all analyzed texts
- ✅ Confidence scores for each text
- ✅ Labels (Hate Speech / Non-Hate)

---

**The system is now much more robust and should handle most CSV files!**

Try uploading your file again - it should work now with the improved error handling.
