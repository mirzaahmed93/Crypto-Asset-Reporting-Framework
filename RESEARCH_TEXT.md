# Research Text & Citations for CARF Audit Notebook

Below are markdown text blocks you can copy into your Jupyter notebook as **Markdown cells**. Each section is clearly labelled.

---

## SECTION 0: Summary / Overview Cell

> Copy this as a markdown cell **immediately after** the title/introduction cell, or integrate it into the introduction.

---

## Summary

This notebook presents a functional prototype for automated CARF compliance analysis applied to real Ethereum blockchain transactions. The system fetches live transaction data from the Ethereum mainnet via the Etherscan API, applies a weighted risk scoring model aligned with HMRC reporting thresholds, and generates both visual analytics and AI-powered audit narratives.

### Notebook Structure

The prototype is organised into the following analytical stages:

| Section | Title | Purpose |
|---|---|---|
| 1 | **Environment Setup** | Installs and imports all required Python packages (`pandas`, `matplotlib`, `seaborn`, `plotly`, `ipywidgets`, `requests`, `python-dotenv`) and configures the analysis environment. |
| 2 | **Fetch Realistic Transaction Data** | Queries the Etherscan V2 API to retrieve 50 real Ethereum transactions from known exchange hot wallets (Binance, etc.). Each transaction includes verified hashes, sender/recipient addresses, block numbers, timestamps, and ETH values. All transaction hashes are independently verifiable on Etherscan.io. |
| 3 | **CARF Risk Scoring** | Applies the `CARFScorer` class to evaluate each transaction against three CARF-aligned risk factors: threshold breach (≥£10,000), stablecoin classification, and high-value transaction status (≥£50,000). Outputs a scored DataFrame with compliance flags and reporting status. |
| 4 | **Interactive Transaction Table** | Renders an interactive HTML table displaying scored transactions with direct clickable verification links to Etherscan.io, enabling independent audit of each transaction hash. |
| 5 | **AM/PM Transaction Analysis** | Produces four analytical visualisations using `matplotlib` and `seaborn`: (i) hourly transaction distribution, (ii) AM vs PM volume comparison, (iii) asset type distribution by time period, and (iv) average transaction value by time period. These charts support temporal pattern analysis relevant to CARF due diligence. |
| 5.5 | **Interactive Risk Heatmap** | Generates an interactive Plotly heatmap showing risk factors (threshold breach, stablecoin status, high value) for each transaction. Includes a dropdown selector for detailed individual transaction inspection with Etherscan verification links. |
| 6 | **AI Audit Report Generator** | An interactive AI-powered compliance report generator using the Groq API (Llama 3.1). Features customisable prompts, tone selection (Professional, Executive, Technical, Risk-Focused, Casual), and real-time generation. Falls back to a deterministic rule-based report if no API key is configured. |
| 7 | **Full Compliance Report** | Produces the final CARF compliance report, displaying the top risk-scored transactions with verification links, and exports the complete dataset to CSV for regulatory record-keeping. |

### Key Outputs

The prototype generates the following compliance artefacts:

1. **Scored Transaction DataFrame** — 50 real Ethereum transactions with 17 data fields including risk scores (0–20), compliance flags, and reporting status (🔴 REPORT / 🟢 OK).
2. **Interactive Risk Visualisations** — Temporal analysis charts and a risk factor heatmap for visual compliance assessment.
3. **AI-Generated Audit Narrative** — A natural language compliance report summarising risk levels, transaction patterns, and HMRC-specific recommendations.
4. **Exportable CSV Report** — A structured dataset (`carf_enhanced_report.csv`) suitable for regulatory submission and archival retention.

### Methodology

The analysis pipeline follows a five-stage workflow:

1. **Data Acquisition** → Real transactions fetched from Etherscan API (Ethereum Mainnet, Chain ID: 1)
2. **Data Transformation** → ETH values converted to GBP at a fixed exchange rate; stablecoin classification applied based on known contract addresses (USDC: `0xa0b86991...`, USDT: `0xdac17f95...`)
3. **Risk Scoring** → Weighted scoring model applied (see Section 3 for methodology details)
4. **Visual Analysis** → Multi-dimensional charting of temporal patterns, asset distributions, and risk factors
5. **Report Generation** → AI-augmented or deterministic compliance narrative with actionable HMRC recommendations

### Technologies Used

- **Data:** Etherscan V2 API (real Ethereum transactions)
- **Analysis:** Python 3, pandas, numpy
- **Visualisation:** matplotlib, seaborn (static charts), Plotly (interactive heatmap)
- **AI:** Groq API with Llama 3.1 8B Instant (free tier)
- **Interactivity:** ipywidgets (dropdowns, text areas, buttons)
- **Environment:** Jupyter Notebook (JupyterLab compatible)

---

## SECTION 1: Opening / Introduction Cell

> Copy this as the **first markdown cell** of the notebook (or replace the existing title cell).

---

# Addressing the UK Crypto-Asset Reporting Gap: A CARF Compliance Prototype

