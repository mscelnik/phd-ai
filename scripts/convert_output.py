import sys
import pandas as pd
from src.io import save_output_excel

def main(csv_path, excel_path):
    df = pd.read_csv(csv_path)
    save_output_excel(df, excel_path)
    print(f"Converted {csv_path} to {excel_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert_output.py <csv_path> <excel_path>")
    else:
        main(sys.argv[1], sys.argv[2])
