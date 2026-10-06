import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from rply import errors

from LexicalAnalyzer import Lexer
from main import clasificar_token, obtener_posicion


class RoundedFrame(tk.Canvas):
    def __init__(
        self,
        parent,
        fill,
        canvas_bg,
        radius=18,
        border_color=None,
        border_width=1,
        padding=10,
        **kwargs,
    ):
        super().__init__(
            parent,
            bg=canvas_bg,
            highlightthickness=0,
            bd=0,
            relief="flat",
            **kwargs,
        )
        self.fill = fill
        self.radius = radius
        self.border_color = border_color or fill
        self.border_width = border_width
        self.padding = padding

        self.inner = tk.Frame(self, bg=fill, bd=0, highlightthickness=0)
        self._inner_window = self.create_window(
            padding,
            padding,
            anchor="nw",
            window=self.inner,
        )

        self.bind("<Configure>", self._redraw)

    def _rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        radius = max(2, min(radius, (x2 - x1) / 2, (y2 - y1) / 2))
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.create_polygon(
            points,
            smooth=True,
            splinesteps=36,
            **kwargs,
        )

    def _redraw(self, _event=None):
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 2 or height <= 2:
            return

        self.delete("rounded_bg")
        inset = max(1, self.border_width)
        self._rounded_rectangle(
            inset,
            inset,
            width - inset,
            height - inset,
            self.radius,
            fill=self.fill,
            outline=self.border_color,
            width=self.border_width,
            tags="rounded_bg",
        )
        self.tag_lower("rounded_bg")

        inner_width = max(1, width - (self.padding * 2))
        inner_height = max(1, height - (self.padding * 2))
        self.coords(self._inner_window, self.padding, self.padding)
        self.itemconfigure(
            self._inner_window,
            width=inner_width,
            height=inner_height,
        )


