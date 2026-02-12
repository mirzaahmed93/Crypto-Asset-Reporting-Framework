# Crypto Asset Reporting Framework (CARF)

A comprehensive Jupyter notebook implementation for HMRC's Crypto-Asset Reporting Framework compliance analysis.

## Features

### 1. Real Ethereum Transaction Data
- Fetches **real and verifiable** Ethereum transactions from Etherscan API
- Uses embedded verified transaction hashes as backup
- All transactions verifiable on Etherscan.io to ensure API calls are real

### 2. CARF Compliance Scoring
- Automatic detection of £10,000+ reportable transactions (as per the cash rule)
- Risk scoring algorithm (0-25 points)
- Stablecoin classification (USDC, USDT, DAI)
- AM/PM transaction pattern analysis

### 3. Interactive Risk Heatmap
- **Plotly heatmap** showing transaction risk factors
- Hover for quick transaction details
- Dropdown selector for full transaction information
- Direct Etherscan verification links

### 4. AI-Powered Audit Reports
- **Customizable prompts** - Ask specific compliance questions
- **Tone selection** - Professional, Executive, Technical, Risk-Focused, or Casual
- Powered by **Groq API** (Llama 3.1) - Free tier available
- Deterministic fallback when no API key

## 📋 Prerequisites

```bash
pip install requests pandas matplotlib seaborn plotly ipywidgets python-dotenv
```

## API Keys

Create a `.env` file in the project root:

```
ETHERSCAN_API_KEY=your_etherscan_key
GROQ_API_KEY=your_groq_key
```

- **Etherscan API**: Free at [etherscan.io/apis](https://etherscan.io/apis)
- **Groq API**: Free at [console.groq.com/keys](https://console.groq.com/keys)

## Running the Notebook

```bash
jupyter notebook CARF_Audit_Final_v4.ipynb
```

Then run all cells (Kernel → Restart & Run All) on Jupyter itself.

## Sections of report

| Section | Description |
|---------|-------------|
| 1 | Environment Setup |
| 2 | Fetch Real Transaction Data |
| 3 | CARF Risk Scoring |
| 4 | Interactive Transaction Table |
| 5 | AM/PM Analysis Charts |
| 5.5 | Interactive Risk Heatmap |
| 6 | AI Audit Report Generator |
| 7 | Full Compliance Report |

## Security

- API keys stored in `.env` file (not committed to git)
- All transaction verification links point to Etherscan.io
- No sensitive data stored in the notebook

## License

MIT License
