import json
from data_structure.paths import NOR_EVAL
def load_ingredients(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

def run_selector(data):
    true_count = 0

    print("Bitte gib für jede Zutat `true` oder `false` ein.\n")

    for entry in data:
        # Jeder Eintrag ist ein Dictionary mit einem Schlüssel
        key = list(entry.keys())[0]
        values = entry[key]

        if "ingredient" in values:
            ingredient = values["ingredient"]
            user_input = input(f"{key} ':' {ingredient}' auswählen? (true/false): ").strip().lower()

            while user_input not in ['true', 'false']:
                user_input = input("Bitte nur 'true' oder 'false' eingeben: ").strip().lower()

            if user_input == 'true':
                true_count += 1

    print(f"\n✅ Anzahl der mit 'true' markierten Zutaten: {true_count}")

if __name__ == "__main__":
    filename = NOR_EVAL / "Pipeline.json" # Name der JSON-Datei
    try:
        data = load_ingredients(filename)
        run_selector(data)
    except FileNotFoundError:
        print(f"❌ Datei '{filename}' nicht gefunden.")
    except json.JSONDecodeError:
        print("❌ Fehler beim Lesen der JSON-Datei. Bitte überprüfe das Format.")
