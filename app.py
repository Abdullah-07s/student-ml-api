from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI()

def get_version():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    version_path = os.path.join(base_dir, "VERSION")
    with open(version_path) as f:
        return f.read().strip()

class PredictRequest(BaseModel):
    value: int  

MODEL_VERSION = "model-1" 

@app.get("/health")
def health():
    return {"status": "healthy","application": "student-ml-api","application_version": get_version(),"model_version": MODEL_VERSION}


@app.post("/predict")
def predict(request: PredictRequest):
    return {"input": request.value, "prediction": request.value*2 }  