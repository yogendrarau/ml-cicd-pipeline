from fastapi import FastAPI
from pydantic import BaseModel
from src.inference import predict_one, load_model

app = FastAPI(title="ML CI/CD Demo", version="1.0.0")

class IrisFeatures(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.on_event("startup")
def warm_model():
    try:
        load_model()  # best-effort warmup
    except Exception:
        pass

@app.post("/predict")
def predict(x: IrisFeatures):
    feats = [x.sepal_length, x.sepal_width, x.petal_length, x.petal_width]
    pred = predict_one(feats)
    return {"prediction": pred}