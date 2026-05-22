import tkinter as tk
from tkinter import messagebox
import socket
import threading
import json

# ==========================================
# 配置常量
# ==========================================
HOST = '127.0.0.1'
PORT = 65432

# ==========================================
# 网络通信层
# ==========================================
class Network:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = None
        self.is_server = False
        self.connected = False

    def start_server(self):
        """启动服务器并等待客户端连接"""
        self.is_server = True
        self.sock.bind((HOST, PORT))
        self.sock.listen(1)
        self.sock.settimeout(1.0) # 设置超时以便可以中断等待
        try:
            while not self.connected:
                try:
                    self.conn, addr = self.sock.accept()
                    self.connected = True
                except socket.timeout:
                    continue
        except KeyboardInterrupt:
            self.sock.close()

    def start_client(self):
        """作为客户端连接到服务器"""
        self.is_server = False
        try:
            self.sock.connect((HOST, PORT))
            self.conn = self.sock
            self.connected = True
        except Exception as e:
            print(f"Connection failed: {e}")

    def send_data(self, data):
        """发送JSON格式的数据"""
        if self.conn:
            try:
                msg = json.dumps(data).encode('utf-8')
                # 添加长度前缀，防止粘包
                length = len(msg).to_bytes(4, 'big')
                self.conn.sendall(length + msg)
            except:
                pass

    def receive_data(self):
        """接收数据"""
        if not self.conn:
            return None
        try:
            # 先读取4字节的长度
            length_bytes = self._recv_exact(4)
            if not length_bytes:
                return None
            length = int.from_bytes(length_bytes, 'big')
            # 读取相应长度的数据
            data_bytes = self._recv_exact(length)
            if data_bytes:
                return json.loads(data_bytes.decode('utf-8'))
            return None
        except:
            return None

    def _recv_exact(self, n):
        """精确接收n个字节"""
        data = b''
        while len(data) < n:
            packet = self.conn.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def close(self):
        """关闭连接"""
        self.connected = False
        if self.conn:
            self.conn.close()
        self.sock.close()

# ==========================================
# 游戏逻辑层
# ==========================================
class GameLogic:
    def __init__(self):
        self.board = [''] * 9
        self.current_turn = 'X' # X 总是先手
        self.winner = None
        self.game_over = False

    def make_move(self, index, player):
        """尝试在指定位置落子"""
        if self.board[index] == '' and not self.game_over and self.current_turn == player:
            self.board[index] = player
            if self.check_win(player):
                self.winner = player
                self.game_over = True
            elif self.check_draw():
                self.game_over = True
            else:
                # 切换回合
                self.current_turn = 'O' if player == 'X' else 'X'
            return True
        return False

    def check_win(self, player):
        """检查是否有玩家获胜"""
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], # 行
            [0, 3, 6], [1, 4, 7], [2, 5, 8], # 列
            [0, 4, 8], [2, 4, 6]             # 对角线
        ]
        for condition in win_conditions:
            if all(self.board[i] == player for i in condition):
                return True
        return False

    def check_draw(self):
        """检查是否平局"""
        return '' not in self.board and not self.winner

    def reset(self):
        """重置游戏状态"""
        self.board = [''] * 9
        self.current_turn = 'X'
        self.winner = None
        self.game_over = False

# ==========================================
# 用户界面层
# ==========================================
class TicTacToeUI:
    def __init__(self, root, network, logic, my_symbol):
        self.root = root
        self.network = network
        self.logic = logic
        self.my_symbol = my_symbol
        
        self.root.title(f"Jogo da Velha - Jogador {self.my_symbol}")
        self.root.resizable(False, False)

        # 界面组件
        self.status_label = tk.Label(root, text="", font=('Arial', 14))
        self.status_label.pack(pady=10)

        self.board_frame = tk.Frame(root)
        self.board_frame.pack()

        self.buttons = []
        for i in range(9):
            btn = tk.Button(self.board_frame, text='', font=('Arial', 24), width=4, height=2,
                            command=lambda idx=i: self.on_click(idx))
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
            self.buttons.append(btn)

        self.restart_btn = tk.Button(root, text="Reiniciar Jogo", font=('Arial', 12), command=self.restart_game)
        self.restart_btn.pack(pady=10)

        self.update_ui()

        # 启动接收消息的线程
        self.receive_thread = threading.Thread(target=self.receive_loop, daemon=True)
        self.receive_thread.start()

    def on_click(self, index):
        """处理按钮点击事件"""
        # 只有在自己的回合且游戏未结束时才能点击
        if self.logic.current_turn == self.my_symbol and not self.logic.game_over:
            if self.logic.make_move(index, self.my_symbol):
                # 发送落子信息给对方
                self.network.send_data({"action": "move", "index": index})
                self.update_ui()

    def restart_game():
        """请求重新开始游戏"""
        self.logic.reset()
        self.network.send_data({"action": "restart"})
        self.update_ui()

    def receive_loop(self):
        """持续监听网络消息"""
        while self.network.connected:
            data = self.network.receive_data()
            if data:
                # 在主线程中更新UI
                self.root.after(0, self.process_data, data)
            else:
                # 连接断开
                self.root.after(0, self.handle_disconnect)
                break

    def process_data(self, data):
        """处理接收到的数据"""
        if data["action"] == "move":
            opponent_symbol = 'O' if self.my_symbol == 'X' else 'X'
            self.logic.make_move(data["index"], opponent_symbol)
            self.update_ui()
        elif data["action"] == "restart":
            self.logic.reset()
            self.update_ui()

    def handle_disconnect(self):
        """处理断开连接"""
        self.status_label.config(text="Oponente desconectou!")
        for btn in self.buttons:
            btn.config(state=tk.DISABLED)

    def update_ui(self):
        """更新界面显示"""
        for i in range(9):
            self.buttons[i].config(text=self.logic.board[i])
            if self.logic.board[i] != '' or self.logic.game_over:
                self.buttons[i].config(state=tk.DISABLED)
            else:
                self.buttons[i].config(state=tk.NORMAL)

        if self.logic.game_over:
            if self.logic.winner:
                if self.logic.winner == self.my_symbol:
                    self.status_label.config(text="Você Venceu! 🎉")
                else:
                    self.status_label.config(text="Você Perdeu! 😢")
            else:
                self.status_label.config(text="Empate! 🤝")
        else:
            if self.logic.current_turn == self.my_symbol:
                self.status_label.config(text="Sua vez!")
            else:
                self.status_label.config(text="Aguardando oponente...")

# ==========================================
# 主程序入口
# ==========================================
def main():
    # 启动选择对话框
    choice = input("Digite 's' para Servidor ou 'c' para Cliente: ").strip().lower()
    
    network = Network()
    logic = GameLogic()

    print("Conectando...")
    if choice == 's':
        network.start_server()
        my_symbol = 'X' # 服务器为 X
    else:
        network.start_client()
        my_symbol = 'O' # 客户端为 O

    if network.connected:
        print("Conectado! Iniciando jogo...")
        root = tk.Tk()
        app = TicTacToeUI(root, network, logic, my_symbol)
        root.mainloop()
        network.close()
    else:
        print("Falha ao conectar.")

if __name__ == "__main__":
    main()

