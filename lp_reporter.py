import os
import requests
import time
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Determine script directory for absolute paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(SCRIPT_DIR, ".env")
load_dotenv(DOTENV_PATH)

MORALIS_API_KEY = os.getenv("MORALIS_API_KEY")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "0x71C7656EC7ab88b098defB751B7401B5f6d8976F")

# Chain Config
CHAINS = {"eth": "ethereum", "bsc": "bsc", "polygon": "polygon", "arbitrum": "arbitrum", "base": "base", "optimism": "optimism"}
EXPLORERS = {
    "ETH": "https://etherscan.io",
    "BSC": "https://bscscan.com",
    "POLYGON": "https://polygonscan.com",
    "ARBITRUM": "https://arbiscan.io",
    "BASE": "https://basescan.org",
    "OPTIMISM": "https://optimistic.etherscan.io"
}

MORALIS_BASE_URL = "https://deep-index.moralis.io/api/v2.2"
DEXSCREENER_BASE_URL = "https://api.dexscreener.com/latest/dex/pairs"

def get_lp_tokens(wallet_address, chain):
    url = f"{MORALIS_BASE_URL}/{wallet_address}/erc20?chain={chain}"
    headers = {"accept": "application/json", "X-API-Key": MORALIS_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200: return []
        tokens = response.json()
    except Exception: return []
    
    lp_indicators = ["LP", "UNI-V2", "SLP", "V0", "CURVE", "CRV", "CVX", "AAVE", "AMUSDC"]
    lp_tokens = []
    for token in tokens:
        symbol = str(token.get("symbol", "")).upper()
        if any(keyword in symbol for keyword in ["VISIT", "CLAIM"]): continue
        if any(indicator in symbol for indicator in lp_indicators):
            lp_tokens.append({
                "address": token["token_address"].lower(),
                "symbol": token["symbol"],
                "decimals": int(token["decimals"]),
                "balance": float(token["balance"]) / (10 ** int(token["decimals"])),
                "chain": chain
            })
    return lp_tokens

def get_historical_price(token_address, chain, block_number):
    url = f"{MORALIS_BASE_URL}/erc20/{token_address}/price?chain={chain}&to_block={block_number}"
    headers = {"accept": "application/json", "X-API-Key": MORALIS_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200: return response.json().get("usdPrice", 0)
    except: pass
    return 0

def get_token_transfers(wallet_address, token_address, chain):
    url = f"{MORALIS_BASE_URL}/{wallet_address}/erc20/transfers?chain={chain}&token_addresses={token_address}"
    headers = {"accept": "application/json", "X-API-Key": MORALIS_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200: return response.json().get("result", [])
    except: pass
    return []

def get_current_price(token_address, chain_m):
    url = f"{DEXSCREENER_BASE_URL}/{CHAINS[chain_m.lower()]}/{token_address}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("pairs"): return float(data["pairs"][0].get("priceUsd", 0))
    except: pass
    return 0

def run_reconciliation():
    print(f"🚀 Whale Audit (0x71C...) Starting Reconciliation...")
    all_lp_positions = []
    for m_chain in CHAINS.keys():
        print(f"Scanning {m_chain.upper()}...")
        lps = get_lp_tokens(WALLET_ADDRESS, m_chain)
        all_lp_positions.extend(lps)
        time.sleep(0.1)

    report_rows = []
    for lp in all_lp_positions[:10]: # Demo cap
        transfers = get_token_transfers(WALLET_ADDRESS, lp["address"], lp["chain"])
        cost_basis_usd = 0; rewards_qty = 0
        for tx in transfers:
            qty = float(tx["value"]) / (10**int(tx["token_decimals"]))
            if tx["to_address"].lower() == WALLET_ADDRESS.lower():
                p = get_historical_price(lp["address"], lp["chain"], tx["block_number"])
                cost_basis_usd += (qty * p)
                if tx["from_address"].startswith("0x000"): rewards_qty += qty
                time.sleep(0.1)
        val = lp["balance"] * get_current_price(lp["address"], lp["chain"])
        pnl = val - cost_basis_usd
        
        base_exp = EXPLORERS.get(lp["chain"].upper(), "https://etherscan.io")
        verify_link = f'<a href="{base_exp}/token/{lp["address"]}?a={WALLET_ADDRESS}">🔍 Verify</a>'
        
        report_rows.append({
            "Verification": verify_link,
            "Chain": lp["chain"].upper(),
            "Token": lp["symbol"],
            "Balance": f"{lp['balance']:.4f}",
            "Cost Basis (USD)": f"${cost_basis_usd:,.2f}",
            "Current Value (USD)": f"${val:,.2f}",
            "PnL (USD)": f"${pnl:+,.2f}",
            "Rewards": f"{rewards_qty:.4f}"
        })

    df = pd.DataFrame(report_rows)
    html_table = df.to_html(index=False, escape=False, classes='reconciliation-table')
    
    html_content = f"<html><body><div class='container'><h2>Whale Audit Reconcilitation (Multi-chain)</h2>{html_table}</div></body></html>"
    
    # Save local report
    reports_dir = os.path.join(SCRIPT_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    filename = os.path.join(reports_dir, f"whale_audit_{datetime.now().strftime('%Y%m%d')}.html")
    with open(filename, "w") as f: f.write(html_content)
    print(f"✅ Whale Audit Complete. Report saved to {filename}")

if __name__ == "__main__":
    if not MORALIS_API_KEY: print("Missing MORALIS_API_KEY in .env.")
    else: run_reconciliation()
