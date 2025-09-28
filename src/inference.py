from pathlib import Path
import joblib

_MODEL = None

def load_model(path: str = "configs/train.yaml"):
    import yaml
    cfg = yaml.safe_load(open(path))
    model_path = cfg["paths"]["model_path"]
    if not Path(model_path).exists():
        raise FileNotFoundError(f"Model not found at {model_path}. Run src/train.py first.")
    global _MODEL
    if _MODEL is None:
        _MODEL = joblib.load(model_path)
    return _MODEL

def predict_one(features):
    """
    features: list[float] of length 4 for iris
    returns: int (class id)
    """
    model = load_model()
    return int(model.predict([features])[0])