from engines import available_engines
import subprocess
import multiprocessing
import argparse
from itertools import repeat

def worker(args):
    i, (cmd, *args) = args
    print(f'worker {i} dispatched')
    # print(args)
    
    result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8').splitlines()
    print(f'worker {i} result: ', result[-1])
    # print()
    return result[-1][:4]

def score(runs, workers, engine1, engine2, dim=3, delay=True, time_limit=30):
    pool = multiprocessing.Pool(processes = workers)
    cmd = ['python3', 'ttt.py', engine1, engine2, f'-d{dim}', f'-t{time_limit}']
    if delay:
        cmd.append('--sleep')

    total = runs * workers
    results = {
        'P1 W': 0,
        'P2 W': 0,
        'DRAW': 0,
        'P1 T': 0,
        'P2 T': 0,
        'P1 E': 0,
        'P2 E': 0,
    }

    print(f'running {runs*workers} games, {dim}x{dim}, P1: {engine1}, P2: {engine2}, time {time_limit}')
    args = (cmd, engine1, engine2, dim, delay, time_limit)
    for i in range(runs):
        print()
        print(f'dispatching workers for run {i+1}/{runs}')
        # print(list(zip(range(workers), repeat(args))))
        returns = pool.map(worker, zip(range(workers), repeat(args)))
        for r in returns:
            results[r] += 1

    p1_wins = results['P1 W']
    p2_wins = results['P2 W']
    draws = results['DRAW']
    p1_timeouts = results['P1 T']
    p2_timeouts = results['P2 T']
    p1_exceptions = results['P1 E']
    p2_exceptions = results['P2 E']
    print()
    print(f'=== P1: {engine1} vs P2: {engine2} | dim={dim}x{dim}, time_limit={time_limit} | {runs*workers} TOTAL RUNS ===')
    print('== WINS ==')
    print(f'P1: {p1_wins:03d} ({100*p1_wins/total:05.1f}%)       P2: {p2_wins:03d} ({100*p2_wins/total:05.1f}%)')
    print(f'== DRAWS: {draws:03d} ==')
    print(f'== TIMEOUTS ==')
    print(f'P1: {p1_timeouts:03d}                P2: {p2_timeouts:03d}')
    print(f'== EXCEPTIONS ==')
    print(f'P1: {p1_exceptions:03d}                P2: {p2_exceptions:03d}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run multiple games of tic-tac-toe with human or computer agents and see stats.')
    parser.add_argument('engine1', type=str, choices=available_engines, help='engine for player 1')
    parser.add_argument('engine2', type=str, choices=available_engines, help='engine for player 2')
    parser.add_argument('--dim', '-d', type=int, default=3, help='size of board')
    parser.add_argument('--time', '-t', type=float, default=30, help='each player\'s time limit')
    parser.add_argument('--sleep', action='store_true', help='add sleep between moves (not counted against engine clocks)')
    parser.add_argument('--runs', '-r', type=int, default=16, help='number of times to run games')
    parser.add_argument('--workers', '-w', type=int, default=16, help='number of games to run in parallel')
    args = parser.parse_args()
    score(args.runs, args.workers, args.engine1, args.engine2, args.dim, args.sleep, args.time)
