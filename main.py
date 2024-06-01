"""
    Project        :   Chess
    Date           :   14-10-2023
    Author         :   Seyf Eddine
    Contact        :   seyfeddine.freelance@gmail.com
    Python Ver.    :   3.11
"""

import socket
import time
import threading
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from tokenize import group

class MainWindow:
    def __init__(self, root):
        width, height = (768, 544)
        x = root.winfo_screenwidth() - width
        y = root.winfo_screenheight() - height - 74
        root.geometry(f"{width}x{height}+{int(x/2)}+{int(y/2)}")
        root.resizable(False, False)
        root.title('Chess')
        root.iconphoto(False, tk.PhotoImage(file='img\\icon.png'))
        root.protocol('WM_DELETE_WINDOW', lambda:self.exit(root))
        root.focus_force()

        self.run = True
        self.play_mode = tk.IntVar()

        self.Master = tk.Frame(root, padx=10, pady=10) 
        self.Master.pack(side='top', fill='none', expand=True)
        self.chess_board = ChessBoard(self.Master)

        frame1 = tk.Frame(root, bg='#fff', pady=5)
        frame1.pack(side='top', fill='x')        
        self.logo = tk.PhotoImage(file='img\\logo.png')
        tk.Label(frame1, textvariable=self.chess_board.state.current_turn_var, bg='#fff', fg='#44b79b', justify='left', font=('Bahnschrift SemiBold SemiConden', 14, 'bold')).pack(side='left', fill='x', expand=True)
        tk.Button(frame1, width=8, text='Exit', fg='#FFFFFF', bg='#345', activebackground='#345', activeforeground='#FFFFFF', font=('Bahnschrift SemiBold SemiConden', 10, 'bold'), relief='flat', command=lambda:self.exit(root)).pack(side='right', fill='none', padx=5)
        tk.Button(frame1, width=10, text='Reset', fg='#FFFFFF', bg='#44b79b', activebackground='#44b79b', activeforeground='#FFFFFF', font=('Bahnschrift SemiBold SemiConden', 10, 'bold'), relief='flat', command=lambda:self.reset()).pack(side='right', fill='none', padx=0)
        self.top_windows(root)

    def top_windows(self, root):
        master = tk.Toplevel()
        width = 550
        height = 250
        x = int(root.winfo_x() + (root.winfo_width() - width)/2)
        y = int(root.winfo_y() + (root.winfo_height() - height)/2)

        master.geometry(f"{width}x{height}+{x}+{y}")
        master.minsize(width, height)
        master.wm_overrideredirect(True)
        master.configure(background='#fff', pady=10, highlightbackground='#000', highlightthickness=1)
        master.focus_force()
        master.grab_set()

        master.grid_columnconfigure((0, 1, 2, 3), minsize=60) 
        master.grid_columnconfigure((1, 2), weight=1) 
        master.grid_rowconfigure((0, 4), minsize=10)
        master.grid_rowconfigure(1, weight=1)

        frame1 = tk.Frame(master, bg='#fff')
        frame1.grid(row=1, column=1, columnspan=2, padx=10, pady=0, sticky='ns')

        self.logo = tk.PhotoImage(file='img\\logo.png')

        tk.Label(frame1, text='', image=self.logo, anchor='center', bg='#fff').pack(side='left')
        tk.Label(frame1, text='Play Chess', bg='#fff', fg='#44b79b', justify='left', font=('Bahnschrift SemiBold SemiConden', 18, 'bold')).pack(side='left')

        self.play_button = tk.Button(master, text='Play', fg='#FFFFFF', bg='#44b79b', activebackground='#44b79b', activeforeground='#FFFFFF', font=('Bahnschrift SemiBold SemiConden', 14, 'bold'), relief='flat')
        self.play_button.grid(row=3, column=2, padx=6, pady=12, sticky='ew')
        self.play_button.config(command=lambda:self.start(master))
        tk.Checkbutton(master, text='Play Online', bg='#ffffff', activebackground='#FFFFFF', variable=self.play_mode, onvalue=1, offvalue=0).grid(row=2, column=1, columnspan=2, sticky='ew')

        tk.Button(master, text='Exit', fg='#FFFFFF', bg='#345', activebackground='#345', activeforeground='#FFFFFF', font=('Bahnschrift SemiBold SemiConden', 14, 'bold'), relief='flat', command=lambda:self.exit(root)).grid(row=3, column=1, padx=6, pady=12, sticky='ew')
        root.update()

    def client_connection(self, host="127.0.0.1", port=55555):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((host, port))
            data = client.recv(1024).decode('utf-8')
            self.chess_board.player = data
            data = client.recv(1024).decode('utf-8')
            if data == 'start':
                HandleThread = threading.Thread(target=self.handle_connection, args=(client,))
                HandleThread.start()
            else:
                raise Exception('No player connected, try again later.')
        except Exception as e:
            print("No server found, starting as server.", e)
            client.close()
            raise e

    def handle_connection(self, client):
        self.chess_board.client = client
        try: 
            while self.run:
                data = client.recv(1024).decode('utf-8')
                if data == 'reset':
                    for widget in self.Master.winfo_children():
                        widget.destroy()
                    self.chess_board = ChessBoard(self.Master)
                    self.top_windows(root)

                elif self.chess_board.player == self.chess_board.state.last_player:
                    try: 
                        source_pos, target_pos = data.split(';')
                        source_pos = tuple(map(lambda x: 7-int(x) if x.isdigit() else x.lower() == 'true', source_pos.strip('()').split(', ')))
                        target_pos = tuple(map(lambda x: 7-int(x) if x.isdigit() else x.lower() == 'true', target_pos.strip('()').split(', ')))
                        self.chess_board.move_piece(source_pos, target_pos)
                    except Exception as e:
                        messagebox.showinfo(title='Error', message=f'Hi, there are some problem\n{e}')
                time.sleep(0.6)
        except Exception as e:
            messagebox.showinfo(title='Error', message=f'Hi, there are some problem\n{e}')
        finally:
            for widget in self.Master.winfo_children():
                widget.destroy()
            self.chess_board = ChessBoard(self.Master)
            self.top_windows(root)
            
    def reset(self):
        Reset = messagebox.askyesno('Chess', 'Are you sure you want to reset Chess?')
        if Reset > 0:
            self.chess_board.reset_game()
            for widget in self.Master.winfo_children():
                widget.destroy()
            self.chess_board = ChessBoard(self.Master)
            self.top_windows(root)

    def start(self, topleval):
        if self.play_mode.get() == 1:
            self.play_button.config(state='disabled')
            try:
                self.client_connection()
            except Exception as e:
                messagebox.showinfo(title='Error', message=f'Hi, there are some problem\n{e}')
                self.play_button.config(state='normal')
                return
            
        self.chess_board.play_mode = self.play_mode.get()
        self.chess_board.setup_pieces()
        topleval.destroy()
        self.chess_board.state.start = True
        self.chess_board.state.thread_ground_time(self.chess_board.player)
        return
            
    def exit(self, root):
        Exit = messagebox.askyesno('Chess', 'Are you sure you want to close Chess?')
        if Exit > 0:
            self.chess_board.reset_game()
            self.chess_board.state.start = False
            self.run = False
            time.sleep(1.001)
            root.destroy()
            time.sleep(.2)
            return
        
