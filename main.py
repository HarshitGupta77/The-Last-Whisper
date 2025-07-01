import pygame
import sys
import random
import asyncio
import aiohttp
import js

pygame.init()
height=500
width=850
window=pygame.display.set_mode((width,height), pygame.SCALED)
pygame.display.set_caption("The Last Whisper")
pygame.mixer.init()

BushSound=pygame.mixer.Sound("BushMovement.ogg")
Screech=pygame.mixer.Sound("Screech1.ogg")
WrongAns=pygame.mixer.Sound("Wrong.ogg")
CorrectAns=pygame.mixer.Sound("Correct.ogg")

Black=(0,0,0)
White=(255,255,255)
Grey=(192,192,192)
Red=(255,0,0)
Orange=(255,128,0)
Green=(0,255,0)

Msg_font=pygame.font.SysFont("times new roman",21)
Subtitle_font=pygame.font.SysFont("times new roman",25)
Btn_font=pygame.font.SysFont("arial",20)
Guess_font=pygame.font.SysFont("monospace",24)
Text_font=pygame.font.SysFont("arial",45)

Word=''
Buttons=[]
Guessed=[]
Hangman=[pygame.image.load("hangman1_.png"),
         pygame.image.load("hangman2_.png"),
         pygame.image.load("hangman3_.png"),
         pygame.image.load("hangman4_.png"),
         pygame.image.load("hangman5_.png"),
         pygame.image.load("hangman6_.png"),
         pygame.image.load("hangman7_.png")]
Limbs=0

Score=0
winScore={"Easy":300, "Medium":600, "Hard":1000}
loseScore={"Easy":100, "Medium":250, "Hard":500}
winmsg=["Sanity Preserved",
        "Soul Fragments Collected",
        "Shadows Repelled",
        "Echoes Silenced"]
losemsg=["Sanity Drained",
         "Soul Fragments Lost",
         "Darkness Increased",
         "Echoes Unleashed"]

Background=[pygame.image.load("Background1_.png").convert(),
            pygame.image.load("Background2.png").convert()]

api_failed=False

Sound=False
Mute=pygame.transform.scale(pygame.image.load("Mute_Icon.png"),(32, 32))
Unmute=pygame.transform.scale(pygame.image.load("Unmute_Icon.png"),(32, 32))
SoundRect=pygame.Rect(width - 42, height - 42, 32, 32)

ReplayIcon=pygame.transform.scale(pygame.image.load("ReplayIcon.png"),(42,32))
ReplayIcon2=pygame.transform.scale(pygame.image.load("ReplayIcon2.png"),(42,32))

