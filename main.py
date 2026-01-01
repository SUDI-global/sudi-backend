from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import psycopg2
from psycopg2.extras import RealDictCursor
import secrets
import os

app = FastAPI(title="SUDI Professional Dashboard")
security = HTTPBasic()

# --- إعدادات الحماية (يمكنك تعديلها) ---
ADMIN_USER = "sudi_admin"
ADMIN_PASS = "Sudi2050$"  # هذه هي كلمة المرور الخاصة بك

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "postgresql://sudi_db_user:tpEGp4DxfWIBF2x3wpBqWoSEeD3yaBEp@dpg-d5af942li9vc73b5e0a0-a/sudi_db"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# دالة التحقق من الهوية
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    is_user_ok = secrets.compare_digest(credentials.username, ADMIN_USER)
    is_pass_ok = secrets.compare_digest(credentials.password, ADMIN_PASS)
    if not (is_user_ok and is_pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="اسم المستخدم أو كلمة المرور غير صحيحة",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# إنشاء الجدول
conn = get_db_connection()
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS leads 
               (id SERIAL PRIMARY KEY, name TEXT, phone TEXT, service TEXT, message TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()
cur.close()
conn.close()

class Lead(BaseModel):
    name: str
    phone: str
    service: str
    message: str

@app.get("/")
def root():
    return {"status": "ok", "message": "SUDI Protected API running"}

@app.post("/submit")
def create_lead(lead: Lead):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO leads (name, phone, service, message) VALUES (%s, %s, %s, %s)', 
                (lead.name, lead.phone, lead.service, lead.message))
    conn.commit()
    cur.close()
    conn.close()
    return {"ok": True}

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def dashboard(username: str = Depends(authenticate)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM leads ORDER BY date DESC')
    leads = cur.fetchall()
    cur.close()
    conn.close()
    
    rows = "".join([f"<tr><td>{l['name']}</td><td>{l['phone']}</td><td>{l['service']}</td><td>{l['date']}</td></tr>" for l in leads])
    
    return f"""
    <html>
        <head><title>SUDI Admin Pro</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; padding: 40px; text-align: right; }}
            h2 {{ color: #333; text-align: center; }}
            table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 0 20px rgba(0,0,0,0.1); margin-top: 20px; }}
            th, td {{ padding: 15px; text-align: right; border-bottom: 1px solid #eee; }}
            th {{ background: #daa520; color: white; }}
            .container {{ max-width: 1000px; margin: auto; }}
            .logout {{ text-align: left; margin-bottom: 10px; }}
        </style>
        </head>
        <body dir='rtl'>
            <div class='container'>
                <h2>لوحة تحكم سودي (مؤمنة برمز دخول)</h2>
                <p>مرحباً بك: {username}</p>
                <table>
                    <tr><th>الاسم</th><th>الجوال</th><th>الخدمة</th><th>التاريخ</th></tr>
                    {rows}
                </table>
            </div>
        </body>
    </html>
    """
