import json
from pathlib import Path

from google.cloud import firestore


def main() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    data_path = backend_dir / "data" / "seed_programs.json"
    programs = json.loads(data_path.read_text(encoding="utf-8"))

    client = firestore.Client()
    for program in programs:
        program_id = program["program_id"]
        evidence = program.pop("evidence", [])
        doc_ref = client.collection("programs").document(program_id)
        doc_ref.set(program)

        evidence_collection = doc_ref.collection("evidence")
        for idx, item in enumerate(evidence):
            evidence_collection.document(str(idx)).set(item)

    print(f"Seeded {len(programs)} programs into Firestore.")


if __name__ == "__main__":
    main()
