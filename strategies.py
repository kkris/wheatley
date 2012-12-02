class State:
    dry = '#'
    flooded = 'o'
    sunk = '.'


class Node(object):

    def __init__(self, state, x, y):
        self.state = state
        self.x = x
        self.y = y

        self.north = self.east = self.south = self.west = None

        self.distance_to_water = -1

    def __str__(self):
#        return self.state + ' '
        return '({}, {}, {})'.format(self.x, self.y, self.distance_to_water)

    def __repr__(self):
        return str(self)

    def iter_neighbors(self):

        if self.north is not None: yield self.north
        if self.east is not None: yield self.east
        if self.south is not None: yield self.south
        if self.west is not None: yield self.west

    @property
    def is_next_to_water(self):
        return self.north is None or self.east is None or self.south is None or self.west is None

class Graph(object):

    def __init__(self, board):

        m = len(board)
        n = len(board[0])
        self.lst = [[None for i in range(n)] for j in range(m)] 
        for y, row in enumerate(board):
            for x, field in enumerate(row):
                node = Node(field.token, x, y)
                self.lst[y][x] = node

        for y, row in enumerate(self.lst):
            for x, node in enumerate(row):
                if x > 0:
                    node.west = row[x-1]
                if x < n-1:
                    node.east = row[x+1]
                if y > 0:
                    node.north = self.lst[y-1][x]
                if y < m-1:
                    node.south = self.lst[y+1][x]
     

    def make_walkable(self):

        for y, row in enumerate(self.lst):
            for x, node in enumerate(row):
                if node.state == State.sunk:
                    self.lst[y][x] = None
                    continue
                if node.north is None or node.north.state == State.sunk:
                    node.north = None
                if node.east is None or node.east.state == State.sunk:
                    node.east = None
                if node.south is None or node.south.state == State.sunk:
                    node.south = None
                if node.west is None or node.west.state == State.sunk:
                    node.west = None

    def make_dry(self):

        for y, row in enumerate(self.lst):
            for x, node in enumerate(row):
                if node is None:
                    continue
                if node.state == State.flooded:
                    self.lst[y][x] = None
                    continue
                if node.north is None or node.north.state == State.flooded:
                    node.north = None
                if node.east is None or node.east.state == State.flooded:
                    node.east = None
                if node.south is None or node.south.state == State.flooded:
                    node.south = None
                if node.west is None or node.west.state == State.flooded:
                    node.west = None


def find_island(node, island):

    island.add(node)

    for neighbor in node.iter_neighbors():
        if neighbor not in island:
            find_island(neighbor, island)

    return island


def split_graph(graph):

    nodes = []
    for row in graph.lst:
        for node in row:
            if node is not None: nodes.append(node)

    islands = []
    while nodes:
        node = nodes.pop()
        
        seen = set()
        island = find_island(node, seen)
        for node in island:
            if node in nodes:
                nodes.remove(node)
        islands.append(list(island))

    return islands
    

def calculate_distance_to_water(node):

    if node.is_next_to_water:
        node.distance_to_water = 0

    for neighbor in node.iter_neighbors():
        if (neighbor.distance_to_water == -1 or 
           neighbor.distance_to_water > node.distance_to_water + 1):
            neighbor.distance_to_water = node.distance_to_water + 1
            calculate_distance_to_water(neighbor)


class TileDry(object):
    token = '#'
class TileFlooded(object):
    token = 'o'
class TileDrowned(object):
    token = '.'


board = [
    [TileDrowned(), TileFlooded(), TileFlooded(), TileFlooded(), TileFlooded(), TileFlooded(), TileFlooded(), TileDrowned()],
    [TileFlooded(), TileFlooded(), TileDry(),  TileDry(), TileDry(), TileDry(), TileFlooded(), TileFlooded()],
    [TileFlooded(), TileFlooded(), TileDry(),  TileDry(), TileDry(), TileDry(), TileFlooded(), TileFlooded()],
    [TileDrowned(), TileFlooded(), TileFlooded(), TileFlooded(), TileFlooded(), TileFlooded(), TileFlooded(), TileDrowned()],   
]

graph = Graph(board)
graph.make_walkable()
graph.make_dry()

islands = split_graph(graph)
import pprint
#pprint.pprint(islands)



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
        for node in island:
            if node.x == x and node.y == y:
                return island

def log(msg):

    with open('/tmp/kkrash.log', 'a') as fh:
        fh.write(msg + '\n')

class MoveAwayFromWaterStrategy(Strategy):

    def play(self, board, position):

        graph = Graph(board)
        graph.make_walkable()
        graph.make_dry()

        island = find_current_island(split_graph(graph), *position)
        
        for node in island:
            if node.is_next_to_water:
                calculate_distance_to_water(node)
                break

        target = island[0]
        
        for node in island:
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
            for neighbor in node.iter_neighbors():
                if not hasattr(neighbor, 'distance') or neighbor.distance > distance + 1:
                    mark(neighbor, distance + 1)
  
        mark(target, 0)

        for i in range(3):
            next_node = sorted(current.iter_neighbors(), key=lambda n: n.distance)[0]

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

