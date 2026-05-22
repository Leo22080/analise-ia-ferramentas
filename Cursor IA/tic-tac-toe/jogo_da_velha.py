#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jogo da Velha multiplayer — Python + Tkinter + sockets TCP.

Uso local (duas instâncias na mesma máquina):
  1. Abra o programa e escolha "Servidor" → aguarde conexão.
  2. Abra outra instância, escolha "Cliente" (127.0.0.1) → conecte.
  3. Servidor joga com X (primeiro turno); cliente joga com O.
"""

import socket
import threading
import tkinter as tk
from tkinter import messagebox, ttk

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO
# ---------------------------------------------------------------------------

HOST_PADRAO = "127.0.0.1"
PORTA_PADRAO = 55555
TAMANHO_TABULEIRO = 3
BUFFER_RECV = 4096

# Símbolos e papéis na rede
SIMBOLO_SERVIDOR = "X"
SIMBOLO_CLIENTE = "O"

# Linhas que definem vitória (índices 0–8 no tabuleiro linear)
LINHAS_VITORIA = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)

# Protocolo de mensagens (uma linha por mensagem, UTF-8)
MSG_MOVE = "MOVE"       # MOVE|linha|coluna
MSG_RESTART = "RESTART" # reinicia partida
MSG_QUIT = "QUIT"       # encerra conexão


# ---------------------------------------------------------------------------
# LÓGICA DO JOGO
# ---------------------------------------------------------------------------


class JogoDaVelha:
    """Estado e regras do tabuleiro (independente de rede e interface)."""

    def __init__(self) -> None:
        self.reiniciar()

    def reiniciar(self) -> None:
        """Limpa o tabuleiro e volta o turno para X."""
        self.tabuleiro = [["" for _ in range(TAMANHO_TABULEIRO)] for _ in range(TAMANHO_TABULEIRO)]
        self.turno_atual = SIMBOLO_SERVIDOR
        self.vencedor: str | None = None
        self.empate = False
        self.jogo_terminado = False

    def jogada_valida(self, linha: int, coluna: int) -> bool:
        """Célula vazia e partida ainda em andamento."""
        if self.jogo_terminado:
            return False
        if not (0 <= linha < TAMANHO_TABULEIRO and 0 <= coluna < TAMANHO_TABULEIRO):
            return False
        return self.tabuleiro[linha][coluna] == ""

    def aplicar_jogada(self, linha: int, coluna: int, simbolo: str) -> bool:
        """
        Registra uma jogada se for válida.
        Retorna True se a jogada foi aceita.
        """
        if not self.jogada_valida(linha, coluna):
            return False
        if simbolo != self.turno_atual:
            return False

        self.tabuleiro[linha][coluna] = simbolo
        self._avaliar_fim_de_jogo()
        if not self.jogo_terminado:
            self.turno_atual = (
                SIMBOLO_CLIENTE if self.turno_atual == SIMBOLO_SERVIDOR else SIMBOLO_SERVIDOR
            )
        return True

    def _avaliar_fim_de_jogo(self) -> None:
        """Verifica vitória ou empate após a última jogada."""
        flat = [self.tabuleiro[r][c] for r in range(TAMANHO_TABULEIRO) for c in range(TAMANHO_TABULEIRO)]

        for a, b, c in LINHAS_VITORIA:
            if flat[a] and flat[a] == flat[b] == flat[c]:
                self.vencedor = flat[a]
                self.jogo_terminado = True
                return

        if all(cel != "" for cel in flat):
            self.empate = True
            self.jogo_terminado = True

    def mensagem_status(self) -> str:
        """Texto amigável para o rótulo da interface."""
        if self.vencedor:
            return f"Vitória do jogador {self.vencedor}!"
        if self.empate:
            return "Empate — tabuleiro cheio."
        return f"Turno: {self.turno_atual}"


# ---------------------------------------------------------------------------
# COMUNICAÇÃO (SOCKETS TCP)
# ---------------------------------------------------------------------------


class ConexaoRede:
    """
    Encapsula socket TCP, envio/recebimento e thread de escuta.
    Callbacks são invocados na thread de rede; a UI deve usar root.after().
    """

    def __init__(
        self,
        ao_conectar=None,
        ao_receber_move=None,
        ao_receber_restart=None,
        ao_desconectar=None,
    ) -> None:
        self.socket: socket.socket | None = None
        self._thread_recv: threading.Thread | None = None
        self._ativo = False
        self._buffer = ""

        self.ao_conectar = ao_conectar
        self.ao_receber_move = ao_receber_move
        self.ao_receber_restart = ao_receber_restart
        self.ao_desconectar = ao_desconectar

    def iniciar_servidor(self, host: str, porta: int) -> None:
        """Aguarda um cliente e aceita uma conexão."""
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, porta))
        servidor.listen(1)
        self.socket, endereco = servidor.accept()
        servidor.close()
        self._apos_conectar(endereco)

    def conectar_cliente(self, host: str, porta: int) -> None:
        """Conecta ao servidor remoto."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, porta))
        self._apos_conectar((host, porta))

    def _apos_conectar(self, endereco) -> None:
        self.socket.settimeout(None)
        self._ativo = True
        self._thread_recv = threading.Thread(target=self._loop_recebimento, daemon=True)
        self._thread_recv.start()
        if self.ao_conectar:
            self.ao_conectar(endereco)

    def enviar(self, mensagem: str) -> None:
        """Envia uma linha de texto (protocolo simples)."""
        if self.socket and self._ativo:
            dados = (mensagem + "\n").encode("utf-8")
            self.socket.sendall(dados)

    def enviar_jogada(self, linha: int, coluna: int) -> None:
        self.enviar(f"{MSG_MOVE}|{linha}|{coluna}")

    def enviar_restart(self) -> None:
        self.enviar(MSG_RESTART)

    def encerrar(self) -> None:
        self._ativo = False
        if self.socket:
            try:
                self.enviar(MSG_QUIT)
            except OSError:
                pass
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                self.socket.close()
            except OSError:
                pass
            self.socket = None

    def _loop_recebimento(self) -> None:
        """Thread: lê mensagens do socket e dispara callbacks."""
        try:
            while self._ativo and self.socket:
                bloco = self.socket.recv(BUFFER_RECV)
                if not bloco:
                    break
                self._buffer += bloco.decode("utf-8")
                while "\n" in self._buffer:
                    linha, self._buffer = self._buffer.split("\n", 1)
                    linha = linha.strip()
                    if linha:
                        self._processar_mensagem(linha)
        except OSError:
            pass
        finally:
            self._ativo = False
            if self.ao_desconectar:
                self.ao_desconectar()

    def _processar_mensagem(self, linha: str) -> None:
        if linha == MSG_QUIT:
            self._ativo = False
            return
        if linha == MSG_RESTART:
            if self.ao_receber_restart:
                self.ao_receber_restart()
            return
        partes = linha.split("|")
        if partes[0] == MSG_MOVE and len(partes) == 3:
            try:
                r, c = int(partes[1]), int(partes[2])
                if self.ao_receber_move:
                    self.ao_receber_move(r, c)
            except ValueError:
                pass


