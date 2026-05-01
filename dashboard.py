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
root.geometry("1280x820")
root.configure(bg="#0b1220")

# ---------- THEME ----------
theme_mode = {"name": "dark"}

THEMES = {
    "dark": {
        "bg_main": "#0b1220",
        "bg_alt": "#0f172a",
        "card_bg": "#132033",
        "card_glow": "#1d3150",
        "accent": "#22d3ee",
        "secondary": "#3b82f6",
        "success": "#10b981",
        "warning": "#f59e0b",
        "text": "#f8fafc",
        "subtext": "#94a3b8",
        "table_row1": "#0f1b2f",
        "table_row2": "#12213a",
    },
    "light": {
        "bg_main": "#e8eef8",
        "bg_alt": "#dbe7f5",
        "card_bg": "#ffffff",
        "card_glow": "#c6d8f2",
        "accent": "#0284c7",
        "secondary": "#2563eb",
        "success": "#059669",
        "warning": "#d97706",
        "text": "#0f172a",
        "subtext": "#334155",
        "table_row1": "#eff6ff",
        "table_row2": "#dbeafe",
    },
}

def c(name):
    return THEMES[theme_mode["name"]][name]

root.option_add("*Font", "Inter 10")

# ---------- MAIN CONTAINER ----------
main = tk.Frame(root, bg=c("bg_main"))
main.pack(fill="both", expand=True, padx=20, pady=20)

# ---------- HEADER ----------
header_frame = tk.Frame(main, bg=c("bg_main"))
header_frame.pack(fill="x", pady=(0, 24))

title = tk.Label(
    header_frame,
    text="🌞 Smart Solar Tracking Dashboard",
    font=("Inter", 28, "bold"),
    fg=c("accent"),
    bg=c("bg_main"),
)
title.pack()

subtitle = tk.Label(
    header_frame,
    text="Real-time Solar Monitoring System",
    font=("Inter", 12),
    fg=c("subtext"),
    bg=c("bg_main"),
)
subtitle.pack(pady=(4, 8))

top_controls = tk.Frame(header_frame, bg=c("bg_main"))
top_controls.pack(fill="x", pady=(2, 0))

live_indicator = tk.Label(
    top_controls, text="● Online", fg=c("success"), bg=c("bg_main"), font=("Inter", 11, "bold")
)
live_indicator.pack(side="left")

def toggle_theme():
    theme_mode["name"] = "light" if theme_mode["name"] == "dark" else "dark"
    apply_theme()

refresh_btn = tk.Button(
    top_controls,
    text="Refresh",
    command=lambda: update_dashboard(force=True),
    bg=c("secondary"),
    fg="white",
    relief="flat",
    padx=12,
    pady=6,
)
refresh_btn.pack(side="right", padx=(8, 0))

theme_btn = tk.Button(
    top_controls,
    text="Dark/Light",
    command=toggle_theme,
    bg=c("card_bg"),
    fg=c("text"),
    relief="flat",
    padx=12,
    pady=6,
)
theme_btn.pack(side="right")

# ---------- CARDS ----------
card_frame = tk.Frame(main, bg=c("bg_main"))
card_frame.pack(fill="x", pady=(0, 24))

def add_hover_effect(frame, base_bg, glow_bg):
    def on_enter(_):
        frame.configure(bg=glow_bg)
    def on_leave(_):
        frame.configure(bg=base_bg)
    frame.bind("<Enter>", on_enter)
    frame.bind("<Leave>", on_leave)

def create_card(parent, icon, title, unit, color_key):
    outer = tk.Frame(parent, bg=c("card_bg"), padx=2, pady=2)
    inner = tk.Frame(outer, bg=c("card_bg"), padx=20, pady=18)
    inner.pack(fill="both", expand=True)

    top = tk.Frame(inner, bg=c("card_bg"))
    top.pack(fill="x")
    tk.Label(top, text=f"{icon}  {title}", fg=c("subtext"), bg=c("card_bg"), font=("Inter", 11, "bold")).pack(side="left")
    tk.Label(top, text=unit, fg=c(color_key), bg=c("card_bg"), font=("Inter", 10)).pack(side="right")

    value_label = tk.Label(inner, text="--", fg=c("text"), bg=c("card_bg"), font=("Inter", 24, "bold"))
    value_label.pack(anchor="w", pady=(10, 0))
    add_hover_effect(outer, c("card_bg"), c("card_glow"))
    return outer, inner, value_label

ldr_card, ldr_inner, ldr_val = create_card(card_frame, "☀️", "LDR", "LEFT | RIGHT", "accent")
temp_card, temp_inner, temp_val = create_card(card_frame, "🌡️", "Temperature", "°C", "warning")
volt_card, volt_inner, volt_val = create_card(card_frame, "⚡", "Voltage", "V", "success")

card_frame.columnconfigure((0, 1, 2), weight=1)
ldr_card.grid(row=0, column=0, padx=8, sticky="ew")
temp_card.grid(row=0, column=1, padx=8, sticky="ew")
volt_card.grid(row=0, column=2, padx=8, sticky="ew")

