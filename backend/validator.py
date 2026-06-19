import json
import re
from datetime import datetime
from pathlib import Path


class TransactionValidator:
    """Handles validation of transaction data according to business rules."""
    
    def __init__(self):
        """Initialize validator with country phone rules."""
        rules_path = Path(__file__).parent / "country_rules.json"
        with open(rules_path, 'r') as f:
            self.country_rules = json.load(f)
        
        self.valid_payment_modes = {"UPI", "Card", "Cash", "NetBanking", "Wallet"}
    
    def validate_order_id(self, order_id):
        """Validate order_id is not empty."""
        if not str(order_id).strip():
            return False, "Missing Order ID"
        return True, None
    
    def validate_customer_name(self, customer_name):
        """Validate customer_name is not empty."""
        if not str(customer_name).strip():
            return False, "Missing Customer Name"
        return True, None
    
    def validate_phone(self, phone_number, country):
        """
        Validate phone number based on country rules.
        Removes spaces and dashes, checks digit count.
        """
        if not phone_number or str(phone_number).strip() == "":
            return False, "Missing Phone Number"
        
        # Handle float values (pandas reads pure numbers as floats)
        phone_str = str(phone_number)
        if phone_str.endswith('.0'):
            phone_str = phone_str[:-2]
        
        # Remove spaces and dashes
        cleaned_phone = re.sub(r'[\s\-]', '', phone_str)
        
        # Check if only digits
        if not cleaned_phone.isdigit():
            return False, "Invalid Phone Number"
        
        # Check against country rules
        country = str(country).strip()
        if country not in self.country_rules:
            return False, f"Unknown Country: {country}"
        
        expected_length = self.country_rules[country]
        if len(cleaned_phone) != expected_length:
            return False, "Invalid Phone Number"
        
        return True, None
    
    def validate_date(self, date_str):
        """Validate date is in YYYY-MM-DD format."""
        if not date_str or str(date_str).strip() == "":
            return False, "Missing Order Date"
        
        try:
            datetime.strptime(str(date_str).strip(), "%Y-%m-%d")
            return True, None
        except ValueError:
            return False, "Invalid Date Format"
    
    def validate_time(self, time_str):
        """Validate time is in HH:MM:SS format."""
        if not time_str or str(time_str).strip() == "":
            return False, "Missing Order Time"
        
        try:
            datetime.strptime(str(time_str).strip(), "%H:%M:%S")
            return True, None
        except ValueError:
            return False, "Invalid Time Format"
    
    def validate_product(self, product_name):
        """Validate product_name is not empty."""
        if not str(product_name).strip():
            return False, "Missing Product Name"
        return True, None
    
    def validate_quantity(self, quantity):
        """Validate quantity is a positive integer."""
        try:
            qty = int(quantity)
            if qty <= 0:
                return False, "Quantity Must Be Positive"
            return True, None
        except (ValueError, TypeError):
            return False, "Invalid Quantity"
    
    def validate_amount(self, amount):
        """Validate amount is a positive numeric value."""
        try:
            amt = float(amount)
            if amt < 0:
                return False, "Negative Amount"
            return True, None
        except (ValueError, TypeError):
            return False, "Invalid Amount"
    
    def validate_payment_mode(self, payment_mode):
        """Validate payment_mode is in allowed list."""
        if not payment_mode or str(payment_mode).strip() == "":
            return False, "Missing Payment Mode"
        
        mode = str(payment_mode).strip()
        if mode not in self.valid_payment_modes:
            return False, "Invalid Payment Mode"
        return True, None
    
    def validate_row(self, row, seen_order_ids):
        """
        Validate a single transaction row.
        Returns (is_valid, error_message, order_id)
        """
        errors = []
        order_id = row.get("order_id", "")
        
        # Validate order_id
        valid, error = self.validate_order_id(order_id)
        if not valid:
            errors.append(error)
        elif str(order_id).strip() in seen_order_ids:
            errors.append("Duplicate Order ID")
        else:
            seen_order_ids.add(str(order_id).strip())
        
        # Validate customer_name
        valid, error = self.validate_customer_name(row.get("customer_name", ""))
        if not valid:
            errors.append(error)
        
        # Validate phone_number
        valid, error = self.validate_phone(
            row.get("phone_number", ""),
            row.get("country", "")
        )
        if not valid:
            errors.append(error)
        
        # Validate order_date
        valid, error = self.validate_date(row.get("order_date", ""))
        if not valid:
            errors.append(error)
        
        # Validate order_time
        valid, error = self.validate_time(row.get("order_time", ""))
        if not valid:
            errors.append(error)
        
        # Validate product_name
        valid, error = self.validate_product(row.get("product_name", ""))
        if not valid:
            errors.append(error)
        
        # Validate quantity
        valid, error = self.validate_quantity(row.get("quantity", ""))
        if not valid:
            errors.append(error)
        
        # Validate amount
        valid, error = self.validate_amount(row.get("amount", ""))
        if not valid:
            errors.append(error)
        
        # Validate payment_mode
        valid, error = self.validate_payment_mode(row.get("payment_mode", ""))
        if not valid:
            errors.append(error)
        
        is_valid = len(errors) == 0
        error_message = "; ".join(errors) if errors else None
        
        return is_valid, error_message, order_id
