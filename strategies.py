from graph import Graph, State, make_walkable, make_dry, split_into_subgraphs

class Strategy(object):

    def __init__(self):

        self.actions = []
    
    def do(self, cmd, direction, x=None, y=None):
        self.actions.append((cmd + ' ' + direction, x, y))

    def commit(self):

        actions = self.actions
        self.actions = []

        return actions

    def play(self, board, position):
        raise NotImplementedError()


class NoOpStrategy(Strategy):

    def play(self, board, position):

        for i in range(3):
            self.do('GO', 'CURRENT')

        return self.commit()


class DryCurrentStrategy(Strategy):

    def play(self, board, position):

        for i in range(3):
            self.do('DRY', 'CURRENT')

            return self.commit()


def find_current_island(islands, x, y):
    for island in islands:
        for node in island.nodes:
            if node.x == x and node.y == y:
                return island

def log(msg):

    with open('/tmp/kkrash.log', 'a') as fh:
        fh.write(msg + '\n')

class MoveAwayFromWaterStrategy(Strategy):

    def play(self, board, position):

        graph = Graph.from_board(board)
        dry = make_dry(graph)

        islands = split_into_subgraphs(dry)

        island = find_current_island(islands, *position)
        if island is None:
            # No where to go to
            for i in range(3): self.do("GO", "CURRENT")
            return self.commit()

        island.calculate_distance_to_water()
        

        target = island.nodes[0]
        
        for node in island.nodes:
            if node.distance_to_water > target.distance_to_water:
                target = node
            if node.x == position[0] and node.y == position[1]:
                current = node
        
        if current == target:
            for i in range(3):
                self.do('GO', 'CURRENT')

            return self.commit()

        def mark(node, distance):

            node.distance = distance
            for neighbor in node.neighbors:
                if not hasattr(neighbor, 'distance') or neighbor.distance > distance + 1:
                    mark(neighbor, distance + 1)
  
        mark(target, 0)

        for i in range(3):
            next_node = sorted(current.neighbors, key=lambda n: n.distance)[0]

            direction = get_direction(current, next_node)
            self.do('GO', direction)

            current = next_node

        return self.commit()


def num_flooded_neighbors(node):

    num = 0
    for neighbor in node.neighbors:
        if neighbor.state == State.flooded: num += 1

    return num

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


    def play(self, board, position):

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
        
