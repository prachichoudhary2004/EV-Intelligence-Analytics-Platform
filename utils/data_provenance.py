import json
import os
from pathlib import Path

def read_dataset_provenance():
    """Reads metadata about the dataset from the bronze layer."""
    prov_path = Path("data/bronze/.dataset_provenance.json")
    if prov_path.exists():
        try:
            with open(prov_path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    
    return {
        "title": "India EV Market Intelligence",
        "profile": "india_production",
        "description": "Synthetic production-grade data for Indian EV market analysis."
    }
