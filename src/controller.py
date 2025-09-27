import datetime
import re
import time
from .news_provider import NewsProvider, TagesschauAPI, SpiegelAPI, HandelsblattAPI
from .finance_provider import FinanceClient
from .ai_client import AIClient
from .data_manager import DataManager


class ExperimentController:
    """Steuert den gesamten Ablauf des Experiments und sammelt die Daten."""

    def __init__(self, model_name: str):
        print("Initialisiere Controller...")
        self.news_providers: list[NewsProvider] = [
            TagesschauAPI(),
            SpiegelAPI(),
            HandelsblattAPI()
        ]

        self.finance = FinanceClient()
        self.ai_client = AIClient(model=model_name)
        columns = [
            'Durchlauf_ID', 'Analyse_Datum', 'Unternehmen', 'Branche',
            'Nachrichten_Zeitraum_Tage', 'Anzahl_Nachrichten', 'Kurs_bei_Prognose',
            'Kurs_nach_7_Tagen', 'KI_Handlungsempfehlung', 'KI_Stimmungsanalyse',
            'KI_Begruendung', 'KI_Prognose_Roh_Text', 'Gefundene_Nachrichten_Snippets'
        ]
        self.data_manager = DataManager(columns=columns)
        print("Controller erfolgreich initialisiert.")

    def _parse_prediction(self, text: str) -> dict:
        recommendation = "Nicht gefunden"
        sentiment = "Nicht gefunden"
        reasoning = "Nicht gefunden"

        rec_match = re.search(r'\b(KAUFEN|VERKAUFEN)\b', text, re.IGNORECASE)
        if rec_match:
            recommendation = rec_match.group(0).upper()
        sentiment_match = re.search(r'Stimmungsanalyse:?([\s\S]*?)Kursanalyse:', text, re.IGNORECASE)
        if sentiment_match:
            sentiment = sentiment_match.group(1).strip()
        reasoning_match = re.search(r'Begründung:?([\s\S]*)', text, re.IGNORECASE)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
        return {
            'KI_Handlungsempfehlung': recommendation,
            'KI_Stimmungsanalyse': sentiment,
            'KI_Begruendung': reasoning,
        }

    def run_experiment_for(self, companies_dict: dict, news_timeframes: list, end_date_str: str):
        """Führt das Experiment für alle Unternehmen und Zeiträume durch."""
        run_id_counter = 1
        for company, industry in companies_dict.items():
            for timeframe in news_timeframes:
                print(
                    f"\n--- Starte Durchlauf {run_id_counter}: {company} ({industry}) mit {timeframe}-Tage-Nachrichten ---")

                all_articles = []
                for provider in self.news_providers:
                    try:
                        articles = provider.fetch_and_extract_articles(
                            company_name=company,
                            timeframe_days=timeframe
                        )
                        all_articles.extend(articles)
                    except Exception as e:
                        print(f"Fehler bei {provider.__class__.__name__}: {e}")

                stock_history = self.finance.get_stock_history(
                    company,
                    period_days=60,
                    end_date_str=end_date_str
                )
                if stock_history is None or stock_history.empty:
                    print(f"-> Kritisch: Keine Aktiendaten für {company}. Überspringe Durchlauf.")
                    run_id_counter += 1
                    continue

                #24.09.2025 - 1 Tag, um den 23.09.2025 zu simulieren und wissenschaftlich korrekt zu arbeiten
                today_for_test = stock_history.index[-1]
                target_date_7_days_prior = today_for_test - datetime.timedelta(days=7)

                try:
                    current_price = stock_history['Close'].iloc[-1]

                    price_in_7_days = stock_history.asof(target_date_7_days_prior)['Close']

                except (IndexError, KeyError) as e:
                    print(
                        f"-> Warnung: Nicht genügend historische Daten für {company} für die 7-Tage-Auswertung. Fehler: {e}")
                    current_price = stock_history['Close'].iloc[-1] if not stock_history.empty else 0
                    price_in_7_days = None

                prediction_text = self.ai_client.get_prediction(company, all_articles, stock_history.tail(timeframe))
                parsed_prediction = self._parse_prediction(prediction_text)
                result = {
                    'Durchlauf_ID': run_id_counter,
                    'Analyse_Datum': end_date_str,
                    'Unternehmen': company,
                    'Branche': industry,
                    'Nachrichten_Zeitraum_Tage': timeframe,
                    'Anzahl_Nachrichten': len(all_articles),
                    'Kurs_bei_Prognose': current_price,
                    'Kurs_nach_7_Tagen': price_in_7_days,
                    'KI_Handlungsempfehlung': parsed_prediction['KI_Handlungsempfehlung'],
                    'KI_Stimmungsanalyse': parsed_prediction['KI_Stimmungsanalyse'],
                    'KI_Begruendung': parsed_prediction['KI_Begruendung'],
                    'KI_Prognose_Roh_Text': prediction_text,
                    'Gefundene_Nachrichten_Snippets': (" ".join(all_articles))[:500] + "..."
                }
                self.data_manager.add_result(result)
                self.data_manager.save_results()
                run_id_counter += 1

        print("\nAlle Durchläufe abgeschlossen.")