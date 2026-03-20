import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Імпортуємо наші функції для БД
# Якщо запускаєш через 'uvicorn backend.main:app', використовуй .database
from backend.database import get_db_connection, init_db

load_dotenv()
app = FastAPI(title="IT Support System API")

# Ініціалізація БД при старті
@app.on_event("startup")
async def startup_event():
    init_db()

class Ticket(BaseModel):
    hostname: str
    username: str
    ip_address: str
    ping_status: str
    registry_category: str
    problem_description: str
    screenshot_path: Optional[str] = None

# Перевірка безпеки
API_KEY = os.getenv("API_KEY")

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

@app.post("/api/tickets")
async def create_ticket(ticket: Ticket, _ = Depends(verify_api_key)):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO support_tickets 
            (hostname, username, ip_address, ping_status, registry_category, problem_description, screenshot_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (ticket.hostname, ticket.username, ticket.ip_address, ticket.ping_status,
              ticket.registry_category, ticket.problem_description, ticket.screenshot_path))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/admin/ticket/{ticket_id}", response_class=HTMLResponse)
async def view_ticket_details(ticket_id: int):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM support_tickets WHERE id = %s", (ticket_id,))
        t = cur.fetchone()
        cur.close()
        conn.close()

        if not t:
            return "<h1>Заявку не знайдено</h1>"

        return f"""
        <html>
            <head>
                <title>Деталі заявки #{t['id']}</title>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
            </head>
            <body class="container mt-5">
                <a href="/admin" class="btn btn-secondary mb-3">⬅ Назад до списку</a>
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h3>Заявка #{t['id']} від {t['username']}</h3>
                    </div>
                    <div class="card-body">
                        <p><strong>Хост:</strong> {t['hostname']} ({t['ip_address']})</p>
                        <p><strong>Система:</strong> {t['registry_category']}</p>
                        <p><strong>Час створення:</strong> {t['created_at']}</p>
                        <hr>
                        <h5>Опис проблеми:</h5>
                        <p class="border p-3 bg-light">{t['problem_description']}</p>
                        <hr>
                        <h5>Результати діагностики (Ping):</h5>
                        <pre class="bg-dark text-success p-3">{t['ping_status']}</pre>
                        <hr>
                        <h5>Шлях до скріншота:</h5>
                        <code>{t['screenshot_path'] if t['screenshot_path'] else "Відсутній"}</code>
                    </div>
                </div>
            </body>
        </html>
        """
    except ConnectionError as e:
        return f"<h1>Помилка: {e}</h1>"

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM support_tickets ORDER BY id DESC")
        tickets = cur.fetchall()
        cur.close()
        conn.close()

        rows = ""
        for t in tickets:
            # Обрізаємо довгий опис для таблиці
            short_desc = (t['problem_description'][:50] + '...') if len(t['problem_description']) > 50 else t['problem_description']
            rows += f"""
            <tr>
                <td>{t['id']}</td>
                <td>{t['hostname']}</td>
                <td>{t['username']}</td>
                <td><span class="badge bg-info text-dark">{t['registry_category']}</span></td>
                <td>{short_desc}</td>
                <td>
                    <a href="/admin/ticket/{t['id']}" class="btn btn-sm btn-primary">Відкрити</a>
                </td>
            </tr>
            """

        return f"""
        <html>
            <head>
                <title>Admin Panel</title>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
            </head>
            <body class="container mt-5">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2>📋 Панель адміністратора техпідтримки</h2>
                    <span class="badge bg-secondary">Всього заявок: {len(tickets)}</span>
                </div>
                <table class="table table-hover shadow-sm">
                    <thead class="table-dark">
                        <tr>
                            <th>ID</th>
                            <th>Хост</th>
                            <th>Користувач</th>
                            <th>Система</th>
                            <th>Опис</th>
                            <th>Дії</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
            </body>
        </html>
        """
    except ConnectionError as e:
        return f"<h1>Помилка БД: {e}</h1>"
    