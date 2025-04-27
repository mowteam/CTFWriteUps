from pwn import *
import numpy as np
import copy

#set up pwntools
r = process("./segvroad")
#r = process("ncat --ssl segvroad.atreides.b01lersc.tf 8443", shell=True)

class Board:

    saved_moves = []    
    level = 0
    max_depth = 35
     
    def __init__(self, uid):
        self.board = np.zeros((10, 10), dtype=int)
        self.options = np.ones(10, dtype=int)
        self.x = 0
        self.y = 0
        self.seed = uid
        self.round = 1
        self.curr_step = 0
        self.prev = 2
        self.moves = []

    def reset(self):
        self.level += 1
        self.x = 0
        self.y = 0 
        self.curr_step = 0
        self.moves = []

        self.initialize()
    
    # keep in bounds (performed by binary)
    def check_bounds(self):
        if self.x < 0:
            self.x = 0
        elif self.x > 9:
            self.x = 9

        if self.y < 0:
            self.y = 0
        elif self.y > 9:
            self.y = 9 

    def initialize(self):
        self.options[0] = 3
        self.options[9] = 3
        
        for i in range(1, 9):
            option = (( (self.seed + self.level + i) * 0x13523 ) >> (2*i) ) & 3
            if option == 2:
                self.set_row_1(i)
            elif option == 0:
                if self.options[i - 1]:
                    self.set_row_0(i)
                else:
                    self.set_row_1(i)
            elif option == 1:
                self.set_row_1(i)
            elif option == 3:
                self.options[i] = 2

    def update(self):
        for i in range(10):
            if self.options[i] == 1 and i & 1 == 0: #even
                self.rotate_row_left(i)
            elif self.options[i] == 1: #odd
                self.rotate_row_right(i)
            elif self.options[i] == 2 and self.round % 7 == 3:
                self.set_all_one(i)
            elif self.options[i] == 2:
                self.set_all_zero(i)
        
        self.round += 1
        self.curr_step += 1

    def set_row_1(self, i):
        if i % 3 == 0:
            calc = (((self.seed + self.level + i) * 0x13523) & 0x3ff) ^ 0x2aa
        elif i % 3 == 1:
            calc = (((self.seed + self.level + i) * 0x13523) & 0x3ff) ^ 0xfffffddd
        else:
            calc = 0x288

        for j in range(10):
            self.board[i][j] = (calc >> j) & 1
        self.options[i] = 1

    def set_row_0(self, i):
        if i % 3 == 0:
            calc = (((self.seed + self.level + i) * 0x13523) & 0x3ff)
        elif i % 3 == 1:
            calc = ~(((self.seed + self.level + i) * 0x13523) & 0x3ff)
        else:
            calc = 0xffffffcf

        for j in range(10):
            self.board[i][j] = (calc >> j) & 1
        self.options[i] = 0
    
    def rotate_row_left(self, i):
        first = self.board[i][0]
        for j in range(9):
            self.board[i][j] = self.board[i][j+1]
        self.board[i][9] = first

    def rotate_row_right(self, i):
        last = self.board[i][9]
        for j in range(9, 0, -1):
            self.board[i][j] = self.board[i][j-1]
        self.board[i][0] = last

    def set_all_one(self, i):
        for j in range(10):
            self.board[i][j] = 1

    def set_all_zero(self, i):
        for j in range(10):
            self.board[i][j] = 0

    def print(self):
        print(f"Round {self.round} - l{self.level}:")
        for i in range(9, -1, -1):
            print(str(self.options[i]) + ":", end=" ")
            for j in range(10):
                if self.y == i and self.x == j:
                    print('@', end=" ")
                else:
                    print('X' if self.board[i][j] else '-', end=" ")
            print()
        print("-"*25) 
    
    def solve(self):
        self.check_bounds()

        # base case: win
        if self.y == 9 and self.x == 9: #win
            self.saved_moves.append(self.moves)
            return self.round
        
        # base case: fail
        if self.board[self.y][self.x] != 0 or self.curr_step > self.max_depth:
            return 0
        
        self.update()
        board_copy = copy.deepcopy(self)
        
        # move piece (4 recursive branches)
        # up
        if self.prev != 1 and self.y != 9:
            self.y += 1
            self.prev = 0
            self.moves.append('w')
            if (result := self.solve()):
                return result
        
        '''    
        # down
        board = copy.deepcopy(board_copy)
        if board.prev != 0:
            board.y -= 1
            board.prev = 1
            board.moves.append('s')
            if (result := board.solve()):
                return result
        '''

        # left
        board = copy.deepcopy(board_copy)
        if board.prev != 3:
            board.x -= 1
            board.prev = 2
            board.moves.append('a')
            if (result := board.solve()):
                return result

        # right
        board = copy.deepcopy(board_copy)
        if board.prev != 2:
            board.x += 1
            board.prev = 3
            board.moves.append('d')
            if (result := board.solve()):
                return result
        
        return 0



def main():
    #read input
    r.readuntil(b"userid: ")
    uid = int(r.readline().decode())

    #setup board
    board = Board(uid)
    board.initialize()

    #solve levels and win ig
    for level in range(10):
        if not (curr_round := board.solve()):
            print("failed to find solution")
            exit()
        board.reset()
        board.round = curr_round

    #send to server/process
    for arr in board.saved_moves:
        for move in arr:
            r.sendline(str(move).encode())
    r.interactive()

main()
