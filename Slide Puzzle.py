#Slide Puzzle
#By Oliver 3392955216@qq.com

import pygame,sys,random
from pygame.locals import *

BOARDWIDTH = 4
BOARDHEIGHT = 4
TILESIZE = 80
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FPS = 30
BLANK = None

#                           R    G    B
BLACK         =          (  0,   0,   0)
WHITE         =          (255, 255, 255)
BRIGHTBLUE    =          (  0,  50, 255)
DARKTURQUOISE =          (  3,  54,  73)
GREEN         =          (  0, 204,   0)
BLUE = (0, 0, 128)

BGCOLOR = DARKTURQUOISE
TILECOLOR = GREEN
TEXTCOLOR = WHITE
BORDERCOLOR = BRIGHTBLUE
BASICFONTSIZE = 20

BUTTONCOLOR = WHITE
BUTTONTEXITCOLOR = BLACK
MESSAGECOLOR = WHITE

XMARGIN = int( (WINDOWWIDTH - (TILESIZE * BOARDWIDTH +(BOARDWIDTH - 1)) ) /2 )
YMARGIN = int( (WINDOWHEIGHT - (BOARDWIDTH * TILESIZE + (BOARDHEIGHT - 1))) /2 )

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, SOLVE_SURF, SOLVE_RECT, MOVENUM

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    pygame.display.set_caption("Slide Puzzle")
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)
    #创建按钮
    RESET_SURF, RESET_RECT = make_text( ' Rect ', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 90)
    SOLVE_SURF, SOLVE_RECT = make_text( ' Solve ', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 60)
    NEW_SURF, NEW_RECT = make_text( ' New Game ', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 30)
    MOVENUM = 0
    mainBoard, solutionSeq = generate_newPuzzle(80)
    SOLVEDBOARD = get_startring_board()
    allMoves = []


    while True:
        slidTo =  None          #贴片移动方向
        msg = ''                #显示的信息
        if mainBoard == SOLVEDBOARD:
            msg = 'Solved!'

        draw_board(mainBoard, msg)

        check_for_quit()            #检查是否退出
        for event in pygame.event.get():
            # 处理鼠标事件
            if event.type == MOUSEBUTTONUP:
                spotx, spoty = get_spot_clicked(mainBoard, event.pos[0], event.pos[1])      #获取鼠标点击的游戏板坐标

                if (spotx, spoty) == (None, None):
                    if RESET_RECT.collidepoint(event.pos):          #重新开始
                        resetAnimation(mainBoard, allMoves)
                        allMoves = []
                    elif NEW_RECT.collidepoint(event.pos):          #新游戏
                        mainBoard, solutionSeq = generate_newPuzzle(80)
                        allMoves = []
                    elif SOLVE_RECT.collidepoint(event.pos):        #解开游戏
                        resetAnimation(mainBoard, solutionSeq + allMoves)
                        allMoves = []
                else:
                    blankx, blanky = get_blank_position(mainBoard)          #根据鼠标点击位置判断空白方块移动方向
                    if spotx == blankx + 1 and spoty == blanky:
                            slidTo = LEFT
                    elif spotx == blankx - 1 and spoty == blanky:
                            slidTo = RIGHT
                    elif spoty == blanky - 1 and spotx == blankx:
                            slidTo = DOWN
                    elif spoty == blanky + 1 and spotx == blankx:
                            slidTo = UP
            elif event.type == KEYUP:               #处理键盘事件（判断移动是否有效）
                if event.key in (K_LEFT, K_a) and is_valid_move(mainBoard, LEFT):
                    slidTo = LEFT
                elif event.key in (K_RIGHT, K_d) and is_valid_move(mainBoard, RIGHT):
                    slidTo = RIGHT
                elif event.key in (K_UP, K_w) and is_valid_move(mainBoard, UP):
                    slidTo = UP
                elif event.key in (K_DOWN, K_s) and is_valid_move(mainBoard, DOWN):
                    slidTo = DOWN
        if slidTo :
            slide_animation(mainBoard, slidTo, 'Click tile or press arrow keys to slide.', 8)
            make_move(mainBoard, slidTo)
            allMoves.append(slidTo)
            MOVENUM +=1
            print(slidTo)

        pygame.display.update()
        FPSCLOCK.tick(FPS)





