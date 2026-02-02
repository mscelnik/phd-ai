import sys
from src.io import load_config

def main(config_path):
    try:
        config = load_config(config_path)
        print("Config loaded and valid.")
    except Exception as e:
        print(f"Error loading config: {e}")
        exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_input.py <config_path>")
    else:
        main(sys.argv[1])
