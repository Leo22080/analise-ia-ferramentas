import tkinter as tk
from tkinter import messagebox
import random

class CampoMinado:
    def __init__(self, root):
        self.root = root
        self.root.title("Campo Minado")
        self.linhas = 8
        self.colunas = 8
        self.num_minas = 10
        self.celulas = {}
        
        # Frame para o contador de bandeiras
        self.frame_topo = tk.Frame(self.root)
        self.frame_topo.pack(pady=5)
        
        self.label_bandeiras = tk.Label(self.frame_topo, text=f"Bandeiras restantes: {self.num_minas}", font=("Arial", 14))
        self.label_bandeiras.pack()
        
        # Frame para o tabuleiro
        self.frame_tabuleiro = tk.Frame(self.root)
        self.frame_tabuleiro.pack()
        
        self.iniciar_jogo()

    def iniciar_jogo(self):
        # Limpa o tabuleiro anterior, se houver
        for widget in self.frame_tabuleiro.winfo_children():
            widget.destroy()
            
        self.minas = set()
        self.bandeiras = set()
        self.reveladas = set()
        self.jogo_ativo = True
        self.bandeiras_restantes = self.num_minas
        self.label_bandeiras.config(text=f"Bandeiras restantes: {self.bandeiras_restantes}")
        
        # Cria os botões para cada célula
        for l in range(self.linhas):
            for c in range(self.colunas):
                btn = tk.Button(self.frame_tabuleiro, width=3, height=1, font=("Arial", 12))
                btn.grid(row=l, column=c)
                btn.bind("<Button-1>", lambda event, l=l, c=c: self.clique_esquerdo(l, c))
                btn.bind("<Button-2>", lambda event, l=l, c=c: self.clique_direito(l, c)) # Mac
                btn.bind("<Button-3>", lambda event, l=l, c=c: self.clique_direito(l, c)) # Windows/Linux
                self.celulas[(l, c)] = btn
                
        # Coloca as minas depois de criar os botões para evitar clicar em mina no primeiro clique
        self.colocar_minas()

    def colocar_minas(self):
        todas_posicoes = [(l, c) for l in range(self.linhas) for c in range(self.colunas)]
        self.minas = set(random.sample(todas_posicoes, self.num_minas))

    def contar_vizinhos(self, l, c):
        count = 0
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if i == 0 and j == 0:
                    continue
                nl, nc = l + i, c + j
                if 0 <= nl < self.linhas and 0 <= nc < self.colunas and (nl, nc) in self.minas:
                    count += 1
        return count

    def clique_esquerdo(self, l, c):
        if not self.jogo_ativo or (l, c) in self.reveladas or (l, c) in self.bandeiras:
            return
        
        if (l, c) in self.minas:
            self.game_over(False)
        else:
            self.revelar(l, c)
            self.verificar_vitoria()

    def clique_direito(self, l, c):
        if not self.jogo_ativo or (l, c) in self.reveladas:
            return
            
        if (l, c) in self.bandeiras:
            self.bandeiras.remove((l, c))
            self.bandeiras_restantes += 1
            self.celulas[(l, c)].config(text="", bg="SystemButtonFace" if self.root.tk.call('tk', 'windowingsystem') == 'win32' else "lightgray")
        else:
            self.bandeiras.add((l, c))
            self.bandeiras_restantes -= 1
            self.celulas[(l, c)].config(text="🚩", fg="red")
            
        self.label_bandeiras.config(text=f"Bandeiras restantes: {self.bandeiras_restantes}")

    def revelar(self, l, c):
        if (l, c) in self.reveladas:
            return
            
        self.reveladas.add((l, c))
        btn = self.celulas[(l, c)]
        btn.config(relief=tk.SUNKEN, state=tk.DISABLED)
        
        # Remove bandeira caso exista ao revelar (segurança)
        if (l, c) in self.bandeiras:
            self.bandeiras.remove((l, c))
            self.bandeiras_restantes += 1
            self.label_bandeiras.config(text=f"Bandeiras restantes: {self.bandeiras_restantes}")

        vizinhos = self.contar_vizinhos(l, c)
        if vizinhos > 0:
            btn.config(text=str(vizinhos), fg=self.obter_cor_numero(vizinhos))
        else:
            btn.config(text="")
            # Revela vizinhos recursivamente se for 0
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    if i == 0 and j == 0:
                        continue
                    nl, nc = l + i, c + j
                    if 0 <= nl < self.linhas and 0 <= nc < self.colunas and (nl, nc) not in self.minas:
                        self.revelar(nl, nc)

    def obter_cor_numero(self, num):
        cores = {
            1: "blue",
            2: "green",
            3: "red",
            4: "darkblue",
            5: "darkred",
            6: "darkcyan",
            7: "black",
            8: "gray"
        }
        return cores.get(num, "black")

    def verificar_vitoria(self):
        total_celulas = self.linhas * self.colunas
        celulas_seguras = total_celulas - self.num_minas
        if len(self.reveladas) == celulas_seguras:
            self.game_over(True)

    def game_over(self, vitoria):
        self.jogo_ativo = False
        # Revela todas as minas
        for (l, c) in self.minas:
            btn = self.celulas[(l, c)]
            if vitoria:
                btn.config(text="🚩", fg="red", state=tk.DISABLED)
            else:
                btn.config(text="💣", bg="red", state=tk.DISABLED)
                
        if vitoria:
            messagebox.showinfo("Campo Minado", "Parabéns! Você venceu! 🎉")
        else:
            messagebox.showinfo("Campo Minado", "Boom! Você perdeu! 💥")
            
        self.iniciar_jogo()

if __name__ == "__main__":
    root = tk.Tk()
    jogo = CampoMinado(root)
    root.mainloop()
