"""
Document Numbering Service
Generates document numbers in format: TYPE-YYYY-NNN
Examples: INV-2026-001, PUR-2026-001, QUO-2026-001
"""

from datetime import datetime
from typing import Optional
from core.database import get_connection


class NumberingService:
    """Service for generating document numbers"""
    
    # Document type prefixes
    PREFIXES = {
        'invoice': 'INV',
        'quote': 'QUO',
        'order': 'ORD',
        'purchase': 'PUR',
        'payment': 'PAY',
        'expense': 'EXP',
        'client': 'CLI',
        'supplier': 'SUP',
        'article': 'ART',
        'depot': 'DEP',
    }
    
    @staticmethod
    def generate_number(doc_type: str, table_name: str, number_column: str = "number") -> str:
        """
        Generate next document number
        
        Args:
            doc_type: Document type (invoice, quote, order, etc.)
            table_name: Database table name
            number_column: Column name for document number
            
        Returns:
            Generated document number (e.g., "INV-2026-001")
        """
        prefix = NumberingService.PREFIXES.get(doc_type.lower(), doc_type.upper()[:3])
        current_year = datetime.now().year
        
        try:
            with get_connection() as conn:
                # Get the last number for this year
                query = f"""
                    SELECT {number_column} 
                    FROM {table_name} 
                    WHERE {number_column} LIKE ? 
                    ORDER BY {number_column} DESC 
                    LIMIT 1
                """
                pattern = f"{prefix}-{current_year}-%"
                cursor = conn.cursor()
                cursor.execute(query, (pattern,))
                row = cursor.fetchone()
                
                if row:
                    last_number = row[0]
                    # Extract sequence number
                    parts = last_number.split('-')
                    if len(parts) == 3:
                        try:
                            last_seq = int(parts[2])
                            next_seq = last_seq + 1
                        except ValueError:
                            next_seq = 1
                    else:
                        next_seq = 1
                else:
                    next_seq = 1
                
                # Format: TYPE-YYYY-NNN
                return f"{prefix}-{current_year}-{next_seq:03d}"
                
        except Exception as e:
            # Fallback: use timestamp-based number
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            return f"{prefix}-{current_year}-{timestamp[-3:]}"
    
    @staticmethod
    def generate_client_code() -> str:
        """Generate client code: CLI-001"""
        return NumberingService.generate_number('client', 'erp_clients', 'code')
    
    @staticmethod
    def generate_supplier_code() -> str:
        """Generate supplier code: SUP-001"""
        return NumberingService.generate_number('supplier', 'erp_suppliers', 'code')
    
    @staticmethod
    def generate_article_code() -> str:
        """Generate article code: ART-001"""
        return NumberingService.generate_number('article', 'erp_articles', 'code')
    
    @staticmethod
    def generate_invoice_number() -> str:
        """Generate invoice number: INV-2026-001"""
        return NumberingService.generate_number('invoice', 'erp_sales_invoices', 'number')
    
    @staticmethod
    def generate_quote_number() -> str:
        """Generate quote number: QUO-2026-001"""
        return NumberingService.generate_number('quote', 'erp_quotes', 'number')
    
    @staticmethod
    def generate_order_number() -> str:
        """Generate order number: ORD-2026-001"""
        return NumberingService.generate_number('order', 'erp_sales_orders', 'number')
    
    @staticmethod
    def generate_purchase_number() -> str:
        """Generate purchase number: PUR-2026-001"""
        return NumberingService.generate_number('purchase', 'erp_purchases', 'number')
    
    @staticmethod
    def generate_payment_number() -> str:
        """Generate payment number: PAY-2026-001"""
        return NumberingService.generate_number('payment', 'erp_client_payments', 'payment_number')
    
    @staticmethod
    def generate_expense_number() -> str:
        """Generate expense number: EXP-2026-001"""
        return NumberingService.generate_number('expense', 'erp_expenses', 'number')
