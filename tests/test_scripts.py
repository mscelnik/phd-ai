import subprocess
import sys


def test_validate_input(tmp_path):
    yaml_path = tmp_path / "test.yaml"
    yaml_path.write_text("a: 1\nb: 2\n")
    result = subprocess.run([sys.executable, "scripts/validate_input.py", str(yaml_path)], capture_output=True)
    assert b"Config loaded and valid." in result.stdout


def test_prepare_output_dir(tmp_path):
    out_dir = tmp_path / "outputs"
    result = subprocess.run([sys.executable, "scripts/prepare_output_dir.py", str(out_dir)], capture_output=True)
    assert b"Created output directory" in result.stdout or b"already exists" in result.stdout
