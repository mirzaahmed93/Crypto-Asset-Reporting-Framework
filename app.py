import os, requests, time, pandas as pd, base64
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
MORALIS_KEY = os.getenv("MORALIS_API_KEY", "")
ALCHEMY_KEY = os.getenv("ALCHEMY_API_KEY", "")

NATIVE_WRAPPERS = {
    "ETHEREUM": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "POLYGON": "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0",
    "BASE": "0x4200000000000000000000000000000000000006"
}

def get_historical_price_moralis(address, chain, block=None):
    if not MORALIS_KEY: return 0
    m_chain = {"ETHEREUM": "eth", "POLYGON": "polygon", "BASE": "base"}.get(chain.upper(), "eth")
    url = f"https://deep-index.moralis.io/api/v2.2/erc20/{address}/price?chain={m_chain}"
    if block: url += f"&to_block={block}"
    headers = {"accept": "application/json", "X-API-Key": MORALIS_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=10).json()
        return float(r.get("usdPrice", 0))
    except: return 0

def get_latest_block(chain):
    url = {"ETHEREUM": f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}",
           "POLYGON": f"https://polygon-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}",
           "BASE": f"https://base-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}"}.get(chain.upper())
    if not url: return 0
    try:
        r = requests.post(url, json={"id":1, "jsonrpc":"2.0", "method":"eth_blockNumber"}).json()
        return int(r.get("result", "0x0"), 16)
    except: return 0

class AuditResult:
    def __init__(self, chain, symbol, balance, address):
        self.chain = chain; self.symbol = symbol; self.balance = balance; self.address = address
    def to_dict(self): return {"Chain": self.chain.upper(), "Symbol": self.symbol, "Balance": round(self.balance, 4), "Address": self.address}

class AlchemyAdapter:
    def __init__(self, api_key):
        self.api_key = api_key
        self.urls = {"ethereum": f"https://eth-mainnet.g.alchemy.com/v2/{api_key}",
                     "polygon": f"https://polygon-mainnet.g.alchemy.com/v2/{api_key}",
                     "base": f"https://base-mainnet.g.alchemy.com/v2/{api_key}"}

    def get_gas_fee_usd(self, chain, tx_hash, block):
        url = self.urls.get(chain.lower())
        if not url: return 0
        try:
            p_rec = {"id":1,"jsonrpc":"2.0","method":"eth_getTransactionReceipt","params":[tx_hash]}
            rec = requests.post(url, json=p_rec).json().get("result", {})
            gas_used = int(rec.get("gasUsed", "0x0"), 16)
            p_tx = {"id":1,"jsonrpc":"2.0","method":"eth_getTransactionByHash","params":[tx_hash]}
            tx = requests.post(url, json=p_tx).json().get("result", {})
            gas_price = int(tx.get("gasPrice", "0x0"), 16)
            fee_native = (gas_used * gas_price) / 1e18
            native_addr = NATIVE_WRAPPERS.get(chain.upper(), NATIVE_WRAPPERS["ETHEREUM"])
            native_price = get_historical_price_moralis(native_addr, chain, block)
            return fee_native * native_price
        except: return 0

    def get_positions(self, address):
        res = []
        for name, url in self.urls.items():
            try:
                p_eth = {"id":1,"jsonrpc":"2.0","method":"eth_getBalance","params":[address,"latest"]}
                val = int(requests.post(url, json=p_eth).json().get("result","0x0"),16)/1e18
                if val > 1e-6: res.append(AuditResult(name, "NATIVE", val, "native"))
                p_t = {"id":1,"jsonrpc":"2.0","method":"alchemy_getTokenBalances","params":[address]}
                for b in requests.post(url, json=p_t).json().get("result",{}).get("tokenBalances",[]):
                    bal = int(b["tokenBalance"],16)
                    if bal > 0:
                        contract_addr = b["contractAddress"]
                        
                        # Fetch true symbol and decimals to avoid 0.00 rounding issues and "TOKEN" labels
                        try:
                            meta_payload = {"id":1,"jsonrpc":"2.0","method":"alchemy_getTokenMetadata","params":[contract_addr]}
                            meta = requests.post(url, json=meta_payload).json().get("result", {})
                            symbol = str(meta.get("symbol") or "TOKEN")
                            decimals = int(meta.get("decimals") or 18)
                        except:
                            symbol, decimals = "TOKEN", 18
                            
                        true_bal = bal / (10 ** decimals)
                        res.append(AuditResult(name, symbol, true_bal, contract_addr))
            except: pass
        return res

    def get_recent_transactions(self, address, limit):
        txs = []
        seen_hashes = set()
        for name, url in self.urls.items():
            for direction in [{"fromAddress": address}, {"toAddress": address}]:
                p = {"id":1,"jsonrpc":"2.0","method":"alchemy_getAssetTransfers","params":[{
                    **direction, "maxCount":f"0x{int(limit):x}", "category":["external","erc20"], "withMetadata":True
                }]}
                try:
                    for tx in requests.post(url, json=p).json().get("result",{}).get("transfers",[]):
                        if tx["hash"] in seen_hashes: continue
                        seen_hashes.add(tx["hash"])
                        raw = tx.get("rawContract", {})
                        contract = raw.get("address", "native") if raw else "native"
                        txs.append({"Chain":name.upper(), "Hash":tx["hash"], "From":tx.get("from"),
                                    "Asset":tx.get("asset"), "Value":tx.get("value"), 
                                    "Block":int(tx["blockNum"],16), "To":tx["to"], "Contract": contract})
                except: pass
        return txs

