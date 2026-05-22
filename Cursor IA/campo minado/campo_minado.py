import random
import tkinter as tk
from tkinter import messagebox


class CampoMinado:
    TAMANHO = 8
    MINAS = 10

    CORES_NUMEROS = {
        1: "#0000ff",
        2: "#008000",
        3: "#ff0000",
        4: "#000080",
        5: "#800000",
        6: "#008080",
        7: "#000000",
        8: "#808080",
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Campo Minado")
        self.label_bandeiras = tk.Label(root, text="", font=("Arial", 14, "bold"))
        self.label_bandeiras.pack(pady=5)
        self.frame_tabuleiro = tk.Frame(root)
        self.frame_tabuleiro.pack(padx=10, pady=10)
        self.botoes: list[list[tk.Button]] = []
        self.minas: set[tuple[int, int]] = set()
        self.numeros: list[list[int]] = []
        self.reveladas: set[tuple[int, int]] = set()
        self.bandeiras: set[tuple[int, int]] = set()
        self.jogo_ativo = True
        self.iniciar_jogo()

    def iniciar_jogo(self):
        self.jogo_ativo = True
        self.minas.clear()
        self.reveladas.clear()
        self.bandeiras.clear()
        self._gerar_minas()
        self._calcular_numeros()
        self._criar_botoes()
        self._atualizar_contador_bandeiras()

    def _gerar_minas(self):
        posicoes = [
            (linha, coluna)
            for linha in range(self.TAMANHO)
            for coluna in range(self.TAMANHO)
        ]
        self.minas = set(random.sample(posicoes, self.MINAS))

    def _calcular_numeros(self):
        self.numeros = [[0] * self.TAMANHO for _ in range(self.TAMANHO)]
        for linha, coluna in self.minas:
            for vizinho in self._vizinhos(linha, coluna):
                vl, vc = vizinho
                if (vl, vc) not in self.minas:
                    self.numeros[vl][vc] += 1

    def _vizinhos(self, linha: int, coluna: int):
        for dl in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dl == 0 and dc == 0:
                    continue
                nl, nc = linha + dl, coluna + dc
                if 0 <= nl < self.TAMANHO and 0 <= nc < self.TAMANHO:
                    yield nl, nc

    def _criar_botoes(self):
        for linha in self.botoes:
            for botao in linha:
                botao.destroy()
        self.botoes = []

        for linha in range(self.TAMANHO):
            linha_botoes = []
            for coluna in range(self.TAMANHO):
                botao = tk.Button(
                    self.frame_tabuleiro,
                    text="",
                    width=3,
                    height=1,
                    font=("Arial", 12, "bold"),
                    relief=tk.RAISED,
                    command=lambda l=linha, c=coluna: self._clique_esquerdo(l, c),
                )
                botao.grid(row=linha, column=coluna, padx=1, pady=1)
                botao.bind(
                    "<Button-3>",
                    lambda event, l=linha, c=coluna: self._clique_direito(l, c),
                )
                linha_botoes.append(botao)
            self.botoes.append(linha_botoes)

    def _atualizar_contador_bandeiras(self):
        restantes = self.MINAS - len(self.bandeiras)
        self.label_bandeiras.config(text=f"Bandeiras restantes: {restantes}")

    def _clique_esquerdo(self, linha: int, coluna: int):
        if not self.jogo_ativo:
            return
        if (linha, coluna) in self.bandeiras:
            return
        if (linha, coluna) in self.reveladas:
            return

        if (linha, coluna) in self.minas:
            self._revelar_todas_minas()
            self.botoes[linha][coluna].config(text="💣", bg="#ffcccc", state=tk.DISABLED)
            self.jogo_ativo = False
            messagebox.showinfo("Campo Minado", "Você perdeu! 💣")
            self.iniciar_jogo()
            return

        self._revelar_celula(linha, coluna)
        if self._verificar_vitoria():
            self._revelar_todas_minas()
            self.jogo_ativo = False
            messagebox.showinfo("Campo Minado", "Parabéns! Você venceu! 🎉")
            self.iniciar_jogo()

    def _clique_direito(self, linha: int, coluna: int):
        if not self.jogo_ativo:
            return
        if (linha, coluna) in self.reveladas:
            return

        botao = self.botoes[linha][coluna]
        if (linha, coluna) in self.bandeiras:
            self.bandeiras.remove((linha, coluna))
            botao.config(text="")
        else:
            self.bandeiras.add((linha, coluna))
            botao.config(text="🚩")
        self._atualizar_contador_bandeiras()

    def _revelar_celula(self, linha: int, coluna: int):
        if (linha, coluna) in self.reveladas or (linha, coluna) in self.bandeiras:
            return

        self.reveladas.add((linha, coluna))
        valor = self.numeros[linha][coluna]
        botao = self.botoes[linha][coluna]
        botao.config(state=tk.DISABLED, relief=tk.SUNKEN)

        if valor == 0:
            botao.config(text="", bg="#e0e0e0")
            for vl, vc in self._vizinhos(linha, coluna):
                self._revelar_celula(vl, vc)
        else:
            botao.config(text=str(valor), fg=self.CORES_NUMEROS.get(valor, "#000000"))

    def _revelar_todas_minas(self):
        for linha, coluna in self.minas:
            botao = self.botoes[linha][coluna]
            botao.config(text="💣", bg="#ffcccc", state=tk.DISABLED)

    def _verificar_vitoria(self) -> bool:
        total_seguras = self.TAMANHO * self.TAMANHO - self.MINAS
        return len(self.reveladas) == total_seguras


if __name__ == "__main__":
    root = tk.Tk()
    CampoMinado(root)
    root.mainloop()
