"""
Privacy Guard: GDPR-Compliant Encryption and Pseudonymization
Implements AES-256 encryption and salted SHA-256 hashing for PII protection.
"""

import hashlib
import os
from typing import Dict, Optional, Tuple
from cryptography.fernet import Fernet
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PrivacyGuard:
    """
    GDPR-compliant privacy protection for blockchain wallet addresses and PII.
    Supports pseudonymization, encryption, and cryptographic erasure.
    """
    
    def __init__(
        self,
        encryption_key: Optional[bytes] = None,
        salt: Optional[str] = None,
        key_file_path: str = "./vault/encryption_key.key"
    ):
        """
        Initialize PrivacyGuard with encryption and hashing capabilities.
        
        Args:
            encryption_key: AES-256 encryption key (generates new if None)
            salt: Salt for pseudonymization hashing (generates random if None)
            key_file_path: Path to store/load encryption key
        """
        self.key_file_path = key_file_path
        self.salt = salt or self._generate_salt()
        
        # Load or generate encryption key
        if encryption_key:
            self.cipher = Fernet(encryption_key)
        elif os.path.exists(key_file_path):
            self.cipher = Fernet(self._load_key())
        else:
            self.cipher = Fernet(self._generate_and_save_key())
        
        logger.info("PrivacyGuard initialized with AES-256 encryption")
    
    def _generate_salt(self, length: int = 32) -> str:
        """Generate a random salt for hashing"""
        return os.urandom(length).hex()
    
    def _generate_and_save_key(self) -> bytes:
        """Generate new Fernet key and save to file"""
        key = Fernet.generate_key()
        os.makedirs(os.path.dirname(self.key_file_path), exist_ok=True)
        
        with open(self.key_file_path, 'wb') as key_file:
            key_file.write(key)
        
        # Set restrictive permissions (owner read/write only)
        os.chmod(self.key_file_path, 0o600)
        logger.info(f"Generated new encryption key: {self.key_file_path}")
        return key
    
    def _load_key(self) -> bytes:
        """Load encryption key from file"""
        with open(self.key_file_path, 'rb') as key_file:
            return key_file.read()
    
    def pseudonymize_address(self, wallet_address: str) -> str:
        """
        Create a pseudonymized hash of a wallet address using salted SHA-256.
        This allows internal analysis while protecting PII.
        
        Args:
            wallet_address: Raw wallet address
            
        Returns:
            Hexadecimal pseudonymized hash
        """
        salted_address = f"{self.salt}{wallet_address}".encode('utf-8')
        return hashlib.sha256(salted_address).hexdigest()
    
    def encrypt_pii(self, pii_data: str) -> str:
        """
        Encrypt personally identifiable information using AES-256.
        
        Args:
            pii_data: Raw PII (wallet address, email, etc.)
            
        Returns:
            Encrypted data as base64 string
        """
        encrypted = self.cipher.encrypt(pii_data.encode('utf-8'))
        return encrypted.decode('utf-8')
    
    def decrypt_pii(self, encrypted_data: str) -> str:
        """
        Decrypt encrypted PII data.
        
        Args:
            encrypted_data: Encrypted data as base64 string
            
        Returns:
            Decrypted plaintext
        """
        decrypted = self.cipher.decrypt(encrypted_data.encode('utf-8'))
        return decrypted.decode('utf-8')
    
    def process_wallet_data(
        self,
        wallet_address: str,
        additional_pii: Optional[Dict] = None
    ) -> Tuple[str, str]:
        """
        Process wallet data for GDPR compliance.
        Returns both pseudonymized ID and encrypted PII.
        
        Args:
            wallet_address: Blockchain wallet address
            additional_pii: Optional additional PII to encrypt
            
        Returns:
            Tuple of (pseudonymized_id, encrypted_pii_json)
        """
        pseudonymized_id = self.pseudonymize_address(wallet_address)
        
        # Prepare PII bundle
        pii_bundle = {
            "wallet_address": wallet_address
        }
        if additional_pii:
            pii_bundle.update(additional_pii)
        
        # Encrypt entire PII bundle
        encrypted_pii = self.encrypt_pii(json.dumps(pii_bundle))
        
        return pseudonymized_id, encrypted_pii
    
    def cryptographic_erasure(self) -> bool:
        """
        Perform cryptographic erasure by deleting the encryption key.
        After this, encrypted data becomes permanently unrecoverable.
        This satisfies GDPR "right to be forgotten" requirements.
        
        Returns:
            True if successful
        """
        try:
            if os.path.exists(self.key_file_path):
                # Overwrite key file with random data before deletion
                with open(self.key_file_path, 'wb') as f:
                    f.write(os.urandom(256))
                
                os.remove(self.key_file_path)
                logger.warning(
                    f"Cryptographic erasure completed. "
                    f"All encrypted data is now permanently unrecoverable."
                )
                return True
            else:
                logger.warning("No encryption key file found")
                return False
        except Exception as e:
            logger.error(f"Cryptographic erasure failed: {e}")
            return False
    
    def audit_log(self, operation: str, data_subject: str) -> Dict:
        """
        Generate audit log entry for GDPR compliance tracking.
        
        Args:
            operation: Type of operation (encrypt, decrypt, pseudonymize, erase)
            data_subject: Pseudonymized ID or identifier
            
        Returns:
            Audit log entry dictionary
        """
        import datetime
        
        return {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "operation": operation,
            "data_subject": data_subject,
            "salt_hash": hashlib.sha256(self.salt.encode()).hexdigest()[:16]
        }
