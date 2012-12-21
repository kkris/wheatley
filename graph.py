def flatten(lst):
    for item in lst:
        if isinstance(item, list):
            for subitem in flatten(item):
                yield subitem
        else:
            yield item


class State(object):
    dry = '#'
    flooded = 'o'
    drowned = '.'
    redry = '~'

class Field(object):

    def __init__(self, x=0, y=0, state=State.dry):
        self.x = x
        self.y = y
        self.state = state


class Board(list):

    def __init__(self, board):
        list.__init__(self, board)

    @staticmethod
    def from_string(s):
        board = []
        for y, line in enumerate(s.strip().split()):
            board.append([])
            for x, state in enumerate(line):
                board[-1].append(Field(x, y, state))
        return Board(board)

    def flood(self, x, y):

        field = self[y][x]
        if field.state == State.dry:
            field.state = State.flooded
        elif field.state == State.flooded:
            field.state = State.drowned

    def dry(self, x, y):

        self[y][x].state = State.redry


class Node(object):

    def __init__(self, x=0, y=0, state=State.dry):
        self.x = x
        self.y = y
        self.state = state
        self.distance_to_water = -1

        self.north = self.east = self.south = self.west = None


    @staticmethod
    def from_node(node):

        return Node(node.x, node.y, node.state)


    @property
    def neighbors(self):

        if self.north is not None: yield self.north
        if self.east is not None: yield self.east
        if self.south is not None: yield self.south
        if self.west is not None: yield self.west


    @property
    def is_water(self):
        return self.state in (State.flooded, State.drowned)

    @property
    def is_dry(self):
        return self.state in (State.dry, State.redry)


    @property
    def is_next_to_water(self):

        for neighbor in self.neighbors:
            if neighbor.state in (State.flooded, State.drowned):
                return True

        return any(n is None for n in [self.north, self.east, self.south, self.west])

    def __eq__(self, other):
        return self.state == other.state and self.x == other.x and self.y == other.y

    def __ne(self, other):
        return not self.__eq__(other)

    def _calculate_distance_to_water(self):
        """
        Recursivly calculate distance to water
        """

        if self.is_next_to_water:
            self.distance_to_water = 0

        for neighbor in self.neighbors:
            if(neighbor.distance_to_water == -1 or
               neighbor.distance_to_water > self.distance_to_water + 1):
                neighbor.distance_to_water = self.distance_to_water + 1
                neighbor._calculate_distance_to_water()


class Graph(object):

    def __init__(self, nodes=None):

        if nodes is None: self._nodes = []
        else: self._nodes = nodes

        self._connect_nodes()

    @staticmethod
    def from_board(board):
        nodes = []
        for line in board:
            nodes.append([])
            for field in line:
                node = Node(field.x, field.y, field.state)
                nodes[-1].append(node)
        return Graph(nodes)

    def _connect_nodes(self):

        for y, line in enumerate(self._nodes):
            for x, node in enumerate(line):
                if node is None: continue
                if x > 0:
                    node.west = line[x-1]
                if x < self.colums - 1:
                    node.east = line[x+1]
                if y > 0:
                    node.north = self._nodes[y-1][x]
                if y < self.rows - 1:
                    node.south = self._nodes[y+1][x]

    @property
    def rows(self):
        return len(self._nodes)

    @property
    def colums(self):
        return len(self._nodes[0])

    @property
    def nodes(self):
        """
        Returns all non-None nodes
        """
        return filter(None, flatten(self._nodes))
    
    def get_node(self, x, y):

        return self._nodes[y][x]

    
    def calculate_distance_to_water(self):
        """
        Marks all node with their respective distance to water
        Graph must be fully connected in order for this to work
        """
        node = self.nodes[0]
        node._calculate_distance_to_water()


        
def make_walkable(graph):
    """
    Transform a graph to only contain nodes, that the bot can enter.
    Returns a new graph and leaves the old one untouched
    """

    nodes = []

    for row in graph._nodes:
        nodes.append([])
        for node in row:
            if node.state == State.drowned:
                nodes[-1].append(None)
            else:
                nodes[-1].append(Node.from_node(node))

    return Graph(nodes)


def make_dry(graph):
    """
    Transform a graph into a graph which only contains nodes, that are dry
    """

    nodes = []

    for row in graph._nodes:
        nodes.append([])
        for node in row:
            if node is None or node.state in (State.flooded, State.drowned):
                nodes[-1].append(None)
            else:
                nodes[-1].append(Node.from_node(node))

    return Graph(nodes)


def _find_connected(node, visited):

    visited.add(node)
    for neighbor in node.neighbors:
        if neighbor not in visited:
            _find_connected(neighbor, visited)

def split_into_subgraphs(graph):

    subgraphs = []
    nodes = list(graph.nodes)
    while nodes:
        node = nodes[0]
        
        visited = set()
        _find_connected(node, visited)
        
        for node in visited:
            nodes.remove(node)

        # build 2-dimensional list from visited nodes
        n = [[None for i in range(graph.colums)] for j in range(graph.rows)]
        for node in visited:
            n[node.y][node.x] = node

        subgraphs.append(Graph(n))

    return subgraphs
        
