"""
Helper functions for Stock Market Tycoon
"""
from typing import Dict, List, Any


def format_currency(amount: float) -> str:
    """Formats a number as currency"""
    return f"${amount:,.2f}"


def format_percentage(value: float) -> str:
    """Formats a number as percentage"""
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.1f}%"


def print_separator(char: str = "=", length: int = 50):
    """Prints a separator line"""
    print(char * length)


def print_header(text: str):
    """Prints a formatted header"""
    print_separator()
    print(f"  {text}")
    print_separator()


def truncate_string(text: str, max_length: int = 20) -> str:
    """Truncates a string to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def calculate_portfolio_value(shares: Dict[str, int], prices: Dict[str, float]) -> float:
    """Calculates total portfolio value"""
    total = 0
    for company_id, quantity in shares.items():
        price = prices.get(company_id, 0)
        total += quantity * price
    return total


def get_color_for_change(change: float) -> str:
    """Returns ANSI color code based on change value"""
    if change > 0:
        return "\033[92m"  # Green
    elif change < 0:
        return "\033[91m"  # Red
    return "\033[0m"  # Default


def reset_color() -> str:
    """Returns ANSI reset code"""
    return "\033[0m"
