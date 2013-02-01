"""
graph
~~~~~

:copyright: (c) 2013 by Matthias Hummel and Kristoffer Kleine.
:license: BSD, see LICENSE for more details.
"""

from collections import defaultdict


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
        if field.state in (State.dry, State.redry):
            field.state = State.flooded
        elif field.state == State.flooded:
            field.state = State.drowned

    def dry(self, x, y):

        self[y][x].state = State.redry


class Node(object):

    def __init__(self, x=0, y=0, state=State.dry):

        self.x = x
        self.y = y

        self._state = state

        self.distance_to_water = -1
        self.distance_to_flooded = -1
        self.distance_to_land = -1

        self._north = self._east = self._south = self._west = None
        self._neighbors = []


        self._is_water = False
        self._is_dry = False
        self._is_next_to_water = False
        self._is_next_to_land = False

        self.should_recalculate_node_properties = True
        self.should_update_neighbors = True


    @staticmethod
    def from_node(node):
        return Node(node.x, node.y, node.state)


    @property
    def is_water(self):
        if self.should_recalculate_node_properties:
            self.calculate_node_properties()
        return self._is_water

    @property
    def is_dry(self):
        return not self.is_water

    @property
    def is_next_to_water(self):
        if self.should_recalculate_node_properties:
            self.calculate_node_properties()
        return self._is_next_to_water

    @property
    def is_next_to_land(self):
        if self.should_recalculate_node_properties:
            self.calculate_node_properties()
        return self._is_next_to_land

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state
        self.should_recalculate_node_properties = True

    @property
    def neighbors(self):
        if self.should_update_neighbors:
            _neighbors = (self._north, self._east, self._south, self._west)
            self._neighbors = [n for n in _neighbors if n is not None]
            self.should_update_neighbors = False
        return self._neighbors

    # north
    @property
    def north(self):
        return self._north

    @north.setter
    def north(self, north):
        self._north = north
        self.should_recalculate_node_properties = True
        self.should_update_neighbors = True

    # east
    @property
    def east(self):
        return self._east

    @east.setter
    def east(self, east):
        self._east = east
        self.should_recalculate_node_properties = True
        self.should_update_neighbors = True

    # south
    @property
    def south(self):
        return self._south

    @south.setter
    def south(self, south):
        self._south = south
        self.should_recalculate_node_properties = True
        self.should_update_neighbors = True

    # west
    @property
    def west(self):
        return self._west

    @west.setter
    def west(self, west):
        self._west = west
        self.should_recalculate_node_properties = True
        self.should_update_neighbors = True


    def calculate_node_properties(self):

        self._is_water = self._get_is_water()
        self._is_dry = not self._is_water

        self._is_next_to_water = self._get_is_next_to_water()
        self._is_next_to_land = self._get_is_next_to_land()

        self.should_recalculate_node_properties = False


    def _get_is_water(self):
        return self._state in (State.flooded, State.drowned)

    def _get_is_next_to_water(self):

        if self._is_water:
            return False

        for neighbor in self.neighbors:
            if neighbor.state in (State.flooded, State.drowned):
                return True

        return any(n is None for n in [self.north, self.east, self.south, self.west])


    def _get_is_next_to_land(self):

        if self._is_dry:
            return False

        for neighbor in self.neighbors:
            if neighbor.state in (State.dry, State.redry):
                return True

        return False

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Node({}, {})'.format(self.x, self.y)


    @property
    def middle_value(self):

        if self.is_water:
            return 0

        value = 1
        for n in self.neighbors:
            value += n.distance_to_water

        return value


