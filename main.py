from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI(title="SUDI Dashboard", version="1.1")

# السماح للموقع بالاتصال بالـ Backend
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

def get_db_connection():
    conn = sqlite3.connect('sudi.db')
    conn.row_factory = sqlite3.Row
    return conn

# إنشاء الجدول تلقائياً
with get_db_connection() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS leads 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, service TEXT, message TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

@app.post("/submit")
def create_lead(lead: Lead):
    with get_db_connection() as conn:
        conn.execute('INSERT INTO leads (name, phone, service, message) VALUES (?, ?, ?, ?)', 
                       (lead.name, lead.phone, lead.service, lead.message))
        conn.commit()
    return {"ok": True}

# صفحة لوحة التحكم التي طلبتها
@app.get("/admin/dashboard", response_class=HTMLResponse)
async def dashboard():
    with get_db_connection() as conn:
        leads = conn.execute('SELECT * FROM leads ORDER BY date DESC').fetchall()
    
    rows = "".join([f"<tr><td>{l['name']}</td><td>{l['phone']}</td><td>{l['service']}</td><td>{l['date']}</td></tr>" for l in leads])
    
    return f"""
    <html>
        <head><title>SUDI Admin</title>
        <style>
            body {{ font-family: Arial; padding: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: right; }}
            th {{ background: #daa520; color: white; }}
            tr:nth-child(even) {{ background: #f9f9f9; }}
        </style>
        </head>
        <body dir='rtl'>
            <h2>لوحة تحكم طلبات شركة سودي</h2>
            <table>
                <tr><th>الاسم</th><th>الجوال</th><th>الخدمة</th><th>التاريخ</th></tr>
                {rows}
            </table>
        </body>
    </html>
    """
