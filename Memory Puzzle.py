# Menory Puzzle.py
#By Oliver 3392955216@qq.com

import random, pygame,sys
from pygame.locals import *

FPS=60      #屏幕刷新频率
WINDOWWIDTH = 640         #窗口宽度
WINDOWHEIGHT = 480        #C窗口高度
REVEALSPEED = 8           #BOX一次揭开或者覆盖的块数
BOXSIZE = 40        #BOX的大小
GAPSIZE = 10        #BOX间的间隙宽度
BOARDWIDTH = 10      #一行的box个数
BOARDHEIGHT = 7     #一列的box个数

assert (BOARDHEIGHT * BOARDWIDTH) % 2 ==0           # ****** 断言（提前崩溃）使用assert语句检查其后的表答式 如果为flase 的话导致会导致崩溃
XMARGIN = int((WINDOWWIDTH-(BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT-(BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)         #分别计算x轴和y轴的空白宽度
#                               R    G    B
GRAY                        = (100, 100, 100)
NAVYBLUE                    = (60,  60,  100)
WHITE                       = (255, 255, 255)
MISTYROSE                   = (255 ,99, 71)
GREENYELLOW                 = (173, 255, 47)
BLUE                        = (0,   0,   255)
LIGHRTYELLOW                = (255, 255, 224)
ORANGE                      = (255, 128, 0)
PURPLE                      = (147, 112, 219)
CYAN                        = (0,  255,  255)           #蓝绿色

BGCOLOR = NAVYBLUE   #BAKEGROUND
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE

#使用常量而不是字符串
DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

#确保有足够的图标
ALLCOLOR = (MISTYROSE, GREENYELLOW, BLUE, LIGHRTYELLOW, ORANGE, PURPLE, CYAN)         #设为元组
ALLSHAPES = (DONUT,SQUARE, DIAMOND, LINES, OVAL)
assert len(ALLCOLOR) *  len(ALLSHAPES)*2 >=BOARDHEIGHT * BOARDWIDTH           # ****** 断言


#主函数
def main():
    global FPSCLOCK, DISPLAYSURF            #global 语句设置全局变量
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    mousex = 0 #用于储存鼠标事件的x坐标
    mousey = 0 #储存鼠标事件的y坐标
    pygame.display.set_caption('Memory Puzzle')

    mainBoard = getRandomizedBoard()        #游戏板数据结构
    revealedBoxes = generateRevealedBoxesData(False)    #揭开的方块

    firstSelection = None   #储存鼠标第一次点击的位置

    DISPLAYSURF.fill(BGCOLOR)
    # 背景音乐
    pygame.mixer.music.load('Zombies.mp3')
    pygame.mixer.music.play(-1, 0.0)
    startGameAnimation(mainBoard)


    #游戏循环
    while True :    #main game loop
        mouseClicked = False
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(mainBoard, revealedBoxes)
        for event in pygame.event.get():     #事件处理循环
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE) :           #如果事件为Esc和QUIT事件则退出
                pygame.mixer.music.stop()  # 立即停止背景音乐
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION :        #鼠标移动
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:       #鼠标点击一次
                mousex, mousey = event.pos
                mouseClicked = True                 #鼠标点击

            #检查鼠标在哪个方块上
            boxx, boxy = getBoxAtPixel(mousex, mousey)       #转换为方块坐标
            if boxx != None and boxy !=None:
                if not revealedBoxes[boxx][boxy]:           #鼠标在没有揭开的方块上则绘制高亮边框
                    drawHightlightbox(boxx, boxy)
                if not revealedBoxes[boxx][boxy] and mouseClicked:          #鼠标点击了没有揭开的方块—绘制揭开动画
                    revealBoxesAnimation(mainBoard, [(boxx, boxy)])
                    revealedBoxes[boxx][boxy] = True

                    if firstSelection == None:
                        firstSelection = (boxx, boxy)

                    else:
                        icon1shape, icon1colar = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
                        icon2shape, icon2colar = getShapeAndColor(mainBoard, boxx, boxy)

                        if icon1colar != icon2colar or icon2shape != icon1shape:
                            pygame.time.wait(1000)
                            coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), ( boxx, boxy)] )
                            revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                            revealedBoxes[boxx][boxy] = False

                        elif hasWon(revealedBoxes):         #游戏获胜
                            gameWonAnimation(mainBoard)
                            pygame.time.wait(1000)
                            #重建一个游戏板
                            mainBoard = getRandomizedBoard()
                            revealedBoxes = generateRevealedBoxesData(False)

                            #绘制
                            drawBoard(mainBoard, revealedBoxes)
                            pygame.display.update()
                            pygame.time.wait(1000)
                            startGameAnimation(mainBoard)

                        firstSelection  = None

        pygame.display.update()
        FPSCLOCK.tick(FPS)









