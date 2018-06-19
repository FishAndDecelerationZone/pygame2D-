#2018.6.6 今天我怀着沉重的心情来吧Python的语法毕业设计给了结了
#消消乐.py     主要数据结构：字典
#Oliver      3392955216@qq.com

import random,time, pygame, sys,copy
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 600
WINDOWHIGHT  = 600
BOARDWIDTH = 8
BOARDHIGHT = 8
GEMIMAGESIZE = 64

NUMGEMIMAGES = 7
assert  NUMGEMIMAGES>5
NUMMATCHSOUNDS = 6

MOVERATE = 25
DEDUCTSPEED = 0.8


#                     R    G    B
PURPLE          =  (255,   0, 255)
LIGHTBLUE       =  (170, 190, 255)
BLUE            =  (  0,   0, 255)
RED             =  (255, 100, 100)
BLACK           =  (0,     0,   0)
BROWN           =  ( 85,  65,   0)
#设置颜色
HIGHTLIGETCOLOR = PURPLE
BGCOLOR = LIGHTBLUE
GRIDECOLOR = BLUE
GAMEOVERCOLOR = RED
GAMEOVERBGCOLOR = BLACK
SCORECOLOR = BROWN
#设置窗口空白
XMARGIN = int( (WINDOWWIDTH - GEMIMAGESIZE * BOARDWIDTH) / 2)
YMARGIN = int( (WINDOWHIGHT - GEMIMAGESIZE * BOARDHIGHT) / 2)
#设置方向
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

EMPTY_SPACE = -1
ROWABOVEBOARD = 'row above board'


def main():
    global FPSCLOCK, DISPLAYSURF, GEMIMAGES, GEMSOUNDS, BASICFONT, BOARDRECTS
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHIGHT))
    pygame.display.set_caption('消消乐')
    BASICFONT = pygame.font.Font('my_fonts.ttf', 36)

    GEMIMAGES = []      #图片列表
    #读取图片
    for i in range(1, NUMGEMIMAGES+1):
        gemImage = pygame.image.load( 'material/gem%s.png' % i)
        if gemImage.get_size != GEMIMAGESIZE:
            gemImage = pygame.transform.smoothscale(gemImage, (GEMIMAGESIZE, GEMIMAGESIZE))  #截取图像
        GEMIMAGES.append(gemImage)

    #load the sounds
    pygame.mixer.music.load('material\Ground.mp3')
    pygame.mixer.music.play(-1, 0.0)
    GEMSOUNDS = {}     #声音字典
    GEMSOUNDS['bad swap']= pygame.mixer.Sound('material\Badswap.wav')
    GEMSOUNDS['match'] = []
    for i in range(NUMMATCHSOUNDS):
        GEMSOUNDS['match'].append( pygame.mixer.Sound('material\Match%s.wav'%i) )

    #Create pygame rect Object
    BOARDRECTS = []
    for x in range(BOARDWIDTH):
        BOARDRECTS.append([])
        for y in range(BOARDHIGHT):
            r = pygame.Rect( (XMARGIN + (GEMIMAGESIZE * x), (YMARGIN + GEMIMAGESIZE * y), GEMIMAGESIZE, GEMIMAGESIZE) )
            BOARDRECTS[x].append(r)

    while True:
        run_game()