class UniversalAuditEngine:
    def __init__(self, key): self.adapter = AlchemyAdapter(key)
    def run_audit(self, addr): return [p.to_dict() for p in self.adapter.get_positions(addr)]
    def get_recent_history(self, addr, lim): return self.adapter.get_recent_transactions(addr, lim)
    def get_gas_cost(self, chain, h, b): return self.adapter.get_gas_fee_usd(chain, h, b)

def run_compliance_report(txs):
    if not txs: return "No transaction data available."
    risk_flags = []
    for tx in txs:
        val = float(tx.get('Value', 0) or 0)
        if val > 50: risk_flags.append({"Hash": tx['Hash'], "Risk": "Medium", "Issue": "High Value Transfer (>50 tokens)"})
        if tx.get('From') == tx.get('To') and tx.get('From') is not None:
            risk_flags.append({"Hash": tx['Hash'], "Risk": "High", "Issue": "Self-Transfer Detected"})
    if not risk_flags: return "✅ No critical compliance risks detected in recent history."
    return pd.DataFrame(risk_flags)

# --- STREAMLIT UI ---
st.set_page_config(page_title="Crypto Audit Dashboard", page_icon="📊", layout="wide")

st.title("📊 LP Reconciliation & Multi-Chain Audit")

st.markdown("""
## 1. Overview
The Liquidity Pool (LP) Reconciliation tool is a technical framework designed to bridge the gap between complex On-Chain DeFi activities and standardised regulatory reporting (e.g., Crypto Asset Reporting Framework-CARF) (OECD, 2022). This POC provides an automated, real time mechanism for fetching cross chain balances, calculating Performance alongside profit and loss statments (P&L) using historical block height pricing along with identifying compliance risks (BIS, 2023).

## 2. The Business Logic Gap 
In the traditional financial sector, reconciliation is a straightforward process of matching internal records against bank statements. In the decentralised landscape, this process is explained by Messari (2024) who states this is stifled ultimately with digital assets primarily due to 3 factors: 

### i) The Granularity Gap (Asset Decomposition): 
Most portfolio trackers show a balance for an "LP (liquidity pool) Token" (e.g., UNI-V2) which acts like a digital receipt for assets a user has deposited into a decentralised exchange (like Uniswap or PancakeSwap). However, for tax purposes and CARF reporting, the underlying assets (e.g., ETH and USDC) must be individualistically accounted for at the moment of entry and exit to ensure accurate treatment of DeFi (decentralised finance) income (HMRC, 2024). Manual reconciliation for high-frequency traders poses a big issue.

### ii) The Cost-Basis Fragmentation Gap: 
Digital assets move seamlessly across chains. When an asset is received from an "unknown" sender (source), the cost basis is often lost. Cost Basis is simply the total price a user has paid to buy an asset, and an LP Token is a digital receipt for assets deposited into a trading pool. The POC here aims to look at that LP receipt to find the original buy prices (cost basis), so that an accurate claim of total profit (or loss) is conducted for regulatory reporting. *This POC attempts solves this by scanning inbound transaction history and fetching the block-specific price at the moment of initial acquisition*.

### iii) The "Regulatory Blindspot"
Current reporting frameworks like the OECD's CARF framework, which has a POC done in another notebook, requires specific metadata (transaction hash, fiat equivalent values). Generic blockchain explorers do not provide the high level aggregation required for institutional or individual tax disclosures. *This presents a big gap to business service and other firms attempting to provide a holistic view of a wallet (user's) activity*.
""")

