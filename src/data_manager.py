import pandas as pd
import datetime
import os

class DataManager:
    """
    Verwaltet die Sammlung und Speicherung der Experiment-Ergebnisse.
    Speichert die Daten in einem Format, das für die Analyse und Visualisierung
    in einer wissenschaftlichen Arbeit optimiert ist.
    """
    def __init__(self, columns: list, output_dir: str = 'results'):
        """
        Initialisiert den DataManager mit den vordefinierten Spalten.

        Args:
            columns (list): Eine Liste der Spaltennamen für den DataFrame.
            output_dir (str): Das Verzeichnis, in dem die Ergebnis-Dateien gespeichert werden.
        """
        self.results_df = pd.DataFrame(columns=columns)
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = "experiment_results"
        filename = f"{base_filename}_{timestamp}.csv"
        self.full_path = os.path.join(self.output_dir, filename)
        print(f"DataManager initialisiert. Ergebnisse werden in '{self.output_dir}' gespeichert.")

    def add_result(self, result_data: dict):
        """
        Fügt eine neue Zeile mit den Ergebnisdaten zum DataFrame hinzu.
        Stellt sicher, dass nur vordefinierte Spalten hinzugefügt werden.
        """
        new_row = pd.DataFrame([result_data])
        self.results_df = pd.concat([self.results_df, new_row], ignore_index=True)
        print(f"Ergebnis für Durchlauf '{result_data.get('Durchlauf_ID', 'N/A')}' zum DataFrame hinzugefügt.")

    def save_results(self):
        """
        Speichert den gesammelten DataFrame in einer CSV-Datei mit Zeitstempel.
        Ein Zeitstempel verhindert, dass Ergebnisse früherer Läufe überschrieben werden.
        """
        if self.results_df.empty:
            print("Keine Ergebnisse zum Speichern vorhanden.")
            return

        try:
            self.results_df.to_csv(self.full_path, index=False, encoding='utf-8-sig', sep=";")
            print(f"Fortschritt gespeichert: {len(self.results_df)} Ergebnisse in '{self.full_path}' gesichert.")
        except Exception as e:
            print(f"Ein Fehler ist beim Speichern der CSV-Datei aufgetreten: {e}")