def run_game():
    """Plays through a single game. When the game is over, this function returns"""
    #initialize the board
    gameBoard = get_blank_board()
    score = 0
    fill_board_and_animate(gameBoard, [], score)

    firstSelectedGem = None
    lastMouseDownX = None
    lastMouseDownY = None
    gameIsOver = False
    lastScoreDeduction = time.time()
    clickContinueTextSurf = None

    while True:
        clickedSpace = None
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.type == K_ESCAPE):
                pygame.mixer.stop()
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP and event.type == K_BACKQUOTE:
                return  # 重新开始游戏
            elif event.type == MOUSEBUTTONUP:
                if gameIsOver:
                    return

                if event.pos == (lastMouseDownX, lastMouseDownY):  # 点击的是同一块方块
                    clickedSpace = check_for_click(event.pos)
                else:
                    firstSelectedGem = check_for_click((lastMouseDownX, lastMouseDownY))
                    clickedSpace = check_for_click(event.pos)
                    if not firstSelectedGem or not clickedSpace:  # 有无效点击
                        firstSelectedGem = None
                        clickedSpace = None

            elif event.type == MOUSEBUTTONDOWN:
                lastMouseDownX, lastMouseDownY = event.pos

        if clickedSpace and not firstSelectedGem: #第一次点击
            firstSelectedGem = clickedSpace
        elif clickedSpace and firstSelectedGem:
            firstSwappingGem, secondSwappingGem = get_swapping_gems(gameBoard,firstSelectedGem, clickedSpace)
            if firstSwappingGem == None and secondSwappingGem == None:
                firstSelectedGem = None
                continue

            boardCopy = get_board_copy_minus_gems(gameBoard, (firstSwappingGem, secondSwappingGem) )
            animate_moving_gems(boardCopy, [firstSwappingGem, secondSwappingGem], [], score)
            gameBoard[ firstSwappingGem['x'] ][ firstSwappingGem['y'] ] = secondSwappingGem['imageNum']
            gameBoard[ secondSwappingGem['x'] ][ secondSwappingGem['y'] ] = firstSwappingGem['imageNum']

            matchedGems = find_matching_gems(gameBoard)
            if matchedGems == []:
                GEMSOUNDS['bad swap'].play()
                animate_moving_gems(boardCopy, [firstSwappingGem, secondSwappingGem], [], score)
                gameBoard[firstSwappingGem['x']][firstSwappingGem['y']] = firstSwappingGem['imageNum']
                gameBoard[secondSwappingGem['x']][secondSwappingGem['y']] = secondSwappingGem['imageNum']
            else:
                scoreAdd = 0
                while matchedGems != []:
                    points = []
                    for gemSet in matchedGems:
                        scoreAdd += (10 +(len(gemSet) - 3 ) *10)
                        for gem in gemSet:
                            gameBoard[gem[0]][gem[1]] = EMPTY_SPACE
                        points.append({'points': scoreAdd, 'x':gem[0] * GEMIMAGESIZE + XMARGIN,
                                       'y':gem[1] * GEMIMAGESIZE + YMARGIN})
                    random.choice(GEMSOUNDS['match']).play()
                    score += scoreAdd

                    fill_board_and_animate(gameBoard, points, score)
                    matchedGems = find_matching_gems(gameBoard)
            firstSelectedGem = None


            if not can_make_move(gameBoard):
                gameIsOver = True
        DISPLAYSURF.fill(BGCOLOR)
        draw_board(gameBoard)
        if firstSelectedGem != None:
            high_light_space(firstSelectedGem['x'], firstSelectedGem['y'])
        if gameIsOver:
            if clickContinueTextSurf == None:
                clickContinueTextSurf = BASICFONT.render('Final Score: %s (Click to continue)' % (score), 1, GAMEOVERBGCOLOR, GAMEOVERBGCOLOR )
                clickContinueTexRect = clickContinueTextSurf.get_rect()
                clickContinueTexRect.center = int(WINDOWWIDTH / 2)
            DISPLAYSURF.blit(clickContinueTextSurf, clickContinueTexRect)
        elif score >0 and time.time() - lastScoreDeduction > DEDUCTSPEED:
            score -= 5
            lastScoreDeduction = time.time()
        draw_score(score)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def get_blank_board():
    """Return a blank board data structure"""
    board = []
    for x in range(BOARDWIDTH):
        board.append([EMPTY_SPACE]*BOARDHIGHT)
    return board


