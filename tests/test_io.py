from src.io import load_config, save_output_csv


def test_load_yaml(tmp_path):
    yaml_path = tmp_path / "test.yaml"
    yaml_path.write_text("a: 1\nb: 2\n")
    config = load_config(str(yaml_path))
    assert config["a"] == 1
    assert config["b"] == 2


def test_load_json(tmp_path):
    json_path = tmp_path / "test.json"
    json_path.write_text('{"a": 1, "b": 2}')
    config = load_config(str(json_path))
    assert config["a"] == 1
    assert config["b"] == 2


def test_save_output_csv(tmp_path):
    data = {"x": [1, 2], "y": [3, 4]}
    out_path = tmp_path / "out.csv"
    save_output_csv(data, str(out_path))
    assert out_path.exists()
    content = out_path.read_text()
    assert "x" in content and "y" in content
