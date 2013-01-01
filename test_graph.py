import graph

g1 = '''
oooooo
o####o
o###~o
ooooo.'''.strip()

g2 = '''
.oooo.
o###~o
o####o
o#~##o
.oooo.
......'''.strip()

g_sub = '''
#~.o#
#.ooo
.oo##
'''.strip()


g_big = '''
...ooooo.....oooooooo..........ooooo..
..oo#ooooo...ooo###ooo...o.oooooooooo.
oooo##oooo..oo######ooooooooo####ooooo
.o######ooo.o#####ooooo..oo###oo##ooo.
.oo######oo.oo###oooo...oo##oo.oo##o..
ooo######o..o#######ooo.oo##oo..oo##oo
.ooo##ooo..oo########oooooo##oooo##oo.
.ooo####oo#####oooo#####oooo##oo##ooo.
..oooo#######oooo.ooooooooooo###oooo..
...ooooo####ooo...ooo....oooo##oooo...
.....ooo###oo.....oooo..oooo##oo......
....oo####oooooo...oooooooo##oooo.....
..ooooo########ooooo.oooo###ooooooo...
oooo######ooo####ooo.oo###oooooo......
ooo########ooo#####oo####oooo.........
.ooo########.#####oo#######oooo.......
..oooo###############oooooooo.........
....oooooo..oooooo..ooooo.............
'''.strip()



g_big_cluttered = '''
...~~~~~......oooo.oo..........ooo.o..
...~#~~~~~...ooo..#ooo...o.oooo.ooooo.
o.~~##~~~~..oo#.##o#o.oo.o.oo###.oooo.
.o.##~oo~~~.o.#..#o..o...oo#.ooo#...o.
.o.###~#~~~..o#..o.oo...oo#.oo.oo.#o..
.oo#o##o~~...#.###.#.oo.oo#o....oo#ooo
..oo.#~~~..oo.o##.##.oooo.o..o.oo##oo.
.ooo#.##~~#####ooo..o##oooo.##oo#oooo.
..ooo...###.#oo.o.o.ooooooo.o.##oo....
...o.ooo####oo....o.o....oo.oo#.ooo...
.....o..o#..o.....oooo..oo.o##oo......
.....o###..ooooo...oooo.o.o#.ooo......
..oooo..###.##.o.ooo.oo.oo##.oooooo...
o.o..#####.oo####ooo..o#.#oo..oo......
ooo###.####o.o#o..#oo..##.oo..........
.....#######.#.###oo###.#.#o.oo.......
..oooo.########o###o#oooooo...........
....oo.oo...o.o.oo..ooooo.............
'''.strip()


def test_flatten():

    assert list(graph.flatten([1, [2, 3], [4, [5,6]]])) == range(1, 7)


def test_graph_from_board():
    """
    Test creation from string
    Test that nodes are in the correct place
    """

    board = graph.Board.from_string(g1)
    
    g = graph.Graph.from_board(board)

    assert g.rows == 4
    assert g.columns == 6

    for y, line in enumerate(g1.split()):
        for x, state in enumerate(line):
            node = g.get_node(x, y)
            assert node.state == state
            assert node.x == x
            assert node.y == y


def test_redry_node():

    board = graph.Board.from_string(g1)

    assert board[1][1].state == graph.State.dry

    board.flood(1, 1)
    assert board[1][1].state == graph.State.flooded

    board.dry(1, 1)
    assert board[1][1].state == graph.State.redry



def test_connections():
    """
    Test that nodes are connected correctly
    """

    board = graph.Board.from_string(g1)
    g = graph.Graph.from_board(board)

    for y, line in enumerate(board):
        for x, _ in enumerate(line):
            node = g.get_node(x, y)
            if x == 0: 
                assert node.west is None
                assert node.east is g.get_node(x+1, y)
            if x == g.columns - 1: 
                assert node.east is None
                assert node.west is g.get_node(x-1, y)
            if y == 0: 
                assert node.north is None
                assert node.south is g.get_node(x, y+1)
            if y == g.rows - 1: 
                assert node.south is None
                assert node.north is g.get_node(x, y-1)