**Author:** Ahmed Mirza  
**Date:** February 2026

## 1. Introduction

The rapid proliferation of crypto-assets has created a significant regulatory blind spot for UK tax authorities. Despite Her Majesty's Revenue and Customs (HMRC) classifying crypto-assets as property subject to Capital Gains Tax and Income Tax (HMRC, 2024a), the infrastructure for systematic reporting has historically lagged behind the traditional financial sector. This notebook presents a working prototype for automated Crypto-Asset Reporting Framework (CARF) compliance analysis, demonstrating how blockchain data can be programmatically assessed against HMRC's emerging reporting thresholds.

The OECD introduced the Crypto-Asset Reporting Framework in 2022 as a global standard for the automatic exchange of tax-relevant information on crypto-asset transactions between jurisdictions (OECD, 2022). The UK confirmed its adoption of CARF in the Autumn Statement 2023, with the framework enacted through the **Finance Act 2024** and secondary legislation introduced on 25 June 2025 (HM Treasury, 2024; KPMG, 2025). Reporting obligations for Registered Crypto-Asset Service Providers (RCASPs) take effect from **1 January 2026**, with the first data submissions to HMRC due by **31 May 2027** (HMRC, 2025).

---

## SECTION 2: The Business Gap Cell

> Copy this as a markdown cell **before** the data fetching section.

---

## 2. The UK Crypto-Asset Reporting Gap

### 2.1 Scale of Non-Compliance

There is a substantial and well-documented gap between UK crypto-asset holdings and tax compliance. HMRC has estimated that non-compliance rates among crypto investors may range from **55% to 95%** (City AM, 2025). This figure is consistent with the decentralised and pseudonymous nature of blockchain transactions, which, unlike traditional bank transfers, do not generate automatic reports to tax authorities.

The scale of unreported revenue is considerable. HMRC projects that the new CARF reporting regime will generate at least **£315 million in additional tax revenue by April 2030** (DigWatch, 2025). In the 2024–25 tax year alone, HMRC issued approximately **65,000 warning letters** to individuals suspected of undeclared crypto gains — a **134% increase** from the 27,700 letters sent in the prior year (FinTax, 2025; The Block, 2025). In 2023, HMRC reported a **432% increase** in unpaid tax owed by wealthy individuals suspected of crypto-related tax evasion (Business West, 2024).

### 2.2 The Compliance Infrastructure Deficit

Despite these enforcement signals, the UK market currently lacks accessible, automated tools for crypto-asset compliance. The business gap can be characterised across three dimensions:

1. **Data Fragmentation:** Crypto transactions occur across multiple blockchains, exchanges, and wallet types. Unlike traditional banking where institutions file automatic reports, the burden of aggregating and reporting crypto data falls on taxpayers or, under CARF, the service providers themselves (OECD, 2022).

2. **Threshold Complexity:** CARF introduces specific thresholds and classification requirements that mirror, but do not replicate, existing Common Reporting Standard (CRS) obligations. Crypto-asset service providers must now perform due diligence procedures including self-certification collection for all users, with pre-existing users requiring certification by **31 March 2027** (IRD NZ, 2025; Transworld Compliance, 2025).

3. **Tooling Gap:** While established financial services firms benefit from mature RegTech solutions for CRS and FATCA compliance, the crypto sector — particularly smaller UK-based exchanges and fintech firms — lacks equivalent automated tooling for CARF. This notebook addresses this gap by demonstrating a prototype scoring and reporting system.

### 2.3 Regulatory Context

The UK's CARF implementation sits within a broader international effort. The EU enacted equivalent provisions through **DAC8** (Directive on Administrative Cooperation), with parallel reporting timelines (Deloitte, 2025). Over **55 jurisdictions** have committed to CARF adoption, enabling automatic cross-border exchange of crypto transaction data from 2027 onwards (OECD, 2024).

Penalties for non-compliance are material: UK RCASPs face fines of up to **£300 per customer** for inaccurate, incomplete, or unverified reports (KPMG, 2025; DigWatch, 2025). Furthermore, new corporate criminal liability provisions may expose crypto exchanges to prosecution for failing to prevent tax evasion by their users (Osborne Clarke, 2025).

---

## SECTION 3: CARF Scoring Methodology Cell

> Copy this as a markdown cell **before** the CARFScorer code cell.

---

## 3. CARF Risk Scoring Methodology

This prototype implements a weighted risk scoring model to classify Ethereum transactions against CARF compliance criteria. The scoring system assigns a numerical risk value (0–20) to each transaction based on three distinct risk factors derived from HMRC's reporting thresholds and OECD CARF guidelines.

### 3.1 Scoring Components

The `CARFScorer` class evaluates each transaction against the following criteria:

