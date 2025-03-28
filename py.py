import tkinter as tk
import random

class SnakeGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("贪吃蛇游戏")
        self.canvas = tk.Canvas(self.root, width=400, height=400, bg='black')
        self.canvas.pack()

        self.snake_coords = [[10, 10], [9, 10], [8, 10]]
        self.direction = 'Right'
        self.food = self.new_food()
        self.score = 0
        self.game_over_flag = False

        self.draw_snake()
        self.draw_food()
        self.draw_score()

        self.root.bind('<Left>', self.change_direction)
        self.root.bind('<Right>', self.change_direction)
        self.root.bind('<Up>', self.change_direction)
        self.root.bind('<Down>', self.change_direction)

        self.root.after(150, self.move)
        self.root.mainloop()

    def draw_snake(self):
        self.canvas.delete("snake")
        for segment in self.snake_coords:
            x1 = segment[0] * 20
            y1 = segment[1] * 20
            x2 = x1 + 20
            y2 = y1 + 20
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='green', tag="snake")

    def draw_food(self):
        x, y = self.food
        x1, y1 = x*20, y*20
        x2, y2 = x1+20, y1+20
        self.canvas.create_rectangle(x1, y1, x2, y2, fill='red', tag="food")

    def draw_score(self):
        self.canvas.delete("score")
        self.canvas.create_text(100, 20, text=f"得分: {self.score}", 
                               fill='white', font=('Arial', 12), tag="score")

    def change_direction(self, event):
        new_dir = event.keysym
        if (new_dir == 'Left' and self.direction != 'Right') or \
           (new_dir == 'Right' and self.direction != 'Left') or \
           (new_dir == 'Up' and self.direction != 'Down') or \
           (new_dir == 'Down' and self.direction != 'Up'):
            self.direction = new_dir

    def new_food(self):
        while True:
            x = random.randint(0, 19)
            y = random.randint(0, 19)
            if [x, y] not in self.snake_coords:
                return [x, y]

    def move(self):
        if self.game_over_flag:
            return

        head = list(self.snake_coords[0])
        if self.direction == 'Right':
            head[0] += 1
        elif self.direction == 'Left':
            head[0] -= 1
        elif self.direction == 'Up':
            head[1] -= 1
        elif self.direction == 'Down':
            head[1] += 1

        # 碰撞检测
        if (head[0] < 0 or head[0] >= 20 or 
            head[1] < 0 or head[1] >= 20 or 
            head in self.snake_coords):
            self.game_over()
            return

        # 食物检测
        if head == self.food:
            self.score += 1
            self.food = self.new_food()
        else:
            del self.snake_coords[-1]

        self.snake_coords.insert(0, head)

        self.draw_snake()
        self.draw_food()
        self.draw_score()

        self.root.after(150, self.move)

    def game_over(self):
        self.game_over_flag = True
        self.canvas.delete("all")
        self.canvas.create_text(200, 200, text="游戏结束！",
                               fill='white', font=('Arial', 20))
        self.canvas.create_text(200, 250, text=f"最终得分: {self.score}",
                               fill='white', font=('Arial', 14))

if __name__ == "__main__":
    SnakeGame()