import tkinter as tk
from tkinter import messagebox
import socket
import os
import requests
import threading
import subprocess  
import platform
import psutil
from datetime import datetime
from PIL import ImageGrab

API_URL = "http://127.0.0.1:8000/api/tickets"
API_KEY = "super-secret-key-123"

class DiagnosticModule:
    @staticmethod
    def get_network_diagnostics():
        """Перевірка доступності ключових вузлів."""
        targets = {
            "Локальний шлюз": "192.168.1.1",
            "Google DNS": "8.8.8.8",
            "Сервер БД": "127.0.0.1"
        }
        results = []
        for name, host in targets.items():
            # Використовуємо -n 1 для Windows
            param = "-n" if platform.system().lower() == "windows" else "-c"
            command = ["ping", param, "1", "-w", "1000", host]
            is_up = subprocess.run(command, capture_output=True, creationflags=0x08000000).returncode == 0
            status = "OK" if is_up else "FAIL"
            results.append(f"{name} ({host}): {status}")
        return "\n".join(results)

    @staticmethod
    def get_system_resources():
        """Збір даних про навантаження системи."""
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return (f"CPU: {cpu_usage}%\n"
                f"RAM: {ram.percent}% (Вільна: {ram.available // (1024**2)} MB)\n"
                f"Disk: {disk.percent}% вільний")
    
def get_system_info(): # 
    hostname = socket.gethostname()
    username = os.getlogin()
    try:
        ip = socket.gethostbyname(hostname)
    except:
        ip = "127.0.0.1"
    return hostname, username, ip

def send_to_api(data):
    headers = {"x-api-key": API_KEY}
    try:
        response = requests.post(API_URL, json=data, headers=headers, timeout=10)
        return response.status_code == 200, response.text
    except Exception as e:
        return False, str(e)

def generation_task(desc, reg, need_screen, wait_win):
    host, user, ip = get_system_info() # 
    
    # Запуск діагностики
    diag = DiagnosticModule()
    ping_results = diag.get_network_diagnostics()
    sys_res = diag.get_system_resources()
    
    full_diagnostic_report = f"--- Network ---\n{ping_results}\n\n--- Resources ---\n{sys_res}"

    # Скріншот
    screen_path = None
    if need_screen:
        save_dir = "Reports"
        if not os.path.exists(save_dir): os.makedirs(save_dir)
        screen_path = os.path.join(save_dir, f"report_{datetime.now().strftime('%H%M%S')}.png")
        ImageGrab.grab().save(screen_path) # 

    payload = {
        "hostname": host,
        "username": user,
        "ip_address": ip,
        "ping_status": full_diagnostic_report, # Відправляємо розширений звіт
        "registry_category": reg,
        "problem_description": desc,
        "screenshot_path": screen_path
    }

    success, msg = send_to_api(payload)
    wait_win.destroy()
    
    if success:
        messagebox.showinfo("Успіх", "Діагностику проведено, заявку відправлено!")
    else:
        messagebox.showerror("Помилка", f"Сервер відхилив запит: {msg}")

def start_flow():
    desc = problem_text.get("1.0", tk.END).strip()
    if not desc: return messagebox.showwarning("Увага", "Опишіть проблему!")
    
    wait_window = tk.Toplevel(root)
    tk.Label(wait_window, text="Відправка на сервер...", padx=20, pady=20).pack()
    
    threading.Thread(target=generation_task, args=(desc, reg_var.get(), screen_var.get(), wait_window)).start()

# GUI Setup 
root = tk.Tk()
root.title("IT Support v2.0")
root.geometry("400x500")

tk.Label(root, text="Опис проблеми:").pack(pady=5)
problem_text = tk.Text(root, height=10)
problem_text.pack(padx=10, fill=tk.X)

reg_var = tk.StringVar(value="Інше")
tk.OptionMenu(root, reg_var, "ЄДДР", "Відомості", "РТГ", "Інше").pack(pady=5)

screen_var = tk.BooleanVar()
tk.Checkbutton(root, text="Додати скріншот", variable=screen_var).pack()

tk.Button(root, text="ВІДПРАВИТИ", command=start_flow, bg="green", fg="white").pack(pady=20)

root.mainloop()