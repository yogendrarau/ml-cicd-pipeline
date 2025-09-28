import subprocess, time, requests, os
from pathlib import Path

def _ensure_model():
    if not Path("artifacts/model.pkl").exists():
        subprocess.check_call(["python", "src/train.py"])

def test_health_and_predict():
    _ensure_model()
    
    proc = subprocess.Popen(["python", "-m", "uvicorn", "app.main:app", "--port", "8001"])
    time.sleep(1.5)
    try:
        r = requests.get("http://127.0.0.1:8001/healthz", timeout=5)
        assert r.status_code == 200

        body = {"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}
        r2 = requests.post("http://127.0.0.1:8001/predict", json=body, timeout=5)
        assert r2.status_code == 200
        assert "prediction" in r2.json()
    finally:
        proc.terminate()