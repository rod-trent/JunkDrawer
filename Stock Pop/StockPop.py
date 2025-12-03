# StockPop.py – FINAL WORKING VERSION (December 2025)
# Real Windows toasts + persistent tray icon + working Config menu

import json
import os
import threading
import queue
import logging
from pathlib import Path
import datetime
import yfinance as yf
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import tkinter as tk
from tkinter import messagebox

# ------------------- WINDOWS TOASTS (RELIABLE 2025) -------------------
try:
    from windows_toasts import Toast, WindowsToaster
    toaster = WindowsToaster('StockPop')
    def send_toast(title: str, body: str):
        t = Toast()
        t.text_fields = [title, body]
        toaster.show_toast(t)
    logging.info("Using windows_toasts → perfect notifications")
except ImportError:
    send_toast = None
    logging.warning("windows_toasts not found → pip install windows-toasts")

# Thread-safe queue for GUI & notifications
gui_queue = queue.Queue()

def show_notification(title: str, message: str):
    title = str(title)[:100]
    message = str(message)[:500].replace('\n', ' | ')
    gui_queue.put(('toast', title, message))

def open_config_menu():
    gui_queue.put(('config',))

# ------------------- APP SETUP -------------------
APP_NAME = "StockPop • Grok Signals"
logging.basicConfig(level=logging.INFO, format="%(H:%M:%S) %(message)s")

load_dotenv()
XAI_API_KEY = os.getenv('XAI_API_KEY')
if not XAI_API_KEY:
    messagebox.showerror("Error", "Add XAI_API_KEY to .env file")
    exit()

client = OpenAI(base_url="https://api.x.ai/v1", api_key=XAI_API_KEY)
MODEL = "grok-4"

CONFIG_FILE = Path("stock_config.json")
config = {"tickers": ["MSFT", "NVDA"], "threshold": 1.0}
last_prices = {}

def load_config():
    global config
    if CONFIG_FILE.exists():
        try:
            loaded = json.load(open(CONFIG_FILE))
            config.update(loaded)
        except Exception as e:
            logging.error(f"Config error: {e}")
    logging.info(f"Loaded {len(config['tickers'])} tickers @ ±{config['threshold']}%")

def save_config():
    try:
        CONFIG_FILE.write_text(json.dumps(config, indent=4))
    except: pass

# ------------------- PRICE FETCHING -------------------
def fetch_price(ticker):
    try:
        t = yf.Ticker(ticker.upper())
        data = t.history(period="1d", interval="1m")
        if not data.empty:
            return round(data["Close"].iloc[-1], 4)
        price = t.fast_info.get("lastPrice") or t.info.get("regularMarketPrice")
        if price:
            return round(float(price), 4)
    except Exception as e:
        logging.debug(f"Fetch failed {ticker}: {e}")
    return None

# ------------------- GROK RECOMMENDATION -------------------
def get_grok_recommendation(ticker, pct):
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": f"{ticker} moved {pct:+.2f}%. Signal → reason."}],
            max_tokens=70,
            temperature=0.4
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Grok error: {e}")
        return "Hold → Check connection"

# ------------------- STOCK MONITOR LOOP -------------------
def check_stocks():
    for ticker in config["tickers"]:
        ticker = ticker.strip().upper()
        if not ticker: continue

        cur = fetch_price(ticker)
        if not cur: continue

        last = last_prices.get(ticker)
        if last and last > 0:
            pct = (cur - last) / last * 100
            if abs(pct) >= config["threshold"]:
                rec = get_grok_recommendation(ticker, pct)
                signal = rec.split("→")[0].strip() if "→" in rec else "Hold"
                direction = "UP" if pct > 0 else "DOWN"
                title = f"{ticker} {pct:+.2f}% {direction} → {signal}"
                body = f"${last:.2f} → ${cur:.2f} | {rec}"
                logging.info(f"ALERT: {title}")
                show_notification(title, body)

        last_prices[ticker] = cur

    threading.Timer(30, check_stocks).start()