def get_swapping_gems(board, firstXY, secondXY):
    """判断移动方向"""
    firstGem = {'imageNum': board[ firstXY['x'] ][ firstXY['y'] ], 'x':firstXY['x'], 'y':firstXY['y']}
    secondGem = {'imageNum': board[ secondXY['x'] ][ secondXY['y'] ], 'x':secondXY['x'], 'y':secondXY['y']}
    if firstGem['x'] == secondXY['x'] and firstGem['y'] == secondGem['y'] + 1:
        firstGem['direction'] = UP
        secondGem['direction'] = DOWN
    elif firstGem['x'] == secondGem['x'] and firstGem['y'] + 1 == secondGem['y']:
        firstGem['direction'] = DOWN
        secondGem['direction'] = UP
    elif firstGem['x'] == secondGem['x'] +1 and firstGem['y'] == secondGem['y']:
        firstGem['direction'] = LEFT
        secondGem['direction'] = RIGHT
    elif firstGem['x'] + 1 == secondGem['x'] and firstGem['y'] == secondGem['y']:
        firstGem['direction'] = RIGHT
        secondGem['direction'] = LEFT
    else:
        return  None,None
    return  firstGem, secondGem


def can_make_move(board):
    """游戏是否能继续"""
    oneOffPatterns = (((0,1), (1,0), (2,0)),
                      ((0,1), (1,1), (2,0)),
                      ((0,0), (1,1), (2,0)),
                      ((0,1), (1,0), (2,1)),
                      ((0,0), (1,0), (2,1)),
                      ((0,0), (1,0), (2,1)),
                      ((0,0), (0,2), (0,3)),
                      ((0,0), (0,1), (0,3))
                      )
    for x in range(BOARDWIDTH):
        for y in range(BOARDHIGHT):
            for pat in oneOffPatterns:
                if (get_gem_at(board, x+pat[0][0], y+pat[0][1]) == get_gem_at(board, x+pat[1][0], y+pat[1][1]) == get_gem_at(board, x+pat[2][0], y+pat[2][1]) != None) or\
                   (get_gem_at(board, x+pat[0][1], y+pat[0][0]) == get_gem_at(board, x+pat[1][1], y+pat[1][0]) == get_gem_at(board, x+pat[2][1], y+pat[2][0])):
                    return  True
    return False


def draw_moving_gem(gem, progress):
    """ 绘制移动中的贴片"""
    movex = 0
    movey = 0
    progress = progress * 0.01

    if 'direction'  in gem:

        if gem['direction'] == UP:
            movey = -int(progress * GEMIMAGESIZE)
        elif gem['direction'] == DOWN:
            movey = int(progress * GEMIMAGESIZE)
        elif gem['direction'] == LEFT:
            movex = -int(progress * GEMIMAGESIZE)
        elif gem['direction'] == RIGHT:
            movex = int(progress * GEMIMAGESIZE)

    if gem['y'] != ROWABOVEBOARD:
        basex = gem['x']
        basey = gem['y']

        pixelx = XMARGIN + (int(basex) * GEMIMAGESIZE)
        pixely = YMARGIN + (int(basey) * GEMIMAGESIZE)

        r = pygame.Rect((pixelx + movex, pixely + movey, GEMIMAGESIZE, GEMIMAGESIZE))
        DISPLAYSURF.blit(GEMIMAGES[gem['imageNum']], r)



def pull_down_all_gems(board):
    """Pull down all gems"""
    for x in range(BOARDWIDTH):
        gemsInColumn = []
        for y in range(BOARDHIGHT):
            if board[x][y] != EMPTY_SPACE:
                gemsInColumn.append(board[x][y])
        board[x] = ( [EMPTY_SPACE] * (BOARDHIGHT - len(gemsInColumn)) + gemsInColumn)


def get_gem_at(board, x,y):
    """ 获取（x,y）位置的贴片"""
    if x < 0 or y <0 or x >= BOARDWIDTH or y >= BOARDHIGHT:
        return None
    else:
        return board[x][y]


