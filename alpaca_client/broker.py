"""
Alpaca Broker API (v1)
"""
from typing import Optional, Dict, List, Any
from .client import AlpacaClient


class BrokerAPI:
    """Broker API for managing sub-accounts (B2B)."""
    
    def __init__(self, client: AlpacaClient, sandbox: bool = True):
        self.client = client
        self.base_url = AlpacaClient.BROKER_SANDBOX if sandbox else AlpacaClient.BROKER_PRODUCTION
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        return self.client._request(method, endpoint, base_url=self.base_url, **kwargs)
    
    # ========== ACCOUNTS ==========
    
    def create_account(self, account_data: Dict) -> Dict:
        """Create a new brokerage account."""
        return self._request("POST", "/v1/accounts", data=account_data)
    
    def get_accounts(self, **params) -> List[Dict]:
        """Get list of accounts."""
        return self._request("GET", "/v1/accounts", params=params)
    
    def get_account(self, account_id: str) -> Dict:
        """Get account by ID."""
        return self._request("GET", f"/v1/accounts/{account_id}")
    
    def update_account(self, account_id: str, **updates) -> Dict:
        """Update an account."""
        return self._request("PATCH", f"/v1/accounts/{account_id}", data=updates)
    
    # ========== DOCUMENTS & KYC ==========
    
    def upload_document(self, account_id: str, document_data: Dict) -> Dict:
        """Upload a document for KYC."""
        return self._request("POST", f"/v1/accounts/{account_id}/documents", data=document_data)
    
    def get_documents(self, account_id: str) -> List[Dict]:
        """Get documents for an account."""
        return self._request("GET", f"/v1/accounts/{account_id}/documents")
    
    # ========== BANKS & TRANSFERS ==========
    
    def create_bank(self, account_id: str, bank_data: Dict) -> Dict:
        """Add a recipient bank."""
        return self._request("POST", f"/v1/accounts/{account_id}/recipient_banks", data=bank_data)
    
    def get_banks(self, account_id: str) -> List[Dict]:
        """Get recipient banks for an account."""
        return self._request("GET", f"/v1/accounts/{account_id}/recipient_banks")
    
    def create_transfer(self, account_id: str, transfer_data: Dict) -> Dict:
        """Create a transfer."""
        return self._request("POST", f"/v1/accounts/{account_id}/transfers", data=transfer_data)
    
    def get_transfers(self, account_id: str, **params) -> List[Dict]:
        """Get transfers for an account."""
        return self._request("GET", f"/v1/accounts/{account_id}/transfers", params=params)
    
    # ========== BROKER TRADING ==========
    
    def create_order(self, account_id: str, order_data: Dict) -> Dict:
        """Create an order for a sub-account."""
        return self._request("POST", f"/v1/trading/accounts/{account_id}/orders", data=order_data)
    
    def get_orders(self, account_id: str, **params) -> List[Dict]:
        """Get orders for a sub-account."""
        return self._request("GET", f"/v1/trading/accounts/{account_id}/orders", params=params)
    
    def get_positions(self, account_id: str) -> List[Dict]:
        """Get positions for a sub-account."""
        return self._request("GET", f"/v1/trading/accounts/{account_id}/positions")
