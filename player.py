import pyxel
import rooms

class Player:
    def __init__(self, x, y, d):
        self.x = x
        self.y = y
        self.dir = d
        self.moving = 0
        self.jumping = 0
        self.grav = 2
        self.on_key = -1
        self.alive = 1

    def move(self, room, current_screen, difficulty, current_movement):

        right = False
        left = False
        jump = False


        if (current_movement == None):
            right = pyxel.btn(pyxel.KEY_RIGHT)
            left = pyxel.btn(pyxel.KEY_LEFT)
            jump = pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.KEY_UP)

        else:
            for m in current_movement:
                if m == "R":
                    right = True
                
                if m == "L":
                    left = True
                
                if m == "J":
                    jump = True


        if (
            right
            and room.collision(self.x + 8, self.y) != 1
            and room.collision(self.x + 8, self.y + 7) != 1
        ):
            self.x += 1
            self.dir = 0
            self.moving = 1
        elif (
            left
            and ( (room.collision(self.x - 1, self.y) != 1
            and room.collision(self.x - 1, self.y + 7) != 1 
            and self.x > 0)
            or (self.x <= 0 and current_screen > 0) )
        ):
            self.x -= 1
            self.dir = 1
            self.moving = 1
        
        else:
            self.moving = 0

        if (
            (jump)
            and (room.collision(self.x, self.y + 8) == 1
                 or room.collision(self.x + 7, self.y + 8) == 1)
        ):
            self.jumping = 12
        


        for i in range(self.grav):
            if (
                self.jumping == 0
                and room.collision(self.x, self.y + 8) != 1
                and room.collision(self.x + 7, self.y + 8) != 1
            ):
                self.y += 1
    
        if (
            room.collision(self.x, self.y - 2) == 1
            or room.collision(self.x + 7, self.y - 2) == 1
        ):
            self.jumping = 0
        
        if self.jumping > 0:
            self.y -= 2
            self.jumping -= 1

        if difficulty <= 1:
            if (room.collision(self.x + 1, self.y + 1) == 5
                or room.collision(self.x + 6, self.y + 1) == 5
                or room.collision(self.x + 1, self.y + 6) == 5
                or room.collision(self.x + 6, self.y + 6) == 5
            ):
                self.alive = 0
        else:
            if (room.collision(self.x, self.y) == 5
                or room.collision(self.x + 7, self.y) == 5
                or room.collision(self.x, self.y + 7) == 5
                or room.collision(self.x + 7, self.y + 7) == 5
            ):
                self.alive = 0

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.dir = 0
        self.moving = 0
        self.jumping = 0


    def draw_player(self):
        if self.jumping > 0:
            pyxel.blt(self.x, self.y, 0, 24, 8*self.dir, 8, 8, 0)
        elif self.moving == 1:
            pyxel.blt(self.x, self.y, 0, 8*(pyxel.frame_count % 2 + 1), 8*self.dir, 8, 8, 0)
        else:
            pyxel.blt(self.x, self.y, 0, 8 + 8*self.dir, 8*self.dir, 8, 8, 0)
