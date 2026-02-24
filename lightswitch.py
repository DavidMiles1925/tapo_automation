import asyncio
import json
import os
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
import tkinter.font as tkfont

try:
    from config import TAPO_PASSWORD, TAPO_USERNAME
except ImportError:
    TAPO_PASSWORD = TAPO_USERNAME = None
# Optional: if you installed packages with pip
try:
    import aiohttp  # noqa: F401 (ensure installed)
    from tapo import ApiClient
except Exception as e:
    # Try to show a friendly message if deps are missing
    try:
        _r = tk.Tk()
        _r.withdraw()
        messagebox.showerror(
            "Missing dependency",
            f"Cannot import required packages: {e}\n\nInstall with:\n  pip install tapo aiohttp"
        )
        _r.destroy()
    except Exception:
        pass
    raise

# File to store known plugs
PLUGS_FILE = os.path.join(os.path.expanduser("~"), ".tapo_plugs.json")


# --------------------------
# Asyncio loop runner (background thread)
# --------------------------
class AsyncioRunner:
    def __init__(self):
        self.loop = None
        self._thread = None
        self._ready = threading.Event()

    def start(self):
        def _run():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self._ready.set()
            self.loop.run_forever()
            try:
                self.loop.close()
            except Exception:
                pass

        self._thread = threading.Thread(target=_run, name="asyncio-runner", daemon=True)
        self._thread.start()
        self._ready.wait()

    def stop(self):
        try:
            if self.loop and self.loop.is_running():
                self.loop.call_soon_threadsafe(self.loop.stop)
        finally:
            if self._thread:
                self._thread.join(timeout=3)

    def submit(self, coro):
        if not self.loop:
            raise RuntimeError("AsyncioRunner not started")
        return asyncio.run_coroutine_threadsafe(coro, self.loop)


RUNNER = AsyncioRunner()
RUNNER.start()