#============================================================================================= 
class GameState():
    def __init__(self, master):
        self.player = 'white'
        self.player1 = tk.StringVar(value='player1') 
        self.player2 = tk.StringVar(value='player2')
        
        self.start = False
        self.last_player = 'Black'
        self.current_player = 'White'
        self.move_history = []  # A list of moves made in the game

        self.check = False
        self.checkmate = False
        self.stalemate = False

        self.captured_piece1 = 0
        self.captured_piece2 = 0
        self.timer1 = tk.StringVar(value='00:00:00')
        self.timer2 = tk.StringVar(value='00:00:00')
        self.current_turn_var = tk.StringVar(value="Current Turn: White")

        self.setup_state_frame(master)

    def setup_state_frame(self, master):
        state_frame = tk.Frame(master, highlightbackground='#D7D7D7', highlightthickness=1) 
        state_frame.pack(side='right', fill='y', expand=True, padx=(10,0))
        state_frame.grid_columnconfigure((0, 1, 2), minsize=79) 
        state_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), minsize=20)
        state_frame.grid_rowconfigure(3, weight=1)

        tk.Label(state_frame, fg='#FFFFFF', bg='#44b79b', textvariable=self.timer2, font=('Bahnschrift SemiBold SemiConden', 12, 'bold')).grid(row=0, column=0, sticky='nsew')
        tk.Label(state_frame, bg='#FFFFFF', fg='#44b79b', textvariable=self.player2, font=('Bahnschrift SemiBold SemiConden', 12, 'bold')).grid(row=0, column=1, columnspan=2, sticky='nsew')
        self.canvas2 = tk.Canvas(state_frame, width=250, height=50, highlightbackground='#D7D7D7', highlightthickness=1)
        self.canvas2.grid(row=1, column=0, columnspan=3, sticky='nsew')
        
        # self.moves_history_text = tk.Text(state_frame, width=28, height=10, state='disabled')
        # self.moves_history_text.grid(row=3, column=0, columnspan=3, sticky='ns')

        self.canvas1 = tk.Canvas(state_frame, width=250, height=50, highlightbackground='#D7D7D7', highlightthickness=1)
        self.canvas1.grid(row=5, column=0, columnspan=3, sticky='nsew')
        tk.Label(state_frame, fg='#FFFFFF', bg='#44b79b', textvariable=self.timer1, font=('Bahnschrift SemiBold SemiConden', 12, 'bold')).grid(row=6, column=0, sticky='nsew')
        tk.Label(state_frame, bg='#FFFFFF', fg='#44b79b', textvariable=self.player1, font=('Bahnschrift SemiBold SemiConden', 12, 'bold')).grid(row=6, column=1, columnspan=2, sticky='nsew')

    def thread_ground_time(self, player):
        self.player = player
        if self.player == 'White':
            self.player1.set('White')
            self.player2.set('Black')
        else:
            self.player1.set('Black')
            self.player2.set('White')
        shutdown_event = threading.Event()
        shutdown_event.set()
        TimerThread = threading.Thread(target=self.count_timer)
        TimerThread.start()

    def count_timer(self):
        time.sleep(0.01)
        while self.start:
            try:
                if self.player == 'White':
                    if self.last_player == 'Black':
                        timer = datetime.strptime(self.timer1.get(), '%H:%M:%S') + timedelta(seconds=1)
                        self.timer1.set(timer.strftime('%H:%M:%S'))
                        self.current_turn_var.set("Current Turn: White")
                    else:
                        timer = datetime.strptime(self.timer2.get(), '%H:%M:%S') + timedelta(seconds=1)
                        self.timer2.set(timer.strftime('%H:%M:%S'))
                        self.current_turn_var.set("Current Turn: Black")
                else:
                    if self.last_player == 'White':
                        timer = datetime.strptime(self.timer1.get(), '%H:%M:%S') + timedelta(seconds=1)
                        self.timer1.set(timer.strftime('%H:%M:%S'))
                        self.current_turn_var.set("Current Turn: Black")
                    else:
                        timer = datetime.strptime(self.timer2.get(), '%H:%M:%S') + timedelta(seconds=1)
                        self.timer2.set(timer.strftime('%H:%M:%S'))
                        self.current_turn_var.set("Current Turn: White")
                time.sleep(1)
            except Exception as e:
                print(str(e))
                break

    def show_captured_piece(self, piece_image):
        if self.player == 'White':
            if self.last_player == 'Black':
                self.canvas1.create_image(20+12*self.captured_piece1, 50, anchor='s', image=piece_image)
                self.captured_piece1 += 1
            else:
                self.canvas2.create_image(20+12*self.captured_piece2, 50, anchor='s', image=piece_image)
                self.captured_piece2 += 1  
        else:
            if self.last_player == 'White':
                self.canvas1.create_image(20+12*self.captured_piece1, 50, anchor='s', image=piece_image)
                self.captured_piece1 += 1
            else:
                self.canvas2.create_image(20+12*self.captured_piece2, 50, anchor='s', image=piece_image)
                self.captured_piece2 += 1        

    def show_moves_history(self):
        # Display moves history in the Text widget
        moves_history = "\n".join(self.move_history)
        self.moves_history_text.delete('1.0', tk.END)
        self.moves_history_text.insert(tk.END, moves_history)    

