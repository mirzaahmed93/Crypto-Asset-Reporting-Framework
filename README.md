# Blockchain CARF Framework

**AI-Driven ETL Pipeline for HMRC's Crypto-Asset Reporting Framework (CARF)**

A modular, Dockerized Python framework for blockchain data engineering with built-in UK Government compliance, GDPR-compliant privacy protection, and AI-powered query capabilities.

---

## 🚀 Features

### 🤖 **AI Orchestration with LangChain**
- Natural language query processing (e.g., *"Find all ETH transfers over £10k"*)
- Complete audit trail for regulatory oversight
- Explainable AI reasoning for transaction flagging

### 🔗 **Multi-Provider Blockchain Data**
- **Blockchain.com API**: Multi-chain support (BTC, ETH, SOL, ADA, DOGE, etc.)
- **Blockbook API**: Self-hostable, unified API across chains
- Automatic pagination and rate limiting
- Configurable failover between providers

### 🔐 **GDPR-Compliant Privacy Protection**
- **AES-256 Encryption**: Secure PII storage with Fernet
- **Salted SHA-256 Pseudonymization**: Internal analysis without exposing wallet addresses
- **Cryptographic Erasure**: "Right to be forgotten" compliance
- Separate vault storage for encryption keys

### 📊 **Advanced ETL Pipeline**
- Smart contract decoding (ERC-20 transfers, DeFi interactions)
- UK/London timezone normalization
- Automated CARF risk scoring (£10,000 threshold)
- Qualifying stablecoin classification

### 📑 **HMRC Reporting**
- Summary tables for qualifying vs. unbacked assets
- CSV and Excel export formats
- Tax year compliance (UK financial year: April 6 - April 5)
- Audit-ready documentation

### 🐳 **Production-Ready Docker Deployment**
- Multi-stage build for minimal image size
- Non-root user execution
- Secure volume mounts for `/data` and `/vault`
- GovCloud-compatible (Azure UK South, AWS eu-west-2)

---

## 📦 Installation

### Prerequisites
- **Python 3.11+**
- **Docker & Docker Compose** (for containerized deployment)
- **Git**

### Local Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd blockchain-carf-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Docker Installation

```bash
# Build the Docker image
docker build -t blockchain-carf .

# Run with docker-compose
docker-compose up -d
```

---

## 🔧 Configuration

Edit `.env` file with your settings:

```bash
# Blockchain Provider
BLOCKCHAIN_PROVIDER=blockchain.com
BLOCKCHAIN_COM_API_KEY=your_api_key_here

# Privacy & Encryption
ENCRYPTION_KEY_PATH=./vault/encryption_key.key
PSEUDONYMIZATION_SALT=generate_random_salt_here

# HMRC Settings
CARF_THRESHOLD_GBP=10000
REPORTING_ENTITY_NAME=Your Organization Ltd
TAX_YEAR=2025-2026

# Exchange Rates (use live API in production)
ETH_TO_GBP_RATE=1800.00
```

---

## 🎯 Usage

### Quick Start Example

```python
from src import (
    BlockchainClient,
    BlockchainProvider,
    PrivacyGuard,
    ETLPipeline,
    BlockchainQueryAgent,
    HMRCReporter
)

# Initialize components
client = BlockchainClient(provider=BlockchainProvider.BLOCKCHAIN_COM)
privacy_guard = PrivacyGuard()
etl = ETLPipeline(carf_threshold=10000)
ai_agent = BlockchainQueryAgent(client, etl)

# Process natural language query
result = ai_agent.query("Find all ETH transfers over £10,000")
print(result)

# Generate HMRC report
reporter = HMRCReporter(reporting_entity="Your Org Ltd")
reporter.export_to_excel(transactions_df, "./data/hmrc_report.xlsx")
```

### Run Example Script

