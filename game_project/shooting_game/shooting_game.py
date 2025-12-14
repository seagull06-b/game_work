from tkinter import *
import time
import pygame
import random

SCREEN_W = 1440
SCREEN_H = 960


class Enemy:
    def __init__(self, canvas, image):
        self.canvas = canvas
        self.image = image
        self.w = image.width()

        self.me = canvas.create_image(
            SCREEN_W + self.w // 2,
            random.randint(20, SCREEN_H - 200),
            image=image,
            tags="enemy"
        )

    def update(self):
        self.canvas.move(self.me, -4, 0)

    def pos(self):
        return self.canvas.coords(self.me)

class ShootingGame:
    def __init__(self):
        self.window = Tk()
        self.window.title("Bat Ultrasonic Shooting Game")
        self.window.geometry(f"{SCREEN_W}x{SCREEN_H}")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.onClose)

        self.canvas = Canvas(self.window, bg="black",
                             width=SCREEN_W, height=SCREEN_H)
        self.canvas.pack()

        self.keys = set()
        self.window.bind("<KeyPress>", self.keyPress)
        self.window.bind("<KeyRelease>", self.keyRelease)

        self.batFrames = [PhotoImage(file="image/bat2.png").subsample(3) for _ in range(40)]
        self.ultra = PhotoImage(file="image/signal.png").subsample(3)
        self.foods = [
            PhotoImage(file="image/butterfly.PNG").subsample(4),
            PhotoImage(file="image/fly.png").subsample(4)
        ]

        self.start_img = PhotoImage(file="image/intro.png")
        self.gameover_img = PhotoImage(file="image/game_over.png")

        self.bg = PhotoImage(file="image/background.png")
        self.bg2 = PhotoImage(file="image/background.png")
        self.bgW = self.bg.width()

        pygame.mixer.init()
        pygame.mixer.music.load("sound/8BitCave.wav")

        self.ch = pygame.mixer.Channel(1)
        self.s_score = pygame.mixer.Sound("sound/get_score.mp3")
        self.s_shoot = pygame.mixer.Sound("sound/shoot.mp3")
        self.s_life_up = pygame.mixer.Sound("sound/get_life.mp3")
        self.s_life_down = pygame.mixer.Sound("sound/lose_life.mp3")
        self.s_gameover = pygame.mixer.Sound("sound/game_over.ogg")

        self.bg1 = self.canvas.create_image(0, 0, image=self.bg, anchor=NW)
        self.bg2i = self.canvas.create_image(self.bgW, 0, image=self.bg2, anchor=NW)

        self.lifeText = self.canvas.create_text(120, 50, fill="white", font=("Arial", 22, "bold"))
        self.scoreText = self.canvas.create_text(120, 90, fill="white", font=("Arial", 22, "bold"))

        self.resetGame()
        self.showStart()
        self.window.mainloop()

    def resetGame(self):
        self.canvas.delete("enemy", "ultra")

        self.score = 0
        self.life = 3
        self.enemies = []
        self.game_running = False
        self.lastShotTime = time.time()

        self.batFrame = 0
        self.bat = self.canvas.create_image(
            200, SCREEN_H // 2,
            image=self.batFrames[0],
            tags="bat"
        )

        self.updateUI()

    def showStart(self):
        self.start_item = self.canvas.create_image(
            SCREEN_W // 2, SCREEN_H // 2,
            image=self.start_img
        )
        self.window.bind("<space>", self.startGame)

    def startGame(self, e=None):
        self.canvas.delete(self.start_item)
        self.window.unbind("<space>")
        pygame.mixer.music.play(-1)
        self.game_running = True
        self.loop()

    def loop(self):
        if not self.game_running:
            return

        self.scrollBG()
        self.moveBat()
        self.moveUltra()
        self.manageEnemy()
        self.animateBat()
        self.updateUI()

        self.window.after(33, self.loop)

    def manageEnemy(self):
        if random.randint(0, 60) == 0:
            self.enemies.append(Enemy(self.canvas, random.choice(self.foods)))

        bat_pos = self.canvas.coords(self.bat)

        for e in self.enemies[:]:
            e.update()
            pos = e.pos()
            if not pos:
                continue

            if pos[0] + e.w / 2 < 0:
                self.life -= 1
                self.ch.play(self.s_life_down)
                self.canvas.delete(e.me)
                self.enemies.remove(e)
                continue

            if abs(pos[0] - bat_pos[0]) < 40 and abs(pos[1] - bat_pos[1]) < 40:
                self.life -= 1
                self.ch.play(self.s_life_down)
                self.canvas.delete(e.me)
                self.enemies.remove(e)
                continue

            for u in self.canvas.find_withtag("ultra"):
                u_pos = self.canvas.coords(u)
                if abs(pos[0] - u_pos[0]) < 30 and abs(pos[1] - u_pos[1]) < 30:
                    self.score += 1
                    self.ch.play(self.s_score)

                    if self.score % 10 == 0:
                        self.life += 1
                        self.ch.play(self.s_life_up)

                    self.canvas.delete(u)
                    self.canvas.delete(e.me)
                    self.enemies.remove(e)
                    break

    def moveBat(self):
        if 38 in self.keys: self.canvas.move(self.bat, 0, -6)
        if 40 in self.keys: self.canvas.move(self.bat, 0, 6)
        if 37 in self.keys: self.canvas.move(self.bat, -6, 0)
        if 39 in self.keys: self.canvas.move(self.bat, 6, 0)

    def moveUltra(self):
        for u in self.canvas.find_withtag("ultra"):
            self.canvas.move(u, 10, 0)
            if self.canvas.coords(u)[0] > SCREEN_W + 50:
                self.canvas.delete(u)

    def animateBat(self):
        self.canvas.itemconfig(self.bat, image=self.batFrames[self.batFrame % 40])
        self.batFrame += 1

    def scrollBG(self):
        self.canvas.move(self.bg1, -2, 0)
        self.canvas.move(self.bg2i, -2, 0)
        if self.canvas.coords(self.bg1)[0] <= -self.bgW:
            self.canvas.coords(self.bg1, self.bgW, 0)
        if self.canvas.coords(self.bg2i)[0] <= -self.bgW:
            self.canvas.coords(self.bg2i, self.bgW, 0)

    def updateUI(self):
        self.canvas.itemconfig(self.lifeText, text=f"LIFE: {self.life}")
        self.canvas.itemconfig(self.scoreText, text=f"SCORE: {self.score}")
        if self.life <= 0:
            self.gameOver()

    def gameOver(self):
        self.game_running = False
        pygame.mixer.music.stop()
        self.ch.play(self.s_gameover)

        self.canvas.create_image(
            SCREEN_W // 2, SCREEN_H // 2 - 120,
            image=self.gameover_img
        )

        self.canvas.create_text(
            SCREEN_W // 2, SCREEN_H // 2 + 40,
            text=f"SCORE : {self.score}",
            fill="white",
            font=("Helvetica", 32, "bold")
        )

        self.canvas.create_text(
            SCREEN_W // 2, SCREEN_H // 2 + 100,
            text="PRESS SPACE TO RESTART",
            fill="yellow",
            font=("Helvetica", 26, "bold")
        )

        self.window.bind("<space>", self.restart)

    def restart(self, e=None):
        self.window.unbind("<space>")
        self.canvas.delete("all")

        self.bg1 = self.canvas.create_image(0, 0, image=self.bg, anchor=NW)
        self.bg2i = self.canvas.create_image(self.bgW, 0, image=self.bg2, anchor=NW)

        self.lifeText = self.canvas.create_text(120, 50, fill="white", font=("Arial", 22, "bold"))
        self.scoreText = self.canvas.create_text(120, 90, fill="white", font=("Arial", 22, "bold"))

        self.resetGame()
        pygame.mixer.music.play(-1)
        self.game_running = True
        self.loop()

    def keyPress(self, e):
        self.keys.add(e.keycode)
        if self.game_running and e.keycode == 32:
            if time.time() - self.lastShotTime > 0.25:
                self.lastShotTime = time.time()
                pos = self.canvas.coords(self.bat)
                self.canvas.create_image(pos[0] + 60, pos[1],
                                         image=self.ultra, tags="ultra")
                self.ch.play(self.s_shoot)

    def keyRelease(self, e):
        self.keys.discard(e.keycode)

    def onClose(self):
        pygame.mixer.quit()
        self.window.destroy()


ShootingGame()