"""Tkinter front end for the android-translator CLI."""

import contextlib
import io
import json
import os
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from android_translator import create_parser

SETTINGS_FILE = Path.home() / ".android_translator_gui.json"
COMMANDS = ("strings export", "strings import", "html export", "html import")
FLAGS = {
    "html export": ("--remove-html-tags", "Remove HTML tags from exported content"),
    "html import": ("--plain-text-to-html", "Wrap each plain-text line in a <p> tag"),
}
PATH_LABELS = {"strings": "Android project", "html": "HTML folder"}


def build_argv(command, path, output_dir, language="", flag_on=False):
    """Translate the form values into CLI arguments."""
    # Absolute paths keep output independent of the launch directory; abspath, not
    # resolve, so a symlinked project keeps the name the CLI would give its Excel folder.
    argv = [
        *command.split(),
        os.path.abspath(Path(path).expanduser()),
        f"--output-dir={os.path.abspath(Path(output_dir).expanduser())}",
    ]
    if command.startswith("strings"):
        argv.append(f"--default-language={language}")
    if flag_on and command in FLAGS:
        argv.append(FLAGS[command][0])
    return argv


def run_command(argv, stream):
    """Run a CLI command, sending all of its output and errors to stream."""
    with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
        try:
            args = create_parser().parse_args(argv)
            args.func(args)
        except SystemExit:  # argparse has already printed the reason
            pass
        except Exception as e:
            print(f"\n❌ Error: {e}")


def load_settings():
    try:
        settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return settings if isinstance(settings, dict) else {}


class QueueStream(io.TextIOBase):
    """Text stream that hands writes to the Tk thread through a queue."""

    def __init__(self, target):
        self.target = target

    def write(self, text):
        self.target.put(text)
        return len(text)


class App:
    def __init__(self, root):
        self.root = root
        self.messages = queue.Queue()
        settings = load_settings()

        command = settings.get("command")
        self.command = tk.StringVar(value=command if command in COMMANDS else COMMANDS[0])
        self.paths = {
            group: tk.StringVar(value=settings.get(f"{group}_path", ""))
            for group in PATH_LABELS
        }
        self.output_dir = tk.StringVar(value=settings.get("output_dir", ""))
        self.language = tk.StringVar(value=settings.get("default_language", "en"))
        self.flag_on = tk.BooleanVar(value=False)

        root.title("Android Translator")
        root.minsize(640, 480)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        form = ttk.Frame(root, padding=12)
        form.grid(sticky="nsew")
        form.columnconfigure(1, weight=1)
        form.rowconfigure(5, weight=1)

        ttk.Label(form, text="Command").grid(row=0, column=0, sticky="w", pady=4)
        choices = ttk.Frame(form)
        choices.grid(row=0, column=1, columnspan=2, sticky="w")
        for name in COMMANDS:
            ttk.Radiobutton(
                choices, text=name, value=name, variable=self.command, command=self.refresh
            ).pack(side="left", padx=(0, 12))

        self.path_label = ttk.Label(form)
        self.path_label.grid(row=1, column=0, sticky="w", pady=4, padx=(0, 12))
        self.path_entry = ttk.Entry(form)
        self.path_entry.grid(row=1, column=1, sticky="ew")
        ttk.Button(form, text="Browse…", command=self.browse_path).grid(row=1, column=2, padx=(8, 0))

        ttk.Label(form, text="Excel folder").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.output_dir).grid(row=2, column=1, sticky="ew")
        ttk.Button(form, text="Browse…", command=self.browse_output).grid(row=2, column=2, padx=(8, 0))

        self.language_label = ttk.Label(form, text="Default language")
        self.language_label.grid(row=3, column=0, sticky="w", pady=4)
        self.language_entry = ttk.Entry(form, textvariable=self.language, width=8)
        self.language_entry.grid(row=3, column=1, sticky="w")
        self.flag_check = ttk.Checkbutton(form, variable=self.flag_on)
        self.flag_check.grid(row=3, column=1, columnspan=2, sticky="w")

        self.run_button = ttk.Button(form, text="Run", command=self.run)
        self.run_button.grid(row=4, column=2, sticky="e", pady=8)

        log_frame = ttk.Frame(form)
        log_frame.grid(row=5, column=0, columnspan=3, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.log = tk.Text(log_frame, height=16, wrap="word", state="disabled")
        self.log.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(log_frame, command=self.log.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log.configure(yscrollcommand=scrollbar.set)

        self.refresh()
        self.poll_messages()

    def group(self):
        return self.command.get().split()[0]

    def refresh(self):
        """Show only the fields the selected command accepts."""
        group = self.group()
        self.path_label.configure(text=PATH_LABELS[group])
        self.path_entry.configure(textvariable=self.paths[group])

        if group == "strings":
            self.language_label.grid()
            self.language_entry.grid()
        else:
            self.language_label.grid_remove()
            self.language_entry.grid_remove()

        self.flag_on.set(False)  # a flag must not carry over to another command
        flag = FLAGS.get(self.command.get())
        if flag:
            self.flag_check.configure(text=flag[1])
            self.flag_check.grid()
        else:
            self.flag_check.grid_remove()

    def browse_path(self):
        variable = self.paths[self.group()]
        chosen = filedialog.askdirectory(initialdir=variable.get() or Path.home(), mustexist=True)
        if chosen:
            variable.set(chosen)

    def browse_output(self):
        chosen = filedialog.askdirectory(initialdir=self.output_dir.get() or Path.home())
        if chosen:
            self.output_dir.set(chosen)

    def save_settings(self):
        settings = {
            "command": self.command.get(),
            "output_dir": self.output_dir.get().strip(),
            "default_language": self.language.get().strip(),
            **{f"{group}_path": var.get().strip() for group, var in self.paths.items()},
        }
        try:
            SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        except OSError as e:
            self.messages.put(f"⚠️ Could not save settings: {e}\n")

    def run(self):
        command = self.command.get()
        path = self.paths[self.group()].get().strip()
        output_dir = self.output_dir.get().strip()
        language = self.language.get().strip()

        if not path or not output_dir or (self.group() == "strings" and not language):
            messagebox.showerror("Missing values", "Fill in all the fields before running.")
            return
        if command.endswith("import") and not messagebox.askyesno(
            "Overwrite translations?",
            f"This writes the translations from the Excel files into:\n\n{path}\n\nContinue?",
        ):
            return

        self.save_settings()
        argv = build_argv(command, path, output_dir, language, self.flag_on.get())
        self.messages.put(f"$ android-translator {' '.join(argv)}\n")
        self.run_button.configure(state="disabled")
        # Not a daemon: closing the window must not kill an import mid-write.
        threading.Thread(target=self.work, args=(argv,)).start()

    def work(self, argv):
        run_command(argv, QueueStream(self.messages))
        self.messages.put(None)

    def poll_messages(self):
        try:
            while True:
                message = self.messages.get_nowait()
                if message is None:
                    self.append_log("\n")
                    self.run_button.configure(state="normal")
                else:
                    self.append_log(message)
        except queue.Empty:
            pass
        self.root.after(100, self.poll_messages)

    def append_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.configure(state="disabled")
        self.log.see("end")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
