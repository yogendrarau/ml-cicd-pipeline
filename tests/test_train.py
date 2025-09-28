import json, os, shutil
from pathlib import Path
import subprocess

def test_training_produces_artifacts(tmp_path):
    
    env = os.environ.copy()
    env["GITHUB_SHA"] = "testsha"
    subprocess.check_call(["python", "src/train.py"], env=env)
    assert Path("artifacts/model.pkl").exists()
    assert Path("artifacts/metrics.json").exists()
    m = json.load(open("artifacts/metrics.json"))
    assert "accuracy" in m
    
    shutil.rmtree("artifacts", ignore_errors=True)