| Risk Factor | Condition | Points | CARF Basis |
|---|---|---|---|
| **CARF Threshold** | Transaction value ≥ £10,000 GBP | +10 | HMRC reporting threshold for qualifying transactions (HMRC, 2024b) |
| **Stablecoin Classification** | Asset identified as a qualifying stablecoin (USDC, USDT, DAI) | +5 | OECD CARF distinguishes between "Relevant Crypto-Assets" and stablecoins, with different reporting considerations (OECD, 2022, Section III) |
| **High-Value Transaction** | Transaction value ≥ £50,000 GBP | +5 | Enhanced Due Diligence (EDD) trigger for high-value transactions under HMRC AML guidance (HMRC, 2024c) |

### 3.2 Risk Classification

Transactions are classified into compliance tiers based on their aggregate score:

| Score Range | Classification | Action Required |
|---|---|---|
| 0 | 🟢 Low Risk | No CARF reporting obligation |
| 5–10 | 🟡 Medium Risk | Monitor; may require reporting depending on asset type |
| 15–20 | 🔴 High Risk | Mandatory CARF disclosure; flag for Enhanced Due Diligence |

### 3.3 Compliance Flags

Each transaction is also tagged with descriptive flags for audit trail purposes:

- `EXCEEDS_CARF_THRESHOLD` — Transaction meets the £10,000 GBP reporting minimum
- `QUALIFYING_STABLECOIN` — Asset is a recognised stablecoin under CARF definitions
- `UNBACKED_ASSET` — Asset is not a stablecoin (e.g., ETH, BTC)
- `HIGH_VALUE` — Transaction exceeds the £50,000 Enhanced Due Diligence threshold

### 3.4 Limitations

This scoring model is a simplified prototype. A production implementation would additionally consider:

- **Aggregation rules:** CARF requires aggregation of transactions per user per reporting period, not per-transaction analysis alone (OECD, 2022).
- **User identification:** Full due diligence requires self-certification and KYC data, which this prototype does not incorporate.
- **Cross-chain tracking:** This implementation analyses Ethereum mainnet only; a comprehensive system would integrate multi-chain data.
- **Exchange rate volatility:** The prototype uses a fixed ETH/GBP rate (£1,800); production systems would use real-time or daily closing rates.

---

## SECTION 4: References Cell

> Copy this as the **final markdown cell** of the notebook.

---

## References

Business West. (2024). *HMRC reports 432% increase in unpaid crypto tax from wealthy individuals.* Available at: https://www.businesswest.co.uk

City AM. (2025). *UK crypto tax non-compliance could be as high as 95%, HMRC estimates.* Available at: https://www.cityam.com

Deloitte. (2025). *DAC8: EU Directive on Administrative Cooperation and crypto-asset reporting.* Available at: https://www.deloitte.com

DigWatch. (2025). *UK adopts OECD Crypto-Asset Reporting Framework.* Available at: https://dig.watch

FinTax. (2025). *HMRC issues 65,000 crypto warning letters in 2024-25.* Available at: https://fintax.tech

HMRC. (2024a). *Cryptoassets Manual.* Available at: https://www.gov.uk/hmrc-internal-manuals/cryptoassets-manual

HMRC. (2024b). *Guidance on the Crypto-Asset Reporting Framework.* Available at: https://www.gov.uk/government/publications/crypto-asset-reporting-framework

HMRC. (2024c). *Anti-Money Laundering guidance for the supervised sector.* Available at: https://www.gov.uk/government/publications/anti-money-laundering-guidance

HMRC. (2025). *Crypto-Asset Reporting Framework: Information for reporting crypto-asset service providers.* Available at: https://www.gov.uk/government/publications/the-international-tax-compliance-crypto-asset-reporting-framework-regulations-2025

HM Treasury. (2024). *Autumn Statement 2023: CARF adoption confirmed.* Available at: https://www.gov.uk/government/topical-events/autumn-statement-2023

IRD New Zealand. (2025). *Crypto-Asset Reporting Framework: Due diligence procedures.* Available at: https://www.ird.govt.nz

KPMG. (2025). *UK CARF regulations: Key provisions and compliance timeline.* Available at: https://kpmg.com/uk

Menzies LLP. (2025). *CARF: What UK crypto businesses need to know.* Available at: https://menzies.co.uk

OECD. (2022). *Crypto-Asset Reporting Framework and Amendments to the Common Reporting Standard.* OECD Publishing, Paris. Available at: https://www.oecd.org/tax/exchange-of-tax-information/crypto-asset-reporting-framework-and-amendments-to-the-common-reporting-standard.htm

OECD. (2024). *International Standards for Automatic Exchange of Information in Tax Matters: Crypto-Asset Reporting Framework and 2023 update to the Common Reporting Standard.* OECD Publishing, Paris.

Osborne Clarke. (2025). *UK corporate criminal liability and crypto exchanges.* Available at: https://www.osborneclarke.com

RSM. (2025). *CARF due diligence: Alignment with CRS and AML obligations.* Available at: https://rsmus.com

The Block. (2025). *HMRC ramps up crypto enforcement with record warning letters.* Available at: https://www.theblock.co

Transworld Compliance. (2025). *OECD CARF reporting rules and due diligence procedures.* Available at: https://transworldcompliance.com
