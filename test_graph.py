import graph

g1 = '''
oooooo
o####o
o####o
ooooo.'''.strip()

g2 = '''
.oooo.
o####o
o####o
o####o
.oooo.
......'''.strip()

g_sub = '''
##.o#
#.ooo
.oo##
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
    assert g.colums == 6

    for y, line in enumerate(g1.split()):
        for x, state in enumerate(line):
            node = g.get_node(x, y)
            assert node.state == state
            assert node.x == x
            assert node.y == y

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
            if x == g.colums - 1: 
                assert node.east is None
                assert node.west is g.get_node(x-1, y)
            if y == 0: 
                assert node.north is None
                assert node.south is g.get_node(x, y+1)
            if y == g.rows - 1: 
                assert node.south is None
                assert node.north is g.get_node(x, y-1)


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
    assert not g.get_node(1, 1).is_water


def test_next_to_water():

    board = graph.Board.from_string(g2)
    g = graph.Graph.from_board(board)

    assert g.get_node(1, 1).is_next_to_water
    assert not g.get_node(2, 2).is_next_to_water

    dry = graph.split_into_subgraphs(graph.make_dry(g))[0]

    assert dry.get_node(1, 1).is_next_to_water
    assert not (dry.get_node(2, 2).is_next_to_water)


def test_make_walkable():

    board = graph.Board.from_string(g2)
    g = graph.Graph.from_board(board)

    walkable = graph.make_walkable(g)

    for y in range(walkable.rows):
        for x in range(walkable.colums):
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
        for x in range(dry.colums):
            node = dry.get_node(x, y)
            assert node == dry2.get_node(x, y)
            if node is None:
                assert g2.split()[y][x] in (graph.State.flooded, graph.State.drowned)
            else:
                assert node.state == graph.State.dry

    assert len(dry.nodes) == 3*4

    assert dry.get_node(1, 1).west is None
    

'''
##.o#
#.ooo
.oo##
'''


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

    dry = graph.make_dry(g)
    dry_islands = graph.split_into_subgraphs(dry)

    for island in dry_islands:
        island.calculate_distance_to_water()

        assert island.get_node(1, 1).distance_to_water == 0
        assert island.get_node(2, 2).distance_to_water == 1


