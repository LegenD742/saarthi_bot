import json
import pandas as pd
from pathlib import Path

# Import the single-scheme transformer
from transform_one_scheme import transform_scheme

# Paths
BASE_DIR = Path(__file__).parent
RAW_DATA_FILE = BASE_DIR / "updated_data.csv"
OUTPUT_FILE = BASE_DIR / "schemes_structured.json"


def load_raw_schemes():
    """
    Safely load raw schemes CSV using pandas.
    Handles commas, full stops, quotes, and long text.
    """
    df = pd.read_csv(
        RAW_DATA_FILE,
        encoding="utf-8",
        quotechar='"',
        escapechar='\\'
    )

    # Convert NaN → empty string to avoid crashes
    df = df.fillna("")

    # Convert dataframe to list of dicts
    return df.to_dict(orient="records")


def transform_all_schemes():
    raw_schemes = load_raw_schemes()
    structured_schemes = []

    print(f"🔄 Loaded {len(raw_schemes)} raw schemes")

    for idx, raw_scheme in enumerate(raw_schemes):
        try:
            transformed = transform_scheme(raw_scheme)
            structured_schemes.append(transformed)
        except Exception as e:
            print(f"❌ Error transforming scheme at row {idx}")
            print(f"Slug: {raw_scheme.get('slug')}")
            print(e)

    # Write structured output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(structured_schemes, f, indent=2, ensure_ascii=False)

    print(f"✅ Successfully transformed {len(structured_schemes)} schemes")
    print(f"📁 Output written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    transform_all_schemes()