# Functions
async def start_screen(): 
    pygame.mixer.music.load("BackgroundMusic_Start.ogg")
    if not Sound:
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1, fade_ms=1000)
    else:
        pygame.mixer.music.set_volume(0)
    
    choice=True
    difficulty_btns=[[Grey, width/6.5, height/2+40, 50, True, "Easy (E)"],
                     [Grey, width/6.5, height/2+110, 80, True, "Medium (M)"],
                     [Grey, width/6.5, height/2+180, 80, True, "Hard (H)"]]
    
    while choice:
        window.fill(Black)
        Bg1=pygame.transform.scale(Background[0], (width,height - 50))
        window.blit(Bg1, (0,0))
        BushSound.fadeout(500)

        for btn in difficulty_btns:
            btnRect=pygame.Rect(btn[1] - 50, btn[2] - 20, 100, 40)
            if btn[4]:
                pygame.draw.rect(window, btn[0], btnRect)
                label5=Btn_font.render(btn[5], 1, Red)
                if btnRect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(window, Red, btnRect, width=3)
                window.blit(label5, (btn[1] - label5.get_width()/2, btn[2] - label5.get_height()/2))
        
        if Sound:
            SoundIcon=Mute
        else:
            SoundIcon=Unmute
        window.blit(SoundIcon, SoundRect)

        scoreText=Subtitle_font.render(f"Score: {Score}", 1, White)
        window.blit(scoreText, (width-scoreText.get_width()-10, 10))
        #window.blit(scoreText, (10, height-scoreText.get_height()-10))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                diff = None
                if event.key == pygame.K_e:
                    diff = "Easy"
                elif event.key == pygame.K_m:
                    diff = "Medium"
                elif event.key == pygame.K_h:
                    diff = "Hard"
                
                if diff:
                    Label6 = Subtitle_font.render(" Loading...", 1, Red)
                    window.blit(Label6, (width/1.3 - Label6.get_width()/2, height/2 + 170))
                    pygame.display.update()

                    choice = False
                    pygame.mixer.music.fadeout(1000)
                    if not Sound:
                        BushSound.play()
                    await asyncio.sleep(1)
                        
                    return diff

            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y=pygame.mouse.get_pos()
                if SoundRect.collidepoint(x,y):
                    volume()
                for point in range(len(difficulty_btns)):
                    btnx=difficulty_btns[point][1] - 40
                    btny=difficulty_btns[point][2] - 20
                    btn_rect = pygame.Rect(btnx, btny, 80, 40)
                    if btn_rect.collidepoint(x,y) :
                        Label6 = Subtitle_font.render(" Loading...", 1, Red)
                        window.blit(Label6, (width/1.3 - Label6.get_width()/2, height/2 + 170))
                        pygame.display.update()

                        choice = False
                        pygame.mixer.music.fadeout(1000)
                        if not Sound:
                            BushSound.play()
                        await asyncio.sleep(1)
                        
                        return difficulty_btns[point][5][:-4]

async def redraw_window():
    global Guessed
    global Hangman
    global Limbs
    Bg2=pygame.transform.scale(Background[1], (width,height))
    window.blit(Bg2, (0,0))

    for i in range(len(Buttons)):
        ltr=chr(Buttons[i][5])
        if Buttons[i][4]:
            pygame.draw.circle(window,Black,(Buttons[i][1], Buttons[i][2]), Buttons[i][3])
            pygame.draw.circle(window,Buttons[i][0], (Buttons[i][1], Buttons[i][2]), Buttons[i][3]-2)
            Label=Btn_font.render(chr(Buttons[i][5]), 1, Black)
            window.blit(Label, (Buttons[i][1]-(Label.get_width()/2), Buttons[i][2]-(Label.get_height()/2)))
        else:
            if ltr.lower() in Word.lower():
                pygame.draw.circle(window,Black,(Buttons[i][1], Buttons[i][2]), Buttons[i][3]+2)
                pygame.draw.circle(window,Green,(Buttons[i][1], Buttons[i][2]), Buttons[i][3])
                Label=Btn_font.render(chr(Buttons[i][5]), 1, Black)
                window.blit(Label, (Buttons[i][1]-(Label.get_width()/2), Buttons[i][2]-(Label.get_height()/2)))
            else:
                pygame.draw.circle(window,Red,(Buttons[i][1], Buttons[i][2]), Buttons[i][3])
                Label=Btn_font.render(chr(Buttons[i][5]), 1, White)
                window.blit(Label, (Buttons[i][1]-(Label.get_width()/2), Buttons[i][2]-(Label.get_height()/2)))

    Space=spaced_out(Word,Guessed)
    Label2=Guess_font.render(Space, 1, White)
    Rect=Label2.get_rect()
    Length=Rect[2]

    window.blit(Label2, (width/2 - Length/2, 400))

    pic=Hangman[Limbs]
    window.blit(pic, (width/2 - pic.get_width()/2 + 20, 150))

    if Sound:
        SoundIcon=Mute
    else:
        SoundIcon=Unmute
    window.blit(SoundIcon, SoundRect)

    scoreText=Subtitle_font.render(f"Score: {Score}", 1, White)
    window.blit(scoreText, (10, height-scoreText.get_height()-10))

    if api_failed:
        msg = Msg_font.render(" The summoning failed... an ancient scroll whispered instead. ", 1, Orange)
        window.blit(msg, (width/2 - msg.get_width()/2, height - 50))

    pygame.display.update()

