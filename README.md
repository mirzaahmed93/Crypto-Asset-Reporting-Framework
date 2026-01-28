# Blockchain CARF Framework - Research Notebook

**AI-Driven Analysis for HMRC's Crypto-Asset Reporting Framework (CARF)**

A streamlined Jupyter notebook demonstrating automated CARF compliance scoring for real Ethereum transactions with AI-powered querying capabilities.

> ## 🆕 NEW: Enhanced Version Available!
> **`CARF_Research_Report_Enhanced.ipynb`** now includes:
> - 🔗 **Clickable blockchain.com verification links** 
> - 🤖 **AI-powered audit report generation**
> - 📊 **Enhanced interactive HTML tables**
> 
> See [NOTEBOOKS_COMPARISON.md](NOTEBOOKS_COMPARISON.md) for details.

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
cd /Users/ahmedmirza/.gemini/antigravity/scratch/blockchain-carf-framework
./run-notebook.sh
```

Opens at **`http://localhost:8888`**

### Option 2: Local Installation

```bash
pip install jupyter pandas matplotlib seaborn requests transformers torch
jupyter notebook CARF_Research_Report.ipynb
```

---

## 📊 Features

### ✅ Real Blockchain Data
- Fetches transactions using actual Ethereum addresses
- Binance exchange wallets, USDC/USDT contracts, major DeFi protocols
- Full 66-character transaction hashes for blockchain.com verification

### ✅ CARF Compliance Scoring
- Automated £10,000 threshold detection
- Qualifying stablecoin classification (USDT, USDC, DAI)
- Risk score calculation (0-20 scale)

### ✅ Time-Based Analysis
- AM/PM transaction popularity visualization
- UTC hourly activity charts
- Asset type distribution by time period

### ✅ AI Query Engine
- Natural language queries about transaction data
- Powered by HuggingFace Transformers
- Example: "How many transactions exceed £10,000?"

### ✅ HMRC-Ready Reports
- Tabular data with full transaction details
- CSV export functionality
- Compliance status indicators

---

## 📂 Repository Structure

```
blockchain-carf-framework/
├── CARF_Research_Report.ipynb           # Original research notebook
├── CARF_Research_Report_Enhanced.ipynb  # ⭐ Enhanced with AI & links
├── NOTEBOOKS_COMPARISON.md              # Feature comparison guide
├── Dockerfile.jupyter                   # Docker configuration
├── run-notebook.sh                      # One-command launcher
├── QUICKSTART.md                        # Setup instructions
├── ENHANCED_README.md                   # Enhanced features guide
├── README.md                            # This file
└── data/                                # Output directory
```

---

## 🤖 AI Query Interface

The notebook includes an AI-powered query engine that lets you ask natural language questions:

```python
# Example queries:
"How many transactions exceed the CARF threshold?"
"What's the total value of stablecoin transactions?"
"Show me the highest risk transactions"
```

The AI analyzes the transaction dataset and provides insights based on your questions.

---

## 📋 What's in the Notebook

1. **Data Fetching** - Real Ethereum addresses and transactions
2. **CARF Scoring** - Automated compliance risk assessment  
3. **Time Analysis** - AM/PM popularity with 4 visualization charts
4. **AI Queries** - Natural language interface for data exploration
5. **Reporting** - HMRC-ready tables with CSV export

---

## 🔗 Transaction Verification

All transaction hashes are in full 66-character format and can be verified at:

**https://www.blockchain.com/explorer/search**

---

## 🐳 Docker Benefits

- **Zero local dependencies** - Everything in container
- **Consistent environment** - Works everywhere
- **Easy cleanup** - Just stop the container
- **Portable** - Share exact setup

---

## 📖 Usage

1. Launch notebook (Docker or local)
2. Open `CARF_Research_Report.ipynb`
3. Run all cells: `Cell > Run All`
4. View visualizations and results
5. Use AI query interface for custom analysis
6. Export reports to CSV

---

## 🛑 Stopping Docker

Press `Ctrl+C` or:

```bash
docker stop carf-notebook
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🆘 Support

- **Technical Issues**: Review notebook comments and markdown cells
- **HMRC CARF**: [GOV.UK Guidelines](https://www.gov.uk/)
- **Blockchain Verification**: [Blockchain.com Explorer](https://www.blockchain.com/explorer)

---

**Built for HMRC CARF Compliance Research - 2026**