def get_drop_slots(board):
    """填充下落后的游戏板, 并返回填入的方块列表"""
    boardCopy = copy.deepcopy(board)
    pull_down_all_gems(boardCopy)

    dropSlots = []
    for x in range(BOARDWIDTH):
        dropSlots.append([])

    for x in range(BOARDWIDTH):
        for y in range(BOARDHIGHT - 1, -1, -1):
            if boardCopy[x][y] == EMPTY_SPACE:

                prossibleGems = list(range(len(GEMIMAGES)))     #???
                for offsetX, offsetY in ((0,-1), (0, 1), (1, 0), (-1, 0)):
                    neighborGem = get_gem_at(boardCopy, offsetX + x, y + offsetY)

                    if neighborGem != None and neighborGem in prossibleGems:
                        prossibleGems.remove(neighborGem)

                NewGem = random.choice(prossibleGems)
                board[x][y] = NewGem
                dropSlots[x].append(NewGem)
    return dropSlots


def find_matching_gems(board):
    """ 查找游戏版中能消去的贴片
        查找算法：1.分列/行 查找是否满足三消 2.查找该列/行 所有能消去的贴片
                    3.分别判断改列/行 每个贴片左右/上下（若相邻的贴片超过3个则会在行/列 查找时消去） 的贴片
                    4.再判断3中消去贴片的 上下/左右贴片
                     - - 4 3 - - - -
                     - - - 2 2 2 2 -
        """
    gemToRemove = []
    boardCopy = copy.deepcopy(board)
    for x in range(BOARDWIDTH):
        for y in range(BOARDHIGHT):

            if get_gem_at(board, x, y) == get_gem_at(board, x+1, y) == get_gem_at(board, x+2, y) != EMPTY_SPACE:
                targetGem = board[x][y]
                offset = 0
                removeSet = []

                while get_gem_at(boardCopy, x + offset, y) == targetGem:

                    if get_gem_at(boardCopy, x + offset, y+1) == targetGem:
                        removeSet.append( ( x + offset, y+1))
                        if get_gem_at(boardCopy, x +offset-1, y+1) == targetGem:
                            removeSet.append( (x + offset -1, y+1) )
                        if get_gem_at(boardCopy, x + offset + 1, y+1) == targetGem:
                            removeSet.append( (x + offset +1, y+1))

                    if get_gem_at(boardCopy, x+offset, y-1) == targetGem:
                        removeSet.append( ( x+offset, y-1) )
                        if get_gem_at(boardCopy, x+offset+1, y-1):
                            removeSet.append((x+offset+1, y-1))
                        if get_gem_at(boardCopy, x+offset-1, y-1):
                            removeSet.append((x+offset-1, y-1))
                    removeSet.append( (x+offset,y) )
                    offset += 1
                gemToRemove.append(removeSet)

            if get_gem_at(board, x, y) == get_gem_at(board, x, y+1) == get_gem_at(board, x, y+2) != EMPTY_SPACE:
                targetGem = board[x][y]
                offset = 0
                removeSet = []

                while get_gem_at(boardCopy, x, y+offset) == targetGem:

                    if get_gem_at(boardCopy, x+1, y+offset) == targetGem:
                        removeSet.append((x+1, y+offset))
                        if get_gem_at(boardCopy, x+1, y+offset+1)== targetGem:
                            removeSet.append((x+1, y+offset+1))
                        if get_gem_at(boardCopy, x+1, y+offset-1)==targetGem:
                            removeSet.append((x+1, y+offset-1))

                    if get_gem_at(boardCopy, x-1, y+offset) == targetGem:
                        removeSet.append((x-1, y+offset))
                        if get_gem_at(boardCopy, x - 1, y + offset+1) == targetGem:
                            removeSet.append((x - 1, y + offset+1))
                        if get_gem_at(boardCopy, x - 1, y + offset-1) == targetGem:
                            removeSet.append((x - 1, y + offset-1))

                    removeSet.append((x, y+offset))
                    offset += 1

                gemToRemove.append(removeSet)

    for gemx in gemToRemove:
        for gemy in gemx:
            boardCopy[gemy[0]][gemy[1]] = EMPTY_SPACE
    return  gemToRemove


def high_light_space(x,y):
    """ """
    pygame.draw.rect(DISPLAYSURF, HIGHTLIGETCOLOR, BOARDRECTS[x][y], 4)
    print(0)

