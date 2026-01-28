# CARF Framework - Quick Start Guide

## 🚀 Running the Jupyter Notebook with Docker

### Option 1: One-Command Launch (Easiest!)

```bash
./run-notebook.sh
```

This will:
1. Build the Docker image
2. Start Jupyter notebook server
3. Open at `http://localhost:8888`

### Option 2: Manual Docker Commands

```bash
# Build the image
docker build -f Dockerfile.jupyter -t carf-jupyter .

# Run the container
docker run -it --rm -p 8888:8888 -v $(pwd):/workspace carf-jupyter
```

### Option 3: Without Docker (Local)

```bash
pip install jupyter pandas matplotlib seaborn requests
jupyter notebook CARF_Research_Report.ipynb
```

---

## 📓 What's in the Notebook

The `CARF_Research_Report.ipynb` demonstrates:

1. ✅ Fetching 100 real ETH transactions
2. ✅ CARF risk scoring (£10,000 threshold)
3. ✅ Visualization with 6 charts
4. ✅ Tabular HMRC-ready reports
5. ✅ CSV export functionality

---

## 🐳 Docker Benefits

- **No local dependencies** - Everything runs in container
- **Consistent environment** - Same setup everywhere
- **Easy cleanup** - Just stop the container
- **Portable** - Works on any machine with Docker

---

## 📊 After Starting

1. Open browser to `http://localhost:8888`
2. Click on `CARF_Research_Report.ipynb`
3. Run all cells: `Cell > Run All`
4. View results and visualizations

---

## 🛑 Stopping

Press `Ctrl+C` in the terminal or:

```bash
docker stop carf-notebook
```
