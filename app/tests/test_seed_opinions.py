import json
from collections import Counter
from pathlib import Path


SEED_DIR = Path(__file__).resolve().parents[1] / "resources" / "db_init"


def test_each_seed_policy_document_has_multiple_feedback_comments():
    documents = json.loads((SEED_DIR / "policy_documents.json").read_text(encoding="utf-8"))["documents"]
    opinions = json.loads((SEED_DIR / "opinions.json").read_text(encoding="utf-8"))["opinions"]

    counts = Counter(opinion["doc_title"] for opinion in opinions)
    missing = [doc["title"] for doc in documents if counts[doc["title"]] < 3]

    assert missing == []
