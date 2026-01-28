"""
ETL Pipeline for Blockchain Transaction Data
Handles extraction, transformation, and CARF risk scoring.
"""

import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
import pytz
from eth_abi import decode as abi_decode
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ETLPipeline:
    """
    Extract, Transform, Load pipeline for blockchain data.
    Includes ERC-20 decoding, timezone normalization, and CARF risk scoring.
    """
    
    # ERC-20 Transfer event signature
    ERC20_TRANSFER_SIG = "0xa9059cbb"  # transfer(address,uint256)
    
    # HMRC CARF reporting threshold (£10,000)
    CARF_THRESHOLD_GBP = 10000
    
    # Qualifying stablecoins per UK regulations
    QUALIFYING_STABLECOINS = {
        "USDT", "USDC", "DAI", "BUSD", "GBPT", "EURS"
    }
    
    def __init__(
        self,
        target_timezone: str = "Europe/London",
        carf_threshold: float = CARF_THRESHOLD_GBP,
        eth_to_gbp_rate: float = 1800.0  # Should be fetched from price API
    ):
        """
        Initialize ETL pipeline.
        
        Args:
            target_timezone: Target timezone for timestamp normalization
            carf_threshold: Reporting threshold in GBP
            eth_to_gbp_rate: ETH to GBP conversion rate
        """
        self.target_timezone = pytz.timezone(target_timezone)
        self.carf_threshold = carf_threshold
        self.eth_to_gbp_rate = eth_to_gbp_rate
        logger.info(f"ETL Pipeline initialized (threshold: £{carf_threshold:,.2f})")
    
    def decode_erc20_transfer(self, input_hex: str) -> Optional[Dict[str, Any]]:
        """
        Decode ERC-20 transfer function call from raw hex input.
        
        Args:
            input_hex: Raw hex input data from transaction
            
        Returns:
            Dictionary with decoded parameters or None if not ERC-20
        """
        if not input_hex or len(input_hex) < 10:
            return None
        
        # Check function signature
        function_sig = input_hex[:10]
        if function_sig.lower() != self.ERC20_TRANSFER_SIG:
            return None
        
        try:
            # Decode parameters: address (20 bytes) + uint256 (32 bytes)
            param_data = bytes.fromhex(input_hex[10:])
            
            # Manual decoding for transfer(address,uint256)
            if len(param_data) >= 64:
                recipient = "0x" + param_data[12:32].hex()  # Last 20 bytes of first param
                amount = int.from_bytes(param_data[32:64], byteorder='big')
                
                return {
                    "function": "transfer",
                    "recipient": recipient,
                    "amount": amount,
                    "amount_decimal": amount / 1e18  # Standard 18 decimals
                }
        except Exception as e:
            logger.warning(f"Failed to decode ERC-20 transfer: {e}")
        
        return None
    
    def normalize_timestamp(self, timestamp: int) -> str:
        """
        Normalize Unix timestamp to UK/London timezone.
        
        Args:
            timestamp: Unix timestamp (seconds)
            
        Returns:
            ISO 8601 formatted string in target timezone
        """
        utc_time = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.UTC)
        local_time = utc_time.astimezone(self.target_timezone)
        return local_time.isoformat()
    
    def calculate_carf_risk_score(
        self,
        value_gbp: float,
        is_stablecoin: bool = False,
        has_smart_contract: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate CARF risk score for transaction.
        
        Args:
            value_gbp: Transaction value in GBP
            is_stablecoin: Whether transaction involves qualifying stablecoin
            has_smart_contract: Whether transaction calls smart contract
            
        Returns:
            Dictionary with risk score and metadata
        """
        risk_score = 0
        flags = []
        
        # Primary threshold check
        if value_gbp >= self.carf_threshold:
            risk_score += 10
            flags.append("EXCEEDS_CARF_THRESHOLD")
        
        # Stablecoin classification
        if is_stablecoin:
            risk_score += 5
            flags.append("QUALIFYING_STABLECOIN")
        else:
            flags.append("UNBACKED_ASSET")
        
        # Smart contract interaction
        if has_smart_contract:
            risk_score += 3
            flags.append("SMART_CONTRACT_INTERACTION")
        
        # Determine reporting requirement
        requires_reporting = value_gbp >= self.carf_threshold
        
        return {
            "risk_score": risk_score,
            "flags": flags,
            "requires_carf_reporting": requires_reporting,
            "value_gbp": value_gbp,
            "threshold_gbp": self.carf_threshold
        }
    
    def transform_transaction(
        self,
        tx: Dict[str, Any],
        pseudonymized_from: str,
        pseudonymized_to: str,
        encrypted_pii: str
    ) -> Dict[str, Any]:
        """
        Transform raw blockchain transaction into CARF-compliant format.
        
        Args:
            tx: Raw transaction dictionary
            pseudonymized_from: Pseudonymized sender address
            pseudonymized_to: Pseudonymized recipient address
            encrypted_pii: Encrypted PII data
            
        Returns:
            Transformed transaction record
        """
        # Extract timestamp (provider-agnostic)
        timestamp = tx.get("time", tx.get("blockTime", 0))
        
        # Extract value and convert to GBP
        value_eth = float(tx.get("value", 0)) / 1e18
        value_gbp = value_eth * self.eth_to_gbp_rate
        
        # Decode smart contract input
        input_data = tx.get("input", tx.get("vin", [{}])[0].get("hex", ""))
        decoded_contract = self.decode_erc20_transfer(input_data)
        
        # Determine if stablecoin
        is_stablecoin = False
        if decoded_contract:
            # In production, you'd lookup token symbol from contract address
            # For now, we'll check against known addresses or use heuristics
            is_stablecoin = value_gbp >= 1000  # Heuristic placeholder
        
        # Calculate CARF risk score
        carf_analysis = self.calculate_carf_risk_score(
            value_gbp=value_gbp,
            is_stablecoin=is_stablecoin,
            has_smart_contract=bool(decoded_contract)
        )
        
        return {
            "tx_hash": tx.get("txid", tx.get("hash", "")),
            "timestamp_utc": timestamp,
            "timestamp_uk": self.normalize_timestamp(timestamp),
            "pseudonymized_from": pseudonymized_from,
            "pseudonymized_to": pseudonymized_to,
            "encrypted_pii": encrypted_pii,
            "value_eth": value_eth,
            "value_gbp": value_gbp,
            "decoded_contract_call": decoded_contract,
            "is_qualifying_stablecoin": is_stablecoin,
            "carf_risk_score": carf_analysis["risk_score"],
            "carf_flags": carf_analysis["flags"],
            "requires_carf_reporting": carf_analysis["requires_carf_reporting"],
            "block_height": tx.get("blockHeight", tx.get("block_height", 0))
        }
    
    def process_transactions(
        self,
        transactions: List[Dict],
        privacy_data: List[Dict]
    ) -> pd.DataFrame:
        """
        Process batch of transactions into normalized DataFrame.
        
        Args:
            transactions: List of raw transaction dictionaries
            privacy_data: List of privacy metadata (pseudonymized IDs, encrypted PII)
            
        Returns:
            Pandas DataFrame with transformed transactions
        """
        processed = []
        
        for i, tx in enumerate(transactions):
            privacy = privacy_data[i] if i < len(privacy_data) else {}
            
            transformed = self.transform_transaction(
                tx=tx,
                pseudonymized_from=privacy.get("pseudonymized_from", "UNKNOWN"),
                pseudonymized_to=privacy.get("pseudonymized_to", "UNKNOWN"),
                encrypted_pii=privacy.get("encrypted_pii", "")
            )
            processed.append(transformed)
        
        df = pd.DataFrame(processed)
        
        logger.info(
            f"Processed {len(df)} transactions. "
            f"{len(df[df['requires_carf_reporting']])} require CARF reporting."
        )
        
        return df
    
    def filter_reportable_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter transactions that require HMRC reporting.
        
        Args:
            df: DataFrame of processed transactions
            
        Returns:
            Filtered DataFrame with only reportable transactions
        """
        return df[df["requires_carf_reporting"] == True].copy()
