import asyncio, json, sys, pygame, __EMSCRIPTEN__ as platform

async def custom_site():
    WIDTH, HEIGHT = platform.window.canvas.width, platform.window.canvas.height
    pygame.init()
    screen = pygame.display.set_mode([WIDTH, HEIGHT], pygame.SRCALPHA, 32)

    def pg_bar(p):                       # simple progress bar
        pygame.draw.rect(screen,(10,10,10), (WIDTH*0.1,HEIGHT*0.45,WIDTH*0.8,40))
        pygame.draw.rect(screen,(0,255,0), (WIDTH*0.1,HEIGHT*0.45,WIDTH*0.8*p,40))
        pygame.display.flip()

    apk  = "hangman.apk"                 # file lives at site-root
    cfg  = json.dumps({"io":"url","type":"mount",
                       "mount":{"point":"/data/data/hangman","path":"/"}})
    track = platform.window.MM.prepare(apk, cfg)
    
    while not track.ready:
        pg_bar(track.pos / max(track.len,1))
        await asyncio.sleep(0.05)

    game_path = "/data/data/hangman/assets/main.py"
    with open(game_path, "r") as fh:
        code = fh.read()
    exec(code, {"__name__": "__main__", "__file__": game_path})

# expose the coroutine for pythons.js
sys.modules["__main__"].custom_site = custom_site