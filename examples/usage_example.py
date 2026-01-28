"""
Usage Example: Blockchain CARF Framework
Demonstrates AI-driven ETL pipeline for HMRC compliance.
"""

import sys
import os

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


def main():
    print("=" * 80)
    print("Blockchain CARF Framework - Usage Example")
    print("=" * 80 + "\n")
    
    # Step 1: Initialize Blockchain Client
    print("Step 1: Initializing Blockchain Client...")
    client = BlockchainClient(
        provider=BlockchainProvider.BLOCKCHAIN_COM,
        api_key=os.getenv("BLOCKCHAIN_COM_API_KEY"),
        rate_limit_delay=0.5
    )
    print("✓ Blockchain client initialized\n")
    
    # Step 2: Initialize Privacy Guard
    print("Step 2: Initializing Privacy Guard (AES-256 + Salted SHA-256)...")
    privacy_guard = PrivacyGuard(
        key_file_path=os.getenv("ENCRYPTION_KEY_PATH", "./vault/encryption_key.key"),
        salt=os.getenv("PSEUDONYMIZATION_SALT", "demo_salt_replace_in_production")
    )
    print("✓ Privacy guard initialized\n")
    
    # Step 3: Initialize ETL Pipeline
    print("Step 3: Initializing ETL Pipeline...")
    etl = ETLPipeline(
        target_timezone="Europe/London",
        carf_threshold=float(os.getenv("CARF_THRESHOLD_GBP", "10000")),
        eth_to_gbp_rate=float(os.getenv("ETH_TO_GBP_RATE", "1800"))
    )
    print("✓ ETL pipeline initialized\n")
    
    # Step 4: Initialize AI Agent
    print("Step 4: Initializing LangChain AI Agent...")
    ai_agent = BlockchainQueryAgent(
        blockchain_client=client,
        etl_pipeline=etl
    )
    print("✓ AI agent initialized\n")
    
    # Step 5: Process Natural Language Query
    print("Step 5: Processing Natural Language Query...")
    query = "Find all ETH transfers over £10,000"
    print(f"   Query: '{query}'")
    
    result = ai_agent.query(query)
    print(f"   Result: {result['result']}")
    print(f"   Tool Calls: {result['tool_calls']}")
    print("✓ Query processed with audit trail\n")
    
    # Step 6: Simulate Transaction Data Processing
    print("Step 6: Processing Sample Transactions...")
    
    # Simulated transaction data
    sample_transactions = [
        {
            "hash": "0xabc123...",
            "time": 1706400000,
            "value": "15000000000000000000",  # 15 ETH
            "input": "0xa9059cbb000000000000000000000000abcd1234...",
            "blockHeight": 19000000
        },
        {
            "hash": "0xdef456...",
            "time": 1706400100,
            "value": "5000000000000000000",  # 5 ETH
            "input": "",
            "blockHeight": 19000001
        }
    ]
    
    # Process privacy for sample wallets
    sample_wallet = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    pseudonymized_id, encrypted_pii = privacy_guard.process_wallet_data(sample_wallet)
    
    print(f"   Original Wallet: {sample_wallet}")
    print(f"   Pseudonymized ID: {pseudonymized_id[:32]}...")
    print(f"   Encrypted PII: {encrypted_pii[:50]}...")
    print("✓ Privacy protection applied\n")
    
    # Prepare privacy data
    privacy_data = [
        {
            "pseudonymized_from": pseudonymized_id,
            "pseudonymized_to": privacy_guard.pseudonymize_address("0x0000..."),
            "encrypted_pii": encrypted_pii
        }
    ] * len(sample_transactions)
    
    # Process through ETL
    df = etl.process_transactions(sample_transactions, privacy_data)
    print(f"   Processed {len(df)} transactions")
    print(f"   Reportable: {len(df[df['requires_carf_reporting']])} transactions\n")
    
    # Step 7: Generate HMRC Report
    print("Step 7: Generating HMRC CARF Report...")
    hmrc_reporter = HMRCReporter(
        reporting_entity=os.getenv("REPORTING_ENTITY_NAME", "Your Organization Ltd"),
        tax_year=os.getenv("TAX_YEAR", "2025-2026")
    )
    
    # Print summary
    hmrc_reporter.print_summary(df)
    
    # Export reports
    output_path = os.getenv("DATA_OUTPUT_PATH", "./data")
    os.makedirs(output_path, exist_ok=True)
    
    hmrc_reporter.export_to_csv(df, f"{output_path}/hmrc_carf_report.csv")
    print(f"✓ CSV report exported to {output_path}/hmrc_carf_report.csv")
    
    # Export audit trail
    audit_path = f"{output_path}/audit_trail.json"
    ai_agent.export_audit_trail(audit_path)
    print(f"✓ Audit trail exported to {audit_path}\n")
    
    # Step 8: Demonstrate Audit Capabilities
    print("Step 8: Audit Trail Summary...")
    audit_trail = ai_agent.get_audit_trail()
    print(f"   Total audit entries: {len(audit_trail)}")
    for entry in audit_trail:
        print(f"   - {entry['action']}: {entry['parameters']}")
    print()
    
    print("=" * 80)
    print("✓ Framework demonstration complete!")
    print("=" * 80)
    print("\nKey Features Demonstrated:")
    print("  ✓ Multi-provider blockchain API integration")
    print("  ✓ AES-256 encryption with GDPR compliance")
    print("  ✓ AI-powered natural language queries")
    print("  ✓ Automated CARF risk scoring")
    print("  ✓ HMRC-compliant reporting")
    print("  ✓ Complete audit trail for regulators")
    print()


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    main()
