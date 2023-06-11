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
        
        self.debug:bool = False

        self.halfSpeed:bool = False
        
        self.all_room_states = []
        self.all_player_states = []
        
        self.passed_frames = 0
        self.max_passed_frames = 0

        # TAS STUFF

        self.TAS = False
        self.TAS_INPUTS = []
        self.movement = []

        import os

        if not os.path.isfile('TAS.txt'):
            open('TAS.txt', "w").close()
        else:
            with open('TAS.txt', 'r') as TAS:
                for line in TAS:
                    line = line.split(',')
                    self.TAS_INPUTS += [line]

        

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

        # Debug toggle

        if (pyxel.btnp(pyxel.KEY_1)):
            self.debug = not self.debug

        # FPS

        if (pyxel.btnp(pyxel.KEY_2)):
            self.halfSpeed = not self.halfSpeed
            

        # Menu stuff

        if self.gamestate == 0:
            
            if (pyxel.btnp(pyxel.KEY_3)):
                self.TAS = not self.TAS

            self.gamestate = self.menu.update_menu()
            if self.gamestate == 1:
                self.difficulty = self.menu.difficulty
                self.load_mask('ressources/mask.json')
                self.rooms[0].spawn_x, self.rooms[0].spawn_y = 0, 112
                self.enter_room_state = copy.deepcopy(self.rooms[0])
            return
        
        # Implements frame advance

        if not self.debug or pyxel.btnp(pyxel.KEY_Q):
                        
            if (self.max_passed_frames  != self.passed_frames):
                self.max_passed_frames = self.passed_frames
                self.all_room_states = self.all_room_states[:self.passed_frames]
                self.all_player_states = self.all_player_states[:self.passed_frames]
                self.movement = self.movement[:self.passed_frames]
            else:
                self.max_passed_frames += 1
                self.passed_frames = self.max_passed_frames
            
            self.all_room_states.append(copy.deepcopy(self.rooms[self.current_screen]))
            self.all_player_states.append(copy.deepcopy(self.player))
            
            # Logs movement

            right = 'R,' if pyxel.btn(pyxel.KEY_RIGHT) else ''
            left = 'L,' if pyxel.btn(pyxel.KEY_LEFT) else ''
            jump = 'J,' if pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.KEY_UP) else ''

            self.movement.append(right+left+jump)
            
            if not self.TAS:
                self.player.move(self.rooms[self.current_screen], self.current_screen, self.difficulty, None)
                
            else:
                try:
                    self.player.move(self.rooms[self.current_screen], self.current_screen, self.difficulty, self.TAS_INPUTS[self.passed_frames])
                except IndexError:
                    pass
            self.update_screen_position()
            self.rooms[self.current_screen].update_room(self.player.x, self.player.y)

            if (self.rooms[self.current_screen].collision(self.player.x, self.player.y) == 6):
                with open("TAS.txt", "w") as TAS:
                    for i in self.movement:
                        TAS.write(i+'\n')
    
        # Reset / Death
    
        if self.player.alive == 0 or pyxel.btnr(pyxel.KEY_R):

            if (pyxel.btnr(pyxel.KEY_R)):
                self.max_passed_frames = 0
                self.passed_frames = 0
                self.all_room_states = []
                self.all_player_states = []

            self.player.reset(self.rooms[self.current_screen].spawn_x, self.rooms[self.current_screen].spawn_y)
            self.player.alive = 1
            self.rooms[self.current_screen] = copy.deepcopy(self.enter_room_state)
  
        # Scroll through frames

        if pyxel.btnv(pyxel.MOUSE_WHEEL_Y) and self.debug:
            add = -1
            if (pyxel.mouse_wheel > 0):
                add = 1
            self.passed_frames += add
            try:
                if (self.passed_frames > self.max_passed_frames):
                    self.passed_frames = self.max_passed_frames
                
                self.rooms[self.current_screen] = self.all_room_states[self.passed_frames]
                self.player = self.all_player_states[self.passed_frames]
            except IndexError:
                pass


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
        if self.gamestate == 0:
            pyxel.cls(0)
            self.menu.draw_menu()
        else:
            if not self.debug or pyxel.btnp(pyxel.KEY_Q) or pyxel.btnv(pyxel.MOUSE_WHEEL_Y):
                pyxel.cls(0)
                pyxel.bltm(0, 0, self.difficulty + 1, self.current_screen*128, 0, 128, 128)
                self.rooms[self.current_screen].draw_room()
                self.player.draw_player()
            if self.debug:
                self.draw_debug_info()

            if pyxel.btnp(pyxel.KEY_LEFTBRACKET) or pyxel.btnp(pyxel.KEY_RIGHTBRACKET):
                if pyxel.btnp(pyxel.KEY_LEFTBRACKET): self.current_screen = (self.current_screen - 1) % len(self.rooms)
                if pyxel.btnp(pyxel.KEY_RIGHTBRACKET): self.current_screen = (self.current_screen + 1) % len(self.rooms)

                if (self.current_screen == 1 or self.current_screen == 3):
                    self.rooms[self.current_screen].spawn_x = 0
                    self.rooms[self.current_screen].spawn_y = 112
                elif (self.current_screen == 2):
                    self.rooms[self.current_screen].spawn_x = 0
                    self.rooms[self.current_screen].spawn_y = 48

                self.enter_room_state = copy.deepcopy(self.rooms[self.current_screen])

                self.player.alive = 0

    def draw_debug_info(self):
        # Display player position
        pyxel.text(5, 5, f"Pos: ({self.player.x}, {self.player.y})", pyxel.COLOR_YELLOW)

        # Display current screen index
        pyxel.text(5, 15, f"Room: {self.current_screen}", pyxel.COLOR_YELLOW)

        # Display offset and room spawn positions

        pyxel.text(5, 25, f"Frame: {self.passed_frames}", pyxel.COLOR_YELLOW)
App()

