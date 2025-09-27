import os
from google import genai
import pandas as pd
from dotenv import load_dotenv
import time

class AIClient:
    """
    Ein Client zur Interaktion mit der Google Gemini API für Aktienprognosen.
    """

    def __init__(self, model: str):
        """
        Initialisiert den Client und konfiguriert die API.
        Stellt sicher, dass der API-Schlüssel als Umgebungsvariable gesetzt ist.
        """
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY Umgebungsvariable nicht gesetzt! Bitte fügen Sie Ihren API-Schlüssel hinzu.")

        self.client = genai.Client(api_key=api_key)
        self.model = model
        print("AIClient erfolgreich initialisiert.")

    def get_prediction(self, company_name: str, news_articles: list, stock_history: pd.DataFrame):
        """
        Generiert eine Aktienkursprognose basierend auf Nachrichten und historischen Kursdaten.
        Versucht bei einer API-Überlastung unendlich oft, die Anfrage erneut zu senden.
        """
        if not news_articles:
            print(f"-> Keine Nachrichten für {company_name} vorhanden. Überspringe KI-Analyse.")
            return "Keine ausreichenden Daten für eine Prognose."

        print(f"-> Generiere Prompt für {company_name}...")
        prompt = self._build_prompt(company_name, news_articles, stock_history)

        attempt_counter = 1
        while True:
            print(f"-> Sende Anfrage an die Gemini API für {company_name} (Versuch {attempt_counter})...")
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                print(f"-> Antwort von Gemini für {company_name} erfolgreich erhalten.")
                print("-> Pausiere für 13 Sekunden, um das Rate Limit (5 RPM) einzuhalten.")
                time.sleep(13)

                return response.text
            except Exception as e:
                if "503" in str(e) and "UNAVAILABLE" in str(e):
                    print(f"-> API überlastet. Warte 30 Sekunden vor dem nächsten Versuch...")
                    time.sleep(30)
                    attempt_counter += 1
                else:
                    print(f"-> Ein unerwarteter, nicht behebbarer Fehler bei der Gemini API ist aufgetreten: {e}")
                    return f"Fehler bei der Analyse für {company_name}."


    def _build_prompt(self, company_name: str, news_articles: list, stock_history: pd.DataFrame):
        """
        Erstellt den detaillierten Text-Prompt für die Gemini API.
        """
        MAX_CHARS = 25000
        formatted_news = "\n\n---\n\n".join(news_articles)

        if len(formatted_news) > MAX_CHARS:
            formatted_news = formatted_news[
                                 :MAX_CHARS] + "\n\n... [HINWEIS: Nachrichten wurden zur Analyse gekürzt] ..."
            print(
                f"-> Warnung: Nachrichten für {company_name} wurden gekürzt, um das Token-Limit nicht zu überschreiten.")

        history_string = stock_history.to_string()
        days_in_history = len(stock_history)

        prompt = f"""
        **Analyse-Auftrag: Aktienkursprognose**

        **Unternehmen:** {company_name}

        **Analyse-Grundlage:**
        Du erhältst im Folgenden aktuelle Nachrichtenartikel und die Aktienkursentwicklung der letzten {days_in_history} Handelstage für das oben genannte Unternehmen. Deine Aufgabe ist es, diese Informationen als Finanzexperte zu analysieren.

        **Aufgaben:**
        1.  **Stimmungsanalyse:** Analysiere die Tonalität und den Inhalt der Nachrichten. Sind sie überwiegend positiv, negativ oder neutral? Gibt es wichtige Ankündigungen (z.B. Quartalszahlen, neue Produkte, Rechtsstreitigkeiten)?
        2.  **Kursanalyse:** Bewerte den bisherigen Kursverlauf. Gibt es einen klaren Trend?
        3.  **Prognose:** Erstelle basierend auf deiner Analyse eine Prognose für den Aktienkurs für die **nächsten 5 Handelstage**.
        4.  **Handlungsempfehlung:** Gib eine klare und prägnante Handlungsempfehlung ab. Entscheide dich zwingend für eine der beiden Optionen: **KAUFEN oder VERKAUFEN**.
        5.  **Begründung:** Fasse die wichtigsten Gründe für deine Empfehlung in 2-3 Sätzen zusammen.

        **Hier sind die Daten:**

        **1. Aktuelle Nachrichtenartikel:**
        ---
        {formatted_news}
        ---

        **2. Aktienkursverlauf der letzten {days_in_history} Handelstage:**
        ---
        {history_string}
        ---

        **Bitte gib deine vollständige Analyse jetzt aus.**
        """
        return prompt