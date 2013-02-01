"""
strategies
~~~~~~~~~~

Various strategies.

:copyright: (c) 2013 by Matthias Hummel and Kristoffer Kleine.
:license: BSD, see LICENSE for more details.
"""

from graph import (State, make_walkable, split_into_extended_islands,
                   split_into_subgraphs, make_flooded)


def get_direction(current, target):

    x = target.x - current.x
    y = target.y - current.y
    if x == -1:
        return 'WEST'
    elif x == 1:
        return 'EAST'
    elif y == -1:
        return 'NORTH'
    elif y == 1:
        return 'SOUTH'
    else:
        return 'CURRENT'



class Strategy(object):

    def __init__(self, debug=False, round_=0):

        self.actions = []
        self.position = (0, 0)
        self.floodlevel = 0

        self.extended_islands = None

        self.debug = debug
        self.round_ = round_


    def do(self, cmd, direction, x=None, y=None):
        self.actions.append((cmd + ' ' + direction, x, y))

        if cmd == 'GO':
            self.position = (x, y)


    def commit(self):

        actions = self.actions
        self.actions = []

        return actions

    def get_actions(self, graph, position):
        raise NotImplementedError()


    def split_graph_into_extended_islands(self, graph):

        self.extended_islands = split_into_extended_islands(graph)


    def dry_one_if_possible(self, graph):

        def _set_dry_state(node):
            graph.get_node(node.x, node.y).state = State.redry

            for island in self.extended_islands:
                n = island.get_node(node.x, node.y)
                if n is not None:
                    n.state = State.redry

        current_node = graph.get_node(*self.position)

        if current_node.state == State.flooded:
            self.do('DRY', 'CURRENT', current_node.x, current_node.y)
            _set_dry_state(current_node)
            return True

        for node in current_node.neighbors:
            if node.state == State.flooded:
                direction = get_direction(current_node, node)
                self.do('DRY', direction, node.x, node.y)
                _set_dry_state(node)
                return True

        return False


    def go(self, graph, start, target):

        next_node = graph.get_next_node_on_path_to(start, target)

        if next_node is not None:
            direction = get_direction(start, next_node)
            self.do('GO', direction, next_node.x, next_node.y)



    def find_target(self, graph):

        current_node = graph.get_node(*self.position)

        target_island = None
        for island in self.extended_islands:
            other_node = graph.get_node(island.nodes[0].x, island.nodes[0].y)
            if not graph.is_reachable(current_node, other_node):
                continue

            if target_island is None:
                target_island = island
            else:
                if island.calculate_island_value() > target_island.calculate_island_value():
                    target_island = island

        target = target_island.get_middle()

        return graph.get_node(target.x, target.y)




class DryMaxStrategy(Strategy):
    """
    Dries as many fields as possible
    """

    def get_actions(self, graph, position):

        self.position = position

        current_node = graph.get_node(*self.position)

        while len(self.actions) < 3 and self.dry_one_if_possible(graph):
            pass

        while len(self.actions) < 3:

            if len(current_node.neighbors) == 0:
                self.do('GO', 'CURRENT')
                continue

            next_node = min(current_node.neighbors, key=lambda n: n.distance_to_flooded)
            direction = get_direction(current_node, next_node)
            self.do('GO', direction)

            current_node = next_node


        return self.commit()





def get_direction(current, target):

    x = target.x - current.x
    y = target.y - current.y
    if x == -1:
        return 'WEST'
    elif x == 1:
        return 'EAST'
    elif y == -1:
        return 'NORTH'
    elif y == 1:
        return 'SOUTH'
    else:
        return 'CURRENT'


import random

class DryMaxStrategy(Strategy):

    def dry_neighbors(self, node):
        for neighbor in node.neighbors:
            if neighbor.state == State.flooded and len(self.actions) < 3:
                direction = get_direction(node, neighbor)
                self.do('DRY', direction, neighbor.x, neighbor.y)


    def get_actions(self, graph, position):

        graph = Graph.from_board(board)

        current_node = graph.get_node(*position)

        while len(self.actions) < 3:

            self.dry_neighbors(current_node)

            if len(self.actions) < 3:
                next_node = random.choice(list(current_node.neighbors))
                direction = get_direction(current_node, next_node)
                self.do('GO', direction)

                current_node = next_node
            

        return self.commit()



class HyperStrategy(Strategy):


    def evaluate_mode(self, board, position):

        graph = Graph.from_board(board)

        extended_islands = split_into_extended_islands(graph)
        
        target_island = None
        for island in extended_islands:
            if target_island is None: target_island = island
            elif island.calculate_island_value() > target_island.calculate_island_value():
                target_island = island

        if target_island.get_node(*position) is not None:
            return 'FARMING'


        return 'MOVING'


    def can_dry_neighbor(self, graph, position):

        current_node = graph.get_node(*position)

        if current_node.state == State.flooded: return True
        for neighbor in current_node.neighbors:
            if neighbor.state == State.flooded: return True
        return False

    
    def dry_one_if_possible(self, graph, position):

        current_node = graph.get_node(*position)

        if current_node.state == State.flooded:
            self.do('DRY', 'CURRENT', current_node.x, current_node.y)
            current_node.state = State.redry
            return True

        for node in current_node.neighbors:
            if node.state == State.flooded:
                direction = get_direction(current_node, node)
                self.do('DRY', direction, node.x, node.y)
                node.state = State.redry
                return True

        return False

    def go(self, start, target):

        next_node = start.get_next_node_on_path_to(target)

        if next_node is None: return None

        direction = get_direction(start, next_node)
        self.do('GO', direction)

        return next_node

    def find_target(self, graph, position):

        current_node = graph.get_node(*position)
        copy = Graph.from_graph(graph)
        islands = split_into_extended_islands(copy) # nebenwirkung, sollte input graph intakt lassen

        target_island = None
        for island in islands:
            if island.get_node(current_node.x, current_node.y) is None: continue # not reachable

            if target_island is None: 
                target_island = island
            else:
                if island.calculate_island_value() > target_island.calculate_island_value():
                    target_island = island

        target = target_island.get_middle()

        return graph.get_node(target.x, target.y)

        

    def play(self, board, position):

        mode = self.evaluate_mode(board, position)

        graph = make_walkable(Graph.from_board(board))

        if mode == 'MOVING':
            while len(self.actions) < 2:
                if not self.dry_one_if_possible(graph, position):
                    current_node = graph.get_node(*position)
                    target = self.find_target(graph, position)
                    next_node = self.go(current_node, target)
                    if next_node is not None:
                        position = (next_node.x, next_node.y)

            

            current_node = graph.get_node(*position)
            target = self.find_target(graph, position)

            next_node = self.go(current_node, target)
            
            return self.commit()

        elif mode == 'FARMING':
            for i in range(3):
                self.dry_one_if_possible(graph, position)

            if len(self.actions) == 3:
                return self.commit()

            

