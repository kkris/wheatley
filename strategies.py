from graph import Graph, State, make_walkable, make_dry, split_into_subgraphs

class Strategy(object):
    pass

    def play(self, board, position):
        raise NotImplementedError()


class NoOpStrategy(Strategy):

    def play(self, board, position):

        for i in range(3):
            yield 'GO CURRENT'


class DryCurrentStrategy(Strategy):

    def play(self, board, position):

        for i in range(3):
            yield 'DRY CURRENT'


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
            for i in range(3): yield "GO CURRENT"
            return

        island.calculate_distance_to_water()
        

        target = island.nodes[0]
        
        for node in island.nodes:
            if node.distance_to_water > target.distance_to_water:
                target = node
            if node.x == position[0] and node.y == position[1]:
                current = node
        
        if current == target:
            for i in range(3):
                yield 'GO CURRENT'

            return

        def mark(node, distance):

            node.distance = distance
            for neighbor in node.neighbors:
                if not hasattr(neighbor, 'distance') or neighbor.distance > distance + 1:
                    mark(neighbor, distance + 1)
  
        mark(target, 0)

        for i in range(3):
            next_node = sorted(current.neighbors, key=lambda n: n.distance)[0]

            x = next_node.x - current.x
            y = next_node.y - current.y
            if x == -1:
                yield 'GO WEST'
            elif x == 1:
                yield 'GO EAST'
            elif y == -1:
                yield 'GO NORTH'
            elif y == 1:
                yield 'GO SOUTH'
            else:
                yield 'GO CURRENT'

            current = next_node        