def volume():
    global Sound
    Sound = not Sound

    if Sound:
        pygame.mixer.music.set_volume(0)
        BushSound.set_volume(0)
        Screech.set_volume(0)
    else:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1, fade_ms=50)
        pygame.mixer.music.set_volume(0.5)
        BushSound.set_volume(1)
        Screech.set_volume(1)

async def random_word(level):
    global api_failed

    api = {"Easy":"https://random-word-api.vercel.app/api?words=1&length=5",
           "Medium":"https://random-word-api.vercel.app/api?words=1&length=7",
           "Hard":"https://random-word-api.vercel.app/api?words=1&length=9"}
    
    if hasattr(js, "fetch"):
        try:
            resp = await js.fetch(api[level])
            data = await resp.json()
            data = data[0].strip()
            if data:
                return data
            
        except:
            api_failed = True

            try:
                file=open(f"{level}.txt")
                words=file.readlines()
                data= random.choice(words).strip()
                file.close()
                #print(data)
                return data
            
            except FileNotFoundError:
                print("Fallback File not found!!")
                return "Fallback" 
            
    else:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api[level], timeout=5) as resp:
                    data = await resp.json()
                    data = data[0].strip()
                    if data:
                        return data
                        
        except:
            api_failed = True

            try:
                file=open(f"{level}.txt")
                words=file.readlines()
                data= random.choice(words).strip()
                file.close()
                #print(data)
                return data
            
            except FileNotFoundError:
                print("Fallback File not found!!")
                return "Fallback" 

def hang(guess):
    global Word
    if guess.lower() not in Word.lower():
        if not Sound:
            WrongAns.set_volume(0.7)
            WrongAns.play()
        return True
    else:
        if not Sound:
            CorrectAns.set_volume(0.5)
            CorrectAns.play()
        return False
    
def spaced_out(Word,Guessed=[]):
    spaced_Word=""
    guessed_Letters=Guessed
    for j in range(len(Word)):
        if Word[j] != " ":
            spaced_Word += "_ "
            for k in range(len(guessed_Letters)):
                if Word[j].lower() == guessed_Letters[k].lower():
                    spaced_Word=spaced_Word[:-2]
                    spaced_Word += Word[j].upper() + " "
        elif Word[j] == " ":
            spaced_Word += " "
    return spaced_Word

def button_Press(x,y):
    for a in range(len(Buttons)):
        btn_circle = pygame.Rect(Buttons[a][1]-20, Buttons[a][2]-20, 40, 40)
        if Buttons[a][4] and btn_circle.collidepoint(x, y):
            Buttons[a][4] = False 
            return Buttons[a][5]
    return None

