import tkinter as tk
from tkinter import ttk
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import warnings

# 🔇 Remove warnings
warnings.filterwarnings("ignore")

# ---------- DATABASE ----------
conn = sqlite3.connect('solar_data.db')

def load_data():
    query = "SELECT * FROM solar_data ORDER BY id DESC LIMIT 50"
    df = pd.read_sql_query(query, conn)
    df = df[::-1]
    return df

# ---------- WINDOW ----------
root = tk.Tk()
root.title("Smart Solar Dashboard")
root.geometry("1100x700")
root.configure(bg="#0f172a")

# ---------- HEADER ----------
header = tk.Label(root, text="Smart Solar Tracking Dashboard",
                  font=("Segoe UI", 22, "bold"),
                  fg="#38bdf8", bg="#0f172a")
header.pack(pady=10)

# ---------- CARDS ----------
card_frame = tk.Frame(root, bg="#0f172a")
card_frame.pack(pady=10)

def create_card(parent, title):
    frame = tk.Frame(parent, bg="#1e293b", padx=20, pady=15)
    title_label = tk.Label(frame, text=title, fg="#94a3b8",
                           bg="#1e293b", font=("Segoe UI", 10))
    value_label = tk.Label(frame, text="--", fg="white",
                           bg="#1e293b", font=("Segoe UI", 16, "bold"))
    title_label.pack()
    value_label.pack()
    return frame, value_label

ldr_card, ldr_val = create_card(card_frame, "LDR")
temp_card, temp_val = create_card(card_frame, "Temperature")
volt_card, volt_val = create_card(card_frame, "Voltage")

ldr_card.grid(row=0, column=0, padx=10)
temp_card.grid(row=0, column=1, padx=10)
volt_card.grid(row=0, column=2, padx=10)

# ---------- GRAPH ----------
fig, ax = plt.subplots(2, 1, figsize=(5, 4))
fig.patch.set_facecolor('#0f172a')

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=10)

# ---------- TABLE ----------
table_frame = tk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=10, pady=10)

tree = ttk.Treeview(table_frame, columns=("Time", "L", "R", "Temp", "Volt"), show='headings')

for col in ("Time", "L", "R", "Temp", "Volt"):
    tree.heading(col, text=col)
    tree.column(col, anchor="center")

tree.pack(fill="both", expand=True)

# ---------- UPDATE ----------
def update_dashboard():
    df = load_data()

    if not df.empty:
        latest = df.iloc[-1]

        # Update cards
        ldr_val.config(text=f"{latest['ldr_left']} | {latest['ldr_right']}")
        temp_val.config(text=f"{latest['temperature']:.2f} °C")
        volt_val.config(text=f"{latest['voltage']:.2f} V")

        # Table update
        for row in tree.get_children():
            tree.delete(row)

        for _, row in df.iterrows():
            tree.insert("", "end", values=(
                row['timestamp'],
                row['ldr_left'],
                row['ldr_right'],
                round(row['temperature'], 2),
                round(row['voltage'], 2)
            ))

        # Graph update
        ax[0].clear()
        ax[1].clear()

        ax[0].plot(df['voltage'])
        ax[0].set_title("Voltage Trend")

        ax[1].plot(df['temperature'])
        ax[1].set_title("Temperature Trend")

        canvas.draw()

    root.after(2000, update_dashboard)

update_dashboard()
root.mainloop()
