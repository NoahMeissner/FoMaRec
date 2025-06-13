import json
from data_structure.paths import NOR_EVAL  # Projektpfad

def load_data(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_annotation(data):
    true_count = 0

    print("Bitte gib für jede erkannte Zutat ein, ob der Match korrekt ist (true/false):\n")

    for entry in data:
        for key, value in entry.items():
            if value and value[0].lower() != "nicht erkannt":
                match = value[0]
                user_input = input(f"'{key}' → '{match}' korrekt? (true/false): ").strip().lower()

                while user_input not in ['true', 'false']:
                    user_input = input("Bitte nur 'true' oder 'false' eingeben: ").strip().lower()

                if user_input == 'true':
                    true_count += 1

    print(f"\n✅ Anzahl der als korrekt ('true') markierten Matches: {true_count}")

if __name__ == "__main__":
    filename = NOR_EVAL / "UNI.json"
    try:
        data = load_data(filename)
        run_annotation(data)
    except FileNotFoundError:
        print(f"❌ Datei '{filename}' nicht gefunden.")
    except json.JSONDecodeError:
        print("❌ Fehler beim Lesen der JSON-Datei.")
