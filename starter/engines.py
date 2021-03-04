from itertools import cycle, chain
from board_util import check_win, check_tie, board_str, lines, Color
import random
import time
import traceback

class Engine:

    engine_name = 'base tictactoe engine'

    def __init__(self, piece, dim):
        self.piece = piece
        self.enemy = 'x' if piece == 'o' else 'o'
        self.dim = dim
        
    def get_move_wrapper(self, board, *args, **kwargs): #don't worry about this too much
        try:
            return True, self.get_move(board, *args, **kwargs)
        except Exception as e:
            print(f'\n{Color.RED}ERROR: exception in {self}{Color.RESET}\n')
            print('board state during exception:')
            print(board_str(board))
            traceback.print_exc()
            print()
            return False, e

    def get_move(self, board):
        raise NotImplementedError('You need to implement get_move')

    def possible_moves(self, board, piece):
        for i, space in enumerate(board):
            if space in '- ':
                yield board[:i] + piece + board[i+1:]

    def __hash__(self):
        return hash((type(self).__name__, self.piece, self.enemy, self.dim))

    def __str__(self):
        return f'<{self.engine_name} [{self.piece}]>'

class RandomEngine(Engine):

    engine_name = 'random'

    def get_move(self, board):
        # raise Exception('testing exceptions')
        print('beep boop randomizing move...')
        b = list(board)
        choices = [i for i, pc in enumerate(board) if pc == '-']
        b[random.choice(choices)] = self.piece
        return ''.join(b)

class HumanEngine(Engine):

    engine_name = 'human'

    def get_move(self, board):
        out = board_str(board, dim=self.dim).splitlines()
        for row in range(2*self.dim+1):
            if (row-1)%2 == 0:
                out[row] += ' ' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[(row-1)//2] + ' '
            else:
                out[row] += '   '
        last_row = ' '
        for x in range(self.dim):
            last_row += f'{x+1} '
        out.insert(0, last_row)
        print('\n'.join(out))
        # ok = False
        while True:
            inp = input(f'Please enter a coordinate pair to place \'{self.piece}\' (such as B2 or 1A): ')
            if len(inp) != 2:
                print('A coordinate pair must be two characters.')
                continue
            sorted_ = sorted(list(inp)) #sort based on ascii values to allow both orderings as input
            if not(sorted_[0].isdigit() and sorted_[1].isalpha()):
                print('Please include one letter and one digit.')
                continue
            x = int(sorted_[0]) - 1
            y = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.index(sorted_[1].upper())
            if not (0 <= x < self.dim and 0 <= y < self.dim):
                print('That cell is not in the grid.')
                continue
            i = y*self.dim + x
            if board[i] == '-':
                return board[:i] + self.piece + board[i+1:]
            else:
                print('That cell is not empty.')

class MinimaxEngine(Engine):
    
    engine_name = 'vanilla minimax'


class DLMinimaxEngine(Engine):

    engine_name = 'depth limited minimax'


class GreedyEngine(Engine):

    engine_name = 'greedy'

    def get_move(self, board):
        moves = list(self.possible_moves(board, self.piece))
        move_scores = {move: self.heuristic(move) for move in moves}
        random.shuffle(moves)
        move = max(moves, key=lambda m: move_scores[m])
        return move
    
    def heuristic(self, board):
        p, _ = self.piece, self.enemy
        h = 0
        if check_win(board, self.dim) == self.piece:
            return float('inf')
        for line in lines(board, self.dim):
            if p+p in line:
                h += 1
        return h

available_engines = {
    'random': RandomEngine,
    'minimax': MinimaxEngine,
    'dlminimax': DLMinimaxEngine,
    'human': HumanEngine,
    'greedy': GreedyEngine
}
