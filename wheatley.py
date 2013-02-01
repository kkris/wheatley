#!/usr/bin/env python

"""
wheatley
~~~~~~~~~

This file is the main entry point for the bot. Execute it and it will
communicate with the server via stdin and stdout

:copyright: (c) 2013 by Matthias Hummel and Kristoffer Kleine.
:license: BSD, see LICENSE for more details.
"""

import sys

from graph import Board, Graph
from strategies import MetaStrategy


class Wheatley(object):

    def __init__(self):

        self.board = None

        self.strategy = MetaStrategy()

        self.position = (1, 1)
        self.current_round = 0
        self.floodlevel = 0

        self.board_str = ''


    def dispatch(self, line):

        if line[0] in ('#', 'o', '.'):
            self.board_str += line + '\n'
        elif line.startswith('GAMEBOARDEND'):
            self.board = Board.from_string(self.board_str)
        elif line.startswith('ROUND'):

            self.current_round = int(line.split()[1])
            self.strategy.round_ = self.current_round

            x, y = map(int, line.split()[2].split(','))
            self.position = (x-1, y-1)

            graph = Graph.from_board(self.board)
            actions, mode = self.strategy.get_actions(graph, self.position)
            for (action, x, y) in actions:
                self.send(action)

                if action.startswith('DRY'):
                    self.board.dry(x, y)
        elif line.startswith('FLOOD'):
            x, y = map(int, line.split()[1].split(','))
            self.board.flood(x-1, y-1)
        elif line.startswith('END'):
            return True

        return False


    def send(self, cmd):
        """
        Send commando cmd back to the server
        """
        sys.stdout.write(cmd + '\n')

        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except IOError:
            pass


    def run(self):

        while True:
            line = sys.stdin.readline().strip()
            if line:
                should_exit = self.dispatch(line)
                if should_exit:
                    break


if __name__ == '__main__':

    wheatley = Wheatley()
    wheatley.run()