class LexerGUI:
    JACARANDA = "#7553A6"
    JACARANDA_DARK = "#51356F"
    JACARANDA_MID = "#8C6BB8"
    JACARANDA_LIGHT = "#EDE4F5"
    JACARANDA_PALE = "#F8F4FB"
    BORDER = "#D9CBE7"
    TEXT = "#2E2435"
    MUTED = "#6D6174"
    WHITE = "#FFFFFF"

    def __init__(self, root):
        self.root = root
        self.root.title("Jacaranda - Lexical Analyzer")
        self._set_window_icon()
        self.root.geometry("1200x720")
        self.root.minsize(900, 600)
        self.root.resizable(True, True)
        self.root.configure(bg=self.JACARANDA)

        self.current_file = None
        self.code_font = self._choose_code_font()
        self._configure_styles()
        self._build_interface()

    def _set_window_icon(self):
        assets_dir = Path(__file__).resolve().parent.parent / "assets"
        png_icon = assets_dir / "jacaranda_icon.png"
        ico_icon = assets_dir / "jacaranda.ico"

        self._icon_image = None

        try:
            if png_icon.exists():
                self._icon_image = tk.PhotoImage(file=str(png_icon))
                self.root.iconphoto(True, self._icon_image)
        except tk.TclError:
            self._icon_image = None

        try:
            if ico_icon.exists():
                self.root.iconbitmap(str(ico_icon))
        except tk.TclError:
            pass

    def _choose_code_font(self):
        available = set(tkfont.families(self.root))
        if "Cascadia Code" in available:
            return ("Cascadia Code", 11)
        if "Cascadia Mono" in available:
            return ("Cascadia Mono", 11)
        return ("Consolas", 11)

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Jacaranda.TFrame",
            background=self.JACARANDA,
        )
        style.configure(
            "Card.TFrame",
            background=self.JACARANDA_PALE,
        )
        style.configure(
            "Section.TLabel",
            background=self.JACARANDA_PALE,
            foreground=self.JACARANDA_DARK,
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "Info.TLabel",
            background=self.JACARANDA_PALE,
            foreground=self.MUTED,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Jacaranda.TButton",
            background=self.JACARANDA,
            foreground=self.WHITE,
            borderwidth=0,
            padding=(14, 8),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Jacaranda.TButton",
            background=[
                ("active", self.JACARANDA_MID),
                ("pressed", self.JACARANDA_DARK),
            ],
            foreground=[("active", self.WHITE), ("pressed", self.WHITE)],
        )
        style.configure(
            "Light.TButton",
            background=self.JACARANDA_LIGHT,
            foreground=self.JACARANDA_DARK,
            borderwidth=0,
            padding=(14, 8),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Light.TButton",
            background=[("active", "#DDD0EB"), ("pressed", "#D1BFE4")],
            foreground=[("active", self.JACARANDA_DARK)],
        )

    def _build_interface(self):
        outer = tk.Frame(self.root, bg=self.JACARANDA, padx=18, pady=18)
        outer.pack(fill="both", expand=True)

        header_card = RoundedFrame(
            outer,
            fill=self.JACARANDA_DARK,
            canvas_bg=self.JACARANDA,
            radius=22,
            border_color=self.JACARANDA_DARK,
            border_width=1,
            padding=18,
            height=92,
        )
        header_card.pack(fill="x", pady=(0, 12))
        header = header_card.inner

        tk.Label(
            header,
            text="JACARANDA",
            bg=self.JACARANDA_DARK,
            fg=self.WHITE,
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Lexical Analyzer",
            bg=self.JACARANDA_DARK,
            fg=self.JACARANDA_LIGHT,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(2, 0))

        card_shell = RoundedFrame(
            outer,
            fill=self.JACARANDA_PALE,
            canvas_bg=self.JACARANDA,
            radius=22,
            border_color=self.JACARANDA_PALE,
            border_width=1,
            padding=18,
        )
        card_shell.pack(fill="both", expand=True)
        card = card_shell.inner

        button_frame = tk.Frame(card, bg=self.JACARANDA_PALE)
        button_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(
            button_frame,
            text="Analyze",
            command=self.analyze_input,
            style="Jacaranda.TButton",
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            button_frame,
            text="Open File",
            command=self.open_file,
            style="Jacaranda.TButton",
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_all,
            style="Light.TButton",
        ).pack(side="left")

        self.file_label = tk.Label(
            button_frame,
            text="No file loaded",
            bg=self.JACARANDA_PALE,
            fg=self.MUTED,
            font=("Segoe UI", 9),
        )
        self.file_label.pack(side="right", padx=(12, 0))

        tk.Label(
            card,
            text="Drag the divider to adjust the panels",
            bg=self.JACARANDA_PALE,
            fg=self.MUTED,
            font=("Segoe UI", 9),
        ).pack(anchor="e", pady=(0, 6))

        self.panes = tk.PanedWindow(
            card,
            orient=tk.HORIZONTAL,
            sashwidth=10,
            sashrelief="flat",
            showhandle=False,
            bg=self.JACARANDA_MID,
            bd=0,
            relief="flat",
            opaqueresize=True,
        )
        self.panes.pack(fill="both", expand=True)

        source_panel = tk.Frame(self.panes, bg=self.JACARANDA_PALE, padx=0, pady=0)
        result_panel = tk.Frame(self.panes, bg=self.JACARANDA_PALE, padx=0, pady=0)

        self.panes.add(source_panel, minsize=320, stretch="always")
        self.panes.add(result_panel, minsize=320, stretch="always")

        tk.Label(
            source_panel,
            text="Source code",
            bg=self.JACARANDA_PALE,
            fg=self.JACARANDA_DARK,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=(0, 6))

        input_card = RoundedFrame(
            source_panel,
            fill=self.WHITE,
            canvas_bg=self.JACARANDA_PALE,
            radius=18,
            border_color=self.BORDER,
            border_width=1,
            padding=8,
        )
        input_card.pack(fill="both", expand=True, pady=(6, 0), padx=(0, 6))
        input_frame = input_card.inner
        input_frame.rowconfigure(0, weight=1)
        input_frame.columnconfigure(0, weight=1)

        self.input_text = tk.Text(
            input_frame,
            wrap="none",
            font=self.code_font,
            undo=True,
            bg=self.WHITE,
            fg=self.TEXT,
            insertbackground=self.JACARANDA_DARK,
            selectbackground=self.JACARANDA_LIGHT,
            selectforeground=self.TEXT,
            relief="flat",
            bd=0,
            padx=8,
            pady=8,
            highlightthickness=0,
        )
        input_scroll_y = ttk.Scrollbar(
            input_frame, orient="vertical", command=self.input_text.yview
        )
        input_scroll_x = ttk.Scrollbar(
            input_frame, orient="horizontal", command=self.input_text.xview
        )
        self.input_text.configure(
            yscrollcommand=input_scroll_y.set,
            xscrollcommand=input_scroll_x.set,
        )

        self.input_text.grid(row=0, column=0, sticky="nsew")
        input_scroll_y.grid(row=0, column=1, sticky="ns", padx=(5, 0))
        input_scroll_x.grid(row=1, column=0, sticky="ew", pady=(5, 0))

        tk.Label(
            result_panel,
            text="Analysis result",
            bg=self.JACARANDA_PALE,
            fg=self.JACARANDA_DARK,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=(6, 0))

        output_card = RoundedFrame(
            result_panel,
            fill=self.JACARANDA_LIGHT,
            canvas_bg=self.JACARANDA_PALE,
            radius=18,
            border_color=self.BORDER,
            border_width=1,
            padding=8,
        )
        output_card.pack(fill="both", expand=True, pady=(6, 0), padx=(6, 0))
        output_frame = output_card.inner
        output_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)

        self.output_text = tk.Text(
            output_frame,
            wrap="none",
            font=self.code_font,
            state="disabled",
            bg=self.JACARANDA_LIGHT,
            fg=self.TEXT,
            selectbackground=self.JACARANDA_MID,
            selectforeground=self.WHITE,
            relief="flat",
            bd=0,
            padx=8,
            pady=8,
            highlightthickness=0,
        )
        output_scroll_y = ttk.Scrollbar(
            output_frame, orient="vertical", command=self.output_text.yview
        )
        output_scroll_x = ttk.Scrollbar(
            output_frame, orient="horizontal", command=self.output_text.xview
        )
        self.output_text.configure(
            yscrollcommand=output_scroll_y.set,
            xscrollcommand=output_scroll_x.set,
        )

        self.output_text.grid(row=0, column=0, sticky="nsew")
        output_scroll_y.grid(row=0, column=1, sticky="ns", padx=(5, 0))
        output_scroll_x.grid(row=1, column=0, sticky="ew", pady=(5, 0))

        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-l>", lambda event: self.clear_all())
        self.root.bind("<F5>", lambda event: self.analyze_input())

        self.root.after(160, self._set_initial_split)
        self.input_text.focus_set()

    def _set_initial_split(self):
        width = self.panes.winfo_width()
        if width > 1:
            self.panes.sash_place(0, int(width * 0.50), 0)

    def _set_output(self, text):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text)
        self.output_text.configure(state="disabled")

    def _format_lexical_error(self, code, error):
        source_position = error.getsourcepos()
        index = source_position.idx
        line, column, line_text, visual_column = obtener_posicion(code, index)

        if 0 <= index < len(code):
            symbol = repr(code[index])
        else:
            symbol = "end of input"

        result = (
            f"LEXICAL ERROR: unrecognized symbol {symbol} "
            f"at line {line}, column {column}.\n"
        )

        if line_text:
            result += f"\n  {line_text}\n"
            result += "  " + " " * (visual_column - 1) + "^\n"

        return result

    def analyze_code(self, code):
        if not code.strip():
            self._set_output("No source code was entered.\nTotal of tokens: 0")
            return

        lexer = Lexer().get_lexer()

        try:
            tokens = list(lexer.lex(code))
        except errors.LexingError as error:
            self._set_output(self._format_lexical_error(code, error))
            return

        if not tokens:
            self._set_output("No tokens were found.\nTotal of tokens: 0")
            return

        lines = ["TOKENS IDENTIFIED:", ""]

        for token in tokens:
            category = clasificar_token(token)
            lines.append(f"{category:<12} {token.getstr()}")

        lines.extend(
            [
                "",
                "Token sequence:",
                " ".join(clasificar_token(token) for token in tokens),
                "",
                f"Total of tokens: {len(tokens)}",
            ]
        )

        self._set_output("\n".join(lines))

    def analyze_input(self):
        code = self.input_text.get("1.0", "end-1c")
        self.analyze_code(code)

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Open source file",
            filetypes=[
                ("Supported source files", "*.txt *.c *.h"),
                ("Text files", "*.txt"),
                ("C source files", "*.c"),
                ("Header files", "*.h"),
            ],
        )

        if not path:
            return

        file_path = Path(path)

        if file_path.suffix.lower() not in {".txt", ".c", ".h"}:
            messagebox.showerror(
                "Unsupported file",
                "This file type is not supported.\n\n"
                "Please select a .txt, .c, or .h file.",
            )
            return

        try:
            code = file_path.read_text(encoding="utf-8")

        except UnicodeDecodeError:
            messagebox.showerror(
                "File error",
                "The file could not be read as text.\n\n"
                "Please select a valid UTF-8 text file.",
            )
            return

        except (PermissionError, OSError):
            messagebox.showerror(
                "File error",
                "The file could not be opened.\n\n"
                "Check the file permissions or try another file.",
            )
            return

        self.current_file = path
        self.file_label.configure(text=file_path.name)

        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", code)
        self.analyze_code(code)

    def clear_all(self):
        self.current_file = None
        self.file_label.configure(text="No file loaded")
        self.input_text.delete("1.0", "end")
        self._set_output("")
        self.input_text.focus_set()


def main():
    root = tk.Tk()
    LexerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
