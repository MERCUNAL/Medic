from pathlib import Path
import json
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSV_PATH = BASE_DIR / "documents" / "Medical_list_with_specs.csv"

_catalog_cache = None

def _load_catalog():
    global _catalog_cache
    if _catalog_cache is not None:
        return _catalog_cache
    if not CSV_PATH.exists():
        _catalog_cache = []
        return _catalog_cache
    df = pd.read_csv(CSV_PATH)
    items = []
    for idx, row in df.iterrows():
        items.append({
            "csv_id": f"csv_{idx}",
            "product_retailer_id": f"csv_{idx}",
            "name": f"{row.get('Name of Device and Device Class','').strip()}",
            "brand": row.get("Brand Name",""),
            "model": row.get("Model Numbers",""),
            "price": row.get("Price (INR)",""),
            "specs": row.get("Specifications / Details",""),
            "intended_use": row.get("Intended Use",""),
            "license": row.get("License Number",""),
            "manufacturer": row.get("Manufacturer/Importer Name and address",""),
            "title": f"{row.get('Brand Name','')} {row.get('Model Numbers','')}".strip(),
            "description": f"{row.get('Name of Device and Device Class','')} | {row.get('Price (INR)','')} INR".strip(),
        })
    _catalog_cache = items
    return _catalog_cache

def list_catalog(q: str = "", category: str = "", page: int = 1, limit: int = 10):
    items = _load_catalog()
    if q:
        ql = q.lower()
        items = [i for i in items if ql in i["name"].lower() or ql in i["brand"].lower() or ql in i["model"].lower() or ql in i["title"].lower()]
    if category:
        cl = category.lower()
        items = [i for i in items if cl in i["name"].lower()]
    total = len(items)
    start = (page-1)*limit
    end = start+limit
    return {"total": total, "page": page, "limit": limit, "items": items[start:end]}

def get_item(csv_id: str):
    for i in _load_catalog():
        if i["csv_id"] == csv_id or i["product_retailer_id"] == csv_id:
            return i
    return None

def categories():
    items = _load_catalog()
    cats = sorted(set(i["name"] for i in items if i["name"]))
    return cats

def to_product_list_sections(items: list[dict], catalog_id: str):
    # Meta product_list sections: each section has title + product_items [{product_retailer_id}]
    # We batch 10 per section
    sections = []
    batch_size = 10
    for s_idx in range(0, len(items), batch_size):
        batch = items[s_idx:s_idx+batch_size]
        sections.append({
            "title": f"Medical Equipment {s_idx//batch_size + 1}",
            "product_items": [{"product_retailer_id": it["product_retailer_id"]} for it in batch]
        })
    return sections

def to_interactive_list_sections(items: list[dict]):
    sections = [{"title": "Catalog", "rows": []}]
    for it in items[:10]:
        sections[0]["rows"].append({
            "id": it["product_retailer_id"],
            "title": it["title"][:24] or it["name"][:24],
            "description": f"INR {it['price']} | {it['name'][:40]}"
        })
    return sections
