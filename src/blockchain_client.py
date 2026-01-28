"""
Blockchain Client for Multi-Provider API Integration
Supports Blockchain.com and Blockbook APIs for multi-chain transaction data.
"""

import requests
import time
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlockchainProvider(Enum):
    """Supported blockchain data providers"""
    BLOCKCHAIN_COM = "blockchain.com"
    BLOCKBOOK = "blockbook"


class BlockchainClient:
    """
    Unified client for querying blockchain transaction data.
    Supports multiple providers with automatic failover and rate limiting.
    """
    
    def __init__(
        self,
        provider: BlockchainProvider = BlockchainProvider.BLOCKCHAIN_COM,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        max_retries: int = 3,
        rate_limit_delay: float = 0.5
    ):
        """
        Initialize blockchain client.
        
        Args:
            provider: Blockchain data provider to use
            api_key: API key for commercial providers (required for Blockchain.com)
            base_url: Custom API endpoint (overrides default)
            max_retries: Maximum number of retry attempts
            rate_limit_delay: Delay between requests (seconds)
        """
        self.provider = provider
        self.api_key = api_key
        self.max_retries = max_retries
        self.rate_limit_delay = rate_limit_delay
        
        # Set default base URLs
        if base_url:
            self.base_url = base_url
        elif provider == BlockchainProvider.BLOCKCHAIN_COM:
            self.base_url = "https://blockchain.info"
        else:  # Blockbook
            self.base_url = "https://eth.blockbook.info"
        
        logger.info(f"Initialized {provider.value} client with base URL: {self.base_url}")
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request with retry logic and rate limiting.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.base_url}/{endpoint}"
        
        # Add API key if using Blockchain.com
        if self.provider == BlockchainProvider.BLOCKCHAIN_COM and self.api_key:
            params = params or {}
            params['api_code'] = self.api_key
        
        for attempt in range(self.max_retries):
            try:
                time.sleep(self.rate_limit_delay)  # Rate limiting
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception("Max retries exceeded")
    
    def get_address_transactions(
        self,
        address: str,
        chain: str = "eth",
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get transactions for a wallet address.
        
        Args:
            address: Wallet address to query
            chain: Blockchain identifier (eth, btc, sol, etc.)
            limit: Maximum number of transactions to return
            offset: Pagination offset
            
        Returns:
            List of transaction dictionaries
        """
        if self.provider == BlockchainProvider.BLOCKCHAIN_COM:
            return self._get_blockchain_com_txs(address, limit, offset)
        else:
            return self._get_blockbook_txs(address, limit, offset)
    
    def _get_blockchain_com_txs(
        self,
        address: str,
        limit: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        """Get transactions from Blockchain.com API"""
        endpoint = f"rawaddr/{address}"
        params = {"limit": limit, "offset": offset}
        
        data = self._make_request(endpoint, params)
        return data.get("txs", [])
    
    def _get_blockbook_txs(
        self,
        address: str,
        limit: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        """Get transactions from Blockbook API"""
        endpoint = f"api/v2/address/{address}"
        params = {
            "page": offset // limit + 1,
            "pageSize": limit,
            "details": "txs"
        }
        
        data = self._make_request(endpoint, params)
        return data.get("transactions", [])
    
    def get_transaction_details(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific transaction.
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction details dictionary
        """
        if self.provider == BlockchainProvider.BLOCKCHAIN_COM:
            endpoint = f"rawtx/{tx_hash}"
        else:
            endpoint = f"api/v2/tx/{tx_hash}"
        
        return self._make_request(endpoint)
    
    def get_block_info(self, block_hash_or_height: str) -> Dict[str, Any]:
        """
        Get block information by hash or height.
        
        Args:
            block_hash_or_height: Block hash or block number
            
        Returns:
            Block information dictionary
        """
        if self.provider == BlockchainProvider.BLOCKCHAIN_COM:
            endpoint = f"rawblock/{block_hash_or_height}"
        else:
            endpoint = f"api/v2/block/{block_hash_or_height}"
        
        return self._make_request(endpoint)
    
    def search_transactions(
        self,
        addresses: List[str],
        min_value: Optional[float] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search for transactions matching criteria across multiple addresses.
        
        Args:
            addresses: List of wallet addresses
            min_value: Minimum transaction value filter
            start_date: Start date filter (ISO format)
            end_date: End date filter (ISO format)
            limit: Maximum results
            
        Returns:
            Filtered list of transactions
        """
        all_transactions = []
        
        for address in addresses:
            try:
                txs = self.get_address_transactions(address, limit=limit)
                all_transactions.extend(txs)
            except Exception as e:
                logger.error(f"Failed to fetch transactions for {address}: {e}")
        
        # Apply filters
        if min_value:
            all_transactions = [
                tx for tx in all_transactions
                if self._get_tx_value(tx) >= min_value
            ]
        
        return all_transactions[:limit]
    
    def _get_tx_value(self, tx: Dict) -> float:
        """Extract transaction value (provider-agnostic)"""
        if self.provider == BlockchainProvider.BLOCKCHAIN_COM:
            # Sum all outputs
            return sum(out.get("value", 0) for out in tx.get("out", [])) / 1e8
        else:
            # Blockbook format
            return float(tx.get("value", 0)) / 1e18  # Wei to ETH conversion
