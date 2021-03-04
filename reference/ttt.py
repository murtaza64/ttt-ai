from board_util import check_win_coords, check_tie, board_str, Color
from engines import available_engines
from itertools import cycle, repeat
import time
import argparse
import multiprocessing
import sys

def step(engine, board, time_remaining, queue):
    queue.put(engine.get_move_wrapper(board))

def timer_f(engine, time_remaining, delta=1):
    t = time_remaining
    while t > 0:
        print(f'time remaining: {t:.1f}s')
        time.sleep(delta)
        t -= delta

def play_human(engine1, engine2, dim=3, delay=True, time_limit=30):
    engines = [available_engines[engine1](piece='x', dim=dim), available_engines[engine2](piece='o', dim=dim)]
    print(f'\n{dim}x{dim} tictactoe game: {engines[0]} against {engines[1]}\n\n')
    print('Note: this mode will not kill the AI player if it takes too long.')
    times = {engines[0]: time_limit, engines[1]: time_limit}
    board = '-'*dim*dim

    for i, engine in enumerate(cycle(engines)):
        if delay:
            time.sleep(0.8)
        print(f'move {i}: waiting for {engine}\'s move...')

        if engine.engine_name != 'human': #timing stuff
            timer = multiprocessing.Process(target=timer_f, args=(engine, times[engine]))
            timer.start()
            start = time.time()

        success, result = engine.get_move_wrapper(board)

        if engine.engine_name != 'human': #timing stuff
            timer.kill()
            times[engine] -= time.time() - start
            if times[engine] < 0: #timeout condition
                print(f'{engine} ran out of time and loses by forfeit!')
                other_index = 1 - engines.index(engine)
                print(f'P{other_index+1} WIN: {engines[other_index]} wins!')
                return

        if success:
            newboard = result
        else:
            print(f'{engine} forfeits due to an exception (printed above).')
            other_index = 1 - engines.index(engine)
            print(f'P{other_index+1} WIN: {engines[other_index]} wins!')
            return

        highlight_index = [i for i in range(len(newboard)) if newboard[i] != board[i]][0]
        board = newboard
        print('move made:')
        print(board_str(board, dim=dim, highlight=(highlight_index,), hi_color=Color.CYAN))
        victory, line_coords = check_win_coords(board, dim)
        if victory:
            print(board_str(board, dim=dim, highlight=line_coords, hi_color=Color.GREEN))
            print(f'P{engines.index(engine)+1} WIN: {engine} wins!')
            return
        elif check_tie(board):
            print('DRAW: game ends in a draw')
            return

def play_worker(args):
    i, args = args
    print(f'worker {i} dispatched')
    print(args)
    return play(*args)

def play(engine1, engine2, dim=3, delay=True, time_limit=30, stdout=None):
    if stdout is not None:
        sys.stdout = stdout

    if 'human' in (engine1, engine2):
        return play_human(engine1, engine2, dim, delay, time_limit)

    engines = [available_engines[engine1](piece='x', dim=dim), available_engines[engine2](piece='o', dim=dim)]
    print(f'\n{dim}x{dim} tictactoe game: {engines[0]} against {engines[1]}\n\n')
    times = {engines[0]: time_limit, engines[1]: time_limit}
    board = '-'*dim*dim


    for i, engine in enumerate(cycle(engines)):
        if delay:
            time.sleep(0.8)
        print(f'move {i}: waiting for {engine}\'s move...')

        queue = multiprocessing.Queue()
        p = multiprocessing.Process(target=step, args=(engine, board, times[engine], queue))
        timer = multiprocessing.Process(target=timer_f, args=(engine, times[engine]))
        p.start()
        timer.start()
        start = time.time()
        p.join(times[engine])
        timer.kill()
        times[engine] -= time.time() - start

        if p.is_alive(): #timeout condition
            p.kill()
            print(f'{engine} ran out of time and loses by forfeit!')
            other_index = 1 - engines.index(engine)
            print(f'P{engines.index(engine)+1} TIMEOUT: {engines[other_index]} wins!')
            return other_index, True

        success, result = queue.get()
        if success:
            newboard = result
        else:
            print(f'{engine} forfeits due to an exception (printed above).')
            other_index = 1 - engines.index(engine)
            print(f'P{engines.index(engine)+1} EXCEPTION: {engines[other_index]} wins!')
            return other_index, True

        highlight_index = [i for i in range(len(newboard)) if newboard[i] != board[i]][0]
        board = newboard
        print('move made:')
        print(board_str(board, dim=dim, highlight=(highlight_index,), hi_color=Color.CYAN))
        victory, line_coords = check_win_coords(board, dim)
        if victory:
            print(board_str(board, dim=dim, highlight=line_coords, hi_color=Color.GREEN))
            print(f'P{engines.index(engine)+1} WIN: {engine} wins!')
            return engines.index(engine), False
        elif check_tie(board):
            print('DRAW: game ends in a draw')
            return -1, False

def score(runs, workers, engine1, engine2, dim=3, delay=True, time_limit=30):
    pool = multiprocessing.Pool(processes = workers)
    print(f'running {runs*workers} games, {dim}x{dim}, P1: {engine1}, P2: {engine2}, time {time_limit}')
    print('dispatching workers...')
    args = (engine1, engine2, dim, delay, time_limit)
    print(list(zip(range(workers), repeat(args))))
    returns = pool.map(play_worker, zip(range(workers), repeat(args)))
    p1_wins = returns.count((0, False))
    p2_wins = returns.count((1, False))
    draws = returns.count((-1, False))
    p1_timeouts = returns.count((0, True))
    p2_timeouts = returns.count((1, True))
    print(p1_wins, p2_wins, draws, p1_timeouts, p2_timeouts)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Play tic-tac-toe (noughts and crosses) with human or computer agents.')
    parser.add_argument('engine1', type=str, choices=available_engines, help='engine for player 1')
    parser.add_argument('engine2', type=str, choices=available_engines, help='engine for player 2')
    parser.add_argument('--dim', '-d', type=int, default=3, help='size of board')
    parser.add_argument('--time', '-t', type=float, default=30, help='each player\'s time limit')
    parser.add_argument('--sleep', action='store_true', help='add sleep between moves (not counted against engine clocks)')
    args = parser.parse_args()
    play(args.engine1, args.engine2, args.dim, args.sleep, args.time)