def terminate():            #终止函数
    pygame.quit()
    sys.exit()


def check_for_quit():
    for event in pygame.event.get(QUIT):            #读取事件
            terminate()
    for event in pygame.event.get(KEYUP):       #从事件列队中“提取”所有KEYUP事件（pygame事件列队最多只有127个Event对象）
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event)                #如果event事件不是针对Esc的事件，则要把event事件放回事件列队队尾


def get_startring_board():
    #Return a board data structure with tiles in the solved state.
    #For example, if BOARDWIDTH and BOARDHEIGHT ARE both 3, this function
    #returns = [[1, 4, 7], [2, 5, 8], [3, 6, none]]
    counter = 1
    board = []
    for x in range(BOARDWIDTH):         #生成一个解开的游戏板数据
        cloumn = []
        for y in range(BOARDHEIGHT):
            cloumn.append(counter)
            counter += BOARDWIDTH
        board.append(cloumn)
        counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH -1

    board[BOARDWIDTH-1][BOARDHEIGHT-1] = None
    return board


def get_blank_position(board):          #查找空白格的游戏板位置
    # Return the x and y of board corrdinates of the blank space.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == None:
                return  ( x, y)


def make_move(board, move):
    # The function does not check if the move is valid
    blankx, blanky = get_blank_position(board)
    if move == UP:
        board[blankx][blanky], board[blankx][blanky+1] = board[blankx][blanky+1], board[blankx][blanky]
    elif move == DOWN:
        board[blankx][blanky], board[blankx][blanky-1] = board[blankx][blanky-1], board[blankx][blanky]
    elif move == LEFT:
        board[blankx][blanky], board[blankx+1][blanky] = board[blankx+1][blanky], board[blankx][blanky]
    elif move == RIGHT:
        board[blankx][blanky], board[blankx-1][blanky] = board[blankx-1][blanky], board[blankx][blanky]


def is_valid_move(board, move):
    #emmmmminteresting  当贴片要上移时，空白格不能在最下端否则是无效的
    blankx, blanky = get_blank_position(board)              #  '\'用来换行
    return (move == UP and blanky != len(board[0]) - 1) or \
           (move == DOWN and blanky != 0) or \
           (move == LEFT and blankx != len(board) - 1) or \
           (move == RIGHT and blankx != 0)


def get_random_move(board, lastMove = None):
    valiMoves = [UP, DOWN, LEFT, RIGHT]

    #intersting
    if lastMove == UP or not is_valid_move(board, DOWN) :           #获取一次随机的有效移动
        valiMoves.remove(DOWN)
    if lastMove == DOWN or not is_valid_move(board, UP) :
        valiMoves.remove(UP)
    if lastMove == LEFT or not is_valid_move(board, RIGHT):
        valiMoves.remove(RIGHT)
    if lastMove == RIGHT or not is_valid_move(board, LEFT):
        valiMoves.remove(LEFT)

    return  random.choice(valiMoves)


def get_left_top_of_tile(tileX, tileY):
    #将贴片坐标转换为像素坐标
    left =( XMARGIN + (tileX * TILESIZE) + (tileX - 1))
    top = (YMARGIN + (tileY * TILESIZE) + (tileY -1))
    return  (left, top)


def get_spot_clicked(board, x, y):
    #将像素坐标转换为贴片坐标
    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
            left, top  = get_left_top_of_tile(tilex, tiley)
            tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tileRect.collidepoint(x,y):
                return (tilex, tiley)
    return  (None, None)


def draw_tile(tilex, tiley, number, adjx=0, adjy=0):
    #绘制一个贴片

    left, top = get_left_top_of_tile(tilex, tiley)
    pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left + adjx, top + adjy, TILESIZE, TILESIZE))
    textSurf = BASICFONT.render(str(number), True, TEXTCOLOR)
    textRect = textSurf.get_rect()              #获取一个新的rect对象用于将surface对象定位
    textRect.center =  left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy          #方便后期移动贴片
    DISPLAYSURF.blit(textSurf, textRect)               #利用rect将surface复制显示到SURFACE上


