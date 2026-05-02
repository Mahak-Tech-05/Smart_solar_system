import tkinter as tk
from tkinter import ttk
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests

# ---------- DATABASE ----------
conn = sqlite3.connect('solar_data.db')

def load_data():
    query = "SELECT * FROM solar_data ORDER BY id DESC LIMIT 50"
    df = pd.read_sql_query(query, conn)
    return df[::-1]

# ---------- REAL TEMP (INDORE) ----------
def get_real_temperature():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=22.72&longitude=75.86&current_weather=true"
        data = requests.get(url, timeout=3).json()
        return float(data["current_weather"]["temperature"])
    except:
        return None

# ---------- WINDOW ----------
root = tk.Tk()
root.title("Smart Solar Dashboard")
root.geometry("1280x820")
root.configure(bg="#0f172a")

# ---------- SCROLL SYSTEM ----------
container = tk.Frame(root, bg="#0f172a")
container.pack(fill="both", expand=True)

canvas = tk.Canvas(container, bg="#0f172a", highlightthickness=0)
scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)

scroll_frame = tk.Frame(canvas, bg="#0f172a")

scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# ---------- MOUSE SCROLL ----------
def on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

def on_linux_scroll_up(event):
    canvas.yview_scroll(-1, "units")

def on_linux_scroll_down(event):
    canvas.yview_scroll(1, "units")

canvas.bind_all("<MouseWheel>", on_mousewheel)   # Windows / Mac
canvas.bind_all("<Button-4>", on_linux_scroll_up)   # Linux scroll up
canvas.bind_all("<Button-5>", on_linux_scroll_down) # Linux scroll down

# ---------- MAIN ----------
main = tk.Frame(scroll_frame, bg="#0f172a")
main.pack(fill="both", expand=True, padx=20, pady=20)

# ---------- HEADER ----------
tk.Label(main, text="🌞 Smart Solar Dashboard",
         font=("Segoe UI", 26, "bold"),
         fg="#38bdf8", bg="#0f172a").pack(pady=10)

# ---------- CARDS ----------
card_frame = tk.Frame(main, bg="#0f172a")
card_frame.pack(fill="x", pady=20)

def create_card(title):
    frame = tk.Frame(card_frame, bg="#1e293b", padx=20, pady=20)
    tk.Label(frame, text=title, fg="#94a3b8", bg="#1e293b").pack()
    value = tk.Label(frame, text="--", fg="#22d3ee", bg="#1e293b",
                     font=("Segoe UI", 20, "bold"))
    value.pack()
    frame.pack(side="left", expand=True, fill="both", padx=10)
    return value

ldr_val = create_card("LDR (L | R)")
temp_val = create_card("Temperature °C (Live)")
volt_val = create_card("Voltage V")

# ---------- GRAPH ----------
graph_frame = tk.Frame(main, bg="#0f172a")
graph_frame.pack(fill="both", expand=True)

fig_v, ax_v = plt.subplots()
fig_t, ax_t = plt.subplots()

fig_v.patch.set_facecolor("#0f172a")
fig_t.patch.set_facecolor("#0f172a")

canvas_v = FigureCanvasTkAgg(fig_v, master=graph_frame)
canvas_v.get_tk_widget().pack(side="left", fill="both", expand=True)

canvas_t = FigureCanvasTkAgg(fig_t, master=graph_frame)
canvas_t.get_tk_widget().pack(side="left", fill="both", expand=True)

# ---------- TABLE ----------
table_frame = tk.Frame(main, bg="#0f172a")
table_frame.pack(fill="both", expand=True, pady=20)

scroll_y = tk.Scrollbar(table_frame, orient="vertical")
scroll_x = tk.Scrollbar(table_frame, orient="horizontal")

table = ttk.Treeview(
    table_frame,
    columns=("Time","L","R","Temp","Volt"),
    show="headings",
    yscrollcommand=scroll_y.set,
    xscrollcommand=scroll_x.set
)

scroll_y.config(command=table.yview)
scroll_x.config(command=table.xview)

scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")
table.pack(fill="both", expand=True)

for col in ("Time","L","R","Temp","Volt"):
    table.heading(col, text=col)
    table.column(col, anchor="center", width=120)

table.column("Time", width=220)

# ---------- UPDATE ----------
def update_dashboard():
    df = load_data()

    if not df.empty:
        latest = df.iloc[-1]

        # 🌍 Real temperature
        real_temp = get_real_temperature()
        if real_temp is None:
            real_temp = latest['temperature']

        # 🎨 Color logic
        if real_temp > 35:
            temp_color = "#ef4444"
        elif real_temp < 20:
            temp_color = "#3b82f6"
        else:
            temp_color = "#22d3ee"

        # Update cards
        ldr_val.config(text=f"{latest['ldr_left']} | {latest['ldr_right']}")
        temp_val.config(text=f"{real_temp:.2f}", fg=temp_color)
        volt_val.config(text=f"{latest['voltage']:.2f}")

        # Table
        for row in table.get_children():
            table.delete(row)

        for _, row in df.iterrows():
            table.insert("", "end", values=(
                row["timestamp"],
                row["ldr_left"],
                row["ldr_right"],
                round(row["temperature"],2),
                round(row["voltage"],2)
            ))

        # Graphs
        ax_v.clear()
        ax_t.clear()

        ax_v.plot(df["voltage"], color="#60a5fa")
        ax_v.set_title("Voltage", color="white")

        ax_t.plot([real_temp]*len(df), color=temp_color)
        ax_t.set_title("Real Temperature", color="white")

        for ax in (ax_v, ax_t):
            ax.set_facecolor("#0f172a")
            ax.tick_params(colors='white')

        canvas_v.draw()
        canvas_t.draw()

    root.after(3000, update_dashboard)

# ---------- START ----------
update_dashboard()
root.mainloop()
