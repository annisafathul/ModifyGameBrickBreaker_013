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