async def end(winner=False):
    global Limbs
    global Score
    global difficulty

    pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
    pygame.event.set_blocked(pygame.MOUSEBUTTONUP)
    pygame.event.set_blocked(pygame.KEYDOWN)
    pygame.event.clear()

    winText = ["You broke the curse", "The darkness retreats", "You survive....for now",
               f"+{winScore[difficulty]} {random.choice(winmsg)}"]
    lostText = ["The whisper fades", "and silence falls", "As darkness claims another...", 
                "The cursed word was: ", Word.upper(), f"-{loseScore[difficulty]} {random.choice(losemsg)}"]
    await redraw_window()
    await asyncio.sleep(2)
    Bg3=pygame.transform.scale(Background[1], (width,height))
    window.blit(Bg3, (0,0))

    if Sound:
        SoundIcon=Mute
    else:
        SoundIcon=Unmute
    window.blit(SoundIcon, SoundRect)

    if winner == True:
        pygame.mixer.music.load("BackgroundMusic_Win.ogg")
        if not Sound:
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1, fade_ms=1000)
        else:
            pygame.mixer.music.set_volume(0)

        Score += winScore[difficulty]

        for line in range(len(winText)):
            label3 = Text_font.render(winText[line], 1, White).convert_alpha()
            for alpha in range(0,256,10):
                label3.set_alpha(alpha)
                window.blit(pygame.transform.scale(Background[1], (width, height)), (0,0))
                window.blit(SoundIcon, SoundRect)
                pygame.event.clear()
                
                for prev in range(line):
                    previous = Text_font.render(winText[prev], 1, White)
                    if prev < 3:
                        ypos=80+(prev*50)
                    else:
                        ypos=275+((prev-3)*50)
                    window.blit(previous, (width/2 - previous.get_width()/2, ypos))

                if line < 3:
                    ypos=80+(line*50)
                else:
                    ypos=275+((line-3)*50)
                window.blit(label3, (width/2 - label3.get_width()/2, ypos))
                pygame.display.update()
                await asyncio.sleep(0.03)
            await asyncio.sleep(0.5)

    else:
        pygame.mixer.music.load("BackgroundMusic_Lose.ogg")
        if not Sound:
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1, fade_ms=1000)
        else:
            pygame.mixer.music.set_volume(0)

        Score -= loseScore[difficulty]

        for line in range(len(lostText)):
            label3 = Text_font.render(lostText[line], 1, White).convert_alpha()
            for alpha in range(0,256,10):
                label3.set_alpha(alpha)
                window.blit(pygame.transform.scale(Background[1], (width, height)), (0,0))
                window.blit(SoundIcon, SoundRect)
                pygame.event.clear()
                
                for prev in range(line):
                    previous = Text_font.render(lostText[prev], 1, White)
                    if prev < 3:
                        ypos=50+(prev*50)
                    else:
                        ypos=245+((prev-3)*50)
                    window.blit(previous, (width/2 - previous.get_width()/2, ypos))

                if line < 3:
                    ypos=50+(line*50)
                else:
                    ypos=245+((line-3)*50)
                window.blit(label3, (width/2 - label3.get_width()/2, ypos))
                pygame.display.update()
                await asyncio.sleep(0.03)
            await asyncio.sleep(0.5)

    ReplayText = Subtitle_font.render("Try again (R)....if you dare", 1, White)
    ReplayRect = ReplayText.get_rect(center=(width/2, 470))
    pygame.draw.rect(window, Black, ReplayRect.inflate(84,10), border_radius=25)
    window.blit(ReplayIcon, (ReplayRect.left-ReplayIcon.get_width()+20, ReplayRect.centery-ReplayIcon.get_height()/2))
    window.blit(ReplayText, (ReplayRect.left+15, ReplayRect.top))
    pygame.display.update()

    scoreText=Subtitle_font.render(f"Score: {Score}", 1, White)
    window.blit(scoreText, (10, height-scoreText.get_height()-10))
    
    pygame.event.clear()
    pygame.event.set_allowed(pygame.MOUSEBUTTONDOWN)
    pygame.event.set_allowed(pygame.MOUSEBUTTONUP)
    pygame.event.set_allowed(pygame.KEYDOWN)

    repeat = True
    while repeat:
        pygame.draw.rect(window, Black, ReplayRect.inflate(89,15), border_radius=25)
        if ReplayRect.inflate(84,10).collidepoint(pygame.mouse.get_pos()):
            Hover = Subtitle_font.render("Try again (R)....if you dare", 1, Orange)
            pygame.draw.rect(window, Orange, ReplayRect.inflate(89,15), border_radius=25)
            icon=ReplayIcon2
        else:
            Hover = Subtitle_font.render("Try again (R)....if you dare", 1, White)
            icon=ReplayIcon

        pygame.draw.rect(window, Black, ReplayRect.inflate(84,10), border_radius=25)
        window.blit(icon, (ReplayRect.left-ReplayIcon.get_width()+20, ReplayRect.centery-ReplayIcon.get_height()/2))
        window.blit(Hover, (ReplayRect.left+15, ReplayRect.top))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    pygame.mixer.music.fadeout(1000)
                    if not Sound:
                        BushSound.play()
                    repeat = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if SoundRect.collidepoint(event.pos):
                    volume()
                    if Sound:
                        SoundIcon=Mute
                    else:
                        SoundIcon=Unmute
                    pygame.draw.rect(window, Black, SoundRect)
                    window.blit(SoundIcon, SoundRect)
                    pygame.display.update()

                elif ReplayRect.inflate(84,10).collidepoint(event.pos):
                    pygame.mixer.music.fadeout(1000)
                    if not Sound:
                        BushSound.play()
                    repeat = False
    await reset()

