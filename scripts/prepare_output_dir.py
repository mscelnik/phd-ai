import os
import sys

def main(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    else:
        print(f"Output directory already exists: {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prepare_output_dir.py <output_dir>")
    else:
        main(sys.argv[1])
