from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="SUDI API", version="1.0")

class Lead(BaseModel):
    name: str
    phone: str
    service: str
    message: str

@app.get("/")
def root():
    return {"status": "ok", "message": "SUDI API running"}

@app.post("/api/leads")
def create_lead(lead: Lead):
    return {
        "ok": True,
        "received": lead
    }
