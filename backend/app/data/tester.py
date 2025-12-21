import pandas as pd
from pathlib import Path

RAW_DATA_FILE = Path(__file__).parent / "updated_data.csv"

# Load CSV safely
df = pd.read_csv(
    RAW_DATA_FILE,
    encoding="utf-8",
    quotechar='"',
    escapechar='\\'
)

print("✅ CSV loaded successfully")
print("Rows:", len(df))
print("Columns:", list(df.columns))

print("\n--- SAMPLE ROW (RAW) ---")
sample = df.iloc[0]

for col in df.columns:
    print(f"{col}:")
    print(sample[col])
    print("-" * 40)
