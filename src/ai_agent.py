"""
AI Agent for Natural Language Query Processing
Interprets queries and orchestrates blockchain data filtering with audit trail.
"""

from typing import List, Dict, Any, Optional
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlockchainQueryAgent:
    """
    LangChain-powered agent for processing natural language queries
    about blockchain data. Provides audit trail for regulatory compliance.
    """
    
    def __init__(
        self,
        blockchain_client,
        etl_pipeline
    ):
        """
        Initialize AI agent with blockchain tooling.
        
        Args:
            blockchain_client: BlockchainClient instance
            etl_pipeline: ETLPipeline instance
        """
        self.blockchain_client = blockchain_client
        self.etl_pipeline = etl_pipeline
        
        # Audit trail for regulatory compliance
        self.audit_trail = []
        
        logger.info("BlockchainQueryAgent initialized")

    
    def _log_audit(self, action: str, parameters: Dict[str, Any]):
        """Log agent action to audit trail"""
        import datetime
        
        entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "action": action,
            "parameters": parameters,
            "reasoning": "AI agent decision"
        }
        self.audit_trail.append(entry)
        logger.info(f"Audit: {action} - {parameters}")
    
    def query(self, natural_language_query: str) -> Dict[str, Any]:
        """
        Process a natural language query about blockchain data.
        
        Args:
            natural_language_query: User's question (e.g., "Find all ETH transfers over £10k")
            
        Returns:
            Dictionary with results and audit trail
        """
        logger.info(f"Processing query: {natural_language_query}")
        
        # Parse query for common patterns
        result = self._parse_and_execute_query(natural_language_query)
        
        return {
            "query": natural_language_query,
            "result": result,
            "audit_trail": self.audit_trail.copy(),
            "tool_calls": len(self.audit_trail)
        }
    
    def _parse_and_execute_query(self, query: str) -> str:
        """
        Parse and execute natural language query.
        This is a simplified implementation for demonstration.
        In production, use full LangChain agent with real LLM.
        """
        query_lower = query.lower()
        
        # Pattern: Find transfers over X amount
        if "over" in query_lower or "above" in query_lower or "exceeding" in query_lower:
            amounts = re.findall(r'[£$€]?([\d,]+)k?', query)
            if amounts:
                amount_str = amounts[0].replace(',', '')
                amount = float(amount_str)
                if 'k' in query_lower:
                    amount *= 1000
                
                self._log_audit("query_parsed", {"type": "high_value_filter", "amount": amount})
                return f"Searching for transactions above £{amount:,.2f}"
        
        # Pattern: Count reportable transactions
        if "count" in query_lower or "how many" in query_lower:
            if "report" in query_lower:
                self._log_audit("query_parsed", {"type": "count_reportable"})
                return "Counting CARF-reportable transactions"
        
        # Pattern: Classify assets
        if "classify" in query_lower or "stablecoin" in query_lower:
            self._log_audit("query_parsed", {"type": "classify_assets"})
            return "Classifying qualifying stablecoins vs unbacked assets"
        
        # Default
        self._log_audit("query_parsed", {"type": "general"})
        return f"Processing query: {query}"
    
    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """
        Retrieve complete audit trail for regulatory review.
        
        Returns:
            List of audit log entries
        """
        return self.audit_trail.copy()
    
    def export_audit_trail(self, filepath: str):
        """
        Export audit trail to JSON file for HMRC submission.
        
        Args:
            filepath: Path to save audit trail JSON
        """
        import json
        
        with open(filepath, 'w') as f:
            json.dump(self.audit_trail, f, indent=2)
        
        logger.info(f"Audit trail exported to {filepath}")
