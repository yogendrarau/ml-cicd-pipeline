import json, os, random
from pathlib import Path

import joblib
import numpy as np
import yaml
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def set_seed(seed: int):
    np.random.seed(seed)
    random.seed(seed)


def main(cfg_path: str = "configs/train.yaml"):
    cfg = yaml.safe_load(open(cfg_path))
    set_seed(cfg["random_seed"])

    # Load data
    data = load_iris()
    X, y = data.data, data.target

    # Deterministic split
    strat = y if cfg["split"]["stratify"] else None
    X_tr, X_te, y_tr, y_te = train_test_split(
        X,
        y,
        test_size=cfg["split"]["test_size"],
        stratify=strat,
        random_state=cfg["random_seed"],
    )

    model = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("lr", LogisticRegression(**cfg["model"]["params"], random_state=cfg["random_seed"])),
        ]
    )
    model.fit(X_tr, y_tr)

    train_acc = float(accuracy_score(y_tr, model.predict(X_tr)))


    paths = cfg["paths"]
    Path(paths["artifacts_dir"]).mkdir(parents=True, exist_ok=True)
    joblib.dump(model, paths["model_path"])

    run_id = os.getenv("GITHUB_SHA", "local")
    metrics = {
    "run_id": run_id,
    "train_accuracy": train_acc,
    "accuracy": train_acc,  # alias for backward-compat with tests
    "notes": "Model trained; evaluate.py will add test metrics."
}
    json.dump(metrics, open(paths["metrics_path"], "w"))
    print(f"Saved model to {paths['model_path']}; train_accuracy={train_acc:.4f}")


if __name__ == "__main__":
    main()