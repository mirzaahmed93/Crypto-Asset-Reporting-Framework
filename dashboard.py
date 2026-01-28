"""
Streamlit GUI Dashboard for Blockchain CARF Framework
Interactive visualization for blockchain data, AI queries, and HMRC compliance.
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import (
    BlockchainClient,
    BlockchainProvider,
    PrivacyGuard,
    ETLPipeline,
    BlockchainQueryAgent,
    HMRCReporter
)

# Page configuration
st.set_page_config(
    page_title="Blockchain CARF Framework",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .reportable {
        background-color: #ffebee;
        padding: 0.5rem;
        border-left: 4px solid #f44336;
    }
    .compliant {
        background-color: #e8f5e9;
        padding: 0.5rem;
        border-left: 4px solid #4caf50;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.transactions_df = None
    st.session_state.audit_trail = []
    st.session_state.client = None
    st.session_state.privacy_guard = None
    st.session_state.etl = None
    st.session_state.ai_agent = None


def initialize_framework():
    """Initialize all framework components"""
    with st.spinner("Initializing Blockchain CARF Framework..."):
        try:
            # Initialize components
            st.session_state.client = BlockchainClient(
                provider=BlockchainProvider.BLOCKCHAIN_COM,
                rate_limit_delay=0.5
            )
            
            st.session_state.privacy_guard = PrivacyGuard(
                salt=os.getenv("PSEUDONYMIZATION_SALT", "demo_salt")
            )
            
            st.session_state.etl = ETLPipeline(
                carf_threshold=10000,
                eth_to_gbp_rate=1800
            )
            
            st.session_state.ai_agent = BlockchainQueryAgent(
                blockchain_client=st.session_state.client,
                etl_pipeline=st.session_state.etl
            )
            
            st.session_state.initialized = True
            st.success("✅ Framework initialized successfully!")
        except Exception as e:
            st.error(f"❌ Initialization failed: {str(e)}")


def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<p class="main-header">🔗 Blockchain CARF Framework</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Driven ETL Pipeline for HMRC Compliance</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=CARF+Framework", use_container_width=True)
        st.markdown("---")
        
        st.markdown("### ⚙️ Configuration")
        
        provider = st.selectbox(
            "Blockchain Provider",
            ["Blockchain.com", "Blockbook"],
            help="Choose your blockchain data source"
        )
        
        carf_threshold = st.number_input(
            "CARF Threshold (£)",
            min_value=1000,
            max_value=100000,
            value=10000,
            step=1000,
            help="HMRC reporting threshold in GBP"
        )
        
        eth_rate = st.number_input(
            "ETH to GBP Rate",
            min_value=100.0,
            max_value=10000.0,
            value=1800.0,
            step=50.0,
            help="Current exchange rate"
        )
        
        st.markdown("---")
        
        if not st.session_state.initialized:
            if st.button("🚀 Initialize Framework", use_container_width=True):
                initialize_framework()
        else:
            st.success("✅ Framework Active")
            if st.button("🔄 Restart", use_container_width=True):
                st.session_state.initialized = False
                st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🤖 AI Query",
        "📊 Transaction Data",
        "📑 HMRC Report",
        "🔐 Privacy Status",
        "📝 Audit Trail"
    ])
    
    # Tab 1: AI Query Interface
    with tab1:
        st.header("🤖 AI-Powered Query Interface")
        st.markdown("Ask natural language questions about blockchain data")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query = st.text_input(
                "Enter your query:",
                placeholder="e.g., Find all ETH transfers over £10,000",
                help="Use natural language to query blockchain data"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            query_button = st.button("🔍 Execute Query", use_container_width=True)
        
        if query_button and query and st.session_state.initialized:
            with st.spinner("Processing query..."):
                result = st.session_state.ai_agent.query(query)
                
                st.success("Query executed successfully!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Query", query)
                with col2:
                    st.metric("Tool Calls", result['tool_calls'])
                
                st.markdown("### Result")
                st.info(result['result'])
                
                # Store audit trail
                st.session_state.audit_trail = result['audit_trail']
        
        # Example queries
        st.markdown("### 💡 Example Queries")
        examples = [
            "Find all ETH transfers over £10,000",
            "Count transactions requiring CARF reporting",
            "Classify stablecoins vs unbacked assets"
        ]
        for example in examples:
            st.markdown(f"- *{example}*")
    
    # Tab 2: Transaction Data
    with tab2:
        st.header("📊 Transaction Data & Risk Scoring")
        
        if st.button("📥 Load Sample Transactions"):
            with st.spinner("Loading transactions..."):
                # Generate sample data
                sample_data = {
                    'tx_hash': ['0xabc123...', '0xdef456...', '0xghi789...'],
                    'timestamp_uk': [
                        datetime.now().isoformat(),
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ],
                    'value_eth': [15.5, 5.2, 25.8],
                    'value_gbp': [27900, 9360, 46440],
                    'carf_risk_score': [18, 0, 23],
                    'requires_carf_reporting': [True, False, True],
                    'is_qualifying_stablecoin': [True, False, True],
                    'carf_flags': [
                        ['EXCEEDS_CARF_THRESHOLD', 'QUALIFYING_STABLECOIN'],
                        [],
                        ['EXCEEDS_CARF_THRESHOLD', 'QUALIFYING_STABLECOIN', 'SMART_CONTRACT_INTERACTION']
                    ]
                }
                
                st.session_state.transactions_df = pd.DataFrame(sample_data)
                st.success("✅ Sample transactions loaded")
        
        if st.session_state.transactions_df is not None:
            df = st.session_state.transactions_df
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Transactions", len(df))
            with col2:
                reportable = len(df[df['requires_carf_reporting'] == True])
                st.metric("CARF Reportable", reportable)
            with col3:
                total_value = df['value_gbp'].sum()
                st.metric("Total Value", f"£{total_value:,.0f}")
            with col4:
                avg_risk = df['carf_risk_score'].mean()
                st.metric("Avg Risk Score", f"{avg_risk:.1f}")
            
            # Data table with color coding
            st.markdown("### Transaction Details")
            
            # Apply styling
            def highlight_reportable(row):
                if row['requires_carf_reporting']:
                    return ['background-color: #ffebee'] * len(row)
                else:
                    return ['background-color: #e8f5e9'] * len(row)
            
            styled_df = df.style.apply(highlight_reportable, axis=1)
            st.dataframe(styled_df, use_container_width=True, height=400)
            
            # Risk distribution chart
            st.markdown("### Risk Score Distribution")
            st.bar_chart(df.set_index('tx_hash')['carf_risk_score'])
    
    # Tab 3: HMRC Report
    with tab3:
        st.header("📑 HMRC CARF Compliance Report")
        
        if st.session_state.transactions_df is not None:
            df = st.session_state.transactions_df
            
            # Summary statistics
            st.markdown("### Summary Statistics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                total = len(df)
                reportable = len(df[df['requires_carf_reporting'] == True])
                stablecoins = len(df[df['is_qualifying_stablecoin'] == True])
                
                summary_data = {
                    'Category': [
                        'All Transactions',
                        'CARF Reportable (≥£10,000)',
                        'Qualifying Stablecoins',
                        'Unbacked Crypto Assets'
                    ],
                    'Count': [
                        total,
                        reportable,
                        stablecoins,
                        total - stablecoins
                    ],
                    'Percentage': [
                        '100%',
                        f'{(reportable/total*100):.1f}%' if total > 0 else '0%',
                        f'{(stablecoins/total*100):.1f}%' if total > 0 else '0%',
                        f'{((total-stablecoins)/total*100):.1f}%' if total > 0 else '0%'
                    ]
                }
                
                st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
            
            with col2:
                st.markdown("### Compliance Status")
                
                if reportable > 0:
                    st.markdown(f"""
                    <div class="reportable">
                    <strong>⚠️ Action Required</strong><br>
                    {reportable} transaction(s) require HMRC reporting
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="compliant">
                    <strong>✅ Compliant</strong><br>
                    No transactions exceed CARF threshold
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Export options
                st.markdown("### 📤 Export Options")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("📄 Export CSV", use_container_width=True):
                        csv = df.to_csv(index=False)
                        st.download_button(
                            "Download CSV",
                            csv,
                            "hmrc_carf_report.csv",
                            "text/csv",
                            use_container_width=True
                        )
                
                with col_b:
                    if st.button("📊 Export Excel", use_container_width=True):
                        st.info("Excel export available via HMRC Reporter module")
        else:
            st.info("👈 Load transactions from the Transaction Data tab first")
    
    # Tab 4: Privacy Status
    with tab4:
        st.header("🔐 Privacy & Security Status")
        
        if st.session_state.initialized:
            st.success("✅ Privacy Guard Active")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Encryption Status")
                st.markdown("""
                - **Algorithm**: AES-256 (Fernet)
                - **Key Storage**: Secure vault directory
                - **Pseudonymization**: Salted SHA-256
                - **GDPR Compliance**: ✅ Active
                """)
            
            with col2:
                st.markdown("### Security Features")
                st.markdown("""
                - 🔒 End-to-end encryption
                - 🔑 Separate key management
                - 🗑️ Cryptographic erasure
                - 📋 Full audit trail
                """)
            
            st.markdown("---")
            
            # Demonstrate pseudonymization
            st.markdown("### 🧪 Test Pseudonymization")
            
            test_address = st.text_input(
                "Enter wallet address:",
                placeholder="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
            )
            
            if test_address and st.session_state.privacy_guard:
                pseudo_id = st.session_state.privacy_guard.pseudonymize_address(test_address)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.text_area("Original Address", test_address, height=100)
                with col2:
                    st.text_area("Pseudonymized ID (SHA-256)", pseudo_id, height=100)
                
                st.info("💡 The pseudonymized ID is deterministic but cannot be reversed to the original address")
        else:
            st.warning("⚠️ Initialize framework to view privacy status")
    
    # Tab 5: Audit Trail
    with tab5:
        st.header("📝 Audit Trail")
        
        if st.session_state.audit_trail:
            st.markdown(f"**Total Entries**: {len(st.session_state.audit_trail)}")
            
            for i, entry in enumerate(st.session_state.audit_trail):
                with st.expander(f"Entry {i+1}: {entry.get('action', 'Unknown')}"):
                    st.json(entry)
            
            if st.button("📥 Export Audit Trail"):
                import json
                audit_json = json.dumps(st.session_state.audit_trail, indent=2)
                st.download_button(
                    "Download JSON",
                    audit_json,
                    "audit_trail.json",
                    "application/json"
                )
        else:
            st.info("No audit entries yet. Execute an AI query to generate audit logs.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
    <small>Blockchain CARF Framework v1.0 | Built for HMRC Compliance 2026</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
