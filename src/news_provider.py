import requests
from bs4 import BeautifulSoup
import urllib.parse
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

class NewsProvider(ABC):
    """
    Abstrakte Basisklasse, die eine einheitliche Schnittstelle für alle
    Nachrichten-Provider vorschreibt.
    """
    @abstractmethod
    def fetch_and_extract_articles(self, company_name: str, timeframe_days: int) -> list[str]:
        """Sucht nach Nachrichten und gibt eine Liste der Volltexte zurück,
           gefiltert nach dem angegebenen Zeitrahmen."""
        pass

def is_within_timeframe(article_date: datetime, timeframe_days: int) -> bool:
    start_date = datetime.now(timezone.utc) - timedelta(days=timeframe_days)
    if article_date.tzinfo is None:
        article_date = article_date.replace(tzinfo=timezone.utc)
    return article_date >= start_date

class TagesschauAPI(NewsProvider):
    """Holt Nachrichten über die offizielle Tagesschau Suche-API."""

    def __init__(self):
        self.base_url = "https://www.tagesschau.de/api2u/search/"
        self.search_keywords = [
            "Aktie", "Bilanz", "Quartalszahlen", "Geschäftszahlen",
            "Gewinnwarnung", "Ausblick", "Prognose", "Vorstand", "Übernahme"
        ]

    def fetch_and_extract_articles(self, company_name: str, timeframe_days: int) -> list[str]:
        print(f"Starte Prozess für Tagesschau für '{company_name}'...")
        articles_with_dates = self._get_article_identifiers(company_name, num_pages_to_fetch=3)

        filtered_articles = []
        for article in articles_with_dates:
            try:
                article_date = datetime.fromisoformat(article['date'])
                if is_within_timeframe(article_date, timeframe_days):
                    filtered_articles.append(article)
            except (ValueError, TypeError):
                continue

        print(f"-> {len(filtered_articles)} Tagesschau-Artikel im {timeframe_days}-Tage-Zeitraum gefunden.")

        all_full_texts = [self._extract_text_from_identifier(article['url']) for article in filtered_articles]
        successful_texts = [text for text in all_full_texts if text]
        print(f"-> Prozess für Tagesschau abgeschlossen. {len(successful_texts)} Artikeltexte extrahiert.")
        return successful_texts

    def _get_article_identifiers(self, company_name: str, num_pages_to_fetch: int) -> list[dict]:
        """
        Interne Logik: Führt mehrere präzise Suchen mit Keywords aus,
        um relevante Artikel-URLs und deren Daten zu finden.
        """
        all_articles = {}

        search_terms = [f'"{company_name}"']
        search_terms.extend([f'"{company_name}" "{keyword}"' for keyword in self.search_keywords])

        for term in search_terms:
            for page_num in range(1, num_pages_to_fetch + 1):
                params = {'searchText': term, 'resultPage': page_num, 'pageSize': 30}
                try:
                    response = requests.get(self.base_url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    results = data.get('searchResults', [])
                    if not results:
                        break
                    for article in results:
                        if 'details' in article and 'date' in article:
                            all_articles[article['details']] = {'url': article['details'], 'date': article['date']}
                except Exception as e:
                    print(f"-> Fehler bei Tagesschau-API-Anfrage für '{term}': {e}")
                    break

        print(f"-> {len(all_articles)} einzigartige, relevante Tagesschau-Artikel gefunden.")
        return list(all_articles.values())

    def _extract_text_from_identifier(self, article_json_url: str) -> str | None:
        """
        Interne Logik: Ruft die JSON-Datei eines Artikels ab und extrahiert den Volltext.
        """
        try:
            response = requests.get(article_json_url)
            response.raise_for_status()
            article_data = response.json()
            content_list = article_data.get('content', [])
            text_parts = []
            for block in content_list:
                if block.get('type') == 'text':
                    html_text = block.get('value', '')
                    clean_text = BeautifulSoup(html_text, "html.parser").get_text(strip=True)
                    text_parts.append(clean_text)
            return "\n\n".join(text_parts)
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"-> Fehler beim Abrufen/Verarbeiten des Artikel-JSON von {article_json_url}: {e}")
            return None