# ------------------- CONFIG GUI -------------------
def show_config_window():
    win = tk.Tk()
    win.title(f"{APP_NAME} • Config")
    win.configure(bg="#0d1117")
    win.resizable(False, False)
    win.geometry("680x860")
    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - 340
    y = (win.winfo_screenheight() // 2) - 430
    win.geometry(f"+{x}+{y}")

    tk.Label(win, text="StockPop", font=("Segoe UI", 30, "bold"), fg="#00ff41", bg="#0d1117").pack(pady=(40,5))
    tk.Label(win, text="Grok-Powered Pop Alerts", fg="#aaa", bg="#0d1117").pack(pady=(0,30))

    tk.Label(win, text="Alert Threshold (%):", fg="white", bg="#0d1117").pack(anchor="w", padx=150)
    thresh_var = tk.DoubleVar(value=config.get("threshold", 1.0))
    tk.Spinbox(win, from_=0.1, to=20, increment=0.1, textvariable=thresh_var,
               font=("Consolas", 18), width=10, bg="#1e1e1e", fg="#00ff41").pack(pady=10)

    tk.Label(win, text="Tickers (one per line, max 10):", fg="white", bg="#0d1117").pack(anchor="w", padx=150, pady=(30,5))
    txt = tk.Text(win, height=12, width=40, font=("Consolas", 16), bg="#1e1e1e", fg="#00ff41", insertbackground="white")
    txt.pack(padx=150, pady=5)
    txt.insert("1.0", "\n".join(config.get("tickers", [])))

    def save():
        try:
            threshold = float(thresh_var.get())
        except:
            messagebox.showerror("Error", "Invalid threshold")
            return
        tickers = [t.strip().upper() for t in txt.get("1.0","end-1c").splitlines() if t.strip()][:10]
        config["tickers"] = tickers
        config["threshold"] = threshold
        save_config()
        last_prices.clear()
        messagebox.showinfo("Saved", f"Now watching {len(tickers)} tickers @ ±{threshold}%")
        win.destroy()

    tk.Button(win, text="SAVE & RESTART", command=save,
              font=("Segoe UI", 20, "bold"), bg="#00ff41", fg="black", width=30, height=2).pack(pady=60)

    def test():
        show_notification("Test Alert", "Notifications are working perfectly!")

    tk.Button(win, text="TEST TOAST", command=test, bg="#ff5500", fg="white").pack(pady=10)

    win.bind("<Return>", lambda e: save())
    win.bind("<Escape>", lambda e: win.destroy())
    win.mainloop()

# ------------------- TRAY ICON -------------------
def create_icon():
    img = Image.new("RGB", (64,64), "black")
    d = ImageDraw.Draw(img)
    d.ellipse((8,8,56,56), fill="#00ff41")
    d.text((18,16), "POP", fill="black", font=None)
    return img

# ------------------- MAIN – KEEPS ALIVE + PROCESSES QUEUE -------------------
if __name__ == "__main__":
    load_config()
    save_config()

    # Startup notification
    if send_toast:
        send_toast("StockPop Started", f"Watching {len(config['tickers'])} tickers @ ±{config['threshold']}%")

    # Start monitoring
    if config.get("tickers"):
        threading.Thread(target=check_stocks, daemon=True).start()

    # Tray icon
    icon = pystray.Icon(
        "StockPop",
        create_icon(),
        APP_NAME,
        menu=pystray.Menu(
            item("Configure", open_config_menu),
            item("Quit", lambda: icon.stop())
        )
    )
    threading.Thread(target=icon.run, daemon=True).start()

    # MAIN LOOP – This keeps the app alive and handles toasts + config
    try:
        while True:
            try:
                msg = gui_queue.get(timeout=1)
                if msg[0] == 'toast' and send_toast:
                    send_toast(msg[1], msg[2])
                elif msg[0] == 'config':
                    show_config_window()
            except queue.Empty:
                pass
    except KeyboardInterrupt:
        icon.stop()