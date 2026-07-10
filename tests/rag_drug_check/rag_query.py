import json
import chromadb

JSONL_PATH = "interactions.jsonl"
COLLECTION_NAME = "drug_interactions"


def load_rows(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def build_metadata(row):
    # Chroma metadata values must be str / int / float / bool (no lists/dicts),
    # so list fields are flattened into comma-separated strings and also
    # duplicated as individual boolean flags for exact-match filtering.
    meta = {
        "doc_type": "drug_interaction",          # lets you filter this collection
                                                    # down to interaction rows only
        "source": "VerificMediCare",
        "chunk_id": row["id"],
        "category": row["category"],
        "primary_medicine": row["primary_medicine"].lower(),
        "avoid_with": ", ".join(row["avoid_with"]).lower(),
        "n_avoid_drugs": len(row["avoid_with"]),
    }
    # one boolean flag per interacting drug -> enables where={"has_warfarin": True}
    for drug in row["avoid_with"]:
        key = "has_" + "".join(c if c.isalnum() else "_" for c in drug.lower())[:60]
        meta[key] = True
    return meta


def main():
    rows = load_rows(JSONL_PATH)

    client = chromadb.PersistentClient(path="./chroma_store")
    # Chroma's default embedding function (all-MiniLM-L6-v2) is fine to start;
    # swap in a medical/domain embedding model (e.g. BioBERT-based) for better recall.
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    collection.upsert(
        ids=[r["id"] for r in rows],
        documents=[r["text"] for r in rows],
        metadatas=[build_metadata(r) for r in rows],
    )

    print(f"Ingested {len(rows)} interaction rows into '{COLLECTION_NAME}'.")

    # --- Example retrieval pattern for a consultation transcript ---
    # Step 1: extract drug mentions from the transcript (regex list-match against
    # a known drug vocabulary, or a lightweight NER/entity-linking pass).
    mentioned_drugs = ["ibuprofen", "losartan"]  # example output of that extraction step

    for drug in mentioned_drugs:
        # A) exact/metadata filter — catches the row where this IS the primary medicine
        exact = collection.get(where={"primary_medicine": drug})

        # B) semantic search — catches rows where the drug appears only in the
        # "avoid_with" list (i.e. it's a dangerous co-prescription, not headline drug)
        semantic = collection.query(
            query_texts=[f"drug interactions and contraindications involving {drug}"],
            n_results=1,
        )

        print(f"\n--- {drug} ---")
        print("Exact primary-medicine matches:", exact["ids"])
        print("Semantic matches:", semantic["documents"])


if __name__ == "__main__":
    main()