async def reset():
    global Limbs
    global Guessed
    global Buttons
    global Word
    global difficulty
    global api_failed

    api_failed = False

    for b in range(len(Buttons)):
        Buttons[b][4] = True
    
    Limbs = 0
    Guessed = []
    difficulty = await start_screen()
    Word = await random_word(difficulty)
    BushSound.fadeout(500)

    pygame.mixer.music.load("BackgroundMusic_Gameplay.ogg")
    if not Sound:
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1, fade_ms=500)
    else:
        pygame.mixer.music.set_volume(0)

# Main
async def main():
    global Buttons
    global Guessed
    global Limbs
    global Word
    global difficulty
    global Sound

    inc = round(width/13)
    for c in range(26):
        if c < 13:
            y=40
            x=25 + (inc*c)
        else:
            x=25 + (inc*(c-13))
            y=85
        Buttons.append([Grey, x, y, 20, True, 65+c]) 

    difficulty = await start_screen()
    Word = await random_word(difficulty)
    BushSound.fadeout(500)
    Playing = True

    pygame.mixer.music.load("BackgroundMusic_Gameplay.ogg")
    if not Sound:
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1, fade_ms=500)

    while Playing:     
        await redraw_window()
        await asyncio.sleep(0.01)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Playing = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    Playing = False
                elif pygame.K_a <= event.key <= pygame.K_z:
                    ltr = chr(event.key).upper()
                    if ltr not in Guessed:
                        Guessed.append(ltr)
                        Buttons[ord(ltr) - 65][4] = False
                        if hang(ltr):
                            if Limbs != 5:
                                Limbs += 1
                            else:
                                Limbs+=1
                                pygame.mixer.music.fadeout(1000)
                                if not Sound:
                                    Screech.play()
                                await end()
                        else:
                            if spaced_out(Word,Guessed).count("_") == 0:
                                pygame.mixer.music.fadeout(1000)
                                await end(True)

            if event.type == pygame.MOUSEBUTTONDOWN:
                clickPos = pygame.mouse.get_pos()
                if SoundRect.collidepoint(clickPos):
                    volume()
                else:
                    letter = button_Press(clickPos[0], clickPos[1])
                    if letter != None:
                        Guessed.append(chr(letter))
                        Buttons[letter - 65][4] = False
                        if hang(chr(letter)):
                            if Limbs != 5:
                                Limbs += 1
                            else:
                                Limbs+=1
                                pygame.mixer.music.fadeout(1000)
                                if not Sound:
                                    Screech.play()
                                await end()
                        else:
                            if spaced_out(Word,Guessed).count("_") == 0:
                                pygame.mixer.music.fadeout(1000)
                                await end(True)

if __name__ == "__main__":
    try:
        import sys
        if sys.platform == "emscripten":
            asyncio.ensure_future(main())
        else:
            asyncio.run(main())
    except SystemExit:
        pygame.quit()
        sys.exit()