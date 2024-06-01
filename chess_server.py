import socket
import threading

class ChessServer:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__HOST = "127.0.0.1"
        self.__PORT = 55555
        self.players = {}
        self.count = 0
        self.setup_server()

    def setup_server(self):
        try:
            self.server.bind((self.__HOST, self.__PORT))
        except Exception as e:
            print("Error binding the server:", e)
            return

        self.server.listen()
        print(f"Server listening on {self.__HOST}:{self.__PORT}")

        while True:
            client, address = self.server.accept()

            game_id = self.count // 2
            self.count += 1
            self.handle_player_connection(game_id, client)

    def handle_player_connection(self, game_id, client):
        player_color = 'White' if self.count % 2 == 1 else 'Black'
        client.send(player_color.encode('utf-8'))
        print(f"{player_color} player connected")

        if self.count % 2 == 0:
            self.players[game_id].append(client)
            self.handle_game_start(game_id)
        else:
            self.players[game_id] = [client]

    def handle_game_start(self, game_id):
        player1 = self.players[game_id][0]
        player2 = self.players[game_id][1]
        player1.send('start'.encode('utf-8'))
        player2.send('start'.encode('utf-8'))

        thread_p1_to_p2 = threading.Thread(target=self.thread_client, args=(game_id, player1, player2))
        thread_p1_to_p2.start()
        thread_p2_to_p1 = threading.Thread(target=self.thread_client, args=(game_id, player2, player1))
        thread_p2_to_p1.start()

    def thread_client(self, game_id, sender, receiver):
        while True:
            try:
                data_sender = sender.recv(1024).decode('utf-8')
                receiver.send(data_sender.encode('utf-8'))
                if data_sender == 'reset':
                    print(f"Game ID: {game_id} - Connection lost.")
                    del self.players[game_id]
                    self.count -= 2
                    break
            except (socket.error, BrokenPipeError):
                print(f"Game ID: {game_id} - Connection lost.")
                del self.players[game_id]
                self.count -= 2
                break

if __name__ == "__main__":
    ChessServer()