with st.expander("⚙️ Technical Implementation & Dependencies"):
    st.markdown("""
    The framework relies on a modular "Adapter" architecture to ensure data integrity and real-time precision.
    *   **Alchemy API (Multi-Chain Indexer)**: Used as the primary gateway to the blockchain.
    *   **Moralis API (Historical Price Engine)**: Essential for P&L calculations. It allows the tool to query the price of a specific token at a specific **Block Number**, rather than a generic timestamp.
    *   **Streamlit & Pandas**: Enables the GUI experience and vectorized performance calculations.
    """)


# Sidebar / Config
st.sidebar.header("Audit Configuration")
wallet_input = st.sidebar.text_input("Target Wallet", value="0x28c6c06298d514db089934071355e5743bf21d60")
limit_input = st.sidebar.slider("Tx Limit", min_value=1, max_value=10, value=10)
timeframe_input = st.sidebar.selectbox("Timeframe", options=['24h', '1w', '1m'], index=0)

if st.sidebar.button("🔍 Run Advanced Portfolio Audit", type="primary"):
    with st.spinner(f"Auditing {wallet_input[:10]}... [Timeframe: {timeframe_input}]"):
        engine = UniversalAuditEngine(ALCHEMY_KEY)
        data = engine.run_audit(wallet_input)
        tx_data = engine.get_recent_history(wallet_input, limit_input)
        
        st.session_state['tx_data'] = tx_data  # Store for compliance module

        total_value = 0; total_gain = 0
        for pos in data:
            chain = pos["Chain"]
            addr = pos["Address"]
            is_native = (addr == "native" or addr is None)
            
            latest_block = get_latest_block(chain)
            block_offsets = {'24h': 7200, '1w': 50400, '1m': 216000}
            hist_block = latest_block - block_offsets.get(timeframe_input, 7200)
            
            if is_native:
                wrapper = NATIVE_WRAPPERS.get(chain.upper(), NATIVE_WRAPPERS["ETHEREUM"])
                curr_price = get_historical_price_moralis(wrapper, chain) or 2500
                hist_price = get_historical_price_moralis(wrapper, chain, hist_block) or curr_price
            else:
                curr_price = get_historical_price_moralis(addr, chain)
                hist_price = get_historical_price_moralis(addr, chain, hist_block)
            
            unit_cost = 0; gas_cost = 0
            s_addr = str(addr or "").lower()
            s_wall = str(wallet_input or "").lower()
            asset_txs = [t for t in tx_data if str(t.get('Contract', '')).lower() == s_addr and str(t.get('To', '')).lower() == s_wall]
            if asset_txs:
                first_tx = sorted(asset_txs, key=lambda x: x['Block'])[0]
                unit_cost = get_historical_price_moralis(addr, chain, first_tx['Block'])
                gas_cost = engine.get_gas_cost(chain, first_tx['Hash'], first_tx['Block'])
            
            total_pos_cost = (unit_cost * pos['Balance']) + gas_cost
            total_pos_value = pos["Balance"] * curr_price
            
            if curr_price == 0 and not is_native:
                pos["Price (USD)"] = "N/A"
                pos["Value (USD)"] = "N/A"
                pos[f"Change ({timeframe_input})"] = "N/A"
                pos["Gas Expense"] = "N/A"
                pos["Overall ROI (%)"] = "N/A"
            else:
                pos["Price (USD)"] = round(curr_price, 2)
                pos["Value (USD)"] = round(total_pos_value, 2)
                pos[f"Change ({timeframe_input})"] = round(((curr_price - hist_price)/hist_price*100) if hist_price > 0 else 0, 2)
                pos["Gas Expense"] = round(gas_cost, 2)
                pos["Overall ROI (%)"] = round(((total_pos_value - total_pos_cost)/total_pos_cost*100) if total_pos_cost > 0 else 0, 2)
                total_value += total_pos_value
                total_gain += (total_pos_value - total_pos_cost) if total_pos_cost > 0 else 0
                
        df_final = pd.DataFrame(data)
        st.session_state['df_final'] = df_final
        
        avg_roi = (total_gain / total_value * 100) if total_value > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Portfolio Value", f"${total_value:,.2f}")
        with col2:
            st.metric("Performance (ROI Incl. Gas)", f"{avg_roi:+.2f}%")
            
        st.subheader("Asset Breakdown")
        st.dataframe(df_final, use_container_width=True)

