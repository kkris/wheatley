#!/usr/bin/env pypy

import sys

import colors
from graph import State, Field, Board
from strategies import *


STRATEGY = 'hyper'

strategies = {
    'noop': NoOpStrategy,
    'drycurrent': DryCurrentStrategy,
    'moveaway': MoveAwayFromWaterStrategy,
    'drymax': DryMaxStrategy,
    'hyper': HyperStrategy
}


color_funcs = {
    '#': colors.yellow,
    'o': colors.blue,
    '.': colors.darkblue 
}


def log(msg):

    with open('/tmp/kkrash.log', 'a') as fh:
        fh.write(msg + '\n')



class Bot(object):

    def __init__(self, strategy):

        self.board = None

        self.strategy = strategy

        self.position = (1, 1)
        self.current_round = 0

        self.board_str = ''

    def log_board(self):

        s = ''
        '''for i, row in enumerate(self.board.board):
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
        log(s + '-'*20)'''

    def dispatch(self, line):

        if line[0] in ('#', 'o', '.'):
            self.board_str += line + '\n'
        elif line.startswith('GAMEBOARDEND'):
            self.board = Board.from_string(self.board_str)
        elif line.startswith('ROUND'):
            self.log_board()

            self.current_round = int(line.split()[1])
            x, y = map(int, line.split()[2].split(','))
            self.position = (x-1, y-1)

            log('\n#### Starting round %d ####' % self.current_round)
            log('Position: (%d, %d)' %(self.position[0], self.position[1]))

            log('\nMaking moves:')

            for (action, x, y) in self.strategy.play(self.board, self.position):
                log(action)
                self.send(action)

                if action.startswith('DRY'):
                    self.board.dry(x, y)


            self.log_board()
        elif line.startswith('FLOOD'):
            x, y = map(int, line.split()[1].split(','))
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