class ChessBoard():
    def __init__(self, master):
        self.play_mode = 0
        self.player = 'White'
        self.board = []
        self.pieces = {}

        self.selected_square = None
        self.selected_pos = (None, None, None)
        self.last_moved_piece = ''

        self.valid_moves = []
        self.compulsory_moves = []

        self.state = GameState(master)
        self.tooltip = None
        self.setup_board(master)
 
    def setup_board(self, master):
        board_frame = tk.Frame(master) 
        cols = [i for i in range(8)]
        rows = [i for i in range(8)]
        board_frame.pack(side='top', fill='none', expand=True)
        board_frame.grid_columnconfigure(cols, minsize=60) 
        board_frame.grid_rowconfigure(rows, minsize=60)
        for row in rows:
            row_board = []
            for col in cols:
                bg_color = '#fff' if ((row%2 == 0 and col%2 == 0) or (row%2 == 1 and col%2 == 1)) else '#999'
                square = tk.Label(board_frame, bg=bg_color)
                square.grid(row=row, column=col, sticky='nsew')
                square.identifier = None
                square.bind('<ButtonPress-1>', lambda e, row=row, col=col: self.on_square_click(e, row, col))
                row_board.append(square)
            self.board.append(row_board)
        self.check_lab = tk.Label(board_frame, width=6, text='check', bg='#fde9a9', fg='#ff6d6d', font=('Courier', 8, 'bold'))

    def setup_pieces(self):
        if self.player == 'Black':
            self.pieces = {
                'White': {
                   "wR2": Rook("White", "wR2"), "wN2": Knight("White", "wN2"), "wB2": Bishop("White", "wB2"), "wK": King("White", "wK"), "wQ": Queen("White", "wQ"), "wB1": Bishop("White", "wB1"), "wN1": Knight("White", "wN1"), "wR1": Rook("White", "wR1"),
                   **{"wP" + str(8-i): Pawn("White", "wP" + str(8-i)) for i in range(0, 8)}
                },
                'Black': {
                    **{"bP" + str(8-i): Pawn("Black", "bP" + str(8-i)) for i in range(0, 8)},
                    "bR2": Rook("Black", "bR2"), "bN2": Knight("Black", "bN2"), "bB2": Bishop("Black", "bB2"), "bK": King("Black", "bK"), "bQ": Queen("Black", "bQ"), "bB1": Bishop("Black", "bB1"), "bN1": Knight("Black", "bN1"), "bR1": Rook("Black", "bR1")
                }
            }
        else:
            self.pieces = {
                'Black': {
                    "bR1": Rook("Black", "bR1"), "bN1": Knight("Black", "bN1"), "bB1": Bishop("Black", "bB1"), "bQ": Queen("Black", "bQ"), "bK": King("Black", "bK"), "bB2": Bishop("Black", "bB2"), "bN2": Knight("Black", "bN2"), "bR2": Rook("Black", "bR2"),
                    **{"bP" + str(i+1): Pawn("Black", "bP" + str(i+1)) for i in range(8)}
                },
                'White': {
                    **{"wP" + str(i+1): Pawn("White", "wP" + str(i+1)) for i in range(8)},
                    "wR1": Rook("White", "wR1"), "wN1": Knight("White", "wN1"), "wB1": Bishop("White", "wB1"), "wQ": Queen("White", "wQ"), "wK": King("White", "wK"), "wB2": Bishop("White", "wB2"), "wN2": Knight("White", "wN2"), "wR2": Rook("White", "wR2")
                }
            }
        x = 0
        for color in self.pieces:
            for j, piece in enumerate(self.pieces[color].values()):
                piece.set_position(self.pieces, self.board, ((j+x)//8, (j+x)%8, False))
            x = 48
        return

    def reset_game(self):
        if self.play_mode == 1:
            text = 'reset'
            self.client.send(text.encode('utf-8'))

    def on_square_click(self, event, row, col):
        if self.player != self.state.last_player or self.play_mode != 1:
            clicked_square = self.board[row][col]
            if self.selected_square:
                if clicked_square != self.selected_square:
                    if self.is_valid_move((row, col)):
                        if self.state.check:
                            self.state.check = False
                            self.check_lab.place_forget()
                        new_pos = self.is_valid_move((row, col))
                        self.move_piece(self.selected_pos, new_pos)
                        if self.play_mode == 1:
                            move = ';'.join([str(self.selected_pos), str(new_pos)])
                            self.client.send(move.encode('utf-8'))
                self.hide_valid_moves()
                self.selected_square = None
                
            if clicked_square.cget('image') and clicked_square.identifier:
                if clicked_square.identifier[0].lower() != self.state.last_player[0].lower():
                    clicked_square.config(bg='#FFEEA3')
                    self.selected_square = clicked_square
                    self.selected_pos = (row, col, False)
                    piece = self.pieces[self.state.current_player][clicked_square.identifier]
                    piece_moves = piece.valid_moves(self.board, self.pieces)

                    if self.state.check:
                        if piece.piece_type!='King':
                            piece_moves = list(set(piece_moves) & set(self.compulsory_moves))

                    self.valid_moves = piece.test_valid_moves(self.pieces, self.board, piece_moves, self.state.check)
                    self.show_valid_moves()
                            
    def is_valid_move(self, target_pos):
        for item in self.valid_moves:
            if item[:len(target_pos)] == target_pos:
                return item
        return None

    def pawn_promotion(self, piece):
        master = tk.Toplevel()
        width = 260
        height = 80
        x = int(root.winfo_x() + (root.winfo_width() - width)/3)
        y = int(root.winfo_y() + (root.winfo_height() - height)/2)
        master.geometry(f"{width}x{height}+{x}+{y}")
        master.minsize(width, height)
        master.wm_overrideredirect(True)
        master.configure(background='#fff', padx=10, pady=10, highlightbackground='#000', highlightthickness=1)
        master.focus_force()
        master.grab_set()
        master.grid_columnconfigure((0, 1, 2, 3), weight=1, minsize=60) 
        master.grid_rowconfigure((0), weight=1, minsize=60)

        def set_promrtion(type):
            _id = piece.identifier
            color = piece.color
            if type == 'Queen':
                self.pieces[color][_id] = Queen(color, _id)
            elif type == 'Knight':
                self.pieces[color][_id] = Knight(color, _id)
            elif type == 'Bishop':
                self.pieces[color][_id] = Bishop(color, _id)
            elif type == 'Rook':
                self.pieces[color][_id] = Rook(color, _id)

            r, c = piece.position
            self.pieces[color][_id].set_position(self.pieces, self.board, (r, c, False))
            master.destroy()

        if piece.color == 'White':
            self._img1 = tk.PhotoImage(file='img\\w_queen.png')
            self._img2 = tk.PhotoImage(file='img\\w_knight.png')
            self._img3 = tk.PhotoImage(file='img\\w_rook.png')
            self._img4 = tk.PhotoImage(file='img\\w_bishop.png')
            tk.Button(master, image=self._img1, bg='#FFFFFF', activebackground='#FFFFFF', relief='flat', command=lambda:set_promrtion('Queen')).grid(row=0, column=0, sticky='nsew')
            tk.Button(master, image=self._img2, bg='#FFFFFF', activebackground='#FFFFFF', relief='flat', command=lambda:set_promrtion('Knight')).grid(row=0, column=1, sticky='nsew')
            tk.Button(master, image=self._img3, bg='#FFFFFF', activebackground='#FFFFFF', relief='flat', command=lambda:set_promrtion('Rook')).grid(row=0, column=2, sticky='nsew')
            tk.Button(master, image=self._img4, bg='#FFFFFF', activebackground='#FFFFFF', relief='flat', command=lambda:set_promrtion('Bishop')).grid(row=0, column=3, sticky='nsew')
        else:
            self._img1 = tk.PhotoImage(file='img\\b_queen.png')
            self._img2 = tk.PhotoImage(file='img\\b_knight.png')
            self._img3 = tk.PhotoImage(file='img\\b_rook.png')
            self._img4 = tk.PhotoImage(file='img\\b_bishop.png')
            tk.Button(master, image=self._img1, bg='#FFFFFF', activebackground='#FFFFFF', relief='flat', command=lambda:set_promrtion('Queen')).grid(row=0, column=0, sticky='nsew')
            tk.Button(master, image=self._img2, bg='#FFFFFF', activebackground='#FFFFFF', relief='flat', command=lambda:set_promrtion('Knight')).grid(row=0, column=1, sticky='nsew')
            tk.Button(master, image=self._img3, bg='#FFFFFF', activebackground='#FFFFFF', relief='flat', command=lambda:set_promrtion('Rook')).grid(row=0, column=2, sticky='nsew')
            tk.Button(master, image=self._img4, bg='#FFFFFF', activebackground='#FFFFFF', relief='flat', command=lambda:set_promrtion('Bishop')).grid(row=0, column=3, sticky='nsew')

    def show_valid_moves(self):
        if self.valid_moves:
            for pos in self.valid_moves:
                row, col, taking = pos
                if (row%2 == 0 and col%2 == 0) or (row%2 == 1 and col%2 == 1):
                    bg_color = '#ff6d6d' if taking else '#9cef69'
                else:
                    bg_color = '#ff0000' if taking else '#4ccb00'
                square = self.board[row][col]
                square.config(bg=bg_color)

    def hide_valid_moves(self):
        moves = self.valid_moves + [self.selected_pos]
        if moves:
            for pos in moves:
                row, col, taking = pos
                bg_color = '#fff' if (row%2 == 0 and col%2 == 0) or (row%2 == 1 and col%2 == 1) else '#999'
                square = self.board[row][col]
                square.config(bg=bg_color)
        
    def move_piece(self, source_pos, target_pos):
        color = self.state.current_player
        row, col, _ = source_pos
        source_square = self.board[row][col]
        identifier = source_square.identifier
        piece = self.pieces[color][identifier]

        bg_color = '#fff' if (row%2 == 0 and col%2 == 0) or (row%2 == 1 and col%2 == 1) else '#999'
        source_square.config(bg=bg_color)
        source_square.config(image='')
        source_square.image = None
        source_square.identifier = None
        
        if color == 'White':
            self.state.current_player = 'Black'
        else:
            self.state.current_player = 'White'

        r, c, t = target_pos
        if t:
            captured_piece = self.board[r][c]
            _id = captured_piece.identifier
            _img = captured_piece.cget('image')
            if isinstance(piece, Pawn):
                if piece.en_passant == (r-piece.direction, c, t): 
                    captured_piece = self.board[piece.en_passant[0]][piece.en_passant[1]]
                    _img = captured_piece.cget('image')
                    captured_piece.config(image='')
                    captured_piece.image = None
                    _id = captured_piece.identifier
                    captured_piece.identifier = None
                    piece.en_passant = (None, None, None)
                piece.column_changed = True

            captured_piece = self.pieces[self.state.current_player][_id]
            captured_piece.captured = True
            captured_piece.position = (None, None)
            self.state.show_captured_piece(_img)        
        piece.set_position(self.pieces, self.board, target_pos)
        
        if isinstance(piece, Pawn) and (r==0 or r==7):
            self.pawn_promotion(piece)

        self.state.last_player = piece.color
        self.is_king_in_check()

    def is_king_in_check(self):
        if self.state.current_player == 'Black':
            r, c = self.pieces['Black']['bK'].position
            wenner = 'Black'
            color = 'White'
        else:
            r, c = self.pieces['White']['wK'].position
            wenner = 'White'
            color = 'Black'

        self.compulsory_moves = self.get_compulsory_moves(color, (r, c))

        if self.state.check:
            if self.compulsory_moves:
                self.set_check(r, c)
            if self.state.checkmate:
                self.set_checkmate(wenner)
        else:
            if self.state.stalemate:
                self.set_stalemate()

    def get_compulsory_moves(self, color, King_pos):
        r, c = King_pos
        compulsory_moves = []
        all_valid_moves = []
        for piece in self.pieces[color].values():
            if not piece.captured:
                _valid_moves = piece.valid_moves(self.board, self.pieces)
                if (r, c, True) in _valid_moves:
                    self.state.check = True
                    x, y = piece.position 
                    positions_between = self.get_positions_between((x, y), (r, c))
                    compulsory_moves.extend(positions_between)
                    if piece.piece_type != 'King':
                        compulsory_moves.append((x, y, True))
                if piece.piece_type == 'King':
                    king_move = _valid_moves

                all_valid_moves.extend(_valid_moves)

        # need logic for checkmate or stalemate
        self.state.checkmate = False
        self.state.stalemate = False 
        return compulsory_moves

    def get_positions_between(self, start, end):
        positions_between = []
        if start[0] == end[0]:
            step = 1 if start[1] < end[1] else -1
            positions_between = [(start[0], col, False) for col in range(start[1] + step, end[1], step)]
        elif start[1] == end[1]:
            step = 1 if start[0] < end[0] else -1
            positions_between = [(row, start[1], False) for row in range(start[0] + step, end[0], step)]
        elif abs(start[0] - end[0]) == abs(start[1] - end[1]):
            row_step = 1 if start[0] < end[0] else -1
            col_step = 1 if start[1] < end[1] else -1
            positions_between = [(start[0] + i * row_step, start[1] + i * col_step, False) for i in range(1, abs(start[0] - end[0]))]    
        return positions_between

    def set_check(self, r, c):
        x = c * 60 + 5
        y = r * 60 + 22
        self.check_lab.place(x=x, y=y)

    def set_checkmate(self, color):
        self.state.checkmate = True
        messagebox.showinfo("Game Over", f"Checkmate! {color} wins the game.")
    
    def set_stalemate(self):
        messagebox.showinfo("Game Over", "Stalemate! The game is a draw.")
           

class ChessPiece():
    def __init__(self, color, piece_type, identifier):
        self.color = color
        self.piece_type = piece_type
        self.identifier = identifier
        self.piece_img = None
        self.position = (None, None)
        self.moves_counter = -1
        self.captured = False

    def set_position(self, pieces, board, pos):
        r, c, t = pos
        board[r][c].config(image=self.piece_img)
        board[r][c].image = self.piece_img
        board[r][c].identifier = self.identifier 

        if isinstance(self, King) and self.moves_counter == 0:
            self.king_rook_switch(pieces, board, r, c)

        if isinstance(self, Pawn):
            if self.moves_counter == -1:
                if r == 1: self.direction = 1 
                elif r == 6: self.direction = -1
            elif self.moves_counter == 0:
                for offset in [-1, 1]:
                    target_col = c + offset
                    if self.is_valid_square(r, target_col) and self.is_opponent_piece(board, r, target_col, self.color):
                        color_pawn = 'White' if self.color == 'Black' else 'Black'
                        my_pawn = board[r][target_col].identifier
                        my_pawn = pieces[color_pawn][my_pawn]
                        if isinstance(my_pawn, Pawn) and my_pawn.moves_counter == 2:
                            my_pawn.en_passant = (r, c, True)
                            print(my_pawn, my_pawn.column_changed)
            else:
                self.en_passant = (None, None, None)     

        self.position = (r, c)
        self.moves_counter += 1

    def king_rook_switch(self, pieces, board, r, c):
        if (self.position[0], self.position[1] + 2) == (r, c):
            rook_img = board[r][7].cget('image')
            board[r][c-1].config(image=rook_img)
            board[r][c-1].image = rook_img
            board[r][c-1].identifier = board[r][7].identifier 
            pieces[self.color][board[r][7].identifier].position = (r, c-1)
            board[r][7].config(image='')
            board[r][7].image = None
            board[r][7].identifier = None 
        elif (self.position[0], self.position[1] - 2) == (r, c):
            rook_img = board[r][0].cget('image')
            board[r][c+1].config(image=rook_img)
            board[r][c+1].image = rook_img
            board[r][c+1].identifier = board[r][0].identifier 
            pieces[self.color][board[r][0].identifier].position = (r, c+1)
            board[r][0].config(image='')
            board[r][0].image = None
            board[r][0].identifier = None 

    def is_valid_square(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8
    
    def is_square_empty(self, board, row, col):
        return board[row][col].identifier is None

    def is_opponent_piece(self, board, row, col, color):
        piece = board[row][col]
        if piece.identifier is not None:
            if piece.identifier[0].lower() != color[0].lower():
                return True
        return False
    
    def global_moves(self, board, directions):
        moves = []
        row, col = self.position

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while self.is_valid_square(r, c):
                if self.is_square_empty(board, r, c):
                    moves.append((r, c, False))
                elif self.is_opponent_piece(board, r, c, self.color):
                    moves.append((r, c, True))
                    break
                else:
                    break
                r, c = r + dr, c + dc
        return moves
    
    def test_valid_moves(self, pieces, board, piece_moves, check):
        all_opponent_moves = []
        if piece_moves:
            if self.color == 'White':
                king_x, king_y = pieces['White']['wK'].position
                opponent_color = 'Black'
            else:
                king_x, king_y = pieces['Black']['bK'].position
                opponent_color = 'White'

            _id = self.identifier
            prohibited_moves = []
            for move in piece_moves:
                simulated_pieces = self.copy_pieces(pieces)
                simulated_board = self.copy_board(board)
                my_piece = simulated_pieces[self.color][_id]
                
                x, y, t = move
                r, c = my_piece.position
                _identifier = simulated_board[x][y].identifier
                 
                simulated_board[x][y].identifier = _id
                my_piece.position = (x, y)

                simulated_board[r][c].identifier = None

                if _identifier:
                    simulated_pieces[opponent_color][_identifier].captured = True
                    simulated_pieces[opponent_color][_identifier].position = (None, None)

                opponent_moves = my_piece.opponent_valid_moves(simulated_board, simulated_pieces, opponent_color)                                    
                all_opponent_moves.extend(opponent_moves)

                if isinstance(self, King):
                    king_x, king_y = x, y
                if (king_x, king_y, True) in opponent_moves:
                    prohibited_moves.append(move)

            piece_moves = list(set(piece_moves) - set(prohibited_moves))
            all_opponent_moves = list(set(all_opponent_moves))

            if isinstance(self, King):
                if self.moves_counter == 0:
                    r, c = self.position
                    if ((r, c+1, False) not in piece_moves or check or (r, 7, True) in all_opponent_moves) and ((r, c+2, False) in piece_moves): 
                        piece_moves.remove((r, c+2, False))
                    if ((r, c-1, False) not in piece_moves or check or (r, 0, True) in all_opponent_moves) and ((r, c-2, False) in piece_moves):
                        piece_moves.remove((r, c-2, False))

        return piece_moves
    
    def opponent_valid_moves(self, board, pieces, opponent_color):
        valid_moves = []
        def tread_fun():
            piece_moves = piece.valid_moves(board, pieces) 
            valid_moves.extend(piece_moves)

        threads = []
        for piece in pieces[opponent_color].values():
            if not piece.captured:
                thread = threading.Thread(target=tread_fun)
                threads.append(thread)
                thread.start()
        for thread in threads:
            thread.join()
            
        valid_moves = list(set(valid_moves))
        return valid_moves
    
    def copy_pieces(self, pieces):
        new_pieces = {}
        for _color, _group in pieces.items():
            new_group = {}
            for key, piece in _group.items():
                new_piece = piece.__class__(piece.color, piece.identifier)
                for attr_name, attr_value in vars(piece).items():
                    setattr(new_piece, attr_name, attr_value)
                new_group[key] = new_piece
            new_pieces[_color] = new_group
        return new_pieces
    
    def copy_board(self, board):
        new_board = []
        cols = [i for i in range(8)]
        rows = [i for i in range(8)]
        for row in rows:
            row_board = []
            for col in cols:
                original_square = board[row][col]
                square = Square(original_square.identifier) 
                row_board.append(square)
            new_board.append(row_board)
        return new_board
    
    def __str__(self):
        return f"{self.identifier} : {self.color} {self.piece_type} at {self.position}"


class Square():
    def __init__(self, identifier=None):
        self.identifier = identifier


class Pawn(ChessPiece):
    def __init__(self, color, identifier):
        super().__init__(color, "Pawn", identifier)
        self.en_passant = (None, None, None)
        self.en_passant_valid = False
        self.column_changed = False

        if color == 'White':
            self.piece_img = tk.PhotoImage(file='img\\w_pawn.png')
        elif color == 'Black':
            self.piece_img = tk.PhotoImage(file='img\\b_pawn.png')

    def valid_moves(self, board, pieces):
        valid_moves = []
        row, col = self.position
        target_row = row + self.direction
        
        if self.is_valid_square(target_row, col):
            if self.is_square_empty(board, target_row, col):
                valid_moves.append((target_row, col, False))
                if self.moves_counter == 0 and self.is_square_empty(board, row + 2 * self.direction, col):
                    valid_moves.append((row + 2 * self.direction, col, False))

        # Check diagonal captures
        for offset in [-1, 1]:
            target_col = col + offset
            if self.is_valid_square(target_row, target_col): 
                if self.is_opponent_piece(board, target_row, target_col, self.color):
                    valid_moves.append((target_row, target_col, True))

        # Check en passant capture
        for offset in [-1, 1]:
            target_col = col + offset
            if self.is_valid_square(row, target_col) and self.is_opponent_piece(board, row, target_col, self.color):
                color_pawn = 'White' if self.color == 'Black' else 'Black'
                my_pawn = board[row][target_col].identifier
                my_pawn = pieces[color_pawn][my_pawn]
                if isinstance(my_pawn, Pawn) and my_pawn.moves_counter == 1 and self.moves_counter == 2 and self.en_passant[:2] == my_pawn.position and not self.column_changed:
                    print(my_pawn,my_pawn.en_passant, self.en_passant)
                    x, y ,t = self.en_passant
                    valid_moves.append((x+self.direction, y ,t))

        return valid_moves


class Rook(ChessPiece):
    def __init__(self, color, identifier):
        super().__init__(color, "Rook", identifier)
        if color == 'White':
            self.piece_img = tk.PhotoImage(file='img\\w_rook.png')
        elif color == 'Black':
            self.piece_img = tk.PhotoImage(file='img\\b_rook.png')

    def valid_moves(self, board, pieces):
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1)
        ]
        return self.global_moves(board, directions)
    

class Knight(ChessPiece):
    def __init__(self, color, identifier):
        super().__init__(color, "Knight", identifier)
        if color == 'White':
            self.piece_img = tk.PhotoImage(file='img\\w_knight.png')
        elif color == 'Black':
            self.piece_img = tk.PhotoImage(file='img\\b_knight.png')
            
    def valid_moves(self, board, pieces):
        valid_moves = []
        row, col = self.position
        moves = [
            (row - 2, col - 1), (row - 2, col + 1),
            (row - 1, col - 2), (row - 1, col + 2),
            (row + 1, col - 2), (row + 1, col + 2),
            (row + 2, col - 1), (row + 2, col + 1)
        ]
        for r, c in moves:
            if self.is_valid_square(r, c):
                if self.is_square_empty(board, r, c):
                    valid_moves.append((r, c, False))
                elif self.is_opponent_piece(board, r, c, self.color):
                    valid_moves.append((r, c, True))
        return valid_moves


class Bishop(ChessPiece):
    def __init__(self, color, identifier):
        super().__init__(color, "Bishop", identifier)
        if color == 'White':
            self.piece_img = tk.PhotoImage(file='img\\w_bishop.png')
        elif color == 'Black':
            self.piece_img = tk.PhotoImage(file='img\\b_bishop.png')

    def valid_moves(self, board, pieces):
        directions = [
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        return self.global_moves(board, directions)


class Queen(ChessPiece):
    def __init__(self, color, identifier):
        super().__init__(color, "Queen", identifier)
        if color == 'White':
            self.piece_img = tk.PhotoImage(file='img\\w_queen.png')
        elif color == 'Black':
            self.piece_img = tk.PhotoImage(file='img\\b_queen.png')

    def valid_moves(self, board, pieces):
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1), 
            (-1, -1), (-1, 1), (1, -1), (1, 1)  
        ]
        return self.global_moves(board, directions)
    

