import os
import sys
from src.io import load_config
from scripts.run_simulation import main as run_single

def main(batch_dir):
    for fname in os.listdir(batch_dir):
        if fname.endswith('.yaml') or fname.endswith('.json'):
            print(f"Running simulation for {fname}")
            run_single(os.path.join(batch_dir, fname))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_batch.py <input_dir>")
    else:
        main(sys.argv[1])