# ---------------------------------------------------------------------------
# INTERFACE (TKINTER)
# ---------------------------------------------------------------------------


class AplicacaoJogoDaVelha:
    """Janela principal: menu inicial, tabuleiro e integração com rede."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Jogo da Velha — Multiplayer TCP")
        self.root.resizable(False, False)

        self.jogo = JogoDaVelha()
        self.rede: ConexaoRede | None = None
        self.meu_simbolo: str | None = None
        self.eh_servidor = False
        self.conectado = False

        self._frame_menu: tk.Frame | None = None
        self._frame_jogo: tk.Frame | None = None
        self._botoes: list[list[tk.Button]] = []
        self._lbl_status: tk.Label | None = None

        self._montar_menu_inicial()

    def _montar_menu_inicial(self) -> None:
        """Tela para escolher servidor ou cliente antes da partida."""
        self._frame_menu = tk.Frame(self.root, padx=20, pady=20)
        self._frame_menu.pack()

        tk.Label(
            self._frame_menu,
            text="Jogo da Velha — Multiplayer",
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=(0, 12))

        tk.Label(self._frame_menu, text="Como deseja jogar?").pack(anchor="w")

        modo = tk.StringVar(value="servidor")
        tk.Radiobutton(
            self._frame_menu,
            text="Servidor (aguarda conexão — joga X)",
            variable=modo,
            value="servidor",
        ).pack(anchor="w")
        tk.Radiobutton(
            self._frame_menu,
            text="Cliente (conecta ao servidor — joga O)",
            variable=modo,
            value="cliente",
        ).pack(anchor="w", pady=(0, 10))

        frame_host = tk.Frame(self._frame_menu)
        frame_host.pack(fill="x", pady=4)
        tk.Label(frame_host, text="Host:").pack(side="left")
        self._entry_host = tk.Entry(frame_host, width=18)
        self._entry_host.insert(0, HOST_PADRAO)
        self._entry_host.pack(side="left", padx=6)

        frame_porta = tk.Frame(self._frame_menu)
        frame_porta.pack(fill="x", pady=4)
        tk.Label(frame_porta, text="Porta:").pack(side="left")
        self._entry_porta = tk.Entry(frame_porta, width=8)
        self._entry_porta.insert(0, str(PORTA_PADRAO))
        self._entry_porta.pack(side="left", padx=6)

        self._lbl_aguarde = tk.Label(self._frame_menu, text="", fg="blue")
        self._lbl_aguarde.pack(pady=8)

        def iniciar() -> None:
            host = self._entry_host.get().strip() or HOST_PADRAO
            try:
                porta = int(self._entry_porta.get().strip())
            except ValueError:
                messagebox.showerror("Erro", "Porta inválida.")
                return

            if modo.get() == "servidor":
                self._iniciar_como_servidor(host, porta)
            else:
                self._iniciar_como_cliente(host, porta)

        ttk.Button(self._frame_menu, text="Iniciar", command=iniciar).pack(pady=10)

        tk.Label(
            self._frame_menu,
            text="Dica: abra duas instâncias — uma como Servidor e outra como Cliente.",
            font=("Segoe UI", 8),
            fg="gray",
        ).pack()

    def _iniciar_como_servidor(self, host: str, porta: int) -> None:
        self.eh_servidor = True
        self.meu_simbolo = SIMBOLO_SERVIDOR
        self._lbl_aguarde.config(text="Aguardando cliente conectar...")

        def trabalho() -> None:
            try:
                rede = ConexaoRede(
                    ao_conectar=lambda addr: self.root.after(0, lambda: self._ao_conectar(addr)),
                    ao_receber_move=lambda r, c: self.root.after(0, lambda: self._ao_receber_jogada(r, c)),
                    ao_receber_restart=lambda: self.root.after(0, self._ao_receber_restart),
                    ao_desconectar=lambda: self.root.after(0, self._ao_desconectar),
                )
                rede.iniciar_servidor(host, porta)
                self.rede = rede
            except OSError as e:
                self.root.after(0, lambda: self._erro_conexao(str(e)))

        threading.Thread(target=trabalho, daemon=True).start()

    def _iniciar_como_cliente(self, host: str, porta: int) -> None:
        self.eh_servidor = False
        self.meu_simbolo = SIMBOLO_CLIENTE
        self._lbl_aguarde.config(text="Conectando ao servidor...")

        def trabalho() -> None:
            try:
                rede = ConexaoRede(
                    ao_conectar=lambda addr: self.root.after(0, lambda: self._ao_conectar(addr)),
                    ao_receber_move=lambda r, c: self.root.after(0, lambda: self._ao_receber_jogada(r, c)),
                    ao_receber_restart=lambda: self.root.after(0, self._ao_receber_restart),
                    ao_desconectar=lambda: self.root.after(0, self._ao_desconectar),
                )
                rede.conectar_cliente(host, porta)
                self.rede = rede
            except OSError as e:
                self.root.after(0, lambda: self._erro_conexao(str(e)))

        threading.Thread(target=trabalho, daemon=True).start()

    def _erro_conexao(self, msg: str) -> None:
        self._lbl_aguarde.config(text="")
        messagebox.showerror("Conexão", f"Não foi possível conectar:\n{msg}")

    def _ao_conectar(self, endereco) -> None:
        """Chamado quando TCP está pronto — monta o tabuleiro e inicia partida."""
        self.conectado = True
        if self._frame_menu:
            self._frame_menu.destroy()
            self._frame_menu = None
        self._montar_tela_jogo(endereco)

    def _montar_tela_jogo(self, endereco) -> None:
        self._frame_jogo = tk.Frame(self.root, padx=16, pady=16)
        self._frame_jogo.pack()

        papel = "Servidor (X)" if self.eh_servidor else "Cliente (O)"
        tk.Label(
            self._frame_jogo,
            text=f"Conectado a {endereco[0]}:{endereco[1]} — Você é {papel}",
            font=("Segoe UI", 10),
        ).pack(pady=(0, 8))

        self._lbl_status = tk.Label(self._frame_jogo, text="", font=("Segoe UI", 11, "bold"))
        self._lbl_status.pack(pady=6)

        grid = tk.Frame(self._frame_jogo)
        grid.pack()
        self._botoes = []
        for r in range(TAMANHO_TABULEIRO):
            linha_btns = []
            for c in range(TAMANHO_TABULEIRO):
                btn = tk.Button(
                    grid,
                    text="",
                    width=4,
                    height=2,
                    font=("Segoe UI", 16, "bold"),
                    command=lambda row=r, col=c: self._clique_celula(row, col),
                )
                btn.grid(row=r, column=c, padx=3, pady=3)
                linha_btns.append(btn)
            self._botoes.append(linha_btns)

        ttk.Button(self._frame_jogo, text="Reiniciar jogo", command=self._pedir_restart).pack(pady=12)

        self._atualizar_interface()

    def _clique_celula(self, linha: int, coluna: int) -> None:
        """Jogador local clica — só aceita se for seu turno."""
        if not self.conectado or not self.rede or not self.meu_simbolo:
            return
        if self.jogo.jogo_terminado:
            return
        if self.jogo.turno_atual != self.meu_simbolo:
            messagebox.showinfo("Aguarde", "Não é o seu turno.")
            return
        if not self.jogo.jogada_valida(linha, coluna):
            return

        if self.jogo.aplicar_jogada(linha, coluna, self.meu_simbolo):
            self.rede.enviar_jogada(linha, coluna)
            self._atualizar_interface()

    def _ao_receber_jogada(self, linha: int, coluna: int) -> None:
        """Oponente jogou — aplica com o símbolo do turno atual na lógica."""
        simbolo_oponente = (
            SIMBOLO_CLIENTE if self.meu_simbolo == SIMBOLO_SERVIDOR else SIMBOLO_SERVIDOR
        )
        if self.jogo.aplicar_jogada(linha, coluna, simbolo_oponente):
            self._atualizar_interface()

    def _pedir_restart(self) -> None:
        if self.rede and self.conectado:
            self.jogo.reiniciar()
            self.rede.enviar_restart()
            self._atualizar_interface()

    def _ao_receber_restart(self) -> None:
        self.jogo.reiniciar()
        self._atualizar_interface()

    def _ao_desconectar(self) -> None:
        self.conectado = False
        if self._lbl_status:
            self._lbl_status.config(text="Conexão encerrada.", fg="red")
        for linha in self._botoes:
            for btn in linha:
                btn.config(state="disabled")

    def _atualizar_interface(self) -> None:
        """Sincroniza botões e rótulo com o estado do JogoDaVelha."""
        if not self._lbl_status:
            return

        for r in range(TAMANHO_TABULEIRO):
            for c in range(TAMANHO_TABULEIRO):
                simbolo = self.jogo.tabuleiro[r][c]
                btn = self._botoes[r][c]
                btn.config(text=simbolo)
                pode_jogar = (
                    self.conectado
                    and not self.jogo.jogo_terminado
                    and self.jogo.turno_atual == self.meu_simbolo
                    and simbolo == ""
                )
                btn.config(state="normal" if pode_jogar else "disabled")

        if self.jogo.jogo_terminado:
            self._lbl_status.config(text=self.jogo.mensagem_status(), fg="green")
        elif self.jogo.turno_atual == self.meu_simbolo:
            self._lbl_status.config(
                text=f"Sua vez ({self.meu_simbolo}) — {self.jogo.mensagem_status()}",
                fg="blue",
            )
        else:
            self._lbl_status.config(
                text=f"Aguardando oponente ({self.jogo.turno_atual})...",
                fg="gray",
            )

    def executar(self) -> None:
        self.root.protocol("WM_DELETE_WINDOW", self._ao_fechar)
        self.root.mainloop()

    def _ao_fechar(self) -> None:
        if self.rede:
            self.rede.encerrar()
        self.root.destroy()


# ---------------------------------------------------------------------------
# PONTO DE ENTRADA
# ---------------------------------------------------------------------------


def main() -> None:
    app = AplicacaoJogoDaVelha()
    app.executar()


if __name__ == "__main__":
    main()