# ---------- GRAPH ----------
graph_frame = tk.Frame(main, bg=c("bg_main"))
graph_frame.pack(fill="x", pady=(0, 24))
graph_frame.columnconfigure((0, 1), weight=1)

voltage_card = tk.Frame(graph_frame, bg=c("card_bg"), padx=16, pady=16)
temp_card_plot = tk.Frame(graph_frame, bg=c("card_bg"), padx=16, pady=16)
voltage_card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
temp_card_plot.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

fig_v, ax_v = plt.subplots(figsize=(5, 2.6))
fig_t, ax_t = plt.subplots(figsize=(5, 2.6))
canvas_v = FigureCanvasTkAgg(fig_v, master=voltage_card)
canvas_t = FigureCanvasTkAgg(fig_t, master=temp_card_plot)
canvas_v.get_tk_widget().pack(fill="both", expand=True)
canvas_t.get_tk_widget().pack(fill="both", expand=True)

# ---------- TABLE ----------
table_outer = tk.Frame(main, bg=c("card_bg"), padx=16, pady=16)
table_outer.pack(fill="both", expand=True)
table_header = tk.Label(table_outer, text="Recent Sensor Data", font=("Inter", 12, "bold"), fg=c("text"), bg=c("card_bg"))
table_header.pack(anchor="w", pady=(0, 10))

table_frame = tk.Frame(table_outer, bg=c("card_bg"))
table_frame.pack(fill="both", expand=True)
tree = ttk.Treeview(table_frame, columns=("Time", "L", "R", "Temp", "Volt"), show='headings', height=10)
scroll = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
tree.configure(yscroll=scroll.set)
scroll.pack(side="right", fill="y")
tree.pack(fill="both", expand=True)

columns = ("Time", "LDR Left", "LDR Right", "Temperature", "Voltage")
for key, col in zip(("Time", "L", "R", "Temp", "Volt"), columns):
    tree.heading(key, text=col)
    tree.column(key, anchor="center", width=120)
tree.column("Time", width=220)

style = ttk.Style()

def apply_theme():
    root.configure(bg=c("bg_main"))
    main.configure(bg=c("bg_main"))
    header_frame.configure(bg=c("bg_main"))
    title.configure(bg=c("bg_main"), fg=c("accent"))
    subtitle.configure(bg=c("bg_main"), fg=c("subtext"))
    top_controls.configure(bg=c("bg_main"))
    live_indicator.configure(bg=c("bg_main"), fg=c("success"))
    card_frame.configure(bg=c("bg_main"))
    for frame in (ldr_card, temp_card, volt_card, ldr_inner, temp_inner, volt_inner, voltage_card, temp_card_plot, table_outer, table_frame):
        frame.configure(bg=c("card_bg"))
    table_header.configure(bg=c("card_bg"), fg=c("text"))
    graph_frame.configure(bg=c("bg_main"))
    refresh_btn.configure(bg=c("secondary"), fg="white")
    theme_btn.configure(bg=c("card_bg"), fg=c("text"))

    for fig, ax in ((fig_v, ax_v), (fig_t, ax_t)):
        fig.patch.set_facecolor(c("card_bg"))
        ax.set_facecolor(c("card_bg"))
        ax.tick_params(colors=c("subtext"))
        for s in ax.spines.values():
            s.set_color(c("subtext"))
    style.configure("Treeview", background=c("table_row1"), fieldbackground=c("table_row1"), foreground=c("text"), rowheight=30, borderwidth=0)
    style.configure("Treeview.Heading", background=c("bg_alt"), foreground=c("accent"), font=("Inter", 10, "bold"))
    style.map("Treeview", background=[("selected", c("secondary"))])
    tree.tag_configure("odd", background=c("table_row1"))
    tree.tag_configure("even", background=c("table_row2"))

# ---------- UPDATE ----------
def update_dashboard(force=False):
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

        for i, (_, row) in enumerate(df.iterrows()):
            tree.insert("", "end", values=(
                row['timestamp'],
                row['ldr_left'],
                row['ldr_right'],
                round(row['temperature'], 2),
                round(row['voltage'], 2)
            ), tags=("even" if i % 2 == 0 else "odd",))

        # Graph update
        ax_v.clear()
        ax_t.clear()
        ax_v.plot(df['voltage'], color=c("accent"), linewidth=2.2)
        ax_t.plot(df['temperature'], color=c("success"), linewidth=2.2)
        ax_v.grid(color=c("subtext"), alpha=0.2, linestyle="--")
        ax_t.grid(color=c("subtext"), alpha=0.2, linestyle="--")
        ax_v.set_title("Voltage Trend", color=c("text"), fontsize=11, pad=8)
        ax_t.set_title("Temperature Trend", color=c("text"), fontsize=11, pad=8)
        ax_v.tick_params(colors=c("subtext"))
        ax_t.tick_params(colors=c("subtext"))
        fig_v.tight_layout()
        fig_t.tight_layout()
        canvas_v.draw()
        canvas_t.draw()

    root.after(2000, update_dashboard)

apply_theme()
update_dashboard()
root.mainloop()
