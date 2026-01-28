"""
HMRC Reporting Module for CARF Compliance
Generates summary tables and exports for UK tax reporting.
"""

import pandas as pd
from typing import Dict, List, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HMRCReporter:
    """
    Generate HMRC-compliant reports for Crypto-Asset Reporting Framework (CARF).
    Formats data according to UK tax authority requirements.
    """
    
    def __init__(
        self,
        reporting_entity: str = "Your Organization Ltd",
        tax_year: Optional[str] = None
    ):
        """
        Initialize HMRC reporter.
        
        Args:
            reporting_entity: Name of reporting organization
            tax_year: UK tax year (e.g., "2025-2026")
        """
        self.reporting_entity = reporting_entity
        self.tax_year = tax_year or self._get_current_tax_year()
        logger.info(f"HMRC Reporter initialized for {reporting_entity}, tax year {self.tax_year}")
    
    def _get_current_tax_year(self) -> str:
        """Determine current UK tax year (April 6 - April 5)"""
        now = datetime.now()
        if now.month < 4 or (now.month == 4 and now.day < 6):
            return f"{now.year - 1}-{now.year}"
        else:
            return f"{now.year}-{now.year + 1}"
    
    def generate_summary_table(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate summary table for HMRC compliance.
        
        Args:
            transactions_df: DataFrame of processed transactions
            
        Returns:
            Summary DataFrame with CARF breakdowns
        """
        summary_data = []
        
        # Total transactions
        total_count = len(transactions_df)
        total_value_gbp = transactions_df["value_gbp"].sum()
        
        # Reportable transactions (above threshold)
        reportable = transactions_df[transactions_df["requires_carf_reporting"] == True]
        reportable_count = len(reportable)
        reportable_value_gbp = reportable["value_gbp"].sum()
        
        # Qualifying stablecoins
        stablecoins = transactions_df[transactions_df["is_qualifying_stablecoin"] == True]
        stablecoin_count = len(stablecoins)
        stablecoin_value_gbp = stablecoins["value_gbp"].sum()
        
        # Unbacked assets
        unbacked = transactions_df[transactions_df["is_qualifying_stablecoin"] == False]
        unbacked_count = len(unbacked)
        unbacked_value_gbp = unbacked["value_gbp"].sum()
        
        # Smart contract interactions
        smart_contract_txs = transactions_df[
            transactions_df["decoded_contract_call"].notna()
        ]
        smart_contract_count = len(smart_contract_txs)
        
        summary_data = [
            {
                "Category": "All Transactions",
                "Count": total_count,
                "Total Value (GBP)": f"£{total_value_gbp:,.2f}",
                "Percentage": "100%"
            },
            {
                "Category": "CARF Reportable (≥£10,000)",
                "Count": reportable_count,
                "Total Value (GBP)": f"£{reportable_value_gbp:,.2f}",
                "Percentage": f"{(reportable_count/total_count*100) if total_count > 0 else 0:.1f}%"
            },
            {
                "Category": "Qualifying Stablecoins",
                "Count": stablecoin_count,
                "Total Value (GBP)": f"£{stablecoin_value_gbp:,.2f}",
                "Percentage": f"{(stablecoin_count/total_count*100) if total_count > 0 else 0:.1f}%"
            },
            {
                "Category": "Unbacked Crypto Assets",
                "Count": unbacked_count,
                "Total Value (GBP)": f"£{unbacked_value_gbp:,.2f}",
                "Percentage": f"{(unbacked_count/total_count*100) if total_count > 0 else 0:.1f}%"
            },
            {
                "Category": "Smart Contract Interactions",
                "Count": smart_contract_count,
                "Total Value (GBP)": "N/A",
                "Percentage": f"{(smart_contract_count/total_count*100) if total_count > 0 else 0:.1f}%"
            }
        ]
        
        return pd.DataFrame(summary_data)
    
    def generate_detailed_report(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate detailed transaction report for HMRC submission.
        
        Args:
            transactions_df: DataFrame of processed transactions
            
        Returns:
            Formatted DataFrame suitable for HMRC submission
        """
        # Select only reportable transactions
        reportable = transactions_df[transactions_df["requires_carf_reporting"] == True].copy()
        
        # Format for HMRC
        hmrc_report = reportable[[
            "tx_hash",
            "timestamp_uk",
            "value_gbp",
            "is_qualifying_stablecoin",
            "carf_risk_score",
            "carf_flags"
        ]].copy()
        
        # Rename columns to HMRC-friendly names
        hmrc_report.columns = [
            "Transaction Hash",
            "Transaction Date (UK Time)",
            "Value (GBP)",
            "Qualifying Stablecoin",
            "Risk Score",
            "Compliance Flags"
        ]
        
        # Sort by value descending
        hmrc_report = hmrc_report.sort_values("Value (GBP)", ascending=False)
        
        return hmrc_report
    
    def export_to_csv(
        self,
        transactions_df: pd.DataFrame,
        output_path: str = "./data/hmrc_carf_report.csv"
    ):
        """
        Export HMRC report to CSV format.
        
        Args:
            transactions_df: DataFrame of processed transactions
            output_path: Path to save CSV file
        """
        report = self.generate_detailed_report(transactions_df)
        report.to_csv(output_path, index=False)
        logger.info(f"HMRC report exported to {output_path}")
    
    def export_to_excel(
        self,
        transactions_df: pd.DataFrame,
        output_path: str = "./data/hmrc_carf_report.xlsx"
    ):
        """
        Export HMRC report to Excel format with summary sheet.
        
        Args:
            transactions_df: DataFrame of processed transactions
            output_path: Path to save Excel file
        """
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary sheet
            summary = self.generate_summary_table(transactions_df)
            summary.to_excel(writer, sheet_name='Summary', index=False)
            
            # Detailed transactions sheet
            detailed = self.generate_detailed_report(transactions_df)
            detailed.to_excel(writer, sheet_name='Reportable Transactions', index=False)
            
            # All transactions sheet (for internal review)
            transactions_df.to_excel(writer, sheet_name='All Transactions', index=False)
        
        logger.info(f"HMRC Excel report exported to {output_path}")
    
    def print_summary(self, transactions_df: pd.DataFrame):
        """
        Print formatted summary to console.
        
        Args:
            transactions_df: DataFrame of processed transactions
        """
        summary = self.generate_summary_table(transactions_df)
        
        print("\n" + "="*80)
        print(f"HMRC CARF COMPLIANCE REPORT - {self.tax_year}")
        print(f"Reporting Entity: {self.reporting_entity}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        print(summary.to_string(index=False))
        print("\n" + "="*80 + "\n")