def getRandomizedBoard():           #返回一个随机的游戏板数据结构
    icons = []
    for color in ALLCOLOR:
        for shape in ALLSHAPES:
            icons.append( (shape, color) )
        random.shuffle(icons)
        numIconsUsed = int(BOARDWIDTH * BOARDHEIGHT / 2)
        icons = icons [:numIconsUsed] * 2               #创造成对的图标
        random.shuffle(icons)               #用random.shuffle方法打乱排序

    #将列表排序到board
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(icons[0])
            del icons[0]
        board.append(column)
    return  board


def generateRevealedBoxesData(val):           #创建“揭开的方块”空列表
    revealedBoxes = []
    for i in range(BOARDWIDTH):
        revealedBoxes.append( [val] * BOARDHEIGHT )
    return revealedBoxes


def splitIntoGroupsOf(groupSize, theList):      #分割列表为2D列表
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i+groupSize])
    return result


def leftTopCoordsOfBox(boxx, boxy):             #转换坐标系  把方块坐标转换为像素坐标
    left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN
    top =boxy * (BOXSIZE + GAPSIZE) + YMARGIN
    return (left, top)

def getBoxAtPixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect= pygame.Rect(left, top, BOXSIZE, BOXSIZE)           #创建Rect对象
            if boxRect.collidepoint(x, y):                  #利用Rect的collidepoint方法进行碰撞检测
                return boxx, boxy
    return (None, None)

def drawIcon(shape, color, boxx, boxy):       #绘制图表 &使用语法糖
    quarter = int(BOXSIZE * 0.25)
    half = int(BOXSIZE * 0.5)

    left, top = leftTopCoordsOfBox(boxx, boxy)
    #绘制形状
    if shape == DONUT:
        pygame.draw.circle(DISPLAYSURF, color, (left + half, top + half), half - 5)
        pygame.draw.circle(DISPLAYSURF, color, (left + half, top + half), quarter -5)
    elif shape == SQUARE:
        pygame.draw.rect(DISPLAYSURF, color, (left + quarter, top + quarter, BOXSIZE - half, BOXSIZE - half))
    elif shape == DIAMOND:
        pygame.draw.polygon(DISPLAYSURF, color, ((left + half, top), (left + BOXSIZE - 1, top + half), (left + half, top + BOXSIZE - 1), (left, top + half)))
    elif shape == LINES:
        for i in range(0, BOXSIZE, 4):
            pygame.draw.line(DISPLAYSURF, color, (left, top + i), (left + i, top))
    elif shape == OVAL:
        pygame.draw.ellipse(DISPLAYSURF, color, (left, top + quarter, BOXSIZE, half))


def getShapeAndColor(board, boxx, boxy):            #获取游戏板控件的形状和颜色 的语法糖
    #shape value for x, y spot is stored in board[x][y][0]
    #color value for x, y spot is stored in board[x][y][0]
    return  board[boxx][boxy][0], board[boxx][boxy][1]

def drawBoxCovers(board, boxes, coverage):              #绘制揭开的方块
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
        shape, color = getShapeAndColor(board, box[0], box[1])
        drawIcon(shape, color, box[0], box[1])
        if coverage > 0:
            pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, coverage, BOXSIZE))
    #更新游戏状态
    pygame.display.update()
    FPSCLOCK.tick(FPS)


def revealBoxesAnimation(board, boxesToReveal):             #揭开动画
    for coverage in range(BOXSIZE, -1, -REVEALSPEED):
        drawBoxCovers(board, boxesToReveal, coverage)


def coverBoxesAnimation(board, boxesToCover):               #覆盖动画
    for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
        drawBoxCovers(board, boxesToCover, coverage)


def drawBoard(board, revealed):                  #绘制整个游戏板
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
                pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
            else:
                shape, color = getShapeAndColor(board, boxx, boxy)
                drawIcon(shape, color, boxx, boxy)


def drawHightlightbox(boxx, boxy):                  #绘制高亮边框
    left, top = leftTopCoordsOfBox( boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE +10), 4)

def startGameAnimation(board):                      #开始游戏动画
    coveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            boxes.append( (x,y) )
        random.shuffle(boxes)
        boxGroups = splitIntoGroupsOf(8, boxes)

        for boxGroup in boxGroups:
            revealBoxesAnimation(board, boxGroup)
            coverBoxesAnimation(board, boxGroup)


def gameWonAnimation(board):                        #游戏获胜动画
    coveredBoxes = generateRevealedBoxesData(True)
    color1 = LIGHTBGCOLOR
    color2 = BGCOLOR

    for i in range(13):
        color1, color2 = color2, color1
        DISPLAYSURF.fill(color1)
        drawBoard(board, coveredBoxes)
        pygame.display.update()
        pygame.time.wait(300)

def hasWon(revealedBoxes):                          #判断玩家是否已经获胜
    for i in revealedBoxes:
        if False in i:
            return False
    return  True

if __name__ == '__main__':
    main()