# --------------------------
# Helpers: read/write plugs
# --------------------------
def load_plugs():
    if not os.path.exists(PLUGS_FILE):
        return []
    try:
        with open(PLUGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                out = []
                for p in data:
                    if isinstance(p, dict) and "name" in p and "ip" in p:
                        out.append({"name": str(p["name"]), "ip": str(p["ip"])})
                return out
            return []
    except Exception:
        return []


def save_plugs(plugs_list):
    try:
        with open(PLUGS_FILE, "w", encoding="utf-8") as f:
            json.dump(plugs_list, f, indent=2)
    except Exception as e:
        print("Failed to save plugs:", e)


# --------------------------
# Tapo client wrapper
# --------------------------
class TapoManager:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client = None
        self.plugs = {}  # cache of ip -> plug object

    async def ensure_client(self):
        if self.client is None:
            self.client = ApiClient(self.username, self.password)

    async def get_plug(self, ip):
        if ip in self.plugs:
            return self.plugs[ip]
        await self.ensure_client()
        plug = await self.client.p100(ip)
        self.plugs[ip] = plug
        return plug

    async def turn_on(self, ip):
        plug = await self.get_plug(ip)
        await plug.on()

    async def turn_off(self, ip):
        plug = await self.get_plug(ip)
        await plug.off()


# --------------------------
# Tkinter GUI
# --------------------------
class PlugRow:
    def __init__(self, parent_frame, name, ip, manager: TapoManager, on_update_callback, fonts):
        self.parent = parent_frame
        self.name = name
        self.ip = ip
        self.manager = manager
        self.on_update = on_update_callback  # called when plug edited/removed
        self.fonts = fonts

        # Increased pady so rows are easier to press
        self.frame = tk.Frame(self.parent, pady=6)
        self.frame.pack(fill="x", anchor="w")

        # Larger name label for kid/touch usability
        self.lbl_name = tk.Label(self.frame, text=self.name, width=20, anchor="w", font=self.fonts["name"])
        self.lbl_name.pack(side="left", padx=(2, 12))

        # IP somewhat smaller but still legible
        self.lbl_ip = tk.Label(self.frame, text=self.ip, width=18, anchor="w", font=self.fonts["ip"])
        self.lbl_ip.pack(side="left", padx=(2, 12))

        # Bigger ON/OFF buttons with larger font and height for touch
        self.btn_on = tk.Button(self.frame, text="ON", width=8, height=2, font=self.fonts["btn"], command=self.on_click_on)
        self.btn_on.pack(side="left", padx=6)

        self.btn_off = tk.Button(self.frame, text="OFF", width=8, height=2, font=self.fonts["btn"], command=self.on_click_off)
        self.btn_off.pack(side="left", padx=6)

        # Edit button larger for touch users
        self.btn_edit = tk.Button(self.frame, text="Edit", width=8, height=2, font=self.fonts["small_btn"], command=self.on_click_edit)
        self.btn_edit.pack(side="right", padx=(12, 6))

        # Remove button now shows "X" only (larger and clear)
        self.btn_remove = tk.Button(self.frame, text="X", width=4, height=2, font=self.fonts["btn"], command=self.on_click_remove, fg="white", bg="#ffcccb")
        self.btn_remove.pack(side="right", padx=(6, 6))

        # Remember default button colors to restore later
        self._default_btn_bg = self.btn_on.cget("bg")
        self._default_btn_fg = self.btn_on.cget("fg")

        self.set_state("unknown")

    def set_state(self, state):
        # state: "on", "off", "unknown" (local UI-only)
        self.state = state

        def reset(btn):
            btn.config(bg=self._default_btn_bg, fg=self._default_btn_fg, relief="raised")

        if state == "on":
            self.btn_on.config(bg="green", fg="white", relief="sunken")
            reset(self.btn_off)
        elif state == "off":
            self.btn_off.config(bg="red", fg="white", relief="sunken")
            reset(self.btn_on)
        else:
            reset(self.btn_on)
            reset(self.btn_off)

    def on_click_on(self):
        fut = RUNNER.submit(self._async_on())
        fut.add_done_callback(lambda f: self._handle_future_error(f, f"Failed to turn ON {self.name} ({self.ip})"))

    async def _async_on(self):
        try:
            await self.manager.turn_on(self.ip)
            # Set local UI state optimistically
            self.parent.after(0, lambda: self.set_state("on"))
        except Exception as e:
            self.parent.after(0, self._show_error, str(e))

    def on_click_off(self):
        fut = RUNNER.submit(self._async_off())
        fut.add_done_callback(lambda f: self._handle_future_error(f, f"Failed to turn OFF {self.name} ({self.ip})"))

    async def _async_off(self):
        try:
            await self.manager.turn_off(self.ip)
            # Set local UI state optimistically
            self.parent.after(0, lambda: self.set_state("off"))
        except Exception as e:
            self.parent.after(0, self._show_error, str(e))

    def on_click_edit(self):
        def do_edit():
            new_name = e_name.get().strip()
            new_ip = e_ip.get().strip()
            if not new_name or not new_ip:
                messagebox.showwarning("Input required", "Name and IP are required.")
                return
            old_name, old_ip = self.name, self.ip
            self.name = new_name
            self.ip = new_ip
            self.lbl_name.config(text=self.name)
            self.lbl_ip.config(text=self.ip)
            edit_win.destroy()
            self.on_update("edit", {"old_name": old_name, "old_ip": old_ip, "name": self.name, "ip": self.ip})

        edit_win = tk.Toplevel(self.parent)
        edit_win.title("Edit plug")
        tk.Label(edit_win, text="Name:").grid(row=0, column=0, sticky="e")
        e_name = tk.Entry(edit_win, width=30)
        e_name.grid(row=0, column=1, padx=6, pady=4)
        e_name.insert(0, self.name)
        tk.Label(edit_win, text="IP:").grid(row=1, column=0, sticky="e")
        e_ip = tk.Entry(edit_win, width=30)
        e_ip.grid(row=1, column=1, padx=6, pady=4)
        e_ip.insert(0, self.ip)
        tk.Button(edit_win, text="Save", command=do_edit).grid(row=2, column=0, columnspan=2, pady=(4, 8))

    def on_click_remove(self):
        if not messagebox.askyesno("Remove plug", f"Remove '{self.name}' ({self.ip})?"):
            return
        self.frame.destroy()
        self.on_update("remove", {"name": self.name, "ip": self.ip})

    def _handle_future_error(self, fut, msg_if_error):
        try:
            fut.result()
        except Exception as e:
            if msg_if_error:
                self._show_error(f"{msg_if_error}: {e}")

    def _show_error(self, msg):
        messagebox.showerror("Tapo Error", msg)


class App:
    def __init__(self, root):
        self.root = root
        root.title("Light Switch")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Create fonts for large/touch-friendly UI
        # Name font is large for readability/touch
        self.font_name = tkfont.Font(size=20, weight="bold")
        # IP font slightly smaller than name
        self.font_ip = tkfont.Font(size=12)
        # Button font large and bold
        self.font_btn = tkfont.Font(size=16, weight="bold")
        # Slightly smaller font for edit button label
        self.font_small_btn = tkfont.Font(size=12, weight="bold")
        # Header font
        self.font_header = tkfont.Font(size=14, weight="bold")

        # Top menu
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Add Plug...", command=self.add_plug_dialog)
        filemenu.add_command(label="Import plugs...", command=self.import_plugs)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.on_close)
        menubar.add_cascade(label="File", menu=filemenu)
        root.config(menu=menubar)

        if TAPO_USERNAME is None or TAPO_PASSWORD is None:
            # try env, then prompt if still missing
            self.username = os.environ.get("TAPO_USERNAME") or ""
            self.password = os.environ.get("TAPO_PASSWORD") or ""
            if not self.username or not self.password:
                self.ask_credentials()
        else:
            self.username = TAPO_USERNAME
            self.password = TAPO_PASSWORD

        self.manager = TapoManager(self.username, self.password)

        # Main frame for plug list
        top = tk.Frame(root, padx=12, pady=12)
        top.pack(fill="both", expand=True)

        header = tk.Frame(top)
        header.pack(fill="x")
        tk.Label(header, text="Name", width=20, font=self.font_header).pack(side="left", padx=(2, 12))
        tk.Label(header, text="IP", width=18, font=self.font_header).pack(side="left", padx=(2, 12))

        # Header buttons for ALL ON / ALL OFF (aligned above individual ON/OFF columns)
        self.btn_all_on = tk.Button(header, text="ALL ON", width=8, height=2, font=self.font_btn, command=self.all_on)
        self.btn_all_on.pack(side="left", padx=6)
        self.btn_all_off = tk.Button(header, text="ALL OFF", width=8, height=2, font=self.font_btn, command=self.all_off)
        self.btn_all_off.pack(side="left", padx=6)

        # Filler to push edit/remove columns to the right visually
        tk.Label(header, text="", width=20).pack(side="left", padx=(12, 0))

        self.plug_container = tk.Frame(top)
        self.plug_container.pack(fill="both", expand=True)

        # bottom controls
        bottom = tk.Frame(root, pady=8)
        bottom.pack(fill="x")
        self.btn_add = tk.Button(bottom, text="Add Plug", command=self.add_plug_dialog, font=self.font_small_btn, height=2)
        self.btn_add.pack(side="left", padx=6)
        self.btn_save = tk.Button(bottom, text="Save List", command=self.save_list, font=self.font_small_btn, height=2)
        self.btn_save.pack(side="right", padx=6)

        # load plugs
        self.plug_rows = []
        self.plugs = load_plugs()
        for p in self.plugs:
            self._add_plug_row(p["name"], p["ip"], save=False)

    def ask_credentials(self):
        if self.username and self.password:
            return
        win = tk.Toplevel(self.root)
        win.title("Tapo credentials - No config file was found.")
        win.transient(self.root)
        win.grab_set()
        tk.Label(win, text="Tapo username (email):").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        e_user = tk.Entry(win, width=36)
        e_user.grid(row=0, column=1, padx=6, pady=4)
        e_user.insert(0, self.username)
        tk.Label(win, text="Tapo password:").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        e_pass = tk.Entry(win, width=36, show="*")
        e_pass.grid(row=1, column=1, padx=6, pady=4)
        e_pass.insert(0, self.password)

        def on_ok():
            self.username = e_user.get().strip()
            self.password = e_pass.get().strip()
            if not self.username or not self.password:
                if not messagebox.askyesno(
                    "Continue without credentials?",
                    "No credentials provided. You will not be able to contact plugs until you enter them. Continue?"
                ):
                    return
            win.destroy()

        tk.Button(win, text="OK", command=on_ok).grid(row=2, column=0, columnspan=2, pady=(4, 8))
        self.root.wait_window(win)

    def add_plug_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Add plug")
        win.transient(self.root)
        win.grab_set()
        tk.Label(win, text="Name:").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        e_name = tk.Entry(win, width=36)
        e_name.grid(row=0, column=1, padx=6, pady=4)
        tk.Label(win, text="IP Address:").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        e_ip = tk.Entry(win, width=36)
        e_ip.grid(row=1, column=1, padx=6, pady=4)

        def do_add():
            name = e_name.get().strip()
            ip = e_ip.get().strip()
            if not name or not ip:
                messagebox.showwarning("Missing", "Both name and IP are required.")
                return
            self._add_plug_row(name, ip, save=True)
            win.destroy()

        tk.Button(win, text="Add", command=do_add).grid(row=2, column=0, columnspan=2, pady=(4, 8))
        self.root.wait_window(win)

    def import_plugs(self):
        fname = filedialog.askopenfilename(
            title="Import plugs from JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not fname:
            return
        try:
            with open(fname, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("File must contain a JSON list of {'name':..., 'ip':...}")

            added_any = False
            for p in data:
                if "name" in p and "ip" in p:
                    name = str(p["name"])
                    ip = str(p["ip"])
                    # Only add if not already present
                    if not any(q["name"] == name and q["ip"] == ip for q in self.plugs):
                        self.plugs.append({"name": name, "ip": ip})
                        # Create the row without triggering per-item save popups
                        self._add_plug_row(name, ip, save=False)
                        added_any = True

            if added_any:
                self.save_list()
                messagebox.showinfo("Imported", "Plugs imported.")
            else:
                messagebox.showinfo("Imported", "No new plugs to import.")

        except Exception as e:
            messagebox.showerror("Import error", f"Failed to import: {e}")

    def _add_plug_row(self, name, ip, save=True):
        fonts = {
            "name": self.font_name,
            "ip": self.font_ip,
            "btn": self.font_btn,
            "small_btn": self.font_small_btn,
        }
        row = PlugRow(self.plug_container, name, ip, self.manager, self._on_row_update, fonts)
        self.plug_rows.append(row)
        if save:
            if not any(p["name"] == name and p["ip"] == ip for p in self.plugs):
                self.plugs.append({"name": name, "ip": ip})
            self.save_list()

    def _on_row_update(self, action, info):
        if action == "remove":
            self.plugs = [p for p in self.plugs if not (p["name"] == info["name"] and p["ip"] == info["ip"])]
            self.plug_rows = [r for r in self.plug_rows if not (r.name == info["name"] and r.ip == info["ip"])]
            self.save_list()
        elif action == "edit":
            updated = False
            for p in self.plugs:
                if p["name"] == info.get("old_name") and p["ip"] == info.get("old_ip"):
                    p["name"] = info["name"]
                    p["ip"] = info["ip"]
                    updated = True
                    break
            if not updated:
                if not any(p["name"] == info["name"] and p["ip"] == info["ip"] for p in self.plugs):
                    self.plugs.append({"name": info["name"], "ip": info["ip"]})
            self.save_list()

    def save_list(self):
        save_plugs(self.plugs)
        messagebox.showinfo("Saved", f"Plug list saved to {PLUGS_FILE}")

    # --------------------------
    # ALL ON / ALL OFF handlers
    # --------------------------
    def all_on(self):
        self._toggle_all("on")

    def all_off(self):
        self._toggle_all("off")

    def _toggle_all(self, action):
        # Disable controls while batch operation runs
        self._set_controls_enabled(False)
        fut = RUNNER.submit(self._async_toggle_all(action))
        fut.add_done_callback(lambda f: self.root.after(0, self._on_all_done, f))

    async def _async_toggle_all(self, action):
        # Iterate through saved plugs in order
        for p in self.plugs:
            ip = p["ip"]
            name = p["name"]
            try:
                if action == "on":
                    await self.manager.turn_on(ip)
                else:
                    await self.manager.turn_off(ip)

                # Update the corresponding row state on the main thread
                def update_row():
                    for r in self.plug_rows:
                        if r.ip == ip:
                            r.set_state("on" if action == "on" else "off")
                self.root.after(0, update_row)

            except Exception as e:
                # Show error but continue with others
                def show_err():
                    messagebox.showerror("Tapo Error", f"Failed to turn {action.upper()} {name} ({ip}): {e}")
                self.root.after(0, show_err)

            # Small delay between devices to avoid hammering the network/device
            await asyncio.sleep(0.15)

    def _on_all_done(self, fut):
        self._set_controls_enabled(True)
        try:
            fut.result()
        except Exception as e:
            messagebox.showerror("Tapo Error", f"Batch operation error: {e}")

    def _set_controls_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        # All/batch buttons
        self.btn_all_on.config(state=state)
        self.btn_all_off.config(state=state)
        # Row buttons and edit/remove
        for r in self.plug_rows:
            r.btn_on.config(state=state)
            r.btn_off.config(state=state)
            r.btn_edit.config(state=state)
            r.btn_remove.config(state=state)
        # Bottom controls
        self.btn_add.config(state=state)
        self.btn_save.config(state=state)

    def on_close(self):
        try:
            RUNNER.stop()
        finally:
            self.root.destroy()


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
