import tkinter as tk
from tkinter import ttk
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------- DATABASE ----------
conn = sqlite3.connect('solar_data.db')

def load_data():
    query = "SELECT * FROM solar_data ORDER BY id DESC LIMIT 50"
    df = pd.read_sql_query(query, conn)
    return df[::-1]

# ---------- WINDOW ----------
root = tk.Tk()
root.title("Smart Solar Dashboard")
root.geometry("1280x820")

# ---------- SCROLLABLE MAIN ----------
container = tk.Frame(root)
container.pack(fill="both", expand=True)

canvas = tk.Canvas(container)
scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)

scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# ---------- MOUSE SCROLL ----------
def enable_mouse_scroll(widget):
    widget.bind_all("<MouseWheel>", lambda e: widget.yview_scroll(int(-1*(e.delta/120)), "units"))
    widget.bind_all("<Button-4>", lambda e: widget.yview_scroll(-1, "units"))
    widget.bind_all("<Button-5>", lambda e: widget.yview_scroll(1, "units"))

enable_mouse_scroll(canvas)

# ---------- MAIN ----------
main = tk.Frame(scrollable_frame)
main.pack(fill="both", expand=True, padx=20, pady=20)

# ---------- HEADER ----------
title = tk.Label(main, text="🌞 Smart Solar Dashboard",
                 font=("Arial", 26, "bold"))
title.pack()

# ---------- CARDS ----------
card_frame = tk.Frame(main)
card_frame.pack(fill="x", pady=20)

def create_card(title):
    frame = tk.Frame(card_frame, bg="#222", padx=20, pady=20)
    label = tk.Label(frame, text=title, fg="white", bg="#222")
    label.pack()
    value = tk.Label(frame, text="--", fg="cyan", bg="#222",
                     font=("Arial", 20, "bold"))
    value.pack()
    frame.pack(side="left", expand=True, fill="both", padx=10)
    return value

ldr_val = create_card("LDR (L | R)")
temp_val = create_card("Temperature °C")
volt_val = create_card("Voltage V")

# ---------- GRAPH ----------
graph_frame = tk.Frame(main)
graph_frame.pack(fill="both", expand=True)

fig_v, ax_v = plt.subplots()
fig_t, ax_t = plt.subplots()

canvas_v = FigureCanvasTkAgg(fig_v, master=graph_frame)
canvas_v.get_tk_widget().pack(side="left", fill="both", expand=True)

canvas_t = FigureCanvasTkAgg(fig_t, master=graph_frame)
canvas_t.get_tk_widget().pack(side="left", fill="both", expand=True)

# ---------- TABLE ----------
table_frame = tk.Frame(main)
table_frame.pack(fill="both", expand=True, pady=10)

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

columns = ("Time", "LDR Left", "LDR Right", "Temperature", "Voltage")
for key, col in zip(("Time","L","R","Temp","Volt"), columns):
    table.heading(key, text=col)
    table.column(key, anchor="center", width=120)

table.column("Time", width=220)

# ---------- UPDATE ----------
def update_dashboard():
    df = load_data()

    if not df.empty:
        latest = df.iloc[-1]

        ldr_val.config(text=f"{latest['ldr_left']} | {latest['ldr_right']}")
        temp_val.config(text=f"{latest['temperature']:.2f}")
        volt_val.config(text=f"{latest['voltage']:.2f}")

        # Clear table
        for row in table.get_children():
            table.delete(row)

        # Insert data
        for _, row in df.iterrows():
            table.insert("", "end", values=(
                row["timestamp"],
                row["ldr_left"],
                row["ldr_right"],
                round(row["temperature"],2),
                round(row["voltage"],2)
            ))

        # Graph update
        ax_v.clear()
        ax_t.clear()

        ax_v.plot(df["voltage"])
        ax_v.set_title("Voltage")

        ax_t.plot(df["temperature"])
        ax_t.set_title("Temperature")

        canvas_v.draw()
        canvas_t.draw()

    root.after(2000, update_dashboard)

# ---------- START ----------
update_dashboard()
root.mainloop()
