from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI(title="SUDI API", version="1.0")

# ضروري جداً لكي يسمح للموقع بالاتصال بالـ Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Lead(BaseModel):
    name: str
    phone: str
    service: str
    message: str

def save_to_db(lead: Lead):
    conn = sqlite3.connect('sudi.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, service TEXT, message TEXT)
    ''')
    cursor.execute('INSERT INTO leads (name, phone, service, message) VALUES (?, ?, ?, ?)', 
                   (lead.name, lead.phone, lead.service, lead.message))
    conn.commit()
    conn.close()

@app.get("/")
def root():
    return {"status": "ok", "message": "SUDI API running"}

@app.post("/submit") # غيرنا المسار ليتوافق مع الرابط في main.js
def create_lead(lead: Lead):
    save_to_db(lead)
    return {"ok": True, "received": lead}