class Graph(object):

    def __init__(self, nodes):

        self._nodes = nodes
        self.rows = len(nodes)
        self.columns = len(nodes[0])

        self._cached_paths = defaultdict(lambda: defaultdict(dict))
        self._cached_distances = defaultdict(lambda: defaultdict(int))

        self._connect_nodes()

        self._update_non_null_nodes()

    @staticmethod
    def from_board(board):
        nodes = []
        for line in board:
            nodes.append([])
            for field in line:
                node = Node(field.x, field.y, field.state)
                nodes[-1].append(node)
        return Graph(nodes)


    @staticmethod
    def from_graph(graph):
        nodes = []
        for row in graph._nodes:
            nodes.append([])
            for field in row:
                if field is None:
                    nodes[-1].append(None)
                else:
                    node = Node(field.x, field.y, field.state)
                    nodes[-1].append(node)
        return Graph(nodes)


    def _connect_nodes(self):

        for y, line in enumerate(self._nodes):
            for x, node in enumerate(line):
                if node is None: continue
                if x > 0:
                    node.west = line[x-1]
                if x < self.columns - 1:
                    node.east = line[x+1]
                if y > 0:
                    node.north = self._nodes[y-1][x]
                if y < self.rows - 1:
                    node.south = self._nodes[y+1][x]

    def _update_non_null_nodes(self):

        self.nodes = []
        for row in self._nodes:
            for node in row:
                if node is not None:
                    self.nodes.append(node)


    def get_node(self, x, y):
        return self._nodes[y][x]

    def add_node(self, node):

        self._nodes[node.y][node.x] = node

        self.nodes.append(node)

        x, y = node.x, node.y

        if x > 0:
            node.west = self._nodes[y][x-1]
            if node.west is not None:
                node.west.east = node
        if x < self.columns - 1:
            node.east = self._nodes[y][x+1]
            if node.east is not None:
                node.east.west = node
        if y > 0:
            node.north = self._nodes[y-1][x]
            if node.north is not None:
                node.north.south = node
        if y < self.rows - 1:
            node.south = self._nodes[y+1][x]
            if node.south is not None:
                node.south.north = node



    def remove_node(self, node):

        if self._nodes[node.y][node.x] is None:
            return

        self._nodes[node.y][node.x] = None

        # set connections referring to this node to None
        if node.east is not None:
            node.east.west = None
        if node.south is not None:
            node.south.north = None
        if node.west is not None:
            node.west.east = None
        if node.north is not None:
            node.north.south = None


        self.nodes.remove(node)

        self._cached_distances.clear()
        self._cached_paths.clear()


    def calculate_distance_to_water(self):
        """
        Marks all node with their respective distance to water
        """

        curset = set()

        for node in self.nodes:
            if node.is_next_to_water:
                node.distance_to_water = 1
                curset.add(node)
            elif node.is_water:
                node.distance_to_water = 0

        distance = 2
        while curset:
            newset = set()
            for node in curset:
                for neighbor in node.neighbors:
                    if neighbor.distance_to_water == -1:
                        neighbor.distance_to_water = distance
                        newset.add(neighbor)
            curset = newset
            distance += 1


    def calculate_distance_to_flooded(self):
        """
        Marks all node with their respective distance to a flooded node
        """

        curset = set()

        for node in self.nodes:
            if node.state == State.flooded:
                node.distance_to_flooded = 0
                curset.add(node)
            elif any(n.state == State.flooded for n in node.neighbors):
                node.distance_to_flooded = 0
                curset.add(node)

        distance = 1
        while curset:
            newset = set()
            for node in curset:
                for neighbor in node.neighbors:
                    if neighbor.distance_to_flooded == -1:
                        neighbor.distance_to_flooded = distance
                        newset.add(neighbor)
            curset = newset
            distance += 1


    def calculate_distance_to_land(self):
        """
        Marks all node with their respective distance to a dry node
        """

        curset = set()

        for node in self.nodes:
            if node.is_dry:
                node.distance_to_land = 0
            elif node.is_next_to_land:
                node.distance_to_land = 1
                curset.add(node)

        distance = 2
        while curset:
            newset = set()
            for node in curset:
                for neighbor in node.neighbors:
                    if neighbor.distance_to_land == -1:
                        neighbor.distance_to_land = distance
                        newset.add(neighbor)
            curset = newset
            distance += 1


    def calculate_island_value(self):

        value = 0
        for node in self.nodes:
            if node.state == State.flooded: value += 2
            elif node.state == State.redry: value += 3
            elif node.state == State.dry: value += 4

        return value

    def get_middle(self):
        
        self.calculate_distance_to_water()

        middle = self.nodes[0]
        for node in self.nodes:
            if node.middle_value > middle.middle_value:
                middle = node

        return middle


    def _add_path_to_cache(self, path, start, target):
        """
        Cache this path and split it into subpaths and cache them too
        """

        distance = 0
        reverse_path = {target: target}

        current = target
        while current != start:
            self._cached_distances[current][target] = distance
            self._cached_distances[target][current] = distance

            self._cached_paths[current][target] = reverse_path.copy()

            next_node = path[current]
            reverse_path[next_node] = current

            distance += 1

            current = next_node

        self._cached_paths[current][target] = reverse_path.copy()
        self._cached_distances[current][target] = distance
        self._cached_distances[target][current] = distance


    def _get_path_between(self, start, target):
        """
        Get the shortest path between start and target using A*
        """

        if start in self._cached_paths and target in self._cached_paths[start]:
            return self._cached_paths[start][target]

        def min_distance(n1, n2):
            return abs(n1.x - n2.x) + abs(n1.y - n2.y)

        closedset = set()
        openset = set([start])
        path = {}

        g_score = {start: 0}
        f_score = {start: min_distance(start, target)}

        while openset:

            # find minimum
            current = None
            for node in openset:
                if current is None:
                    current = node
                elif f_score[node] < f_score[current]:
                    current = node

            if current.x == target.x and current.y == target.y:
                self._add_path_to_cache(path, start, target)
                return self._cached_paths[start][target]

            openset.remove(current)
            closedset.add(current)

            for neighbor in current.neighbors:
                if neighbor in closedset:
                    continue

                tentative_g_score = g_score[current] + 1

                if neighbor not in openset or tentative_g_score <= g_score[neighbor]:
                    path[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + min_distance(neighbor, target)
                    if neighbor not in openset:
                        openset.add(neighbor)

        self._cached_paths[start][target] = None
        self._cached_paths[target][start] = None
        self._cached_distances[start][target] = -1
        self._cached_distances[target][start] = -1

        return None


    def get_distance_between(self, start, target):
        """
        Get the shortest distance between start and target
        """

        if start in self._cached_distances and target in self._cached_distances[start]:
            return self._cached_distances[start][target]

        path = self._get_path_between(start, target)
        if path is None:
            return -1
        else:
            return self._cached_distances[start][target]

    def is_reachable(self, start, target):
        """
        Return whether target is reachable from start or not
        """

        return self.get_distance_between(start, target) != -1


    def get_next_node_on_path_to(self, start, target):
        """
        Return the next node on the way from start to target
        If it is not possible return None
        """

        path = self._get_path_between(start, target)
        if path is None:
            return None
        else:
            return path[start]



def make_walkable(graph):
    """
    Transform a graph to only contain nodes, that the bot can enter.
    Returns a new graph and leaves the old one untouched
    """

    nodes = []

    for row in graph._nodes:
        nodes.append([])
        for node in row:
            if node is None or node.state == State.drowned:
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



def algorithm(node, island, islands):
    
    dry_states = (State.dry, State.redry)

    if (node.state in dry_states or 
        any(n.state in dry_states and n in island for n in node.neighbors)):

        if node.distance_to_land > 1:
            for ext_island in islands:
                if node in ext_island:
                    ext_island.remove(node)

        island.add(node)

        node.distance_to_land = 1

    for neighbor in node.neighbors:
        if neighbor.state == State.flooded:
            if node.state in dry_states:
                algorithm(neighbor, island, islands)
            elif neighbor.distance_to_land == node.distance_to_land + 1:
                if neighbor not in island:
                    island.add(neighbor)
            elif (neighbor.distance_to_land == -1 or 
                  neighbor.distance_to_land > node.distance_to_land + 1):
                neighbor.distance_to_land = node.distance_to_land + 1

                for ext_island in islands:
                    if neighbor in ext_island:
                        ext_island.remove(neighbor)
                island.add(neighbor)
                algorithm(neighbor, island, islands)



def split_into_extended_islands(graph):

    walkable = make_walkable(graph)
    dry = make_dry(graph)
    dry_islands = split_into_subgraphs(dry)

    extended_islands = []
    for dry_island in dry_islands:
        extended_island = set()
        for node in dry_island.nodes:
            walkable_node = walkable.get_node(node.x, node.y)

            extended_island.add(walkable_node)

        extended_islands.append(extended_island)


    for extended_island in extended_islands:
        for node in list(extended_island):
            algorithm(node, extended_island, extended_islands)


    islands = []
    for ext_island in extended_islands:
        nodes = [[None for _ in range(graph.columns)] for _ in range(graph.rows)]
        for node in ext_island:
            nodes[node.y][node.x] = node

        islands.append(Graph(nodes))

    return islands



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
        n = [[None for i in range(graph.columns)] for j in range(graph.rows)]
        for node in visited:
            n[node.y][node.x] = node

        subgraphs.append(Graph(n))

    return subgraphs


