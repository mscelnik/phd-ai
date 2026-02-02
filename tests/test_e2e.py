import yaml
from phdai.run import run_simulation


def test_e2e_quick_run(tmp_path):
    cfg = {
        "t0": 0.0,
        "tf": 0.2,
        "steps": 2,
        "C0": 1.0,
        "k": 1.0,
        "k_nuc": 0.01,
        "n_seed": 2,
        "seed_size": 1.0,
        "coag_steps": 1,
        "bins": 4,
        "out_dir": str(tmp_path / "out"),
        "max_iters": 100,
    }
    out = run_simulation(cfg)
    assert "summary_csv" in out
