#!/usr/bin/env python

import sys
import time

import colors
from strategies import *


STRATEGY = 'moveaway'

strategies = {
    'noop': NoOpStrategy,
    'drycurrent': DryCurrentStrategy,
    'moveaway': MoveAwayFromWaterStrategy
}


color_funcs = {
    '#': colors.yellow,
    'o': colors.blue,
    '.': colors.darkblue 
}


def log(msg):

    with open('/tmp/kkrash.log', 'a') as fh:
        fh.write(msg + '\n')

class Tile(object):
    token = ''

    @classmethod
    def from_token(self, token):
        if token == '#': return TileDry()
        elif token == 'o': return TileFlooded()
        else: return TileDrowned()

    def __str__(self):
        return color_funcs[self.token](self.token)

    def __repr__(self):
        return str(self)


class TileDry(Tile):
    token = '#'
class TileFlooded(Tile):
    token = 'o'
class TileDrowned(Tile):
    token = '.'


class Gameboard(object):

    def __init__(self, rows, colums):

        self.board = [[None for i in range(colums)] for i in range(rows)]

        self._counter = 0 # internal counter (what row will be set next)

    def set_row_from_string(self, description):

        for i, token in enumerate(description):
            if token == '#':
                self.board[self._counter][i] = TileDry()
            elif token == 'o':
                self.board[self._counter][i] = TileFlooded()
            else:
                self.board[self._counter][i] = TileDrowned()

        self._counter += 1

    def flood(self, x, y):
        tile = self.board[x][y]
        if isinstance(tile, TileDry):
            self.board[x][y] = TileFlooded()
        elif isinstance(tile, TileFlooded):
            self.board[x][y] = TileDrowned()

    def dry(self, x, y):

        self.board[x][y] = TileDry()



class Bot(object):

    def __init__(self, strategy):

        self.board = None

        self.strategy = strategy

        self.position = (1, 1)
        self.current_round = 0

    def log_board(self):

        s = ''
        for i, row in enumerate(self.board.board):
            for j, token in enumerate(row):
                if (j, i) == self.position:
                    x, y = self.position
                    if isinstance(self.board.board[y][x], TileDry):
                        s += colors.yellow('b ')
                    elif isinstance(self.board.board[y][x], TileFlooded):
                        s += colors.blue('b ')
                    else:
                        s += colors.darkblue('b ')
                else:
                    s += str(token) + ' '
            s += '\n'
        log('-'*20)
        log(s + '-'*20)

    def dispatch(self, line):

        if line.startswith('GAMEBOARDSTART'):
            cols, rows = map(int, line.split()[1].split(','))
            self.board = Gameboard(rows, cols)
        elif line[0] in ('#', 'o', '.'):
            self.board.set_row_from_string(line)
        elif line.startswith('GAMEBOARDEND'):
            pass
        elif line.startswith('ROUND'):
            self.log_board()

            self.current_round = int(line.split()[1])
            x, y = map(int, line.split()[2].split(','))
            self.position = (x-1, y-1)

            log('\n#### Starting round %d ####' % self.current_round)
            log('Position: (%d, %d)' %(self.position[0], self.position[1]))

            log('\nMaking moves:')

            for action in self.strategy.play(self.board.board, self.position):
                log(action)
                self.send(action)

            self.log_board()
        elif line.startswith('FLOOD'):
            y, x = map(int, line.split()[1].split(','))
            self.board.flood(x-1, y-1)
            log('\nFlooding ({}, {})'.format(x-1, y-1))

        elif line.startswith('DRY'):
            pass
        elif line.startswith('END'):
            return True

        return False


    def send(self, cmd):
        """
        Send commando cmd back to the server
        """
        sys.stdout.write(cmd + '\n')
        sys.stdout.flush()


    def run(self):

        log('\n\n\n########## Start new Game ##########\n')

        counter = 0
        while True:
            if counter > 10000:
                break
            line = sys.stdin.readline().strip()
            if line:
                should_exit = self.dispatch(line)
                if should_exit:
                    self.log_board()
                    log('########## Game end ##########')
                    break

            counter += 1
            #time.sleep(0.1)



if __name__ == '__main__':
    strategy = strategies[STRATEGY]()
    bot = Bot(strategy)
    bot.run()