def make_text(text, color, bgcolor, top, left):
    #创建用于显示 solve等按钮的文本
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)              #通过rect对象的topleft属性设置其位置，还可通过center属性来设置位置
    return (textSurf, textRect)


def draw_board(board, message):
    #绘制游戏板
    DISPLAYSURF.fill(BGCOLOR)
    if message:             #显示信息
        textSurf, textRect = make_text(message, MESSAGECOLOR, BGCOLOR, 5, 5)

        DISPLAYSURF.blit( textSurf, textRect)
    textSurf, textRect = make_text('Moves: ' + str(MOVENUM), MESSAGECOLOR, BGCOLOR, WINDOWWIDTH - XMARGIN, 10)
    DISPLAYSURF.blit( textSurf, textRect)
    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
            if board[tilex][tiley]:
                draw_tile(tilex, tiley, board[tilex][tiley])

    #绘制高亮边框
    left, top = get_left_top_of_tile(0, 0)
    width = TILESIZE * BOARDWIDTH
    height = TILESIZE * BOARDHEIGHT
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
    DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)


def slide_animation(board, direction, message, animationSpeed):
    #tile滑动动画
    blankx, blanky = get_blank_position(board)
    assert not direction in ('UP', 'DOWN', 'LEFT', 'RIGHT')
    if direction == UP:
        movex = blankx
        movey = blanky + 1
    elif direction == DOWN:
        movex = blankx
        movey = blanky - 1
    elif direction == LEFT:
        movex = blankx + 1
        movey = blanky
    elif direction == RIGHT:
        movex = blankx - 1
        movey = blanky

#* * * * * ** ** ** ** * * ** *
    draw_board(board, message)
    baseSurf = DISPLAYSURF.copy()               # Surface对象的copy方法能复制一个副本 这样就能防止原对象被修改
    moveLeft, moveTop = get_left_top_of_tile(movex, movey)
    pygame.draw.rect(baseSurf, BGCOLOR, (moveLeft, moveTop, TILESIZE, TILESIZE ))       #如果不把空白格提前设置成空白，移动贴片的时候会怪怪的

    for i in range(0, TILESIZE, animationSpeed):
        check_for_quit()
        DISPLAYSURF.blit(baseSurf, (0, 0))
        if direction == UP:
            draw_tile(movex, movey, board[movex][movey], 0, -i)
        if direction == DOWN:
            draw_tile(movex, movey, board[movex][movey], 0, i)
        if direction == LEFT:
            draw_tile(movex, movey, board[movex][movey], -i, 0)
        if direction == RIGHT:
            draw_tile(movex, movey, board[movex][movey], i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generate_newPuzzle( numSlides ):            #产生一个新谜题
    sequence = []
    global MOVENUM
    MOVENUM= 0
    board = get_startring_board()
    draw_board(board, '')
    pygame.display.update()
    pygame.time.wait(500)

    lastMove = None
    for i in range(numSlides):                  #随机移动numSlides次
        move = get_random_move(board, lastMove)
        slide_animation(board, move, 'Generating new puzzle....', int(TILESIZE / 3))
        make_move(board, move)
        sequence.append( move )
        lastMove = move

    return (board, sequence)


def resetAnimation(board, allMoves):
    #游戏板重置动画
    reALLMves = allMoves[:]
    reALLMves.reverse()             #倒制函数

    for move in reALLMves:
        if move == UP:
            oppositeMove = DOWN
        if move == DOWN:
            oppositeMove = UP
        if move == LEFT:
            oppositeMove = RIGHT
        if move == RIGHT:
            oppositeMove = LEFT

        slide_animation(board, oppositeMove, '', int( TILESIZE / 2))
        make_move(board, oppositeMove)
    global MOVENUM
    MOVENUM = 0


if __name__ in '__main__':
    main()