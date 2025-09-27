import yfinance as yf
from datetime import datetime, timedelta

class FinanceClient:
    """Ruft Finanzdaten über die yfinance-Bibliothek ab."""

    def __init__(self):
        self.ticker_map = {
            'volkswagen': 'VOW3.DE',
            'siemens': 'SIE.DE',
            'allianz': 'ALV.DE',
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'sap': 'SAP.DE',
            'deutsche bank': 'DBK.DE',
            'rheinmetall': 'RHM.DE',
            'bmw': 'BMW.DE',
            'adidas': 'ADS.DE'
        }

    def _get_ticker_for_company(self, company_name: str):
        """Findet das passende Ticker-Symbol für einen Unternehmensnamen."""
        return self.ticker_map.get(company_name.lower())

    def get_stock_history(self, company_name: str, period_days: int = 60, end_date_str: str = None):
        """
        Ruft die Aktienkurshistorie für ein Unternehmen über einen bestimmten Zeitraum ab.

        Args:
            company_name (str): Der Name des Unternehmens.
            period_days (int): Der Zeitraum in Tagen (z.B. 60 für 60 Tage).
            end_date_str (str): Das Enddatum im Format 'YYYY-MM-DD'. Wenn None, wird heute verwendet.

        Returns:
            pandas.DataFrame: Ein DataFrame mit den historischen Kursdaten.
        """
        ticker_symbol = self._get_ticker_for_company(company_name)
        if not ticker_symbol:
            print(f"-> Fehler: Kein Ticker-Symbol für '{company_name}' gefunden.")
            return None

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = datetime.now()

        start_date = end_date - timedelta(days=period_days)
        print(
            f"Rufe Aktienhistorie für '{company_name}' (Ticker: {ticker_symbol}) ab: {start_date.strftime('%Y-%m-%d')} bis {end_date.strftime('%Y-%m-%d')}...")
        try:
            stock = yf.Ticker(ticker_symbol)
            history = stock.history(start=start_date, end=end_date)

            if history.empty:
                print(f"-> Warnung: Keine Daten für Ticker '{ticker_symbol}' gefunden.")
                return None

            print(f"-> Daten für '{company_name}' erfolgreich abgerufen.")
            return history

        except Exception as e:
            print(f"-> Ein Fehler ist aufgetreten: {e}")
            return None