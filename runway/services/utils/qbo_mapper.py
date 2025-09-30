"""
QBO Data Mapper

Centralized QBO field mapping for consistent data access across the application.
This mapper provides a single source of truth for QBO field names and data transformation,
making it easier to maintain when QBO API changes.

This mapper follows the established pattern of centralized data transformation
and eliminates direct QBO field access throughout the codebase.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class QBOMapper:
    """
    Centralized QBO field mapping for consistent data access.
    
    This class provides static methods to map QBO API responses to standardized
    field names used throughout the application. This eliminates direct QBO field
    access and makes the codebase more maintainable.
    """
    
    @staticmethod
    def map_bill_data(qbo_bill: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map QBO bill data to standardized field names.
        
        Args:
            qbo_bill: Raw QBO bill data from API
            
        Returns:
            Dict with standardized field names
        """
        try:
            return {
                'qbo_id': qbo_bill.get('Id'),
                'doc_number': qbo_bill.get('DocNumber'),
                'amount': float(qbo_bill.get('TotalAmt', 0)),
                'balance': float(qbo_bill.get('Balance', 0)),
                'due_date': qbo_bill.get('DueDate'),
                'txn_date': qbo_bill.get('TxnDate'),
                'vendor': {
                    'id': qbo_bill.get('VendorRef', {}).get('value'),
                    'name': qbo_bill.get('VendorRef', {}).get('name', 'Unknown')
                },
                'private_note': qbo_bill.get('PrivateNote'),
                'sync_token': qbo_bill.get('SyncToken'),
                'status': qbo_bill.get('Balance', 0) > 0 and 'unpaid' or 'paid'
            }
        except (ValueError, TypeError) as e:
            logger.error(f"Error mapping bill data: {e}")
            return {
                'qbo_id': None,
                'doc_number': None,
                'amount': 0.0,
                'balance': 0.0,
                'due_date': None,
                'txn_date': None,
                'vendor': {'id': None, 'name': 'Unknown'},
                'private_note': None,
                'sync_token': None,
                'status': 'unknown'
            }
    
    @staticmethod
    def map_invoice_data(qbo_invoice: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map QBO invoice data to standardized field names.
        
        Args:
            qbo_invoice: Raw QBO invoice data from API
            
        Returns:
            Dict with standardized field names
        """
        try:
            return {
                'qbo_id': qbo_invoice.get('Id'),
                'doc_number': qbo_invoice.get('DocNumber'),
                'amount': float(qbo_invoice.get('TotalAmt', 0)),
                'balance': float(qbo_invoice.get('Balance', 0)),
                'due_date': qbo_invoice.get('DueDate'),
                'txn_date': qbo_invoice.get('TxnDate'),
                'customer': {
                    'id': qbo_invoice.get('CustomerRef', {}).get('value'),
                    'name': qbo_invoice.get('CustomerRef', {}).get('name', 'Unknown')
                },
                'private_note': qbo_invoice.get('PrivateNote'),
                'sync_token': qbo_invoice.get('SyncToken'),
                'status': qbo_invoice.get('Balance', 0) > 0 and 'unpaid' or 'paid'
            }
        except (ValueError, TypeError) as e:
            logger.error(f"Error mapping invoice data: {e}")
            return {
                'qbo_id': None,
                'doc_number': None,
                'amount': 0.0,
                'balance': 0.0,
                'due_date': None,
                'txn_date': None,
                'customer': {'id': None, 'name': 'Unknown'},
                'private_note': None,
                'sync_token': None,
                'status': 'unknown'
            }
    
    @staticmethod
    def map_payment_data(qbo_payment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map QBO payment data to standardized field names.
        
        Args:
            qbo_payment: Raw QBO payment data from API
            
        Returns:
            Dict with standardized field names
        """
        try:
            return {
                'qbo_id': qbo_payment.get('Id'),
                'amount': float(qbo_payment.get('TotalAmt', 0)),
                'txn_date': qbo_payment.get('TxnDate'),
                'payment_ref_num': qbo_payment.get('PaymentRefNum'),
                'private_note': qbo_payment.get('PrivateNote'),
                'sync_token': qbo_payment.get('SyncToken'),
                'payment_method': qbo_payment.get('PaymentMethodRef', {}).get('name', 'Unknown')
            }
        except (ValueError, TypeError) as e:
            logger.error(f"Error mapping payment data: {e}")
            return {
                'qbo_id': None,
                'amount': 0.0,
                'txn_date': None,
                'payment_ref_num': None,
                'private_note': None,
                'sync_token': None,
                'payment_method': 'Unknown'
            }
    
    @staticmethod
    def map_customer_data(qbo_customer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map QBO customer data to standardized field names.
        
        Args:
            qbo_customer: Raw QBO customer data from API
            
        Returns:
            Dict with standardized field names
        """
        try:
            return {
                'qbo_id': qbo_customer.get('Id'),
                'name': qbo_customer.get('Name', 'Unknown'),
                'company_name': qbo_customer.get('CompanyName'),
                'email': qbo_customer.get('PrimaryEmailAddr', {}).get('Address'),
                'phone': qbo_customer.get('PrimaryPhone', {}).get('FreeFormNumber'),
                'billing_address': qbo_customer.get('BillAddr', {}),
                'shipping_address': qbo_customer.get('ShipAddr', {}),
                'sync_token': qbo_customer.get('SyncToken'),
                'active': qbo_customer.get('Active', True)
            }
        except (ValueError, TypeError) as e:
            logger.error(f"Error mapping customer data: {e}")
            return {
                'qbo_id': None,
                'name': 'Unknown',
                'company_name': None,
                'email': None,
                'phone': None,
                'billing_address': {},
                'shipping_address': {},
                'sync_token': None,
                'active': True
            }
    
    @staticmethod
    def map_vendor_data(qbo_vendor: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map QBO vendor data to standardized field names.
        
        Args:
            qbo_vendor: Raw QBO vendor data from API
            
        Returns:
            Dict with standardized field names
        """
        try:
            return {
                'qbo_id': qbo_vendor.get('Id'),
                'name': qbo_vendor.get('Name', 'Unknown'),
                'company_name': qbo_vendor.get('CompanyName'),
                'email': qbo_vendor.get('PrimaryEmailAddr', {}).get('Address'),
                'phone': qbo_vendor.get('PrimaryPhone', {}).get('FreeFormNumber'),
                'billing_address': qbo_vendor.get('BillAddr', {}),
                'sync_token': qbo_vendor.get('SyncToken'),
                'active': qbo_vendor.get('Active', True)
            }
        except (ValueError, TypeError) as e:
            logger.error(f"Error mapping vendor data: {e}")
            return {
                'qbo_id': None,
                'name': 'Unknown',
                'company_name': None,
                'email': None,
                'phone': None,
                'billing_address': {},
                'sync_token': None,
                'active': True
            }
    
    @staticmethod
    def map_company_info(qbo_company: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map QBO company info to standardized field names.
        
        Args:
            qbo_company: Raw QBO company data from API
            
        Returns:
            Dict with standardized field names
        """
        try:
            return {
                'qbo_id': qbo_company.get('Id'),
                'name': qbo_company.get('CompanyName', 'Unknown'),
                'legal_name': qbo_company.get('LegalName'),
                'address': qbo_company.get('CompanyAddr', {}),
                'phone': qbo_company.get('PrimaryPhone', {}).get('FreeFormNumber'),
                'email': qbo_company.get('PrimaryEmailAddr', {}).get('Address'),
                'website': qbo_company.get('WebAddr', {}).get('URI'),
                'fiscal_year_start': qbo_company.get('FiscalYearStartMonth'),
                'country': qbo_company.get('Country'),
                'currency': qbo_company.get('CurrencyRef', {}).get('value'),
                'sync_token': qbo_company.get('SyncToken')
            }
        except (ValueError, TypeError) as e:
            logger.error(f"Error mapping company data: {e}")
            return {
                'qbo_id': None,
                'name': 'Unknown',
                'legal_name': None,
                'address': {},
                'phone': None,
                'email': None,
                'website': None,
                'fiscal_year_start': None,
                'country': None,
                'currency': None,
                'sync_token': None
            }
    
    @staticmethod
    def map_account_data(qbo_account: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map QBO account data to standardized field names.
        
        Args:
            qbo_account: Raw QBO account data from API
            
        Returns:
            Dict with standardized field names
        """
        try:
            return {
                'qbo_id': qbo_account.get('Id'),
                'name': qbo_account.get('Name', 'Unknown'),
                'account_type': qbo_account.get('AccountType'),
                'account_sub_type': qbo_account.get('AccountSubType'),
                'classification': qbo_account.get('Classification'),
                'current_balance': float(qbo_account.get('CurrentBalance', 0)),
                'currency': qbo_account.get('CurrencyRef', {}).get('value'),
                'active': qbo_account.get('Active', True),
                'sync_token': qbo_account.get('SyncToken')
            }
        except (ValueError, TypeError) as e:
            logger.error(f"Error mapping account data: {e}")
            return {
                'qbo_id': None,
                'name': 'Unknown',
                'account_type': None,
                'account_sub_type': None,
                'classification': None,
                'current_balance': 0.0,
                'currency': None,
                'active': True,
                'sync_token': None
            }
