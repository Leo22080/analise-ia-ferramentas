import tkinter as tk


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora")
        self.resizable(False, False)
        self._create_widgets()

    def _create_widgets(self):
        self.display_var = tk.StringVar()

        entry = tk.Entry(self, textvariable=self.display_var, font=("Segoe UI", 24), bd=10, relief=tk.RIDGE, justify="right")
        entry.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=5, pady=5)

        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3),
        ]

        for (text, row, col) in buttons:
            cmd = lambda t=text: self._on_button(t)
            btn = tk.Button(self, text=text, width=5, height=2, font=("Segoe UI", 18), command=cmd)
            btn.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

        clear_btn = tk.Button(self, text='C', width=5, height=2, font=("Segoe UI", 18), command=self._clear)
        clear_btn.grid(row=5, column=0, columnspan=2, padx=4, pady=4, sticky="nsew")

        back_btn = tk.Button(self, text='⌫', width=5, height=2, font=("Segoe UI", 18), command=self._backspace)
        back_btn.grid(row=5, column=2, padx=4, pady=4, sticky="nsew")

        quit_btn = tk.Button(self, text='Sair', width=5, height=2, font=("Segoe UI", 18), command=self.destroy)
        quit_btn.grid(row=5, column=3, padx=4, pady=4, sticky="nsew")

        for i in range(6):
            self.grid_rowconfigure(i, weight=1)
        for j in range(4):
            self.grid_columnconfigure(j, weight=1)

        self.bind('<Return>', lambda e: self._on_button('='))
        self.bind('<KP_Enter>', lambda e: self._on_button('='))
        self.bind('<BackSpace>', lambda e: self._backspace())

    def _on_button(self, char):
        if char == '=':
            self._evaluate()
            return
        current = self.display_var.get()
        new = current + str(char)
        self.display_var.set(new)

    def _clear(self):
        self.display_var.set('')

    def _backspace(self):
        current = self.display_var.get()
        self.display_var.set(current[:-1])

    def _evaluate(self):
        expr = self.display_var.get()
        if not expr:
            return
        try:
            # Evaluate only the basic arithmetic operators
            # Replace unicode operators if any
            expr = expr.replace('×', '*').replace('÷', '/')
            # Evaluate safely using eval with restricted globals
            result = eval(expr, {"__builtins__": None}, {})
            self.display_var.set(str(result))
        except Exception:
            self.display_var.set('Erro')


def main():
    app = Calculator()
    app.mainloop()


if __name__ == '__main__':
    main()