def test_remove_and_add_node():

    board = graph.Board.from_string(g1)
    g = graph.Graph.from_board(board)

    node = g.get_node(1, 1)

    assert len(list(node.neighbors)) == 4
    
    assert g.get_node(2, 1).west is node
    assert g.get_node(1, 2).north is node
    assert g.get_node(0, 1).east is node
    assert g.get_node(1, 0).south is node

    g.remove_node(node)

    assert g.get_node(1, 1) is None

    assert g.get_node(2, 1).west is None
    assert g.get_node(1, 2).north is None
    assert g.get_node(0, 1).east is None
    assert g.get_node(1, 0).south is None


    g.add_node(node)

    assert g.get_node(1, 1) is node

    assert g.get_node(2, 1).west is node
    assert g.get_node(1, 2).north is node
    assert g.get_node(0, 1).east is node
    assert g.get_node(1, 0).south is node





def test_neighbors():

    board = graph.Board.from_string(g1)
    g = graph.Graph.from_board(board)

    assert len(list(g.get_node(0, 0).neighbors)) == 2
    assert len(list(g.get_node(0, 1).neighbors)) == 3
    assert len(list(g.get_node(1, 1).neighbors)) == 4


def test_is_water():

    board = graph.Board.from_string(g2)
    g = graph.Graph.from_board(board)

    assert g.get_node(0, 0).is_water
    assert g.get_node(1, 0).is_water
    assert not g.get_node(1, 1).is_water
    assert not g.get_node(4, 1).is_water


def test_next_to_water():

    board = graph.Board.from_string(g2)
    g = graph.Graph.from_board(board)

    assert g.get_node(1, 1).is_next_to_water
    assert g.get_node(4, 1).is_next_to_water
    assert not g.get_node(2, 2).is_next_to_water

    # flooded or drowned nodes are by definition not next to water
    assert not g.get_node(0, 0).is_next_to_water
    assert not g.get_node(1, 0).is_next_to_water

    dry = graph.split_into_subgraphs(graph.make_dry(g))[0] # get some None nodes in the graph

    assert dry.get_node(1, 1).is_next_to_water
    assert not dry.get_node(2, 2).is_next_to_water


def test_make_walkable():

    board = graph.Board.from_string(g2)
    g = graph.Graph.from_board(board)

    walkable = graph.make_walkable(g)

    for y in range(walkable.rows):
        for x in range(walkable.columns):
            node = walkable.get_node(x, y)
            if node is None:
                assert g2.split()[y][x] == graph.State.drowned

    assert len(walkable.nodes) == 5*6 - 4

    assert walkable.get_node(0, 1).west is None


def test_make_dry():

    board = graph.Board.from_string(g2)
    g = graph.Graph.from_board(board)

    dry = graph.make_dry(g)

    # Test that first making it walkable and then dry is the same as making it dry right away    
    walkable = graph.make_walkable(g)
    dry2 = graph.make_dry(walkable)
    for y in range(dry.rows):
        for x in range(dry.columns):
            node = dry.get_node(x, y)
            assert node == dry2.get_node(x, y)
            if node is None:
                assert g2.split()[y][x] in (graph.State.flooded, graph.State.drowned)
            else:
                assert node.state in (graph.State.dry, graph.State.redry)

    assert len(dry.nodes) == 3*4

    assert dry.get_node(1, 1).west is None
    


def test_subgraphs():

    board = graph.Board.from_string(g_sub)
    g = graph.Graph.from_board(board)

    walkable = graph.make_walkable(g)
    dry = graph.make_dry(g)

    walkable_islands = graph.split_into_subgraphs(walkable)
    dry_islands = graph.split_into_subgraphs(dry)

    assert len(walkable_islands) == 2
    for island in walkable_islands:
        assert len(island.nodes) in (3, 9)

    assert len(dry_islands) == 3
    for island in dry_islands:
        assert len(island.nodes) in (1, 2, 3)



