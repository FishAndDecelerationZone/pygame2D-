# Ukulee.py
# 3392955216@qq.com

import pygame, sys, random, time
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 640
WINDOWHIGHT = 480
FLASHSPEED = 500            #
FLASHDELAY = 200            #
BUTTONSIZE = 200
BUTTONGAPSIZE = 20
TIMOUT = 4                  #间隔时间
#                      R    G    B
WHITE             =  (255, 255, 255)
BLACK             =  (  0,   0,   0)
NAVYBLUE          = (120,  120,  200)
MISTYROSE         = (255 ,99, 71)               #粉玫瑰
GREENYELLOW       = (173, 255, 47)              #蓝绿色
CYAN              =  (0,  255,  255)            #蓝绿色
GRAY              =  (100, 100, 100)
bgColor = CYAN

XMARGIN = int( (WINDOWWIDTH - (BUTTONSIZE * 2 + BUTTONGAPSIZE)) /2)         #设置游戏板与窗口间距
YMARGIN = int( (WINDOWHIGHT - (BUTTONGAPSIZE + (BUTTONSIZE*2))) /2)
#设置方块
RECT1 = pygame.Rect(XMARGIN, YMARGIN, BUTTONSIZE, BUTTONSIZE)
RECT2 = pygame.Rect(XMARGIN + BUTTONSIZE + BUTTONGAPSIZE, YMARGIN, BUTTONSIZE, BUTTONSIZE)
RECT3 = pygame.Rect(XMARGIN, YMARGIN + BUTTONGAPSIZE + BUTTONSIZE, BUTTONSIZE, BUTTONSIZE)
RECT4 = pygame.Rect(XMARGIN + BUTTONGAPSIZE + BUTTONSIZE, YMARGIN + BUTTONSIZE + BUTTONGAPSIZE, BUTTONSIZE, BUTTONSIZE)
ModeRect = pygame.Rect(0, 10, 20,20)

Rect1 = 1
Rect2 = 2
Rect3 = 3
Rect4 = 4
Change = 0
def main():
    global FPSCOLCK, DISPLAYSURF, BASICFONT, BEEP1, BEEP2, BEEP3, BEEP4
    pygame.init()
    FPSCOLCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHIGHT))
    pygame.display.set_caption("Ukulele")

    BASICFONT = pygame.font.Font('my_fonts.ttf',16)

    infoSurf = BASICFONT.render('创造Match the pattern by clicking on the button or using the A, S, D, F keys.', 1, BLACK)      #底部提示
    inforRect = infoSurf.get_rect()
    inforRect.topleft= (10, WINDOWHIGHT-25)


    BEEP1 = pygame.mixer.Sound('beep1.ogg')   #sound 对象适合做游戏音效
    BEEP2 = pygame.mixer.Sound('beep2.ogg')
    BEEP3 = pygame.mixer.Sound('beep3.ogg')
    BEEP4 = pygame.mixer.Sound('beep4.ogg')

    pattern = []
    waitingForInput = False
    currentStep = 0
    lastClickTime = 0
    mode = 'game'
    score = 0
    while True:
        clickButton  = None
        Change = False
        DISPLAYSURF.fill(bgColor)
        drawButton()

        scoreSurf = BASICFONT.render('Score: '+ str(score), 1,BLACK)
        scoreRect = scoreSurf.get_rect()

        scoreRect.topleft = (WINDOWWIDTH - 100, 10)

        ModeSurf = BASICFONT.render('Change Mode', True, BLACK)

        DISPLAYSURF.blit(scoreSurf, scoreRect)
        DISPLAYSURF.blit(infoSurf, inforRect)
        DISPLAYSURF.blit(ModeSurf, ModeRect)

        checkForQuit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                mouseX, mouseY = event.pos
                clickButton = getButtonClicked(mouseX, mouseY)
                Change = ModeRect.collidepoint(mouseX, mouseY)
            elif event.type == KEYUP:
                if event.key == K_a:
                    clickButton = Rect1
                elif event.key == K_s:
                    clickButton = Rect2
                elif event.key == K_d:
                    clickButton = Rect3
                elif event.key == K_f:
                    clickButton = Rect4

            if mode == 'game' :     #判断游戏状态
                if  Change:
                    mode = 'play'
                    continue

                if not waitingForInput:                     #提示输入状态
                    pygame.display.update()
                    pygame.time.wait(1000)
                    pattern.append(random.choice((Rect1, Rect2, Rect3, Rect4)))
                    for button in pattern:
                        flashButtonAnimation(button)
                        pygame.time.wait(FLASHDELAY)
                    waitingForInput = True
                else:                                       #输入状态
                    if clickButton and clickButton == pattern[currentStep]:  # 点击是否正确
                        flashButtonAnimation(clickButton)
                        currentStep += 1
                        lastClickTime = time.time()  # 更新 点击时间

                        if currentStep == len(pattern):  # 判断点击结束后这个回合是否结束
                            score += 1
                            currentStep = 0
                            waitingForInput = False
                    elif (clickButton and clickButton != pattern[currentStep]) or (
                            currentStep != 0 and time.time() - TIMOUT > lastClickTime):
                        pattern = []
                        currentStep = 0
                        score = 0
                        waitingForInput = False
                        pygame.time.wait(1000)
            else:
                pattern = []
                currentStep = 0
                score = 0
                waitingForInput = False
                if Change:
                    mode = 'game'
                    continue
                if clickButton:
                    flashButtonAnimation(clickButton)


            pygame.display.update()
            FPSCOLCK.tick(FPS)


