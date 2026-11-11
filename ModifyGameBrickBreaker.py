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
