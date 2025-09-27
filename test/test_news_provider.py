# test/test_news_provider.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.news_provider import NewsProvider, TagesschauAPI, SpiegelAPI, HandelsblattAPI

def run_news_tests():
    """Führt Tests für alle implementierten Nachrichten-Provider aus."""
    test_company = "Google"
    print(f"--- Starte News-Tests für das Unternehmen: '{test_company}' ---\n")

    test_configs = [
        {
            "provider": TagesschauAPI(),
            "params": {"num_articles": 10}
        },
        {
            "provider": SpiegelAPI(),
            "params": {}
        },
        {
            "provider": HandelsblattAPI(),
            "params": {"num_pages": 2}
        }
    ]

    # 2. Wir gehen die Konfigurationen in einer Schleife durch.
    for config in test_configs:
        provider = config["provider"]
        params = config["params"]
        provider_name = provider.__class__.__name__

        print(f"--- Teste {provider_name} ---")

        try:
            articles = provider.fetch_and_extract_articles(
                company_name=test_company,
                **params
            )

            print(f"-> {provider_name}-Test: {len(articles)} Artikel gefunden.")
            if articles:
                print(f"   Auszug: '{articles[0][:75]}...'")

        except Exception as e:
            print(f"!! Ein unerwarteter Fehler ist im Test für {provider_name} aufgetreten: {e}")

        finally:
            print("-" * (len(provider_name) + 10) + "\n")

    print("--- Alle News-Tests abgeschlossen ---")


if __name__ == "__main__":
    run_news_tests()