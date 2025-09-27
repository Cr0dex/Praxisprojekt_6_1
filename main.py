from src.controller import ExperimentController

def main():
    print("Starte Aktienprognose-Experiment...")

    companies_to_analyze = {
        'Volkswagen': 'Automobil',
        'Siemens': 'Industrie',
        'Allianz': 'Finanzen',
        'Apple': 'Technologie',
        'Microsoft': 'Technologie',
        'SAP': 'Software',
        'Deutsche Bank': 'Finanzen',
        'Rheinmetall': 'Rüstung',
        'BMW': 'Automobil',
        'Adidas': 'Konsumgüter'
    }

    news_timeframes_to_test = [2, 7, 14]

    controller = ExperimentController(model_name="gemini-2.5-pro")
    controller.run_experiment_for(companies_to_analyze, news_timeframes_to_test, end_date_str="2025-09-23")

    print("\nExperiment vollständig beendet. Ergebnisse sind im 'results'-Ordner gespeichert.")

if __name__ == "__main__":
    main()