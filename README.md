# Crypto Asset Reporting and Liquidity Pool Reconciliation Framework

A professional-grade suite of Jupyter notebooks for **CARF (Crypto-Asset Reporting Framework)** compliance, multi-chain portfolio reconciliation, and automated P&L auditing.

## Modules (notebooks)

### 1. CARF Compliance Audit (`CARF_Audit.ipynb`)
Focuses on individual transaction risk scoring and regulatory reporting (HMRC/OECD standards).
- **Compliance Scoring**: Automatic detection of £10,000+ reportable transactions.
- **Risk Heatmaps**: Interactive Plotly visualizations of transaction risk factors.
- **AI Audit Reports**: Automated executive summaries powered by Llama 3.1 (Groq).

### 2. LP Reconciliation & Multi-Chain P&L (`lp_reconciliation.ipynb`)
Focuses on "unbundling" complex DeFi positions and establishing a verifiable audit trail across Ethereum, Polygon, and Base.
- **LP Decomposition**: "Looks through" LP tokens (like UNI-V2) to report the underlying asset balances (e.g., ETH/USDC) for accurate tax disclosure.
- **Advanced Cost Basis**: Searches historical transaction data to find the "initial entry" block height.
- **Gas Fee Accounting**: Dynamically fetches and converts historical gas fees into USD to provide a true **ROI (Return on Investment)**.
- **Multi-Chain Governance**: Consolidated view of assets across different EVM-compatible ecosystems.

## Prerequisites

```bash
pip install requests pandas ipywidgets python-dotenv numpy
```

## API Keys

Create a `.env` file in the project root --> (https://github.com/ahmedmirza1/Crypto-Asset-Reporting-Framework/blob/main/.env.example):

```env
# CARF Audit Keys
ETHERSCAN_API_KEY=your_etherscan_key
GROQ_API_KEY=your_groq_key

# LP Reconciliation Keys (Required for Module 2)
ALCHEMY_API_KEY=your_alchemy_key
MORALIS_API_KEY=your_moralis_key
```

*   **Alchemy**: Multi-chain indexing and balance retrieval. [Get Key](https://dashboard.alchemy.com/)
*   **Moralis**: Historical block-specific pricing. [Get Key](https://admin.moralis.io/)
*   **Etherscan**: Ethereum transaction history. [Get Key](https://etherscan.io/)
*   **Groq**: AI Audit generation. [Get Key](https://console.groq.com/)

## Running the Tools

### Local Notebook
```bash
# To run the Compliance Audit:
jupyter notebook CARF_Audit.ipynb

# To run the LP Reconciliation & P&L tool:
jupyter notebook lp_reconciliation.ipynb
```

### Dashboard Mode (Voilà)
To run the P&L tool as a clean, code-free web dashboard (best for non-technical stakeholders):
```bash
pip install voila
voila lp_reconciliation.ipynb --theme=dark
```
This will open a local web app where users can interact with the GUI without seeing any Python code.

## Web Deployment (Zero Install)
You can deploy this dashboard to the web for free so stakeholders don't need to install anything:
1. Create an account on [HuggingFace Spaces](https://huggingface.co/spaces) or [Render](https://render.com/)
2. Connect this GitHub repository
3. Set the build command to `pip install -r requirements.txt`
4. Set the run command to `voila lp_reconciliation.ipynb --no-browser --port=$PORT`
5. Add your `ALCHEMY_API_KEY` and `MORALIS_API_KEY` as Environment Secrets in the deployment settings.

## Bibliography & Research
This project is built upon established regulatory and academic frameworks, including:
*  **BIS (2023)**: Ecosystem Risks and Options for Regulation.
*  **Chainalysis (2023)**: Patterns of cross-border DeFi flow.
*  **HMRC (2024)**: Cryptoassets Manual for DeFi and Staking.
*  **OECD (2022)**: Crypto-Asset Reporting Framework (CARF).

## Security & Privacy
- API keys are stored in a local `.env` file (never committed to git).
- All audit data is processed locally within the Jupyter environment.
- No sensitive wallet data is ever sent to external servers beyond public API requests.

## License
MIT License
