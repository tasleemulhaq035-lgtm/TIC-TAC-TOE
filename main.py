from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import StringProperty
import random
import os
import socket
import threading


# --- HELPER TO GET YOUR PHONE'S WI-FI IP ---
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# --- NEW 3D ARCADE UI WIDGETS ---
class ArcadeTitle(FloatLayout):
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        # Layering text to create a thick, extruded 3D logo effect
        # 1. Drop shadow
        self.add_widget(Label(text=text, font_size=85, bold=True, color=(0, 0, 0, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.44}))
        # 2. Thick grey/brown outline extrusion
        self.add_widget(Label(text=text, font_size=85, bold=True, color=(0.3, 0.25, 0.25, 1), pos_hint={'center_x': 0.5, 'center_y': 0.47}))
        # 3. Main core color (Vibrant Orange/Red)
        self.add_widget(Label(text=text, font_size=82, bold=True, color=(1, 0.3, 0.1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        # 4. Top bright highlight (Yellowish)
        self.add_widget(Label(text=text, font_size=82, bold=True, color=(1, 0.8, 0.2, 1), pos_hint={'center_x': 0.5, 'center_y': 0.51}))

class ArcadeButton(Button):
    def __init__(self, main_color, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1) # Pure white text
        self.font_size = 36
        self.bold = True
        self.size_hint = (1, None)
        self.height = 105
        
        # Calculate a darker version of the main color for the 3D bottom lip
        dark_color = (main_color[0]*0.6, main_color[1]*0.6, main_color[2]*0.6, 1)
        rim_color = (0.5, 0.5, 0.5, 1) # Metallic grey rim

        with self.canvas.before:
            # 1. Outer Drop Shadow
            Color(0, 0, 0, 0.6)
            self.shadow = RoundedRectangle(radius=[35])
            # 2. Outer Metallic Rim
            Color(*rim_color)
            self.rim = RoundedRectangle(radius=[35])
            # 3. Inner Dark Lip (gives the button physical depth)
            Color(*dark_color)
            self.inner_bottom = RoundedRectangle(radius=[28])
            # 4. Main Bright Face
            Color(*main_color)
            self.face = RoundedRectangle(radius=[28])
            # 5. Glossy Top Highlight (Fake lighting reflection)
            Color(1, 1, 1, 0.15)
            self.highlight = RoundedRectangle(radius=[28, 28, 8, 8]) 
            
        self.bind(pos=self.update_canvas, size=self.update_canvas, state=self.update_canvas)

    def update_canvas(self, *args):
        x, y, w, h = self.x, self.y, self.width, self.height
        push = 8 if self.state == 'down' else 0 # Physical squish distance

        self.shadow.pos = (x + 2, y - 6)
        self.shadow.size = (w, h)

        self.rim.pos = (x, y - push)
        self.rim.size = (w, h)

        # The inner colored pill sits inside the rim
        self.inner_bottom.pos = (x + 8, y + 8 - push)
        self.inner_bottom.size = (w - 16, h - 16)

        # The face leaves a gap at the bottom to expose the dark lip
        self.face.pos = (x + 8, y + 16 - push)
        self.face.size = (w - 16, h - 24)

        # Highlight on the top half of the face
        self.highlight.pos = (x + 8, y + 16 + (h-24)/2 - push)
        self.highlight.size = (w - 16, (h - 24)/2)

class SmallArcadeButton(ArcadeButton):
    def __init__(self, main_color, **kwargs):
        super().__init__(main_color, **kwargs)
        self.font_size = 20
        self.height = 65
        # Smaller radii for the smaller button
        self.bind(pos=self.update_small_canvas, size=self.update_small_canvas, state=self.update_small_canvas)

    def update_small_canvas(self, *args):
        x, y, w, h = self.x, self.y, self.width, self.height
        push = 5 if self.state == 'down' else 0

        self.shadow.radius = self.rim.radius = [20]
        self.inner_bottom.radius = self.face.radius = [15]
        self.highlight.radius = [15, 15, 4, 4]

        self.shadow.pos, self.shadow.size = (x + 2, y - 4), (w, h)
        self.rim.pos, self.rim.size = (x, y - push), (w, h)
        self.inner_bottom.pos, self.inner_bottom.size = (x + 5, y + 5 - push), (w - 10, h - 10)
        self.face.pos, self.face.size = (x + 5, y + 10 - push), (w - 10, h - 15)
        self.highlight.pos, self.highlight.size = (x + 5, y + 10 + (h-15)/2 - push), (w - 10, (h - 15)/2)


# --- GAME PIECES (Untouched Neon style) ---
class PieceButton(Button):
    piece_type = StringProperty(' ')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0) 
        self.bind(pos=self.update_canvas, size=self.update_canvas, piece_type=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.after.clear()
        if self.piece_type == ' ': return
        x, y = self.pos
        w, h = self.size
        pad = min(w, h) * 0.25 

        with self.canvas.after:
            if self.piece_type == 'X':
                Color(0, 1, 1, 0.2)
                Line(points=[x+pad, y+pad, x+w-pad, y+h-pad], width=10, cap='round')
                Line(points=[x+w-pad, y+pad, x+pad, y+h-pad], width=10, cap='round')
                Color(0, 1, 1, 0.5)
                Line(points=[x+pad, y+pad, x+w-pad, y+h-pad], width=5, cap='round')
                Line(points=[x+w-pad, y+pad, x+pad, y+h-pad], width=5, cap='round')
                Color(0, 1, 1, 1)
                Line(points=[x+pad, y+pad, x+w-pad, y+h-pad], width=2, cap='round')
                Line(points=[x+w-pad, y+pad, x+pad, y+h-pad], width=2, cap='round')
            elif self.piece_type == 'O':
                cx, cy = self.center_x, self.center_y
                r = min(w, h) * 0.3
                Color(1, 0.2, 0.8, 0.2)
                Line(circle=(cx, cy, r), width=10)
                Color(1, 0.2, 0.8, 0.5)
                Line(circle=(cx, cy, r), width=5)
                Color(1, 0.2, 0.8, 1)
                Line(circle=(cx, cy, r), width=2)


# --- SCREENS ---
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            if os.path.exists('bg.png'):
                 self.rect = Rectangle(source='bg.png', size=Window.size, pos=self.pos)
            else:
                 Color(0.05, 0.05, 0.08, 1) 
                 self.rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation='vertical', padding=40, spacing=25, size_hint=(0.95, 0.85), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        
        title_box = BoxLayout(size_hint=(1, 0.4))
        title = ArcadeTitle(text="TIC TAC TOE")
        title_box.add_widget(title)
        
        # vibrant orange like the reference image
        btn_bot = ArcadeButton(text="1 PLAYER", main_color=(1, 0.5, 0, 1))
        btn_bot.bind(on_press=self.go_difficulty)

        # Vibrant green
        btn_local = ArcadeButton(text="2 PLAYERS", main_color=(0.4, 0.8, 0.1, 1))
        btn_local.bind(on_press=self.start_local)
        
        # Vibrant blue
        btn_lan = ArcadeButton(text="PLAY ON LAN", main_color=(0.1, 0.5, 1, 1)) 
        btn_lan.bind(on_press=self.go_lan_menu)
        
        layout.add_widget(title_box)
        layout.add_widget(btn_bot)
        layout.add_widget(btn_local)
        layout.add_widget(btn_lan)
        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def go_difficulty(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'difficulty'

    def start_local(self, instance):
        game_screen = self.manager.get_screen('game')
        game_screen.set_mode(bot_mode=False, lan_mode=False)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'game'

    def go_lan_menu(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'lan_menu'

class DifficultyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            if os.path.exists('bg.png'):
                 self.rect = Rectangle(source='bg.png', size=Window.size, pos=self.pos)
            else:
                 Color(0.05, 0.05, 0.08, 1) 
                 self.rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation='vertical', padding=40, spacing=25, size_hint=(0.95, 0.85), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        
        title_box = BoxLayout(size_hint=(1, 0.3))
        title = ArcadeTitle(text="SELECT AI")
        title_box.add_widget(title)
        
        btn_easy = ArcadeButton(text="EASY", main_color=(0.1, 0.8, 0.3, 1))
        btn_easy.bind(on_press=lambda x: self.start_bot('easy'))

        btn_medium = ArcadeButton(text="MEDIUM", main_color=(1, 0.7, 0, 1))
        btn_medium.bind(on_press=lambda x: self.start_bot('medium'))
        
        btn_hard = ArcadeButton(text="HARD", main_color=(1, 0.2, 0.2, 1))
        btn_hard.bind(on_press=lambda x: self.start_bot('hard'))

        btn_back_layout = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.3))
        btn_back = SmallArcadeButton(text="< BACK", main_color=(0.4, 0.4, 0.4, 1), size_hint=(0.4, None))
        btn_back.bind(on_press=self.go_back)
        btn_back_layout.add_widget(btn_back)
        
        layout.add_widget(title_box)
        layout.add_widget(btn_easy)
        layout.add_widget(btn_medium)
        layout.add_widget(btn_hard)
        layout.add_widget(btn_back_layout)
        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def start_bot(self, difficulty):
        game_screen = self.manager.get_screen('game')
        game_screen.set_mode(bot_mode=True, lan_mode=False, difficulty=difficulty)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'game'

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'menu'

class LanMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            if os.path.exists('bg.png'):
                 self.rect = Rectangle(source='bg.png', size=Window.size, pos=self.pos)
            else:
                 Color(0.05, 0.05, 0.08, 1) 
                 self.rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation='vertical', padding=40, spacing=25, size_hint=(0.95, 0.85), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        
        title_box = BoxLayout(size_hint=(1, 0.4))
        title = ArcadeTitle(text="LAN PLAY")
        title_box.add_widget(title)
        
        btn_host = ArcadeButton(text="HOST GAME (X)", main_color=(0.1, 0.7, 1, 1))
        btn_host.bind(on_press=self.go_host)

        btn_join = ArcadeButton(text="JOIN GAME (O)", main_color=(0.8, 0.2, 0.8, 1))
        btn_join.bind(on_press=self.go_join)

        btn_back_layout = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.3))
        btn_back = SmallArcadeButton(text="< BACK", main_color=(0.4, 0.4, 0.4, 1), size_hint=(0.4, None))
        btn_back.bind(on_press=self.go_back)
        btn_back_layout.add_widget(btn_back)
        
        layout.add_widget(title_box)
        layout.add_widget(btn_host)
        layout.add_widget(btn_join)
        layout.add_widget(btn_back_layout)
        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def go_host(self, instance):
        game_screen = self.manager.get_screen('game')
        game_screen.set_mode(bot_mode=False, lan_mode=True, lan_role='host')
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'game'

    def go_join(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'join_screen'

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'menu'

class JoinScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            if os.path.exists('bg.png'):
                 self.rect = Rectangle(source='bg.png', size=Window.size, pos=self.pos)
            else:
                 Color(0.05, 0.05, 0.08, 1) 
                 self.rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation='vertical', padding=40, spacing=25, size_hint=(0.95, 0.85), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        
        title_box = BoxLayout(size_hint=(1, 0.3))
        title = ArcadeTitle(text="ENTER IP")
        title_box.add_widget(title)
        
        self.ip_input = TextInput(hint_text="e.g. 192.168.1.5", font_size=40, halign="center", size_hint=(1, None), height=100,
                                  background_color=(0.1, 0.1, 0.1, 1), foreground_color=(1, 1, 1, 1), multiline=False)
        
        btn_connect = ArcadeButton(text="CONNECT", main_color=(0.1, 0.8, 0.3, 1))
        btn_connect.bind(on_press=self.connect_to_host)

        btn_back_layout = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.3))
        btn_back = SmallArcadeButton(text="< BACK", main_color=(0.4, 0.4, 0.4, 1), size_hint=(0.4, None))
        btn_back.bind(on_press=self.go_back)
        btn_back_layout.add_widget(btn_back)
        
        layout.add_widget(title_box)
        layout.add_widget(self.ip_input)
        layout.add_widget(btn_connect)
        layout.add_widget(btn_back_layout)
        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def connect_to_host(self, instance):
        ip = self.ip_input.text.strip()
        if ip:
            game_screen = self.manager.get_screen('game')
            game_screen.set_mode(bot_mode=False, lan_mode=True, lan_role='client', target_ip=ip)
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'game'

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'lan_menu'