def get_dropping_gems(board):
    """Find all the gems that have an empty space below them"""
    boardCopy = copy.deepcopy(board)
    droppingGems = []       #字典的列表
    for x in range(BOARDWIDTH):
        for y in range(BOARDHIGHT-2, -1, -1):
            if boardCopy[x][y + 1] == EMPTY_SPACE and boardCopy[x][y] != EMPTY_SPACE:
                droppingGems.append({ 'imageNum':boardCopy[x][y], 'x':x, 'y':y, 'direction': DOWN})
                boardCopy[x][y] = EMPTY_SPACE
    return  droppingGems


def animate_moving_gems(board, gems, pointsText, score):
    """ """
    progress = 0
    while progress<100:
        DISPLAYSURF.fill(BGCOLOR)
        draw_board(board)
        for gem in gems:
            draw_moving_gem(gem, progress)
        draw_score(score)
        for pointText in pointsText:
            pointsSurf = BASICFONT.render(str(pointText['points']), 1, SCORECOLOR)
            pointsRect = pointsSurf.get_rect()
            pointsRect.center = (pointText['x'], pointText['y'])
            DISPLAYSURF.blit(pointsSurf, pointsRect)

        pygame.display.update()
        FPSCLOCK.tick(FPS)
        progress += MOVERATE


def move_gems(board, movingGems):
    """ """
    for gem in movingGems:
        if gem['y'] != ROWABOVEBOARD:
            board[gem['x']][gem['y']] = EMPTY_SPACE
            movex = 0
            movey = 0
            if gem['direction'] == LEFT:
                movex = -1
            elif gem['direction'] == RIGHT:
                movex = 1
            elif gem['direction'] == UP:
                movey = -1
            elif gem['direction'] == DOWN:
                movey = 1

            board[gem['x'] + movex][gem['y'] + movey] = gem['imageNum']
        else:
            #gem is located above the board (where new gems come form )
            board[gem['x']][0] = gem['imageNum']


def fill_board_and_animate(board, points, score):
    """ 填充并绘制动画"""
    dropSlots = get_drop_slots(board)
    while dropSlots != [[]]* BOARDWIDTH:
        movingGems = get_dropping_gems(board)
        for x in range(len(dropSlots)):
            if len(dropSlots[x]) != 0:
                movingGems.append({'imageNum' : dropSlots, 'x' : x, 'y': ROWABOVEBOARD})

        boardCopy = get_board_copy_minus_gems(board, movingGems)
        animate_moving_gems(boardCopy, movingGems, points, score)
        move_gems(board, movingGems)

        for x in range(len(dropSlots)):
            if len(dropSlots[x]) == 0:
                continue
            board[x][0] = dropSlots[x][0]
            del dropSlots[x][0]


def check_for_click(pos):
    """ see if mouse clidk was on the board"""
    for x in range(BOARDWIDTH):
        for y in range(BOARDHIGHT):
            if BOARDRECTS[x][y].collidepoint(pos[0],pos[1]):
                return {'x':x, 'y':y}
    return None    #click is not in the board


def draw_board(board):
    """绘制游戏板"""
    for x in range(BOARDWIDTH):
        for y in range(BOARDHIGHT):
            pygame.draw.rect(DISPLAYSURF, GRIDECOLOR, BOARDRECTS[x][y], 1)

            gemTodrow = board[x][y]
            if gemTodrow != EMPTY_SPACE:
                DISPLAYSURF.blit(GEMIMAGES[gemTodrow], BOARDRECTS[x][y])

def get_board_copy_minus_gems(board, gems):     #???
    """"""
    boardCopy = copy.deepcopy(board)

    for gem in gems:
        if gem['y'] != ROWABOVEBOARD:
            boardCopy[gem['x']][gem['y']] = EMPTY_SPACE
    return  boardCopy

def draw_score(score):
    """ 绘制计分方块"""
    scoreImg = BASICFONT.render(str(score), 1, SCORECOLOR)
    scoreRect = scoreImg.get_rect()
    scoreRect.bottomleft = (10, WINDOWHIGHT - 10)
    DISPLAYSURF.blit(scoreImg, scoreRect)


if __name__ == '__main__':
    main()