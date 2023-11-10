import chess
import chess.svg
import chess.pgn
import asyncio
from pyodide import create_proxy
from pyodide.http import open_url
import js
from js import console
from js import document

import sys
from queue import Queue

#BFS structures
adj = [[] for _ in range(64)]
dist = [-1] * 64
visited = [False] * 64
bfs_queue = Queue()

# Found solutions
recMoneyCount = -1
recPositions = []



# POSITION MAPPING
def getIdx(row, column): #nodes count from 0
    return (row - 1) * 8 + column - 1

def getRowColumn(idx):
    row = (idx)//8+1
    column = (idx)%8+1
    return(row, column)

def inBounds(row, col):
    return 1 <= row <= 8 and 1 <= col <= 8


# STRUCTURE PREPARATION
def generateKnightAdj():  # creates an adjacency matrix of all possible horse' moves for each position
    for row in range(1, 9):
        for col in range(1, 9):
            idx = getIdx(row, col)
            if inBounds(row + 3, col + 1):
                adj[idx].append(getIdx(row + 3, col + 1))
            if inBounds(row + 1, col + 3):
                adj[idx].append(getIdx(row + 1, col + 3))
            if inBounds(row - 1, col + 3):
                adj[idx].append(getIdx(row - 1, col + 3))
            if inBounds(row - 3, col + 1):
                adj[idx].append(getIdx(row - 3, col + 1))
            if inBounds(row - 3, col - 1):
                adj[idx].append(getIdx(row - 3, col - 1))
            if inBounds(row - 1, col - 3):
                adj[idx].append(getIdx(row - 1, col - 3))
            if inBounds(row + 1, col - 3):
                adj[idx].append(getIdx(row + 1, col - 3))
            if inBounds(row + 3, col - 1):
                adj[idx].append(getIdx(row + 3, col - 1))


def resetStructures():
    global dist, visited, bfs_queue
    #adj = [[] for _ in range(64)] # no need - after generation always the same
    dist = [-1] * 64
    visited = [False] * 64
    bfs_queue = Queue()


# BACKTRACKING
def bfs(idx):
    visited[idx] = True
    dist[idx] = 0
    bfs_queue.put(idx)
    while not bfs_queue.empty():
        parent = bfs_queue.get()
        if(dist[parent]+1 >k):
            break
        for current in adj[parent]:
            if (visited[current]):
                continue
            visited[current] = True
            dist[current] = dist[parent] + 1
            bfs_queue.put(current)


# GUI
lastDisplayed = 0
output=[]
def printWeb(contents): #logs in console and displays on the browser
    output.append(contents)
    console.log(contents)
    pyscript.write("output", "\r\n".join(output))

# async def get_square(event):
#     global board
#     piece = js.get_object()
#     if len(piece) > 0:
#         console.log(f'Focused on piece: {piece}')
#         draw(board, focus=piece)

async def _new_variables(event):#reads input parameters
    global M, k
    M = document.querySelector("#inputM").value
    k = document.querySelector("#inputK").value

    try:
        M = int(M)
        printWeb(f"Money count player can carry -> {M}")
        k = int(k)
        printWeb(f"Depth: -> {k}")
    except(Exception):
        printWeb("ERROR: Not an integer.")

    console.log(f"Mk {M} {k}")


def draw(board, draw_text=False, focus=False): # displays board
    fill = {}
    if focus:
        fill = dict.fromkeys([index for index, value in enumerate(visited) if value], "#ff0000aa")# | {chess.parse_square(focus): "#fdda0dff"}
    if not draw_text:
        b_svg = chess.svg.board(
            board=board,
            fill=fill,
            colors={'margin':'#30ac10'},
            size=700)
        pyscript.write('svg', b_svg)
    else:
        pyscript.write('svg', '')
        pyscript.write('text', '')
        for row in str(board).split('\n'):
            pyscript.write('text', row, append=True)

def displayOption(id):
    global recPositions, board, lastDisplayed
    lastDisplayed = id
    (row, column) = recPositions[id]
    idx=getIdx(row, column)
    resetStructures()
    bfs(idx)
    board.clear()
    board.set_piece_at(chess.square(column-1, row-1), chess.Piece(chess.KNIGHT, chess.WHITE))
    draw(board, focus=True)
    
async def calculateClicked(*args, **kwargs): # initiates board scanning and displays results
    global board
    global M, k
    global recMoneyCount, recPositions

    board.clear()
    draw(board)

    await _new_variables(None)


    generateKnightAdj()
    recMoneyCount = -1
    recPositions = [] # in tuple (row, column)

    for row in range(1, 9):
        for col in range(1, 9):
            idx = getIdx(row, col)
            resetStructures()
            bfs(idx)
            totalMoney = sum([2 ** (k - p) for p in dist if p<=k and p!=-1])
            printWeb(f"Row: {row} Col: {col}  Idx: {idx} Money: {totalMoney}")

            if recMoneyCount < totalMoney and totalMoney <= M:
                recMoneyCount = totalMoney
                recPositions.clear()
                recPositions.append((row, col))
            elif recMoneyCount==totalMoney:
                recPositions.append((row, col))
    
    #results
    if(recMoneyCount>=0):
        printWeb(f"Amount of money player will get: {recMoneyCount}.")
        printWeb(f"If the knight will stood in these places:")
        for row, col in recPositions:
            printWeb(f"  * Row = {row}, Column = {col}")
        displayOption(0)
    else:
        printWeb("Player needs to run!")

async def nextClicked(*args, **kwargs):
    global recMoneyCount, recPositions, lastDisplayed
    if(recMoneyCount>=0):
        if(lastDisplayed<len(recPositions)):
            lastDisplayed+=1
            displayOption(lastDisplayed)

async def prevClicked(*args, **kwargs):
    global recMoneyCount, recPositions, lastDisplayed
    if(recMoneyCount>=0):
        if(lastDisplayed>0):
            lastDisplayed-=1
            displayOption(lastDisplayed)


new_variables = create_proxy(_new_variables)# when one of the parameters change
# document.querySelector("#inputK").addEventListener("change", new_variables)
# document.querySelector("#inputM").addEventListener("change", new_variables)

# click_proxy = create_proxy(get_square)
# document.addEventListener("click", click_proxy)

board = chess.Board()
board.clear()
draw(board)

