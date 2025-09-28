import json
from pathlib import Path

import joblib
import yaml
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


def main(cfg_path: str = "configs/train.yaml"):
    cfg = yaml.safe_load(open(cfg_path))
    paths = cfg["paths"]
    assert Path(paths["model_path"]).exists(), "Model not found. Run src/train.py first."

    # Deterministic split must match train.py
    data = load_iris()
    X, y = data.data, data.target
    strat = y if cfg["split"]["stratify"] else None
    _, X_te, _, y_te = train_test_split(
        X,
        y,
        test_size=cfg["split"]["test_size"],
        stratify=strat,
        random_state=cfg["random_seed"],
    )

    model = joblib.load(paths["model_path"])
    test_acc = float(accuracy_score(y_te, model.predict(X_te)))

    # Merge into metrics.json
    metrics_path = Path(paths["metrics_path"])
    base = {}
    if metrics_path.exists():
        base = json.load(open(metrics_path))
    base.update({"test_accuracy": test_acc})
    json.dump(base, open(metrics_path, "w"))
    print(f"Evaluated model; test_accuracy={test_acc:.4f}. Wrote {metrics_path}.")


if __name__ == "__main__":
    main()