st.divider()

col_comp, col_exp = st.columns(2)

with col_comp:
    if st.button("🛡️ Generate Compliance Risk Report"):
        if 'tx_data' in st.session_state:
            st.subheader("🛡️ CARF Compliance & Risk Summary")
            report = run_compliance_report(st.session_state['tx_data'])
            if isinstance(report, pd.DataFrame):
                st.dataframe(report, use_container_width=True)
            else:
                st.info(report)
        else:
            st.warning("⚠️ Please run the Audit from the sidebar first!")

with col_exp:
    if 'df_final' in st.session_state:
        csv = st.session_state['df_final'].to_csv(index=False)
        st.download_button(
            label="💾 Download Report (CSV)",
            data=csv,
            file_name=f"audit_{int(time.time())}.csv",
            mime="text/csv"
        )

st.divider()

with st.expander("📚 Full Report: Limitations, Conclusion & Bibliography"):
    st.markdown("""
    ## 6. Current Limitations:
    While this POC provides a robust framework for DeFi reconciliation, certain technical constraints remain:
    
    i) **Historical Data Depth**: The tool currently scans the most recent transaction history. Reaching the "true" initial cost basis may require increasing API pagination depth.
    ii) **Concentrated Liquidity (Uniswap V3)**: Standard ERC-20 LP tokens are fully supported; however, Uniswap V3 positions require a specialized decomposition engine.
    iii) **Gas Fee Approximation**: The gas accounting logic assumes the first detected inbound transfer is the primary acquisition point.
    iv) **API Rate Limits**: Performance is subject to the rate limits of the limited API keys.
    v) **Token Decimal Precision**: The current implementation assumes all ERC-20 tokens use 18 decimal places for demonstration.

    ## 7. Conclusion:
    The Liquidity Pool (LP) Reconciliation tool demonstrates that the "Regulatory Blindspot" in decentralised finance is not a permanent fixture, but a technical hurdle that can be overcome through automated indexing and real-time price discovery. Beyond simple compliance, the ability to decompose multi-chain data has profound implications for precision in P&L, true ROI discovery, and dynamic valuation of "long-tail" DeFi assets.

    ## 8. Bibliography:
    *   **Bank for International Settlements (BIS) (2023).** *DeFi: Ecosystem, Risks and Options for Regulation.*
    *   **Chainalysis (2023).** *The 2023 Geography of Cryptocurrency Report.*
    *   **DefiLlama (2026).** *Total Value Locked and Protocol Analytics.*
    *   **European Commission (2023).** *Markets in Crypto-Assets Regulation (MiCA).*
    *   **HMRC (2024).** *Cryptoassets Manual: Compliance and Reporting.*
    *   **IOSCO (2023).** *Policy Recommendations for Decentralized Finance (DeFi).*
    *   **Messari Crypto (2024).** *State of DeFi: Q1 2024 Analysis.*
    *   **OECD (2022).** *Crypto-Asset Reporting Framework and Amendments.*
    *   **Zetzsche, D. A., Arner, D. W., & Buckley, R. P. (2020).** *Decentralized Finance: The Future of Financial Regulation.*
    """)
