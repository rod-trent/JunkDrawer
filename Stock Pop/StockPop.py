# StockPop.py - FINAL ULTIMATE - NOW WITH GROK TRADING RECOMMENDATIONS
import json, os, threading, queue
from pathlib import Path
import yfinance as yf
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
from plyer import notification
import tkinter as tk
from tkinter import messagebox

APP_NAME = "Stock Pop - powered by Grok"

load_dotenv()
XAI_API_KEY = os.getenv('XAI_API_KEY')
if not XAI_API_KEY:
    messagebox.showerror("Error", "Add XAI_API_KEY to .env file")
    exit()

client = OpenAI(base_url="https://api.x.ai/v1", api_key=XAI_API_KEY)
MODEL = "grok-4"

CONFIG_FILE = Path("stock_config.json")
config = {"tickers": [], "threshold": 2.0}
last_prices = {}
gui_queue = queue.Queue()

def load_config():
    global config
    if CONFIG_FILE.exists():
        try: config.update(json.load(open(CONFIG_FILE)))
        except: pass

def save_config():
    CONFIG_FILE.write_text(json.dumps(config, indent=4))

def fetch_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period="1d", interval="1m")
        return round(data["Close"].iloc[-1], 4) if not data.empty else None
    except: return None

# GROK TRADING RECOMMENDATION ENGINE
def get_grok_recommendation(ticker, change_pct):
    direction = "up" if change_pct > 0 else "down"
    prompt = f"""
    You are an elite quantitative trader. {ticker} just moved {change_pct:+.2f}% in minutes.
    Current time: {tk.datetime.now().strftime('%b %d, %H:%M')}.
    Give me ONE of these exact signals: Strong Buy / Buy / Hold / Sell / Strong Sell
    Then one brutally honest sentence why.
    Example: Strong Buy → Momentum breakout with volume surge, likely continues.
    """
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=70,
            temperature=0.4
        )
        return resp.choices[0].message.content.strip()
    except:
        return "Hold → Grok offline"

def check_stocks():
    if not config["tickers"]:
        threading.Timer(60, check_stocks).start()
        return
    for ticker in config["tickers"]:
        cur = fetch_price(ticker)
        if not cur: continue
        last = last_prices.get(ticker)
        if last:
            pct = (cur - last) / last * 100
            if abs(pct) >= config["threshold"]:
                recommendation = get_grok_recommendation(ticker, pct)
                notification.notify(
                    app_name=APP_NAME,
                    title=f"{ticker} • {pct:+.2f}% → {recommendation.split('→')[0].strip()}",
                    message=f"${last:.2f} → ${cur:.2f}\n\n{recommendation.split('→',1)[1].strip() if '→' in recommendation else recommendation}",
                    timeout=25
                )
        last_prices[ticker] = cur
    threading.Timer(60, check_stocks).start()

# CONFIG WINDOW (unchanged except slightly larger for new power)
def show_config_window():
    win = tk.Tk()
    win.title(f"{APP_NAME} • Configuration")
    win.configure(bg="#0d1117")
    win.resizable(False, False)
    win.geometry("620x800")

    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - 310
    y = (win.winfo_screenheight() // 2) - 400
    win.geometry(f"+{x}+{y}")

    tk.Label(win, text=APP_NAME, font=("Segoe UI", 26, "bold"), fg="#00ff41", bg="#0d1117").pack(pady=(40, 10))
    tk.Label(win, text="AI trading signals on every pop", fg="#cccccc", bg="#0d1117", font=("Segoe UI", 11)).pack(pady=(0, 40))

    tk.Label(win, text="Alert threshold (% change):", fg="white", bg="#0d1117", font=("Segoe UI", 12)).pack(anchor="w", padx=120)
    threshold_var = tk.DoubleVar(value=config.get("threshold", 2.0))
    tk.Spinbox(win, from_=0.1, to=50, increment=0.1, textvariable=threshold_var,
               font=("Consolas", 16), width=12, bg="#1e1e1e", fg="#00ff41").pack(pady=15)

    tk.Label(win, text="Stocks to monitor (one per line, max 5):", fg="white", bg="#0d1117", font=("Segoe UI", 12)).pack(anchor="w", padx=120, pady=(40, 10))
    text_box = tk.Text(win, height=11, width=36, font=("Consolas", 16), bg="#1e1e1e", fg="#00ff41", insertbackground="white")
    text_box.pack(padx=120, pady=5)
    text_box.insert("1.0", "\n".join(config.get("tickers", [])))
    text_box.bind("<Return>", lambda e: (text_box.insert(tk.INSERT, "\n"), "break")[1])

    def save():
        try:
            threshold = float(threshold_var.get())
            if not 0.1 <= threshold <= 50: raise ValueError
        except:
            messagebox.showerror("Error", "Threshold must be 0.1–50")
            return
        tickers = [t.strip().upper() for t in text_box.get("1.0","end").splitlines() if t.strip()][:5]
        config["tickers"] = tickers
        config["threshold"] = threshold
        save_config()
        last_prices.clear()
        messagebox.showinfo("Saved", f"Watching {len(tickers)} stock(s)\nThreshold: ±{threshold}%\nGrok signals active")
        win.destroy()
        if tickers: threading.Thread(target=check_stocks, daemon=True).start()

    bottom_frame = tk.Frame(win, bg="#0d1117")
    bottom_frame.pack(side="bottom", pady=70)

    tk.Button(bottom_frame,
              text="SAVE & CLOSE",
              font=("Segoe UI", 22, "bold"),
              bg="#00ff41", fg="black",
              activebackground="#00cc00", activeforeground="white",
              width=26, height=3,
              relief="raised", bd=12,
              command=save).pack()

    win.bind("<Return>", lambda e: save())
    win.bind("<Escape>", lambda e: win.destroy())
    win.mainloop()

# TRAY ICON
def create_icon():
    img = Image.new("RGB", (64,64), "black")
    d = ImageDraw.Draw(img)
    d.ellipse((8,8,56,56), fill="#00ff41")
    d.text((15,10), "POP", fill="black", font_size=26)
    return img

def open_config(): gui_queue.put("open")
def quit_app(icon,_): icon.stop(); os._exit(0)

if __name__ == "__main__":
    load_config()
    menu = pystray.Menu(item("Configure", open_config), item("Quit", quit_app))
    icon = pystray.Icon("StockPop", create_icon(), APP_NAME, menu)

    if config.get("tickers"):
        threading.Thread(target=check_stocks, daemon=True).start()

    threading.Thread(target=icon.run, daemon=True).start()

    while True:
        try:
            if gui_queue.get(timeout=0.1) == "open":
                show_config_window()
        except queue.Empty:
            pass