def terminate():
    """退出"""
    pygame.quit()
    sys.exit()

def checkForQuit():
    """ 检查退出"""
    for event in pygame.event.get(QUIT):
        terminate()
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event)                #将KEYUP事件返回到列队

def flashButtonAnimation(rect, animationSpeed = 50):
    """按钮闪烁动画"""
    rectangle = None
    flashColor = BLACK
    if rect == Rect1:
        sound = BEEP1
        flashColor = getRandomColor()
        rectangle = RECT1
    elif rect == Rect2:
        sound = BEEP2
        flashColor = getRandomColor()
        rectangle = RECT2
    elif rect == Rect3:
        sound = BEEP3
        flashColor = getRandomColor()
        rectangle = RECT3
    elif rect == Rect4:
        sound = BEEP4
        flashColor = getRandomColor()
        rectangle = RECT4
#创建副本，实现渐变
    origSurf = DISPLAYSURF.copy()
    flashSurf = pygame.Surface((BUTTONSIZE, BUTTONSIZE))
    flashSurf = flashSurf.convert_alpha()
    r, g, b = flashColor
    sound.play()
    for start, end, step in ((0, 255, 1), (255, 0, -1)):
        for alpha in range(start, end, animationSpeed * step):
            checkForQuit()
            DISPLAYSURF.blit(origSurf, (0, 0))
            flashSurf.fill((r, g, b, alpha))
            DISPLAYSURF.blit(flashSurf, rectangle.topleft)
            pygame.display.update()
            FPSCOLCK.tick(FPS)

    DISPLAYSURF.blit(origSurf,(0, 0))


def getRandomColor():
    """返回一个随机演示"""
    r, g, b = random.choice( (GRAY, MISTYROSE, NAVYBLUE, GREENYELLOW) )
    return  (r, g, b)

def drawButton():
    """绘制按钮"""
    pygame.draw.rect(DISPLAYSURF, WHITE, RECT1)
    pygame.draw.rect(DISPLAYSURF, WHITE, RECT2)
    pygame.draw.rect(DISPLAYSURF, WHITE, RECT3)
    pygame.draw.rect(DISPLAYSURF, WHITE, RECT4)


def gameOverAnimation(color = WHITE, animationSpeed = 50):
    """ """
    origSurf = DISPLAYSURF.copy()
    flashSurf = pygame.Surface(DISPLAYSURF.get_size())
    flashSurf = flashSurf.convert_alpha()
    BEEP1.play()
    BEEP2.play()
    BEEP3.play()
    BEEP4.play()
    r, g, b = color
    for i in range(3):
        for start, end, step in ((0, 255, 1), (255, 0, -1)):
            for alpha in range(start, end, animationSpeed*step):
                checkForQuit()
                flashSurf.fill(r, g, b, alpha)
                DISPLAYSURF.bilt(origSurf, (0, 0))
                DISPLAYSURF.bilt(flashSurf, (0, 0))
                drawButton()
                pygame.display.update()
                FPSCOLCK.tick(FPS)


def getButtonClicked(x, y):
    """ """
    if RECT1.collidepoint( (x, y)):
        return  Rect1
    elif RECT2.collidepoint( (x, y)):
        return  Rect2
    elif RECT3.collidepoint( (x, y)):
        return  Rect3
    elif RECT4.collidepoint( (x, y)):
        return Rect4
    return None


def drewHight():
    """ """
    return  True
if __name__ == '__main__':
    main()