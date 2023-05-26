import pyxel, json, copy
from player import Player
from rooms import Room
from menu import Menu

class App:
    def __init__(self):
        self.gamestate = 0
        self.player = Player(0, 112, 0)
        self.current_screen = 0
        self.offset_x = 0
        self.menu = Menu()

        pyxel.init(128, 128, title='SpaceWarp')
        pyxel.load("ressources/assets.pyxres")
        pyxel.run(self.update, self.draw)
        
    def load_mask(self, file_name):
        with open(file_name, 'r') as file:
            mask = json.load(file)
            self.rooms = []
            for i in range(mask[self.difficulty][0]):
                self.rooms.append(Room(mask[self.difficulty][1][i], mask[self.difficulty][2][i]))

    def update(self):
        if self.gamestate == 0:
            self.gamestate = self.menu.update_menu()
            if self.gamestate == 1:
                self.difficulty = self.menu.difficulty
                self.load_mask('ressources/mask.json')
                self.rooms[0].spawn_x, self.rooms[0].spawn_y = 0, 112
                self.enter_room_state = copy.deepcopy(self.rooms[0])
            return

        self.player.move(self.rooms[self.current_screen], self.current_screen)
        self.update_screen_position()
        self.rooms[self.current_screen].update_room(self.player.x, self.player.y)
        
        if self.player.alive == 0 or pyxel.btnr(pyxel.KEY_R):
            self.player.reset(self.rooms[self.current_screen].spawn_x, self.rooms[self.current_screen].spawn_y)
            self.player.alive = 1
            self.rooms[self.current_screen] = copy.deepcopy(self.enter_room_state)

    def update_screen_position(self):
        if self.player.x == 124:
            self.offset_x += 128
            self.current_screen += 1
            self.player.x -= 128
            self.rooms[self.current_screen].spawn_x = self.player.x + 4
            self.rooms[self.current_screen].spawn_y = self.player.y
            self.enter_room_state = copy.deepcopy(self.rooms[self.current_screen])
        elif self.player.x == -5 and self.current_screen != 0:
            self.offset_x -= 128
            self.current_screen -= 1
            self.player.x += 128
            self.rooms[self.current_screen].spawn_x = self.player.x - 4
            self.rooms[self.current_screen].spawn_y = self.player.y
            self.enter_room_state = copy.deepcopy(self.rooms[self.current_screen])


    def draw(self):
        pyxel.cls(0)
        if self.gamestate == 0:
            self.menu.draw_menu()
        else:
            pyxel.bltm(0, 0, self.difficulty + 1, self.offset_x, 0, 128, 128)
            self.rooms[self.current_screen].draw_room()
            self.player.draw_player()

App()