```bash
python examples/usage_example.py
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Natural Language Query               │
│              "Find ETH transfers over £10k"             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │   AI Agent (LangChain)      │
         │   - Query interpretation    │
         │   - Audit trail logging     │
         └──────────┬──────────────────┘
                    │
                    ▼
         ┌─────────────────────────────┐
         │   Blockchain Client         │
         │   - Blockchain.com API      │
         │   - Blockbook API           │
         └──────────┬──────────────────┘
                    │
                    ▼
         ┌─────────────────────────────┐
         │   ETL Pipeline              │
         │   - Smart contract decode   │
         │   - CARF risk scoring       │
         │   - Timezone normalization  │
         └──────────┬──────────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
         ▼                     ▼
┌─────────────────┐   ┌──────────────────┐
│ Privacy Guard   │   │  HMRC Reporter   │
│ - Encrypt PII   │   │ - Summary tables │
│ - Pseudonymize  │   │ - Export CSV/XLS │
└─────────────────┘   └──────────────────┘
```

---

## 📂 Project Structure

```
blockchain-carf-framework/
├── src/
│   ├── blockchain_client.py   # Multi-provider API client
│   ├── privacy_guard.py        # AES-256 encryption & pseudonymization
│   ├── etl_pipeline.py         # Data transformation & CARF scoring
│   ├── ai_agent.py             # LangChain AI orchestration
│   └── hmrc_reporting.py       # Compliance reporting
├── examples/
│   └── usage_example.py        # Demonstration script
├── data/                       # Output reports (gitignored)
├── vault/                      # Encryption keys (gitignored)
├── tests/                      # Unit tests
├── Dockerfile                  # Multi-stage Docker build
├── docker-compose.yml          # Orchestration configuration
├── requirements.txt            # Python dependencies
├── .env.example                # Configuration template
└── README.md                   # This file
```

---

## 🔒 Security & Compliance

### GDPR Compliance
- **Pseudonymization**: Wallet addresses hashed with salted SHA-256
- **Encryption**: PII encrypted with AES-256 (Fernet)
- **Cryptographic Erasure**: Delete encryption keys to make data unrecoverable
- **Audit Trail**: Complete logging for "right to access" requests

### UK Data (Use and Access) Act 2026
- Encryption keys stored separately in `/vault` directory
- Read-only Docker volumes prevent unauthorized modification
- Non-root container execution

### CARF Compliance
- Automatic flagging of transactions ≥ £10,000
- Classification of qualifying stablecoins (USDT, USDC, DAI, BUSD, GBPT, EURS)
- Tax year alignment with UK financial calendar (April 6 - April 5)

---

## 🧪 Testing

```bash
# Run unit tests (when implemented)
pytest tests/

# Validate Docker build
docker build -t blockchain-carf . && echo "Build successful"

# Validate docker-compose configuration
docker-compose config
```

---

## 🚢 Deployment

### Local Development
```bash
python examples/usage_example.py
```

### Docker Production
```bash
docker-compose up -d
docker logs -f blockchain-carf-framework
```

### GovCloud Deployment (Azure UK South)
```bash
# Build and tag
docker build -t myregistry.azurecr.io/blockchain-carf:latest .

# Push to Azure Container Registry
az acr login --name myregistry
docker push myregistry.azurecr.io/blockchain-carf:latest

# Deploy to Azure Container Instances
az container create \
  --resource-group hmrc-compliance \
  --name carf-framework \
  --image myregistry.azurecr.io/blockchain-carf:latest \
  --location uksouth
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🆘 Support

For questions about:
- **HMRC Compliance**: Refer to [GOV.UK CARF Guidelines](https://www.gov.uk/)
- **Technical Issues**: Open a GitHub issue
- **Security Concerns**: Contact maintainers privately

---

## 🏆 Why This Framework?

### Audit Trail
Every AI decision is logged with timestamps and reasoning. When HMRC asks *"Why was transaction X flagged?"*, you have a complete audit trail.

### Future-Proof Cryptography
Uses AES-256 and Salted SHA-256, the 2026 gold standards for blockchain data under the UK's updated Data (Use and Access) Act.

### Infrastructure Portability
Docker configuration ensures your environment is identical from local development to GovCloud deployment (Azure UK South, AWS eu-west-2).

---

**Built for Senior Blockchain Data Engineers. Designed for UK Gov Compliance.**
