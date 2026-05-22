import tkinter as tk
from tkinter import ttk

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora Tkinter")
        self.resizable(False, False)
        self._create_widgets()
        self._expression = ""

    def _create_widgets(self):
        self.display_var = tk.StringVar(value="0")

        display = ttk.Entry(self, textvariable=self.display_var, font=("Segoe UI", 24), justify="right", state="readonly")
        display.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=8, pady=8)

        buttons = [
            ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("/", 1, 3),
            ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3),
            ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
            ("0", 4, 0), (".", 4, 1), ("=", 4, 2), ("+", 4, 3),
        ]

        for (text, row, col) in buttons:
            action = self._create_action(text)
            button = ttk.Button(self, text=text, command=action)
            button.grid(row=row, column=col, sticky="nsew", padx=4, pady=4, ipadx=8, ipady=12)

        clear_button = ttk.Button(self, text="C", command=self._clear)
        clear_button.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=4, pady=4, ipadx=8, ipady=12)

        delete_button = ttk.Button(self, text="⌫", command=self._backspace)
        delete_button.grid(row=5, column=2, columnspan=2, sticky="nsew", padx=4, pady=4, ipadx=8, ipady=12)

        for i in range(6):
            self.rowconfigure(i, weight=1)
        for j in range(4):
            self.columnconfigure(j, weight=1)

    def _create_action(self, char):
        if char == "=":
            return self._calculate
        return lambda: self._append(char)

    def _append(self, char):
        if self._expression == "0" and char not in ".+-*/":
            self._expression = char
        else:
            self._expression += char
        self.display_var.set(self._expression)

    def _clear(self):
        self._expression = ""
        self.display_var.set("0")

    def _backspace(self):
        self._expression = self._expression[:-1]
        self.display_var.set(self._expression or "0")

    def _calculate(self):
        try:
            result = eval(self._expression)
            self._expression = str(result)
            self.display_var.set(self._expression)
        except Exception:
            self.display_var.set("Erro")
            self._expression = ""

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
