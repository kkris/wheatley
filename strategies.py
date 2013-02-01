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



class MetaStrategy(Strategy):
    """
    Evaluates the current situation and chooses the right strategy
    """

    def evaluate_mode(self, walkable, position):

        current_node = walkable.get_node(*position)

        target_island = None
        for island in self.extended_islands:
            other_node = walkable.get_node(island.nodes[0].x, island.nodes[0].y)
            if not walkable.is_reachable(current_node, other_node): continue

            if target_island is None:
                target_island = island
            elif island.calculate_island_value() > target_island.calculate_island_value():
                target_island = island


        if target_island is None:
            return 'DRYMAX'
        if target_island.get_node(*position) is not None:
            return 'FARMING'

        return 'MOVING'


    def get_actions(self, graph, position):

        walkable = make_walkable(graph)

        self.split_graph_into_extended_islands(walkable)

        mode = self.evaluate_mode(walkable, position)

        if mode == 'MOVING':
            strategy = MovingStrategy(self.debug, self.round_)
        elif mode == 'FARMING':
            strategy = FarmingStrategy(self.debug, self.round_)
        elif mode == 'DRYMAX':
            strategy = DryMaxStrategy(self.debug, self.round_)

        strategy.extended_islands = self.extended_islands
        return strategy.get_actions(walkable, position), mode


class MovingStrategy(Strategy):
    """
    This Strategy moves the bot towards more safe places on the island while
    drying fields on its way there.
    """

    def get_actions(self, graph, position):

        self.position = position

        moved = False
        while len(self.actions) < 2 or (moved and len(self.actions) < 3):
            if not self.dry_one_if_possible(graph):
                moved = True
                current_node = graph.get_node(*self.position)
                target = self.find_target(graph)
                self.go(graph, current_node, target)

        if len(self.actions) < 3:
            current_node = graph.get_node(*self.position)
            target = self.find_target(graph)

            if target == current_node: # we already are at our destination, go towards water
                graph.calculate_distance_to_flooded()
                target = min(current_node.neighbors, key=lambda n: n.distance_to_flooded)
                self.go(graph, current_node, target)
            else:
                self.go(graph, current_node, target)

        return self.commit()


class FarmingStrategy(Strategy):
    """
    This Strategy aims to dry as many fields as possible.
    """


    def get_nearest_node(self, walkable, island, current_node):
        """
        Returns the node of the island that is nearest to our current position
        """

        x, y = current_node.x, current_node.y

        nearest_node = (None, -1)

        for node in island.nodes:
            if abs(node.x - x) + abs(node.y - y) > 10:
                continue

            node = walkable.get_node(node.x, node.y)

            if nearest_node[0] is None:
                distance = walkable.get_distance_between(current_node, node)
                nearest_node = (node, distance)
            else:
                distance = walkable.get_distance_between(current_node, node)
                if distance < nearest_node[1]:
                    nearest_node = (node, distance)

        return nearest_node


    def calculate_distance_value(self, walkable, island, current_node):
        """
        Calculates a value of an island consisting of the normal island value
        minus the distance times 4. This way islands which are near by get a
        better overall value
        """

        nearest_node, distance = self.get_nearest_node(walkable, island, current_node)

        self.nearest_nodes[island] = nearest_node

        if nearest_node is None:
            distance = 1000

        return island.calculate_island_value() - (distance*4)


    def get_best_island(self, walkable, current_node):
        """
        Returns a flooded island (which is not really an island) which has the
        most fields that can be dried, but is not too far away.
        """

        best_island = (None, -1)
        for island in self.flooded_islands:
            node = walkable.get_node(island.nodes[0].x, island.nodes[0].y)
            if not walkable.is_reachable(current_node, node):
                continue

            if best_island[0] is None:
                value = self.calculate_distance_value(walkable, island, current_node)
                best_island = (island, value)
            else:
                value = self.calculate_distance_value(walkable, island, current_node)
                if value > best_island[1]:
                    best_island = (island, value)

        return best_island[0]


    def go_towards_best_flooded(self, walkable):
        """
        Goes one field in the direction where a maximum number of fields can be dried
        but it does not take too far away fields into account.
        """

        self.nearest_nodes = {}

        current_node = walkable.get_node(*self.position)

        best_island = self.get_best_island(walkable, current_node)
        if best_island is None:
            return False

        nearest_node = self.nearest_nodes[best_island]

        if nearest_node is None:
            return False

        target = walkable.get_node(nearest_node.x, nearest_node.y)

        next_node = walkable.get_next_node_on_path_to(current_node, target)
        if next_node is None:
            return False


        return True


    def get_actions(self, graph, position):

        self.flooded_islands = None
        self.position = position

        while len(self.actions) < 3:
            dried = False
            while len(self.actions) < 3 and self.dry_one_if_possible(graph):
                dried = True

            if dried or self.flooded_islands is None:
                self.flooded_islands = split_into_subgraphs(make_flooded(graph))

            if len(self.actions) == 3:
                return self.commit()

            did_succeed = self.go_towards_best_flooded(graph)

            if not did_succeed:

                current_node = graph.get_node(*self.position)
                if current_node.distance_to_flooded == -1:
                    target = self.find_target(graph)
                    self.go(graph, current_node, target)
                else:
                    target = min(current_node.neighbors, key=lambda n: n.distance_to_flooded)
                    self.go(graph, current_node, target)

        return self.commit()