class King(ChessPiece):
    def __init__(self, color, identifier):
        super().__init__(color, "King", identifier)
        if color == 'White':
            self.piece_img = tk.PhotoImage(file='img\\w_king.png')
        elif color == 'Black':
            self.piece_img = tk.PhotoImage(file='img\\b_king.png')

    def valid_moves(self, board, pieces):
        valid_moves = []
        row, col = self.position
        
        if self.moves_counter == 0:
            x = self.color[0].lower()

            R2 = pieces[self.color][x + 'R2'] 
            if R2.moves_counter == 0 and not R2.captured:
                if all(board[row][c].identifier is None for c in range(col + 1, 7)):
                    valid_moves.append((row, col + 2, False))

            R1 = pieces[self.color][x + 'R1'] 
            if R1.moves_counter == 0 and not R1.captured:
                if all(board[row][c].identifier is None for c in range(1, col)):
                    valid_moves.append((row, col - 2, False))

        moves = [
            (row - 1, col - 1), (row - 1, col), (row - 1, col + 1),
            (row, col - 1), (row, col + 1),
            (row + 1, col - 1), (row + 1, col), (row + 1, col + 1)
        ]
        for r, c in moves:
            if self.is_valid_square(r, c):
                if self.is_square_empty(board, r, c):
                    valid_moves.append((r, c, False))
                elif self.is_opponent_piece(board, r, c, self.color):
                    valid_moves.append((r, c, True))
        return valid_moves


#============================================================================================= 
if __name__ == '__main__':
    try:
        root = tk.Tk()
        application = MainWindow(root)
        root.mainloop()
    except Exception as e:
        messagebox.showinfo(title='Error', message=f'Hi, you can\'t access this app, please contact the developer\n\n{e}')
        raise e

#=============================================================================================
# cd C:\Users\seyfe\OneDrive\Bureau\Seyf Eddine\python\projet-17-Chess
# pyinstaller --onefile --windowed --add-data="img\Logo.png;." --name "Chess" main.py

