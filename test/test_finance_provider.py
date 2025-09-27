# test/test_finance_provider.py
import sys
import os

# Fügt das Hauptverzeichnis zum Python-Pfad hinzu, damit src importiert werden kann
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.finance_provider import FinanceClient

def run_finance_test():
    """Führt einen Test für den FinanceClient aus."""
    print("--- Teste FinanceClient ---\n")
    finance_client = FinanceClient()
    companies_to_test = ["Google", "Apple", "Siemens"]

    for company in companies_to_test:
        stock_data = finance_client.get_stock_history(company, period="7d")
        if stock_data is not None and not stock_data.empty:
            print(f"--- Aktienhistorie für {company} ---")
            print(stock_data)
            last_close = stock_data['Close'].iloc[-1]
            print(f"Letzter Schlusskurs: {last_close:.2f}")
            print("----------------------------------\n")
        else:
            print(f"-> Konnten keine Daten für {company} abrufen.\n")


if __name__ == "__main__":
    run_finance_test()