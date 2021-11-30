# to keep track of the board states and all of their info
class Node:
    def __init__(self, board, turn, depth, score, parent, children):
        self.board = board
        self.turn = turn  # whos turn is next, so if the boards are possible black moves, then turn = white
        self.depth = depth
        self.score = score  # static eval score for terminal nodes, min/max from children nodes for non-terminals
        self.parent = parent
        self.children = children


# takes in the initial board, size of the board, whos turn it is, and the amount of moves to look ahead
# returns the best next move
def hexapawn(board, size, turn, movesahead):
    best = minimax(board, turn, movesahead, 0, [])
    return best


# minimax algorithm
# takes in the inital board, whos turn it is, moves ahead, depth, and the game tree
# returns the next best move
def minimax(board, turn, movesahead, depth, tree):
    # generating the game tree to movesahead amount of levels
    if turn == "b":
        next = "w"  # whos turn it'll be next
    else:
        next = "b"
    if depth == 0 and movesahead == 0:
        return board
    if depth != movesahead:  # 0 depth = initial board
        if depth == 0:  # generating new states and appending to tree, then recursing
            root = Node(board, turn, 0, 0, [], [])
            tree.append(root)
            newMoves = generateNewMoves(board, turn)
            for b in newMoves:
                temp = Node(b, next, 1, 0, root, [])
                root.children.append(temp)
                tree.append(temp)
            minimax(board, next, movesahead, 1, tree)
        else:
            for node in tree:
                if node.depth == depth:
                    for state in generateNewMoves(node.board, node.turn):
                        nn = Node(state, next, depth + 1, 0, node, [])
                        node.children.append(nn)  # adding child to parent
                        tree.append(nn)  # adding child to tree
            minimax(board, next, movesahead, depth + 1, tree)
    else:
        # we now have the fished game tree (but no scores yet)
        # getting static eval scores for the terminal nodes
        for i in range(len(tree)):
            if tree[i].depth == movesahead:
                score = staticEval(tree[i].board, tree[i].turn, tree[0].turn)
                tree[i].score = score
            # if score == 10/-10, its a game over, cant move after that so delete the nodes children
            for i in range(len(tree)):
                score = staticEval(tree[i].board, tree[i].turn, tree[0].turn)
                if score == 10 or score == -10:
                    tree[i].score = score
                    tree[i].children.clear()
        # assigning scores to the rest of the tree by propagating values upward
        tree = getParentNodeScores(tree, depth)
        # for child in tree[0].children:  # for testing purposes, checking root's children
        #     print(child.board, child.score)
        # print("========")
    return getMaxScore(tree[0]).board


# board evaluator
# returns +10 if the board is such that black wins, -10 if white wins
# if neither win, returns # max pawns - # min pawns
def staticEval(state, turn, max):
    # checking if there is any legal moves
    if len(generateNewMoves(state, turn)) == 0:  # cant move
        # the specified player can't move
        if turn == max:
            return -10
        else:
            return 10
    whitepawns = 0
    blackpawns = 0
    for tile in state[0]:  # top row, if black is here, black wins
        if tile == "b" and max == "b":  # if black is max
            return 10
        if tile == "b" and max != "b":  # if white is max
            return -10
        if tile == "w":  # counting white pawns
            whitepawns += 1
    for tile in state[len(state) - 1]:  # bottom row, if white is here, white wins
        if tile == "w" and max != "w":  # if black is max
            return -10
        if tile == "w" and max == "w":  # if white is max
            return 10
        if tile == "b":  # counting black pawns
            blackpawns += 1
    # looking at rows inbetween first and last
    for row in state[1:len(state) - 1]:
        for tile in row:
            if tile == "w":
                whitepawns += 1
            if tile == "b":
                blackpawns += 1
    if max == "b":
        return blackpawns - whitepawns
    else:
        return whitepawns - blackpawns


# gets the scores for the non-terminal nodes by starting at the bottom, getting min/max score from children, then
# going one layer up and repeating
# returns the updated tree with the scores for all the nodes
def getParentNodeScores(tree, depth):
    for x in range(depth - 1, -1, -1):  # start at depth - 1 since we have scores for terminal nodes already
        for i in range(len(tree)):
            if tree[i].depth == x:
                if tree[i].turn == tree[0].turn:
                    tree[i].score = getMinScore(tree[i]).score
                if tree[i].turn != tree[0].turn:
                    tree[i].score = getMaxScore(tree[i]).score
    return tree


# gets the min score of a Node's children
# returns the node with the lowest score
# if no children, just returns the same node that was passed to it
def getMinScore(node):
    if len(node.children) > 0:
        temp = node.children[0]
    else:
        return node
    for child in node.children:
        if child.score < temp.score:
            temp = child
    return temp


# gets the max score of a Node's children
# returns the node with the highest score
# if not children, just returns the same node that was passed to it
def getMaxScore(node):
    if len(node.children) > 0:
        temp = node.children[0]
    else:
        return node
    for child in node.children:
        if child.score > temp.score:
            temp = child
    return temp


