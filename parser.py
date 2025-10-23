from abc import ABC, abstractmethod
from typing import List, Dict
import re
import pdfplumber
from pydantic import BaseModel


class StatementData(BaseModel):
    """Data model for credit card statement information."""
    issuer: str
    card_last_4: str
    billing_cycle: str
    due_date: str
    total_balance: float
    transactions: List[Dict]


class BaseParser(ABC):
    """Abstract base class for PDF statement parsers."""
    
    @abstractmethod
    def parse(self, file_path: str) -> StatementData:
        """Parse a PDF statement file and return structured data.
        
        Args:
            file_path (str): Path to the PDF file to parse
            
        Returns:
            StatementData: Parsed statement data
        """
        pass


class ChaseParser(BaseParser):
    """Concrete parser for Chase credit card statements."""
    
    def parse(self, file_path: str) -> StatementData:
        """Parse a Chase PDF statement file and return structured data.
        
        Args:
            file_path (str): Path to the PDF file to parse
            
        Returns:
            StatementData: Parsed statement data
        """
        # Extract text from all pages of the PDF
        text = self._extract_text_from_pdf(file_path)
        
        # Extract specific fields using regex patterns
        card_last_4 = self._extract_card_last_4(text)
        billing_cycle = self._extract_billing_cycle(text)
        due_date = self._extract_due_date(text)
        total_balance = self._extract_total_balance(text)
        
        # Extract transaction data
        transactions = self._extract_transactions(file_path)
        
        return StatementData(
            issuer="Chase",
            card_last_4=card_last_4,
            billing_cycle=billing_cycle,
            due_date=due_date,
            total_balance=total_balance,
            transactions=transactions
        )
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract all text from PDF file."""
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    
    def _extract_card_last_4(self, text: str) -> str:
        """Extract last 4 digits of card number."""
        # Look for patterns like "****1234" or "ending in 1234"
        patterns = [
            r'\*{4}(\d{4})',
            r'ending in (\d{4})',
            r'card ending (\d{4})',
            r'account ending (\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ""
    
    def _extract_billing_cycle(self, text: str) -> str:
        """Extract billing cycle period."""
        # Look for patterns like "Statement Period: 01/01/2024 - 01/31/2024"
        patterns = [
            r'statement period[:\s]+([^-\n]+?)\s*-\s*([^-\n]+)',
            r'billing period[:\s]+([^-\n]+?)\s*-\s*([^-\n]+)',
            r'period[:\s]+([^-\n]+?)\s*-\s*([^-\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"{match.group(1).strip()} - {match.group(2).strip()}"
        
        return ""
    
    def _extract_due_date(self, text: str) -> str:
        """Extract payment due date."""
        # Look for patterns like "Due Date: 02/15/2024"
        patterns = [
            r'due date[:\s]+(\d{1,2}/\d{1,2}/\d{4})',
            r'payment due[:\s]+(\d{1,2}/\d{1,2}/\d{4})',
            r'due[:\s]+(\d{1,2}/\d{1,2}/\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ""
    
    def _extract_total_balance(self, text: str) -> float:
        """Extract total balance amount."""
        # Look for patterns like "Total Balance: $1,234.56"
        patterns = [
            r'total balance[:\s]+\$?([\d,]+\.?\d*)',
            r'current balance[:\s]+\$?([\d,]+\.?\d*)',
            r'balance[:\s]+\$?([\d,]+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Remove commas and convert to float
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return 0.0
    
    def _extract_transactions(self, file_path: str) -> List[Dict]:
        """Extract transaction data from PDF using table extraction.
        
        Args:
            file_path (str): Path to the PDF file to parse
            
        Returns:
            List[Dict]: List of transaction dictionaries with Date, Description, Amount
        """
        transactions = []
        
        with pdfplumber.open(file_path) as pdf:
            # Start with page 1 (index 0) as specified
            first_page = pdf.pages[0]
            
            # Extract tables from the first page
            tables = first_page.extract_tables()
            
            for table in tables:
                if not table or len(table) < 2:  # Skip empty tables or tables with only headers
                    continue
                
                # Process each row in the table
                for row in table:
                    if not row or len(row) < 3:  # Skip rows that don't have at least 3 columns
                        continue
                    
                    # Clean up the row data
                    date = str(row[0]).strip() if row[0] else ""
                    description = str(row[1]).strip() if row[1] else ""
                    amount = str(row[2]).strip() if row[2] else ""
                    
                    # Skip header rows and empty rows
                    if (date.lower() in ['date', 'transaction date', ''] or 
                        description.lower() in ['description', 'merchant', ''] or
                        amount.lower() in ['amount', '']):
                        continue
                    
                    # Skip rows that don't look like valid transactions
                    if not date or not description or not amount:
                        continue
                    
                    # Clean up amount - remove currency symbols and extra spaces
                    amount_clean = re.sub(r'[^\d.,\-]', '', amount)
                    
                    # Try to convert amount to float for validation
                    try:
                        amount_float = float(amount_clean.replace(',', ''))
                    except (ValueError, AttributeError):
                        # If conversion fails, skip this row
                        continue
                    
                    # Create transaction dictionary
                    transaction = {
                        "Date": date,
                        "Description": description,
                        "Amount": amount_float
                    }
                    
                    transactions.append(transaction)
        
        return transactions


def parse_statement(file_path):
    """Parse a PDF statement file.
    
    Args:
        file_path (str): Path to the PDF file to parse
    """
    print('Parsing file...')


if __name__ == '__main__':
    # Instantiate the ChaseParser
    parser = ChaseParser()
    
    # Parse a sample PDF file
    sample_file = 'statements/chase_sample.pdf'
    
    try:
        # Call the parse method
        result = parser.parse(sample_file)
        
        # Print the extracted data as formatted JSON
        print("Extracted Statement Data:")
        print("=" * 50)
        print(result.model_dump_json(indent=4))
        
    except FileNotFoundError:
        print(f"Sample file '{sample_file}' not found.")
        print("Please add a Chase statement PDF to the statements/ directory.")
    except Exception as e:
        print(f"Error parsing PDF: {e}")
