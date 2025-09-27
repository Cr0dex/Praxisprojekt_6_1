# test/data_manager_test.py
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_manager import DataManager


def run_data_manager_test():
    """
    Führt einen Test für den DataManager aus, um die Speicherfunktion zu überprüfen.
    """
    print("--- Starte DataManager Test ---")

    # 1. Definiere die Spalten, genau wie im Controller
    test_columns = [
        'Durchlauf_ID', 'Analyse_Datum', 'Unternehmen', 'Branche',
        'Nachrichten_Zeitraum_Tage', 'Anzahl_Nachrichten', 'Kurs_bei_Prognose',
        'Kurs_nach_7_Tagen', 'KI_Handlungsempfehlung', 'KI_Stimmungsanalyse',
        'KI_Begruendung', 'KI_Prognose_Roh_Text', 'Gefundene_Nachrichten_Snippets'
    ]

    # 2. Initialisiere den DataManager in einem speziellen Test-Ordner
    test_output_dir = 'test_results'
    data_manager = DataManager(columns=test_columns, output_dir=test_output_dir)

    # 3. Erstelle zwei Beispieldatensätze
    sample_result_1 = {
        'Durchlauf_ID': 1,
        'Analyse_Datum': '2025-09-23',
        'Unternehmen': 'Test AG',
        'Branche': 'Software',
        'Nachrichten_Zeitraum_Tage': 7,
        'Anzahl_Nachrichten': 5,
        'Kurs_bei_Prognose': 150.75,
        'Kurs_nach_7_Tagen': 155.25,
        'KI_Handlungsempfehlung': 'KAUFEN',
        'KI_Stimmungsanalyse': 'Überwiegend positiv',
        'KI_Begruendung': 'Starke Quartalszahlen und positive Nachrichtenlage.',
        'KI_Prognose_Roh_Text': 'Der komplette Text der KI-Antwort...',
        'Gefundene_Nachrichten_Snippets': 'Ausschnitt der gefundenen Nachrichten...'
    }

    sample_result_2 = {
        'Durchlauf_ID': 2,
        'Analyse_Datum': '2025-09-23',
        'Unternehmen': 'Beispiel GmbH',
        'Branche': 'Industrie',
        'Nachrichten_Zeitraum_Tage': 14,
        'Anzahl_Nachrichten': 2,
        'Kurs_bei_Prognose': 88.20,
        'Kurs_nach_7_Tagen': 85.10,
        'KI_Handlungsempfehlung': 'VERKAUFEN',
        'KI_Stimmungsanalyse': 'Eher negativ',
        'KI_Begruendung': 'Schwacher Ausblick und negative Analystenkommentare.',
        'KI_Prognose_Roh_Text': 'Ein anderer kompletter Text der KI-Antwort...',
        'Gefundene_Nachrichten_Snippets': 'Ein anderer Ausschnitt der Nachrichten...'
    }

    # 4. Füge die Beispieldaten hinzu
    data_manager.add_result(sample_result_1)
    data_manager.add_result(sample_result_2)

    # 5. Speichere die Ergebnisse
    test_filename_base = "test_run"
    data_manager.save_results(base_filename=test_filename_base)

    # 6. Überprüfe, ob die Datei tatsächlich erstellt wurde
    print("\n--- Überprüfe Testergebnis ---")
    try:
        # Finde die neueste Datei im Test-Ordner, die mit unserem Test-Dateinamen beginnt
        files = [f for f in os.listdir(test_output_dir) if f.startswith(test_filename_base)]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(test_output_dir, x)))
        latest_file = files[-1]

        file_path = os.path.join(test_output_dir, latest_file)

        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            print(f"-> ERFOLG: Die Datei '{file_path}' wurde erfolgreich erstellt.")
            print(f"-> Die Datei enthält {len(df)} Zeilen.")
            if len(df) == 2:
                print("-> ERFOLG: Die Anzahl der gespeicherten Zeilen ist korrekt.")
            else:
                print(f"-> FEHLER: Es wurden {len(df)} Zeilen gespeichert, aber 2 erwartet.")
        else:
            print(f"-> FEHLER: Die Datei '{file_path}' wurde NICHT erstellt.")

    except (IndexError, FileNotFoundError):
        print("-> FEHLER: Keine Ergebnisdatei im Ordner 'test_results' gefunden.")
    except Exception as e:
        print(f"-> Ein unerwarteter Fehler bei der Überprüfung ist aufgetreten: {e}")

    print("--- DataManager Test beendet ---")


if __name__ == "__main__":
    run_data_manager_test()