def test_distance_to_water():

    board = graph.Board.from_string(g2)
    g = graph.Graph.from_board(board)

    g.calculate_distance_to_water()

    # all water nodes must have distance 0
    for node in g.nodes:
        if node.is_water:
            assert node.distance_to_water == 0

    assert g.get_node(1, 1).distance_to_water == 1
    assert g.get_node(2, 1).distance_to_water == 1
    assert g.get_node(4, 1).distance_to_water == 1
    assert g.get_node(2, 2).distance_to_water == 2
    assert g.get_node(3, 2).distance_to_water == 2
    assert g.get_node(2, 3).distance_to_water == 1



def test_distance_to_flooded():

    board = graph.Board.from_string(g2)
    g = graph.make_walkable(graph.Graph.from_board(board))


    g.calculate_distance_to_flooded()

    for node in g.nodes:
        if node.state == graph.State.flooded:
            assert node.distance_to_flooded == 0
        elif any(n.state == graph.State.flooded for n in node.neighbors):
            assert node.distance_to_flooded == 0

    assert g.get_node(2, 2).distance_to_flooded == 1

    


    board = graph.Board.from_string(g_sub)
    g = graph.make_walkable(graph.Graph.from_board(board))

    g.calculate_distance_to_flooded()

    for node in g.nodes:
        if node.state == graph.State.flooded:
            assert node.distance_to_flooded == 0
        elif any(n.state == graph.State.flooded for n in node.neighbors):
            assert node.distance_to_flooded == 0

    assert g.get_node(1, 0).distance_to_flooded == -1



def test_distance_to_land():

    board = graph.Board.from_string(g2)
    g = graph.Graph.from_board(board)

    g.calculate_distance_to_land()

    # all dry, redry nodes have distance 0
    for node in g.nodes:
        if node.is_dry:
            assert node.distance_to_land == 0

    assert g.get_node(0, 0).distance_to_land == 2
    assert g.get_node(1, 0).distance_to_land == 1
    assert g.get_node(2, 0).distance_to_land == 1
    assert g.get_node(3, 0).distance_to_land == 1


def test_middle_value():

    board = graph.Board.from_string(g2)
    g = graph.Graph.from_board(board)

    g.calculate_distance_to_water()

    # all water nodes have middle value 0
    for node in g.nodes:
        if node.is_water:
            assert node.middle_value == 0

    assert g.get_node(1, 1).middle_value == 2
    assert g.get_node(2, 1).middle_value == 4
    assert g.get_node(3, 1).middle_value == 4
    assert g.get_node(4, 1).middle_value == 2

    assert g.get_node(1, 2).middle_value == 4
    assert g.get_node(2, 2).middle_value == 5
    assert g.get_node(3, 2).middle_value == 5
    assert g.get_node(4, 2).middle_value == 4

def test_island_value():

    board = graph.Board.from_string(g1)
    g = graph.Graph.from_board(board)

    walkable = graph.make_walkable(g)
    island = graph.split_into_subgraphs(walkable)[0]

    value = island.calculate_island_value()
    assert value == 15*2 + 3 + 7*4

    
    board = graph.Board.from_string(g2)
    g = graph.Graph.from_board(board)

    walkable = graph.make_walkable(g)
    island = graph.split_into_subgraphs(walkable)[0]

    value = island.calculate_island_value()
    assert value == 14*2 + 2*3 + 10*4

    
    board = graph.Board.from_string(g_sub)
    g = graph.Graph.from_board(board)

    walkable = graph.make_walkable(g)
    
    island1, island2 = graph.split_into_subgraphs(walkable)


    value = island1.calculate_island_value()
    assert value in (1*3 + 2*4, 6*2 + 3*4)

    value = island2.calculate_island_value()
    assert value in (1*3 + 2*4, 6*2 + 3*4)


def test_contains_subgraph():

    board = graph.Board.from_string(g_sub)
    g = graph.Graph.from_board(board)

    walkable = graph.make_walkable(g)
    dry = graph.make_dry(g)

    walkable_islands = graph.split_into_subgraphs(walkable)
    dry_islands = graph.split_into_subgraphs(dry)

    for walkable_island in walkable_islands:
        if walkable_island.get_node(4, 2) is not None: break

    for dry_island in dry_islands:
        if dry_island.get_node(4, 2) is not None: break

    assert dry_island in walkable_island
    assert walkable_island not in dry_island