# --- GAME SCREEN ---
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.turn = 'X'
        self.board = [' '] * 9
        self.locked = False 
        
        self.bot_mode = False 
        self.difficulty = 'easy'
        self.lan_mode = False
        self.lan_role = None 
        self.network_socket = None
        self.client_conn = None 
        
        with self.canvas.before:
            if os.path.exists('bg.png'):
                self.rect = Rectangle(source='bg.png', size=Window.size, pos=self.pos)
            else:
                Color(0.05, 0.05, 0.08, 1) 
                self.rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.main_layout = FloatLayout()
        
        self.top_bar = BoxLayout(orientation='horizontal', size_hint=(0.95, 0.1), pos_hint={'top': 0.98, 'center_x': 0.5}, spacing=15)
        
        back_btn = SmallArcadeButton(text="< LEAVE", main_color=(1, 0.2, 0.2, 1), size_hint=(0.3, None), pos_hint={'center_y': 0.5})
        back_btn.bind(on_press=self.go_to_menu)
        
        self.turn_label = Label(text="LOADING...", font_size=24, bold=True, color=(1, 1, 1, 1), size_hint=(0.7, 1))
        
        self.top_bar.add_widget(back_btn)
        self.top_bar.add_widget(self.turn_label)
        self.main_layout.add_widget(self.top_bar)

        self.board_layer = AnchorLayout(size_hint=(1, 0.85), pos_hint={'bottom': 1})
        side_length = min(Window.width, Window.height) * 0.95 
        
        self.grid_bg = BoxLayout(size_hint=(None, None), size=(side_length, side_length))
        
        with self.grid_bg.canvas.before:
            Color(0, 0.8, 1, 0.3) 
            self.line_v1_glow = Line(width=6, cap='round')
            self.line_v2_glow = Line(width=6, cap='round')
            self.line_h1_glow = Line(width=6, cap='round')
            self.line_h2_glow = Line(width=6, cap='round')
            
            Color(0, 0.8, 1, 1) 
            self.line_v1 = Line(width=2, cap='round')
            self.line_v2 = Line(width=2, cap='round')
            self.line_h1 = Line(width=2, cap='round')
            self.line_h2 = Line(width=2, cap='round')

        self.grid_bg.bind(pos=self._update_grid_lines, size=self._update_grid_lines)
        
        self.grid = GridLayout(cols=3, spacing=0, size_hint=(1, 1))
        
        self.buttons = []
        for i in range(9):
            btn = PieceButton() 
            btn.bind(on_press=lambda instance, index=i: self.local_move_attempt(index))
            self.buttons.append(btn)
            self.grid.add_widget(btn)
            
        self.grid_bg.add_widget(self.grid)
        self.board_layer.add_widget(self.grid_bg)
        self.main_layout.add_widget(self.board_layer)
        
        self.line_layer = Widget()
        self.main_layout.add_widget(self.line_layer)

        self.menu_layer = FloatLayout(opacity=0) 
        self.add_widget(self.main_layout)

    def set_mode(self, bot_mode=False, lan_mode=False, difficulty='easy', lan_role=None, target_ip=None):
        self.bot_mode = bot_mode
        self.lan_mode = lan_mode
        self.difficulty = difficulty
        self.lan_role = lan_role
        self.target_ip = target_ip

    def on_pre_enter(self, *args):
        self.reset_board(full_reset=True)
        
        if self.lan_mode:
            if self.lan_role == 'host':
                my_ip = get_local_ip()
                self.turn_label.text = f"IP: {my_ip} | WAITING..."
                self.turn_label.color = (1, 1, 1, 1)
                self.locked = True 
                threading.Thread(target=self.host_server, daemon=True).start()
            elif self.lan_role == 'client':
                self.turn_label.text = "CONNECTING..."
                self.locked = True 
                threading.Thread(target=self.connect_to_server, daemon=True).start()
        else:
            self.update_turn_signal()

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        
    def _update_grid_lines(self, instance, value):
        x, y = self.grid_bg.pos
        w, h = self.grid_bg.size
        
        v1_x, v2_x = x + w/3, x + 2*w/3
        h1_y, h2_y = y + h/3, y + 2*h/3
        
        v1_pts = [v1_x, y+10, v1_x, y+h-10]
        v2_pts = [v2_x, y+10, v2_x, y+h-10]
        self.line_v1_glow.points = self.line_v1.points = v1_pts
        self.line_v2_glow.points = self.line_v2.points = v2_pts
        
        h1_pts = [x+10, h1_y, x+w-10, h1_y]
        h2_pts = [x+10, h2_y, x+w-10, h2_y]
        self.line_h1_glow.points = self.line_h1.points = h1_pts
        self.line_h2_glow.points = self.line_h2.points = h2_pts

    # --- NETWORKING LOGIC ---
    def host_server(self):
        try:
            self.network_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.network_socket.bind(('0.0.0.0', 65432))
            self.network_socket.listen(1)
            self.client_conn, addr = self.network_socket.accept()
            Clock.schedule_once(lambda dt: self.start_lan_match())
            while True:
                data = self.client_conn.recv(1024).decode()
                if not data: break
                index = int(data)
                Clock.schedule_once(lambda dt, idx=index: self.execute_move(idx))
        except Exception as e:
            print("Host error:", e)

    def connect_to_server(self):
        try:
            self.network_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.network_socket.connect((self.target_ip, 65432))
            Clock.schedule_once(lambda dt: self.start_lan_match())
            while True:
                data = self.network_socket.recv(1024).decode()
                if not data: break
                index = int(data)
                Clock.schedule_once(lambda dt, idx=index: self.execute_move(idx))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error("CONNECTION FAILED"))

    def start_lan_match(self):
        self.update_turn_signal()

    def update_turn_signal(self):
        if self.lan_mode:
            my_piece = 'X' if self.lan_role == 'host' else 'O'
            is_my_turn = self.turn == my_piece
            
            if is_my_turn:
                self.turn_label.text = f"YOUR TURN ({my_piece})"
                self.turn_label.color = (0, 1, 1, 1) if my_piece == 'X' else (1, 0.2, 0.8, 1)
                self.locked = False
            else:
                self.turn_label.text = "WAITING FOR OPPONENT..."
                self.turn_label.color = (0.7, 0.7, 0.7, 1)
                self.locked = True
        else:
            if self.turn == 'X':
                self.turn_label.color = (0, 1, 1, 1)
                self.turn_label.text = "YOUR TURN (X)" if self.bot_mode else "PLAYER 1 (X)"
            else:
                self.turn_label.color = (1, 0.2, 0.8, 1)
                self.turn_label.text = "AI IS THINKING..." if self.bot_mode else "PLAYER 2 (O)"

    # --- GAME LOGIC ---
    def local_move_attempt(self, index):
        if self.board[index] != ' ' or self.locked:
            return

        self.locked = True
        
        if self.lan_mode:
            try:
                if self.lan_role == 'host':
                    self.client_conn.send(str(index).encode())
                else:
                    self.network_socket.send(str(index).encode())
            except Exception as e:
                print("Failed to send move", e)
                
        self.execute_move(index)

    def execute_move(self, index):
        button = self.buttons[index]
        button.piece_type = self.turn
        self.board[index] = self.turn
        
        win_combo = self.check_win(self.board)
        
        if win_combo:
            self.draw_winning_line(win_combo)
        elif ' ' not in self.board:
            self.show_menu("MATCH DRAW", "DRAW")
        else:
            self.turn = 'O' if self.turn == 'X' else 'X'
            self.update_turn_signal()
            
            if self.bot_mode and self.turn == 'O':
                Clock.schedule_once(self.trigger_bot, 0.6) 

    def trigger_bot(self, dt):
        empty_spots = [i for i, spot in enumerate(self.board) if spot == ' ']
        if not empty_spots: return
        best_move = None
        if self.difficulty == 'easy': best_move = random.choice(empty_spots)
        elif self.difficulty == 'medium':
            for move in empty_spots:
                self.board[move] = 'O'
                if self.check_win(self.board): best_move = move
                self.board[move] = ' '
            if best_move is None:
                for move in empty_spots:
                    self.board[move] = 'X'
                    if self.check_win(self.board): best_move = move
                    self.board[move] = ' '
            if best_move is None: best_move = random.choice(empty_spots)
        elif self.difficulty == 'hard':
            best_score = -float('inf')
            for move in empty_spots:
                self.board[move] = 'O'
                score = self.minimax(self.board, 0, False)
                self.board[move] = ' '
                if score > best_score:
                    best_score = score
                    best_move = move
        self.execute_move(best_move)

    def minimax(self, board, depth, is_maximizing):
        win_combo = self.check_win(board)
        if win_combo:
            winner = board[win_combo[0]]
            if winner == 'O': return 10 - depth
            if winner == 'X': return -10 + depth 
        if ' ' not in board: return 0 
        
        if is_maximizing:
            best_score = -float('inf')
            for i in range(9):
                if board[i] == ' ':
                    board[i] = 'O'
                    score = self.minimax(board, depth + 1, False)
                    board[i] = ' '
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(9):
                if board[i] == ' ':
                    board[i] = 'X'
                    score = self.minimax(board, depth + 1, True)
                    board[i] = ' '
                    best_score = min(score, best_score)
            return best_score

    def check_win(self, board_state):
        win_lines = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b, c in win_lines:
            if board_state[a] == board_state[b] == board_state[c] != ' ':
                return (a, b, c) 
        return None

    def draw_winning_line(self, combo):
        btn_start = self.buttons[combo[0]]
        btn_end = self.buttons[combo[2]]
        
        x1, y1 = btn_start.to_window(btn_start.center_x, btn_start.center_y)
        x2, y2 = btn_end.to_window(btn_end.center_x, btn_end.center_y)
        
        line_color = (0, 1, 1) if self.turn == 'X' else (1, 0.2, 0.8)
        
        with self.line_layer.canvas:
            Color(*line_color, 0.3)
            self.win_line_outer = Line(points=[x1, y1, x1, y1], width=15, cap='round')
            Color(*line_color, 1)   
            self.win_line_inner = Line(points=[x1, y1, x1, y1], width=4, cap='round')
            
        anim_outer = Animation(points=[x1, y1, x2, y2], duration=1.0)
        anim_inner = Animation(points=[x1, y1, x2, y2], duration=1.0)
        
        if self.lan_mode:
            my_piece = 'X' if self.lan_role == 'host' else 'O'
            if self.turn == my_piece:
                winner_text = "YOU WIN!"
                state = "WIN"
            else:
                winner_text = "YOU LOSE!"
                state = "LOSE"
        elif self.bot_mode:
            winner_text = "YOU WIN!" if self.turn == 'X' else "AI WINS!"
            state = "WIN" if self.turn == 'X' else "LOSE"
        else:
            player_num = "1" if self.turn == 'X' else "2"
            winner_text = f"PLAYER {player_num} WINS!"
            state = "WIN"
            
        anim_inner.bind(on_complete=lambda *args: self.show_menu(winner_text, state))
        anim_outer.start(self.win_line_outer)
        anim_inner.start(self.win_line_inner)

    def show_error(self, message):
        self.show_menu(message, "LOSE")

    def show_menu(self, message, state):
        self.menu_layer.clear_widgets()
        self.turn_label.text = "GAME OVER"
        self.locked = True
        
        bg = Button(background_normal='', background_color=(0, 0, 0, 0.95), size_hint=(1, 1))
        self.menu_layer.add_widget(bg)
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=30, size_hint=(0.9, 0.5), pos_hint={'center_x': 0.5, 'center_y': 0.55})
        
        if state == "WIN":
            txt_color = (0, 1, 1, 1) if self.turn == 'X' else (1, 0.2, 0.8, 1)
        elif state == "LOSE":
            txt_color = (1, 0.2, 0.2, 1) 
        else:
            txt_color = (1, 1, 1, 1) 
            
        title_box = FloatLayout(size_hint=(1, 0.5))
        title_box.add_widget(Label(text=message, font_size=58, bold=True, color=(*txt_color[:3], 0.3), pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        title_box.add_widget(Label(text=message, font_size=55, bold=True, color=txt_color, pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        
        btn_layout = BoxLayout(orientation='vertical', spacing=20, size_hint=(1, None), height=220)
        
        play_btn = ArcadeButton(text="REMATCH", main_color=(0, 0.6, 1, 1))
        play_btn.bind(on_press=self.reset_board)

        menu_btn = ArcadeButton(text="MAIN MENU", main_color=(0.8, 0.2, 0.5, 1))
        menu_btn.bind(on_press=self.go_to_menu)
        
        if not self.lan_mode:
            btn_layout.add_widget(play_btn)
            
        btn_layout.add_widget(menu_btn)
        
        content.add_widget(title_box)
        content.add_widget(btn_layout)
        self.menu_layer.add_widget(content)
        
        self.main_layout.add_widget(self.menu_layer)
        self.menu_layer.opacity = 1

    def close_sockets(self):
        try:
            if self.client_conn: self.client_conn.close()
            if self.network_socket: self.network_socket.close()
        except: pass

    def reset_board(self, instance=None, full_reset=False):
        self.board = [' '] * 9
        self.turn = 'X'
        self.locked = False
        self.line_layer.canvas.clear() 
        for btn in self.buttons:
            btn.piece_type = ' '
            
        if self.menu_layer in self.main_layout.children:
            self.main_layout.remove_widget(self.menu_layer)
        self.menu_layer.opacity = 0
        
        if not full_reset:
            self.update_turn_signal()

    def go_to_menu(self, instance):
        if self.lan_mode:
            self.close_sockets()
        self.reset_board(full_reset=True)
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'menu'

class TicTacToeApp(App):
    def build(self):
        self.title = "NEON XO"
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(DifficultyScreen(name='difficulty'))
        sm.add_widget(LanMenuScreen(name='lan_menu'))
        sm.add_widget(JoinScreen(name='join_screen'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    TicTacToeApp().run()