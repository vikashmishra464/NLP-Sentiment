# Dataset Setup Guide

## 📁 Where to Put the IMDB Dataset

The IMDB dataset should be placed in: **`NLP-Sentiment/data/aclImdb/`**

---

## 📥 Step-by-Step Instructions

### Option 1: Download Manually (Recommended for Windows)

1. **Download the dataset**:
   - Visit: https://ai.stanford.edu/~amaas/data/sentiment/
   - Download: `aclImdb_v1.tar.gz` (84 MB)

2. **Extract the archive**:
   - Extract `aclImdb_v1.tar.gz`
   - You'll get a folder named `aclImdb`

3. **Move to correct location**:
   - Move the `aclImdb` folder to: `NLP-Sentiment/data/`
   - Final path: `NLP-Sentiment/data/aclImdb/`

### Option 2: Command Line (Linux/Mac/Git Bash)

```bash
# Navigate to data directory
cd NLP-Sentiment/data

# Download dataset
wget https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz

# Extract
tar -xzf aclImdb_v1.tar.gz

# Clean up
rm aclImdb_v1.tar.gz

# Go back to project root
cd ../..
```

### Option 3: PowerShell (Windows)

```powershell
# Navigate to data directory
cd NLP-Sentiment\data

# Download dataset
Invoke-WebRequest -Uri "https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz" -OutFile "aclImdb_v1.tar.gz"

# Extract (requires 7-Zip or similar)
# You may need to extract manually using Windows Explorer or 7-Zip

# Go back to project root
cd ..\..
```

---

## ✅ Verify Correct Structure

After extraction, your directory structure should look like this:

```
NLP-Sentiment/
└── data/
    └── aclImdb/                    ← This folder should exist
        ├── train/                  ← Training data
        │   ├── pos/                ← 12,500 positive reviews
        │   │   ├── 0_9.txt
        │   │   ├── 1_7.txt
        │   │   └── ... (12,500 files)
        │   └── neg/                ← 12,500 negative reviews
        │       ├── 0_3.txt
        │       ├── 1_1.txt
        │       └── ... (12,500 files)
        ├── test/                   ← Test data
        │   ├── pos/                ← 12,500 positive reviews
        │   │   └── ... (12,500 files)
        │   └── neg/                ← 12,500 negative reviews
        │       └── ... (12,500 files)
        ├── imdb.vocab
        ├── imdbEr.txt
        └── README
```

---

## 🔍 Quick Verification Commands

### Check if dataset exists (PowerShell/CMD):
```powershell
# Check if main folder exists
Test-Path NLP-Sentiment\data\aclImdb

# Count files in train/pos (should be 12,500)
(Get-ChildItem NLP-Sentiment\data\aclImdb\train\pos).Count

# Count files in train/neg (should be 12,500)
(Get-ChildItem NLP-Sentiment\data\aclImdb\train\neg).Count
```

### Check if dataset exists (Linux/Mac/Git Bash):
```bash
# Check if main folder exists
ls -la NLP-Sentiment/data/aclImdb

# Count files in train/pos (should be 12,500)
ls NLP-Sentiment/data/aclImdb/train/pos | wc -l

# Count files in train/neg (should be 12,500)
ls NLP-Sentiment/data/aclImdb/train/neg | wc -l
```

---

## 📊 Dataset Information

| Property | Value |
|----------|-------|
| **Total Reviews** | 50,000 |
| **Training Set** | 25,000 (12,500 positive + 12,500 negative) |
| **Test Set** | 25,000 (12,500 positive + 12,500 negative) |
| **File Format** | Plain text (.txt) |
| **Size** | ~84 MB (compressed), ~300 MB (extracted) |
| **Source** | Stanford AI Lab |

---

## 🚀 After Dataset Setup

Once the dataset is in place, you can run:

```bash
# Train a model
python train.py --data-path NLP-Sentiment/data/aclImdb

# Or use default path (same as above)
python train.py
```

The code will automatically:
1. Find the dataset at `NLP-Sentiment/data/aclImdb/`
2. Load 25,000 training reviews
3. Load 25,000 test reviews
4. Start training

---

## ❌ Common Issues

### Issue 1: "Dataset not found" error

**Problem**: 
```
FileNotFoundError: [Errno 2] No such file or directory: 'NLP-Sentiment/data/aclImdb/train/pos'
```

**Solution**:
- Check the path is exactly: `NLP-Sentiment/data/aclImdb/`
- Make sure you extracted the archive
- Verify the folder structure matches the diagram above

### Issue 2: Wrong folder structure

**Problem**: You have `NLP-Sentiment/data/aclImdb_v1/aclImdb/`

**Solution**: 
- Move the inner `aclImdb` folder up one level
- Final path should be: `NLP-Sentiment/data/aclImdb/`

### Issue 3: Empty folders

**Problem**: Folders exist but no .txt files inside

**Solution**:
- Re-download the dataset
- Make sure extraction completed successfully
- Check you have ~50,000 .txt files total

---

## 🔧 Alternative: Use Custom Path

If you want to put the dataset somewhere else:

```bash
# Put dataset anywhere you want
python train.py --data-path /path/to/your/aclImdb

# Example: Desktop
python train.py --data-path C:\Users\YourName\Desktop\aclImdb

# Example: External drive
python train.py --data-path D:\datasets\aclImdb
```

---

## 📝 Quick Checklist

Before running training, verify:

- [ ] Downloaded `aclImdb_v1.tar.gz` from Stanford
- [ ] Extracted the archive
- [ ] Moved `aclImdb` folder to `NLP-Sentiment/data/`
- [ ] Path is: `NLP-Sentiment/data/aclImdb/`
- [ ] `train/pos/` has 12,500 .txt files
- [ ] `train/neg/` has 12,500 .txt files
- [ ] `test/pos/` has 12,500 .txt files
- [ ] `test/neg/` has 12,500 .txt files

---

## 💡 Pro Tips

1. **Don't modify the files**: Keep the original .txt files as-is
2. **Keep the structure**: Don't rename folders (pos, neg, train, test)
3. **Disk space**: Make sure you have at least 500 MB free
4. **Backup**: Keep the .tar.gz file in case you need to re-extract

---

## 🎯 Ready to Train?

Once the dataset is in place:

```bash
# Simple training
python train.py

# Training with deployment
python train.py --deploy

# Check if it's working
python train.py --data-path NLP-Sentiment/data/aclImdb
```

You should see:
```
Loading data from NLP-Sentiment/data/aclImdb
Loaded 25000 train and 25000 test samples
Tokenizing dataset...
Starting training...
```

---

## 📞 Need Help?

If you're still having issues:

1. Check the path exists:
   ```bash
   ls NLP-Sentiment/data/aclImdb/train/pos
   ```

2. Verify file count:
   ```bash
   find NLP-Sentiment/data/aclImdb -name "*.txt" | wc -l
   # Should output: 50000
   ```

3. Check the code is looking in the right place:
   - Open `train.py`
   - Line 21: `default="NLP-Sentiment/data/aclImdb"`

---

**Dataset URL**: https://ai.stanford.edu/~amaas/data/sentiment/
**Expected Path**: `NLP-Sentiment/data/aclImdb/`
**Total Files**: 50,000 .txt files
