from itertools import chain
import sys

sys.stdout.reconfigure(encoding='utf-8')
# print('imported board_util')
if sys.stdout.isatty():
    # print('IN A TTY!', file=sys.stderr)
    class Color:
        GREEN = '\u001b[32m'
        RESET = '\u001b[0m'
        BLUE = '\u001b[34m'
        MAGENTA = '\u001b[35m'
        CYAN = '\u001b[36m'
        BLACK = '\u001b[30m'
        RED = '\u001b[31m'
        YELLOW = '\u001b[33m'
        WHITE = '\u001b[37m'
else:
    # print('NOT IN A TTY!', file=sys.stderr)
    # print(sys.stdout.encoding, file=sys.stderr)
    class Color:
        GREEN = ''
        RESET = ''
        BLUE = ''
        MAGENTA = ''
        CYAN = ''
        BLACK = ''
        RED = ''
        YELLOW = ''
        WHITE = ''

def board_str(board, dim=3, highlight=(-1,), hi_color=Color.GREEN):
    b = board
    out = ''
    # out += '┌─┬─┬─┐\n'
    out += '┌'+'─┬'*(dim-1)+'─┐\n'
    for y in range(dim):
        # out += f'│{b[0]}│{b[1]}│{b[2]}│\n'
        out += '│'
        for x in range(dim):
            if y*dim + x in highlight:
                out += hi_color + b[y*dim + x] + Color.RESET + '│'
            else:
                out += b[y*dim + x] + '│'
        out += '\n'
        # out += '├─┼─┼─┤\n'
        if y != dim-1:
            out += '├'+'─┼'*(dim-1)+'─┤\n'
    out += '└'+'─┴'*(dim-1)+'─┘\n'
    # out += '└─┴─┴─┘\n'
    return out

def rows(board, dim=3, coords=False):

    for row_start in range(0, dim*(dim-1) + 1, dim):
        if coords:
            yield board[row_start:row_start + dim], tuple(range(row_start, row_start + dim))
        else:
            yield board[row_start:row_start + dim]
    # yield board[0:3]
    # yield board[3:6]
    # yield board[6:9]

def cols(board, dim=3, coords=False):
    rows_ = [r for r, _ in rows(board, dim, coords=True)]
    for x, col in enumerate(zip(*rows_)):
        if coords:
            yield ''.join(col), tuple(range(x, dim*dim, dim))
        else:
            yield ''.join(col)
    # yield board[0] + board[3] + board[6]
    # yield board[1] + board[4] + board[7]
    # yield board[2] + board[5] + board[8]

def diags(board, dim=3, coords=False):
    out = ''
    coords_ = []
    for i in range(dim):
        out += board[i*dim + i]
        coords_.append(i*dim + i)
    if coords:
        yield out, tuple(coords_)
    else:
        yield out
    out = ''
    coords_ = []
    for i in range(dim):
        out += board[(i+1)*dim - (i+1)]
        coords_.append((i+1)*dim - (i+1))
    if coords:
        yield out, tuple(coords_)
    else:
        yield out
    # yield board[0] + board[4] + board[8]
    # yield board[2] + board[4] + board[6]

lines = lambda x, dim, coords=False: chain(rows(x, dim, coords), cols(x, dim, coords), diags(x, dim, coords)) #TODO: adapt for 4x4

def all_equal(iterator):
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    if all(first == rest for rest in iterator):
        return first
    return False

def check_win(board, dim=3, coords=False):
    for line in lines(board, dim):
        # print(line, line_coords)
        char = all_equal(line) 
        if char and char in 'ox':
            return char
    return False

def check_win_coords(board, dim=3):
    for line, line_coords in lines(board, dim, coords=True):
        # print(line, line_coords)
        char = all_equal(line) 
        if char and char in 'ox':
            return char, line_coords
    return False, None


def check_tie(board):
    return '-' not in board