def test_split_extended_islands():

    board = graph.Board.from_string(g_sub)
    g = graph.Graph.from_board(board)

    walkable = graph.make_walkable(g)

    extended_islands = graph.split_into_extended_islands(walkable)

    assert len(extended_islands) == 3
    for island in extended_islands:
        if island.get_node(0, 0) is not None: 
            assert len(island.nodes) == 3
        elif island.get_node(4, 0) is not None: 
            island2 = island
            assert len(island.nodes) == 3
        elif island.get_node(4, 2) is not None: 
            island3 = island
            assert len(island.nodes) == 7

    
    assert island2.get_node(4, 1) is not None
    assert island3.get_node(4, 1) is not None

    assert island2.get_node(3, 1) is None
    assert island3.get_node(3, 1) is not None


def test_split_extended_islands_big():

    board = graph.Board.from_string(g_big_cluttered)
    g = graph.Graph.from_board(board)

    walkable = graph.make_walkable(g)

    extended_islands = graph.split_into_extended_islands(walkable)

    assert len(extended_islands) == len(graph.split_into_subgraphs(graph.make_dry(g)))

    for island in extended_islands:
        if island.get_node(18, 6) is not None:
            assert len(island.nodes) == 5
            assert island.get_node(19, 6) is not None
            assert island.get_node(19, 5) is not None
            assert island.get_node(19, 4) is not None
            assert island.get_node(20, 4) is not None

        if island.get_node(5, 9) is not None:
            node = island.get_node(5, 9)
            assert node.distance_to_land == 3

        if island.get_node(8, 9) is not None:
            assert island.get_node(5, 9) is not None
        if island.get_node(5, 13) is not None:
            assert island.get_node(5, 9) is not None

        if island.get_node(17, 2) is not None:
            assert island.get_node(18, 2) is not None
        if island.get_node(18, 1) is not None:
            assert island.get_node(18, 2) is not None
        if island.get_node(19, 2) is not None:
            assert island.get_node(18, 2) is not None


        if island.get_node(30, 3)  is not None:
            assert island.get_node(4, 1) is None
        if island.get_node(4, 1) is not None:
            assert island.get_node(30, 3) is None

        assert island.get_node(31, 0) is None




def test_get_middle():

    board = graph.Board.from_string(g1)
    g = graph.Graph.from_board(board)

    middle = g.get_middle()

    assert middle.x in (2, 3)
    assert middle.y in (1, 2)


    board = graph.Board.from_string(g2)
    g = graph.Graph.from_board(board)

    middle = g.get_middle()

    assert middle.x in (2, 3)
    assert middle.y == 2


def test_reachable():

    board = graph.Board.from_string(g_sub)
    g = graph.Graph.from_board(board)

    walkable = graph.make_walkable(g)

    upper_left = walkable.get_node(0, 0)
    upper_right = walkable.get_node(4, 0)
    lower_right = walkable.get_node(4, 2)

    assert not lower_right.reachable(upper_left)
    assert upper_right.reachable(lower_right)



def test_reachable_big():

    board = graph.Board.from_string(g_big)
    g = graph.Graph.from_board(board)

    walkable = graph.make_walkable(g)

    start = walkable.get_node(4, 1)
    target = walkable.get_node(7, 14)

    assert start.reachable(target)



def test_get_next_node_on_path_to():

    board = graph.Board.from_string(g_sub)
    g = graph.Graph.from_board(board)

    walkable = graph.make_walkable(g)

    island1, island2 = sorted(graph.split_into_subgraphs(walkable), key=lambda i: len(i.nodes))

    start = island1.get_node(0, 0)
    target = island2.get_node(4, 2)

    assert start.get_next_node_on_path_to(target) is None

    start = island2.get_node(4, 0)

    assert start.get_next_node_on_path_to(target) is island2.get_node(4, 1)


def test_get_next_node_on_path_to_big():

    board = graph.Board.from_string(g_big)
    g = graph.Graph.from_board(board)

    walkable = graph.make_walkable(g)

    start = walkable.get_node(4, 1)
    target = walkable.get_node(7, 14)

    assert start.get_next_node_on_path_to(target) is walkable.get_node(5, 1)