class SpiegelAPI(NewsProvider):
    """Holt Nachrichten über die interne Such-API von Spiegel Online und extrahiert den Volltext."""

    def __init__(self):
        self.base_url = "https://www.spiegel.de/services/sitesearch/search?segments=spon&q={suchbegriff}&page={page_num}&page_size=10"
        self.article_text_selector = 'div[data-area="text"] p'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json'
        }

    def fetch_and_extract_articles(self, company_name: str, timeframe_days: int) -> list[str]:
        print(f"Starte Prozess für Spiegel Online für '{company_name}'...")
        articles_with_dates = self._get_article_identifiers(company_name, num_pages_to_fetch=5)

        filtered_articles = []
        for article in articles_with_dates:
            article_date = datetime.fromtimestamp(article['date'], tz=timezone.utc)
            if is_within_timeframe(article_date, timeframe_days):
                filtered_articles.append(article)

        print(f"-> {len(filtered_articles)} Spiegel-Artikel im {timeframe_days}-Tage-Zeitraum gefunden.")

        all_full_texts = [self._extract_text_from_identifier(article['url']) for article in filtered_articles]
        successful_texts = [text for text in all_full_texts if text]
        print(f"-> Prozess für Spiegel Online abgeschlossen. {len(successful_texts)} Artikeltexte extrahiert.")
        return successful_texts

    def _get_article_identifiers(self, company_name: str, num_pages_to_fetch: int) -> list[dict]:
        all_articles = []
        for page_num in range(1, num_pages_to_fetch + 1):
            search_url = self.base_url.format(suchbegriff=urllib.parse.quote(company_name), page_num=page_num)
            try:
                response = requests.get(search_url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                results = data.get('results', [])
                if not results:
                    break
                for article in results:
                    is_free_article = article.get('access_level') == 'free'
                    if is_free_article and 'url' in article and 'publish_date' in article:
                        all_articles.append({'url': article['url'], 'date': article['publish_date']})
            except Exception as e:
                print(f"-> Fehler bei Spiegel-API-Anfrage (Seite {page_num}): {e}")
                break
        print(f"-> {len(all_articles)} Spiegel-Artikel von {num_pages_to_fetch} Seiten abgerufen.")
        return all_articles

    def _extract_text_from_identifier(self, article_url: str) -> str | None:
        """
        Interne Logik: Extrahiert den sauberen Volltext von einer gegebenen Artikel-URL.
        """
        try:
            response = requests.get(article_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            text_paragraphs = soup.select(self.article_text_selector)
            full_text = "\n\n".join([p.get_text(strip=True) for p in text_paragraphs])
            return full_text
        except requests.exceptions.RequestException as e:
            print(f"-> Fehler beim Scrapen der URL {article_url}: {e}")
            return None


class HandelsblattAPI(NewsProvider):
    """Holt Nachrichten über die interne Such-API von Handelsblatt und extrahiert den Volltext."""

    def __init__(self):
        self.search_api_url = "https://content.www.handelsblatt.com/api/search/site/"
        self.content_api_url = "https://content.www.handelsblatt.com/api/content/eager/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_and_extract_articles(self, company_name: str, timeframe_days: int) -> list[str]:
        print(f"Starte Prozess für Handelsblatt für '{company_name}'...")
        articles_with_dates = self._get_article_identifiers(company_name, num_pages_to_fetch=5)

        filtered_articles = []
        for article in articles_with_dates:
            article_date = datetime.fromisoformat(article['date'].replace('Z', '+00:00'))
            if is_within_timeframe(article_date, timeframe_days):
                filtered_articles.append(article)

        print(f"-> {len(filtered_articles)} Handelsblatt-Artikel im {timeframe_days}-Tage-Zeitraum gefunden.")

        all_full_texts = [self._extract_text_from_identifier(article['path']) for article in filtered_articles]
        successful_texts = [text for text in all_full_texts if text]
        print(f"-> Prozess für Handelsblatt abgeschlossen. {len(successful_texts)} Artikeltexte extrahiert.")
        return successful_texts

    def _get_article_identifiers(self, company_name: str, num_pages_to_fetch: int) -> list[dict]:
        all_articles = []
        for page_num in range(1, num_pages_to_fetch + 1):
            params = {'searchTerm': company_name, 'page': page_num}
            try:
                response = requests.get(self.search_api_url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                teasers = data.get('teasers', [])
                if not teasers:
                    break
                for article in teasers:
                    is_free_article = article.get('contentAccessCategory') == 'NONE'

                    if is_free_article and 'url' in article and 'href' in article[
                        'url'] and 'dates' in article and 'published' in article['dates']:
                        all_articles.append({'path': article['url']['href'], 'date': article['dates']['published']})
            except Exception as e:
                print(f"-> Fehler bei Handelsblatt-API (Seite {page_num}): {e}")
                break
        print(f"-> {len(all_articles)} Handelsblatt-Artikel von {num_pages_to_fetch} Seiten abgerufen.")
        return all_articles


    def _extract_text_from_identifier(self, article_path: str) -> str | None:
        """
        Interne Logik: Extrahiert den Volltext eines Artikels über die Content-API,
        basierend auf dem relativen Pfad.
        """
        params = {'url': article_path}
        try:
            response = requests.get(self.content_api_url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            text_parts = []

            header = data.get('header', {})
            if header.get('headline'):
                text_parts.append(header['headline'])
            if header.get('leadText'):
                text_parts.append(header['leadText'])

            elements = data.get('elements', [])
            for element in elements:
                if element.get('type') == 'paragraphStorylineElement':
                    paragraph_text = element.get('data', {}).get('text', '')
                    clean_text = BeautifulSoup(paragraph_text, "html.parser").get_text(strip=True)
                    text_parts.append(clean_text)

            return "\n\n".join(text_parts)
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"-> Fehler beim Verarbeiten des Handelsblatt-Artikels {article_path}: {e}")
            return None