# white move generator
# generates all possible white moves
# returns a list of all of the new possible states (a list of lists)
def generateNewWhiteMoves(state):
    rownum = 0
    tilenum = 0
    newMoves = []
    for row in state:
        tilenum = 0
        for tile in row:
            if tile == "w":
                if rownum + 1 != len(row):  # at the end of the board
                    if state[rownum + 1][tilenum] == "-":  # checking if w can move forward
                        # can move forward
                        newMove = [elem[:] for elem in state]
                        newMove[rownum] = newMove[rownum][:tilenum] + "-" + newMove[rownum][tilenum + 1:]  # old pos
                        newMove[rownum + 1] = newMove[rownum + 1][:tilenum] + "w" + newMove[rownum + 1][tilenum + 1:]
                        newMoves.append(newMove)
                    if tilenum > 0:
                        if state[rownum + 1][tilenum - 1] == "b":
                            newMove = [elem[:] for elem in state]
                            newMove[rownum] = newMove[rownum][:tilenum] + "-" + newMove[rownum][tilenum + 1:]  # old pos
                            newMove[rownum + 1] = newMove[rownum + 1][:tilenum - 1] + "w" + newMove[rownum + 1][tilenum:]
                            newMoves.append(newMove)
                    if tilenum + 1 < len(row):
                        if state[rownum + 1][tilenum + 1] == "b":
                            newMove = [elem[:] for elem in state]
                            newMove[rownum] = newMove[rownum][:tilenum] + "-" + newMove[rownum][tilenum + 1:]  # old pos
                            newMove[rownum + 1] = newMove[rownum + 1][:tilenum + 1] + "w" + newMove[rownum + 1][tilenum + 2:]
                            newMoves.append(newMove)
            tilenum += 1
        rownum += 1
    return newMoves


# black move generator
# generates all possible black moves
# returns a list of all of the new possible states (a list of lists)
def generateNewBlackMoves(state):
    rownum = len(state) - 1  # starting at bottom of board
    tilenum = 0
    newMoves = []
    for row in reversed(state):
        tilenum = 0
        for tile in row:
            if tile == "b":
                if rownum - 1 >= 0:  # at the top of the board
                    if state[rownum - 1][tilenum] == "-":  # checking if b can move forward
                        # can move forward
                        newMove = [elem[:] for elem in state]
                        newMove[rownum] = newMove[rownum][:tilenum] + "-" + newMove[rownum][tilenum + 1:]  # old pos
                        newMove[rownum - 1] = newMove[rownum - 1][:tilenum] + "b" + newMove[rownum - 1][tilenum + 1:]
                        newMoves.append(newMove)
                    if tilenum > 0:
                        if state[rownum - 1][tilenum - 1] == "w":
                            newMove = [elem[:] for elem in state]
                            newMove[rownum] = newMove[rownum][:tilenum] + "-" + newMove[rownum][tilenum + 1:]  # old pos
                            newMove[rownum - 1] = newMove[rownum - 1][:tilenum - 1] + "b" + newMove[rownum - 1][tilenum:]
                            newMoves.append(newMove)
                    if tilenum + 1 < len(row):
                        if state[rownum - 1][tilenum + 1] == "w":
                            newMove = [elem[:] for elem in state]
                            newMove[rownum] = newMove[rownum][:tilenum] + "-" + newMove[rownum][tilenum + 1:]  # old pos
                            newMove[rownum - 1] = newMove[rownum - 1][:tilenum + 1] + "b" + newMove[rownum - 1][tilenum + 2:]
                            newMoves.append(newMove)
            tilenum += 1
        rownum -= 1
    return newMoves


# generates new moves depending on whos turn it is
# returns a list of the new possible moves
def generateNewMoves(state, turn):
    if turn == "w":
        return generateNewWhiteMoves(state)
    return generateNewBlackMoves(state)


# prints the board state nicely
def printBoard(state):
    for x in state:
        print(x)


# plays a game of hexapawn against itself
def playGame(board, turn, movesahead):
    over = staticEval(board, turn, turn)
    while over != -10 and over != 10:
        x = hexapawn(board, 73, turn, movesahead)
        printBoard(x)
        print("=======")
        board = x
        if turn == "b":
            turn = "w"
        else:
            turn = "b"
        over = staticEval(board, turn, turn)
        if len(generateNewMoves(board, turn)) == 0:
            break


test4 = ['----', 'wbww', 'b-wb', '----']
test3 = ['www', '---', 'bbb']
# print("Starting board:", test)
# printBoard(test)
# print("======")

# best = hexapawn(test3, 4, "w", 5)
# print("Best next move:", best)
# print("In board format:")
# printBoard(best)

# playGame(['www','---','bbb'], 'w', 4)
# playGame(['wwww','----','----','bbbb'], 'w', 4)

# print("BEsst", hexapawn(["w-w","-w-","b-b"],3,'b',2))

