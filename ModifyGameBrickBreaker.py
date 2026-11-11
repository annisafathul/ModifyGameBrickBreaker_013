import tkinter as tk
from itertools import cycle
 
 
class GameObject(object):
    """Kelas dasar untuk semua objek di canvas (bola, paddle, brick)."""
 
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item
 
    def get_position(self):
        return self.canvas.coords(self.item)
 
    def move(self, x, y):
        self.canvas.move(self.item, x, y)
 
    def delete(self):
        self.canvas.delete(self.item)

class Ball(GameObject):
    # Warna bola berganti-ganti (animasi pelangi)
    COLORS = ['#2d3436', '#d63031', '#e17055', '#e84393',
              '#6c5ce7', '#0984e3', '#00b894', '#fdcb6e']
    TRAIL_LENGTH = 6  # jumlah "jejak" di belakang bola

    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 10
        self.color_cycle = cycle(Ball.COLORS)
        self.trail = []  # list of [item, center_x, center_y]
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill=next(self.color_cycle),
                                  outline='')
        super(Ball, self).__init__(canvas, item)

    def animate(self):
        """Animasi bola: ganti warna + jejak yang mengecil."""
        coords = self.get_position()
        cx = (coords[0] + coords[2]) / 2
        cy = (coords[1] + coords[3]) / 2

        color = next(self.color_cycle)
        self.canvas.itemconfig(self.item, fill=color)

        ghost = self.canvas.create_oval(*coords, fill=color, outline='')
        self.canvas.tag_lower(ghost, self.item)
        self.trail.append([ghost, cx, cy])
        if len(self.trail) > Ball.TRAIL_LENGTH:
            old = self.trail.pop(0)
            self.canvas.delete(old[0])

        total = len(self.trail)
        for i, (ghost_item, gx, gy) in enumerate(self.trail):
            r = self.radius * (i + 1) / (total + 1)
            self.canvas.coords(ghost_item, gx - r, gy - r, gx + r, gy + r)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        self.animate()
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()

    def delete(self):
        for ghost_item, _, _ in self.trail:
            self.canvas.delete(ghost_item)
        self.trail = []
        super(Ball, self).delete()

class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#00cec9', outline='')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)

class Brick(GameObject):
    COLORS = {1: '#fd79a8', 2: '#a29bfe', 3: '#2d3436'}
 
    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, outline='#ffffff',
                                       tags='brick')
        super(Brick, self).__init__(canvas, item)
 
    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#87ceeb',
                                width=self.width,
                                height=self.height,
                                highlightthickness=0)
        self.canvas.pack()
        self.pack()
 
        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 326)
        self.items[self.paddle.item] = self.paddle
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 2)
            self.add_brick(x + 37.5, 70, 1)
            self.add_brick(x + 37.5, 90, 1)
 
        self.hud = None
        self.text = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>',
                         lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>',
                         lambda _: self.paddle.move(10))
 
    def setup_game(self):
        self.add_ball()
        self.update_lives_text()
        self.text = self.draw_text(300, 200, 'Tekan Spasi untuk mulai')
        self.canvas.bind('<space>', lambda _: self.start_game())
 
    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)
 
    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick
 
    def draw_text(self, x, y, text, size=30):
        font = ('Helvetica', size, 'bold')
        return self.canvas.create_text(x, y, text=text,
                                       font=font, fill='#1e3a5f')
 
    def update_lives_text(self):
        text = 'Nyawa: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(60, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)
 
    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()
 
    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            self.ball.speed = None
            self.draw_text(300, 200, 'Kamu Menang!')
        elif self.ball.get_position()[3] >= self.height:
            self.ball.speed = None
            self.lives -= 1
            self.update_lives_text()
            if self.lives <= 0:
                self.draw_text(300, 200, 'Game Over!')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)
 
    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Brick Breaker - Hello, Jarvis!')
    root.resizable(False, False)
    game = Game(root)
    game.mainloop()