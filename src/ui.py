import json
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

import session


APP_DIR = Path(__file__).resolve().parent


def format_duration(seconds):
    seconds = max(0, int(float(seconds or 0)))
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


class ProductivityApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Focus Session")
        self.root.geometry("820x680")
        self.root.minsize(680, 560)
        self.root.configure(bg="#0b1020")
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.events = queue.Queue()
        self.running = False
        self.stop_pending = False
        self._configure_styles()
        self._build_ui()
        self.root.after(100, self._drain_events)

    def _configure_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("App.TFrame", background="#0b1020")
        style.configure("Card.TFrame", background="#151c30")
        style.configure("Title.TLabel", background="#0b1020", foreground="#f8fafc", font=("Helvetica Neue", 25, "bold"))
        style.configure("Muted.TLabel", background="#0b1020", foreground="#93a4bd", font=("Helvetica Neue", 11))
        style.configure("CardLabel.TLabel", background="#151c30", foreground="#93a4bd", font=("Helvetica Neue", 10, "bold"))
        style.configure("Clock.TLabel", background="#151c30", foreground="#70e1b0", font=("Menlo", 38, "bold"))
        style.configure("Status.TLabel", background="#151c30", foreground="#d9e2f2", font=("Helvetica Neue", 11))
        style.configure("Accent.TButton", font=("Helvetica Neue", 11, "bold"), padding=(18, 11), background="#6d5dfc", foreground="white")
        style.map("Accent.TButton", background=[("active", "#8175ff"), ("disabled", "#343957")])
        style.configure("Secondary.TButton", font=("Helvetica Neue", 11), padding=(16, 10), background="#252e49", foreground="#edf2f7")
        style.map("Secondary.TButton", background=[("active", "#34405f")])

    def _build_ui(self):
        shell = ttk.Frame(self.root, style="App.TFrame", padding=30)
        shell.pack(fill="both", expand=True)

        ttk.Label(shell, text="Focus Session", style="Title.TLabel").pack(anchor="w")
        ttk.Label(shell, text="Track your attention, then review where the time went.", style="Muted.TLabel").pack(anchor="w", pady=(4, 22))

        card = ttk.Frame(shell, style="Card.TFrame", padding=24)
        card.pack(fill="x")
        ttk.Label(card, text="ELAPSED TIME", style="CardLabel.TLabel").pack(anchor="center")
        self.clock = ttk.Label(card, text="00:00:00", style="Clock.TLabel")
        self.clock.pack(pady=(8, 4))
        self.status = ttk.Label(card, text="Ready to begin", style="Status.TLabel")
        self.status.pack()

        goal_row = ttk.Frame(shell, style="App.TFrame")
        goal_row.pack(fill="x", pady=(22, 12))
        ttk.Label(goal_row, text="What do you want to accomplish?", style="Muted.TLabel").pack(anchor="w", pady=(0, 7))
        self.goal = tk.Entry(goal_row, font=("Helvetica Neue", 13), bg="#151c30", fg="#f8fafc", insertbackground="#f8fafc", relief="flat", highlightthickness=1, highlightbackground="#34405f", highlightcolor="#6d5dfc")
        self.goal.pack(fill="x", ipady=11)
        self.goal.bind("<Return>", lambda _event: self.start_session())

        actions = ttk.Frame(shell, style="App.TFrame")
        actions.pack(fill="x", pady=(0, 20))
        self.start_button = ttk.Button(actions, text="Start session", command=self.start_session, style="Accent.TButton")
        self.start_button.pack(side="left")
        self.end_button = ttk.Button(actions, text="End session", command=self.end_session, style="Secondary.TButton", state="disabled")
        self.end_button.pack(side="left", padx=10)
        ttk.Button(actions, text="Preview saved report", command=self.preview_report, style="Secondary.TButton").pack(side="right")

        report_card = ttk.Frame(shell, style="Card.TFrame", padding=18)
        report_card.pack(fill="both", expand=True)
        ttk.Label(report_card, text="SESSION REPORT", style="CardLabel.TLabel").pack(anchor="w", pady=(0, 10))
        text_frame = tk.Frame(report_card, bg="#151c30")
        text_frame.pack(fill="both", expand=True)
        self.report = tk.Text(text_frame, wrap="word", font=("Helvetica Neue", 11), bg="#10172a", fg="#dce6f5", relief="flat", padx=16, pady=14, state="disabled", spacing1=2, spacing3=5)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.report.yview)
        self.report.configure(yscrollcommand=scrollbar.set)
        self.report.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self._set_report("Your completed session analysis will appear here.\n\nUse “Preview saved report” to view the existing output.json sample.")

    def start_session(self):
        goal = self.goal.get().strip()
        if not goal:
            messagebox.showinfo("Add a goal", "Describe what you want to accomplish first.")
            self.goal.focus_set()
            return
        try:
            session.start_session(goal)
        except Exception as exc:
            messagebox.showerror("Could not start", str(exc))
            return
        self.running = True
        self.stop_pending = False
        self.goal.configure(state="disabled")
        self.start_button.configure(state="disabled")
        self.end_button.configure(state="normal")
        self.status.configure(text="Tracking active app and browser activity")
        self._set_report("Session in progress…")
        threading.Thread(target=self._tracking_loop, daemon=True).start()

    def end_session(self):
        if not self.running or self.stop_pending:
            return
        self.stop_pending = True
        session.end_session()
        self.end_button.configure(state="disabled")
        self.status.configure(text="Analyzing session with Ollama…")

    def _tracking_loop(self):
        while self.running:
            try:
                report = session.process_tracker_tick()
                self.events.put(("tick", report))
                if session.stop_requested:
                    self.events.put(("report", report))
                    return
            except Exception as exc:
                self.events.put(("error", exc))
                return
            threading.Event().wait(0.5)

    def _drain_events(self):
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "tick":
                    self.clock.configure(text=format_duration(payload.get("duration", 0)))
                elif kind == "report":
                    self.running = False
                    self.stop_pending = False
                    self._show_report(payload)
                    self.status.configure(text="Session complete")
                    self.goal.configure(state="normal")
                    self.start_button.configure(state="normal")
                elif kind == "error":
                    self.running = False
                    self.stop_pending = False
                    self.status.configure(text="Session stopped because of an error")
                    self.goal.configure(state="normal")
                    self.start_button.configure(state="normal")
                    self.end_button.configure(state="disabled")
                    messagebox.showerror("Tracking error", f"{payload}\n\nIf this happened while ending, make sure Ollama is running with the gemma3:latest model.")
        except queue.Empty:
            pass
        self.root.after(100, self._drain_events)

    def preview_report(self):
        try:
            with (APP_DIR / "output.json").open(encoding="utf-8") as handle:
                self._show_report(json.load(handle))
            self.status.configure(text="Showing saved report preview")
        except (OSError, json.JSONDecodeError) as exc:
            messagebox.showerror("Could not open report", str(exc))

    def _show_report(self, data):
        analysis = data.get("analysis", {})
        lines = [
            f"Productivity score: {analysis.get('productivity_score', '—')} / 100",
            f"Classification: {analysis.get('classification', 'Not analyzed')}",
            f"Reason: {analysis.get('reason', 'No explanation available.')}",
            "",
            f"Duration: {format_duration(data.get('duration', 0))}",
            f"Idle time: {format_duration(data.get('time_spent_idle', 0))}",
            "",
            "Most frequented apps",
        ]
        apps = data.get("most_frequented_apps", {})
        lines.extend(f"  {name}: {format_duration(seconds)}" for name, seconds in apps.items())
        if not apps:
            lines.append("  None recorded")
        lines.extend(["", "Most frequented websites"])
        websites = data.get("most_frequented_websites", {})
        lines.extend(f"  {name}: {format_duration(seconds)}" for name, seconds in websites.items())
        if not websites:
            lines.append("  None recorded")
        self._set_report("\n".join(lines))

    def _set_report(self, content):
        self.report.configure(state="normal")
        self.report.delete("1.0", "end")
        self.report.insert("1.0", content)
        self.report.configure(state="disabled")

    def close(self):
        if self.running:
            session.end_session()
        self.running = False
        self.root.destroy()

    def run(self):
        self.goal.focus_set()
        self.root.mainloop()
