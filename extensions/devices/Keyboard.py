import pygame
import time
from collections import deque
from api.Device import Device

class Keyboard(Device):
    def __init__(self, canvas):
        super().__init__(canvas, "Keyboard")
        
        # Серийный номер устройства
        self.serial_number = self.config.get("serial_number", 0x4e)
        
        # ИСПРАВЛЕННАЯ раскладка - стрелки справа
        self.layout = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '', ''],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '', ''],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', '', 'UP'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'LT', 'DN', 'RT'],
            ['SPACE', 'ENT', 'BS']  # Нижний ряд упрощен
        ]
        
        # Размеры клавиш
        self.key_width = self.config.get("key_width", 35)
        self.key_height = self.config.get("key_height", 35)
        self.key_gap = self.config.get("gap_size", 3)
        
        # Цветовая схема в стиле дисплея
        self.background_color = self.config.get("background_color", [40, 40, 40])
        self.frame_color = self.config.get("frame_color", [60, 60, 60])
        self.key_color = self.config.get("key_color", [50, 50, 50])
        self.key_pressed_color = self.config.get("key_pressed_color", [0, 180, 60])
        self.key_text_color = self.config.get("key_text_color", [200, 200, 200])
        self.border_color = self.config.get("border_color", [100, 100, 100])
        self.arrow_key_color = self.config.get("arrow_key_color", [70, 70, 70])
        self.special_key_color = self.config.get("special_key_color", [65, 65, 65])
        
        # Рамка клавиатуры
        self.frame_thickness = 6
        
        # Обновляем размеры устройства
        max_keys_in_row = max(len(row) for row in self.layout)
        keyboard_width = max_keys_in_row * (self.key_width + self.key_gap) + self.key_gap
        keyboard_height = len(self.layout) * (self.key_height + self.key_gap) + self.key_gap
        
        self.width = keyboard_width + self.frame_thickness * 2
        self.height = keyboard_height + self.frame_thickness * 2 + 20
        self.surface = pygame.Surface((self.width, self.height))
        
        # Состояние клавиш
        self.pressed_keys = set()
        self.key_press_times = {}
        
        # Буфер клавиш для процессора
        self.key_buffer = deque(maxlen=256)
        
        # Шрифты
        pygame.font.init()
        self.font = pygame.font.Font(None, 18)
        self.small_font = pygame.font.Font(None, 14)
        
        # ИСПРАВЛЕННЫЙ маппинг клавиш с текстовыми представлениями
        self.pygame_to_char = {
            pygame.K_1: '1', pygame.K_2: '2', pygame.K_3: '3', pygame.K_4: '4', pygame.K_5: '5',
            pygame.K_6: '6', pygame.K_7: '7', pygame.K_8: '8', pygame.K_9: '9', pygame.K_0: '0',
            pygame.K_q: 'Q', pygame.K_w: 'W', pygame.K_e: 'E', pygame.K_r: 'R', pygame.K_t: 'T',
            pygame.K_y: 'Y', pygame.K_u: 'U', pygame.K_i: 'I', pygame.K_o: 'O', pygame.K_p: 'P',
            pygame.K_a: 'A', pygame.K_s: 'S', pygame.K_d: 'D', pygame.K_f: 'F', pygame.K_g: 'G',
            pygame.K_h: 'H', pygame.K_j: 'J', pygame.K_k: 'K', pygame.K_l: 'L', pygame.K_SEMICOLON: ';',
            pygame.K_z: 'Z', pygame.K_x: 'X', pygame.K_c: 'C', pygame.K_v: 'V', pygame.K_b: 'B',
            pygame.K_n: 'N', pygame.K_m: 'M', pygame.K_COMMA: ',', pygame.K_PERIOD: '.', pygame.K_SLASH: '/',
            pygame.K_SPACE: 'SPACE', pygame.K_RETURN: 'ENT', pygame.K_BACKSPACE: 'BS',
            # Стрелки как текст
            pygame.K_UP: 'UP', pygame.K_DOWN: 'DN', pygame.K_LEFT: 'LT', pygame.K_RIGHT: 'RT'
        }
        
    def get_default_config(self):
        """Обновленная конфигурация"""
        config = super().get_default_config()
        config.update({
            "accepts_keyboard_input": True,
            "serial_number": 0x4e,
            "key_width": 35,
            "key_height": 35,
            "gap_size": 3,
            "background_color": [40, 40, 40],
            "frame_color": [60, 60, 60],
            "key_color": [50, 50, 50],
            "key_pressed_color": [0, 180, 60],
            "key_text_color": [200, 200, 200],
            "border_color": [100, 100, 100],
            "arrow_key_color": [70, 70, 70],
            "special_key_color": [65, 65, 65],
            "width": 480,
            "height": 220,
            "x": 30,
            "y": 350
        })
        return config
    
    def get_key_rect(self, row, col):
        """Возвращает прямоугольник клавиши"""
        key = self.layout[row][col]
        
        # Пропускаем пустые клавиши
        if key == '':
            return None
            
        base_x = self.frame_thickness + self.key_gap
        base_y = self.frame_thickness + self.key_gap + row * (self.key_height + self.key_gap)
        
        if row < 4:  # Обычные ряды
            x = base_x + col * (self.key_width + self.key_gap)
            width = self.key_width
            
        elif row == 4:  # Нижний ряд с SPACE, ENT, BS
            if col == 0:  # SPACE
                x = base_x
                width = self.key_width * 6  # Широкий пробел
            elif col == 1:  # ENT
                x = base_x + self.key_width * 6 + self.key_gap
                width = self.key_width * 2
            elif col == 2:  # BS
                x = base_x + self.key_width * 8 + self.key_gap * 2
                width = self.key_width * 2
            else:
                x = base_x + col * (self.key_width + self.key_gap)
                width = self.key_width
        else:
            x = base_x + col * (self.key_width + self.key_gap)
            width = self.key_width
            
        return pygame.Rect(x, base_y, width, self.key_height)
    
    def find_key_at_position(self, local_x, local_y):
        """Находит клавишу по координатам"""
        for row in range(len(self.layout)):
            for col in range(len(self.layout[row])):
                key = self.layout[row][col]
                if key == '':  # Пропускаем пустые
                    continue
                key_rect = self.get_key_rect(row, col)
                if key_rect and key_rect.collidepoint(local_x, local_y):
                    return key
        return None
    
    def handle_click(self, local_x, local_y):
        """Обрабатывает клик по клавише"""
        key = self.find_key_at_position(local_x, local_y)
        if key:
            self.press_key(key)
            print(f"Клавиша '{key}' нажата мышью")
    
    def handle_key_down(self, event):
        """Обрабатывает нажатие клавиши с клавиатуры"""
        if event.key in self.pygame_to_char:
            key = self.pygame_to_char[event.key]
            self.press_key(key)
            print(f"Клавиша '{key}' нажата с клавиатуры")
    
    def handle_key_up(self, event):
        """Обрабатывает отпускание клавиши"""
        if event.key in self.pygame_to_char:
            key = self.pygame_to_char[event.key]
            self.release_key(key)
    
    def press_key(self, key):
        """Нажатие клавиши"""
        self.pressed_keys.add(key)
        self.key_press_times[key] = time.time()
        
        # Добавляем в буфер для процессора
        if key == 'SPACE':
            self.key_buffer.append(ord(' '))
        elif key == 'ENT':
            self.key_buffer.append(10)
        elif key == 'BS':
            self.key_buffer.append(8)
        elif key in ['UP', 'DN', 'LT', 'RT']:
            # Стрелки как специальные коды
            arrow_codes = {'UP': 200, 'DN': 201, 'LT': 202, 'RT': 203}
            self.key_buffer.append(arrow_codes[key])
        elif len(key) == 1:
            self.key_buffer.append(ord(key))
    
    def release_key(self, key):
        """Отпускание клавиши"""
        self.pressed_keys.discard(key)
        if key in self.key_press_times:
            del self.key_press_times[key]
    
    def update(self):
        """Обновляет состояние клавиатуры"""
        current_time = time.time()
        
        # Автоматически отпускаем клавиши
        keys_to_release = []
        for key, press_time in self.key_press_times.items():
            if current_time - press_time > 0.2:
                keys_to_release.append(key)
        
        for key in keys_to_release:
            self.release_key(key)
    
    def draw(self):
        """Рисует клавиатуру в новом стиле"""
        # Фон
        self.surface.fill(self.background_color)
        
        # Рамка клавиатуры
        outer_rect = pygame.Rect(0, 0, self.width, self.height - 20)
        pygame.draw.rect(self.surface, self.frame_color, outer_rect)
        pygame.draw.rect(self.surface, self.border_color, outer_rect, 3)
        
        # Внутренняя область
        inner_rect = pygame.Rect(
            self.frame_thickness, 
            self.frame_thickness, 
            self.width - self.frame_thickness * 2, 
            self.height - self.frame_thickness * 2 - 20
        )
        pygame.draw.rect(self.surface, [35, 35, 35], inner_rect)
        
        # Рисуем клавиши
        for row in range(len(self.layout)):
            for col in range(len(self.layout[row])):
                key = self.layout[row][col]
                if key == '':  # Пропускаем пустые
                    continue
                key_rect = self.get_key_rect(row, col)
                if key_rect:
                    self._draw_key(key, key_rect)
        
        # Лейбл клавиатуры
        label_text = self.small_font.render("KEYBOARD", True, [150, 150, 150])
        label_rect = label_text.get_rect()
        label_rect.centerx = self.width // 2
        label_rect.y = self.height - 18
        self.surface.blit(label_text, label_rect)
    
    def _draw_key(self, key, key_rect):
        """Рисует отдельную клавишу"""
        # Определяем цвет клавиши
        if key in self.pressed_keys:
            color = self.key_pressed_color
            text_color = [255, 255, 255]
            border_color = [0, 255, 100]
        elif key in ['UP', 'DN', 'LT', 'RT']:
            color = self.arrow_key_color
            text_color = self.key_text_color
            border_color = [120, 120, 120]
        elif key in ['SPACE', 'ENT', 'BS']:
            color = self.special_key_color
            text_color = self.key_text_color
            border_color = [120, 120, 120]
        else:
            color = self.key_color
            text_color = self.key_text_color
            border_color = [80, 80, 80]
        
        # Рисуем клавишу
        pygame.draw.rect(self.surface, color, key_rect)
        
        # 3D эффект
        if key not in self.pressed_keys:
            # Светлые линии
            pygame.draw.line(self.surface, [min(255, c + 30) for c in color], 
                           key_rect.topleft, key_rect.topright, 1)
            pygame.draw.line(self.surface, [min(255, c + 30) for c in color], 
                           key_rect.topleft, key_rect.bottomleft, 1)
            # Темные линии
            pygame.draw.line(self.surface, [max(0, c - 30) for c in color], 
                           key_rect.bottomleft, key_rect.bottomright, 1)
            pygame.draw.line(self.surface, [max(0, c - 30) for c in color], 
                           key_rect.topright, key_rect.bottomright, 1)
        
        # Рамка
        pygame.draw.rect(self.surface, border_color, key_rect, 1)
        
        # Текст клавиши
        self._draw_key_text(key, key_rect, text_color)
    
    def _draw_key_text(self, key, key_rect, text_color):
        """Рисует текст на клавише"""
        # Используем только текстовые представления
        display_text = key
        
        # Выбираем размер шрифта в зависимости от длины текста
        if len(key) > 2:
            text_surface = self.small_font.render(display_text, True, text_color)
        else:
            text_surface = self.font.render(display_text, True, text_color)
        
        text_rect = text_surface.get_rect(center=key_rect.center)
        
        # Проверяем, помещается ли текст
        if text_surface.get_width() > key_rect.width - 4:
            small_text_surface = self.small_font.render(display_text, True, text_color)
            text_rect = small_text_surface.get_rect(center=key_rect.center)
            self.surface.blit(small_text_surface, text_rect)
        else:
            self.surface.blit(text_surface, text_rect)
    
    def device_in(self, value):
        """Получает команды от процессора"""
        self._last_command = value
        
        if value == 0x01:
            self.key_buffer.clear()
            print("Keyboard: буфер очищен")
        elif value == 0x02:
            print(f"Keyboard: размер буфера {len(self.key_buffer)}")
        elif value == 0x4e:
            print(f"Keyboard: запрос серийного номера")
        else:
            print(f"Keyboard: неизвестная команда 0x{value:02X}")
    
    def device_out(self):
        """Отправляет данные процессору"""
        if hasattr(self, '_last_command') and self._last_command == 0x4e:
            self._last_command = None
            print(f"Keyboard: отправлен серийный номер 0x{self.serial_number:02X}")
            return self.serial_number
        else:
            if self.key_buffer:
                char_code = self.key_buffer.popleft()
                if 200 <= char_code <= 203:
                    arrows = {200: 'UP', 201: 'DN', 202: 'LT', 203: 'RT'}
                    print(f"Keyboard: отправлена стрелка {arrows[char_code]} (код {char_code})")
                else:
                    print(f"Keyboard: отправлен символ {char_code} ('{chr(char_code) if 32 <= char_code <= 126 else '?'}')")
                return char_code
            else:
                return 0
    
    def get_buffer_size(self):
        return len(self.key_buffer)
    
    def peek_buffer(self):
        return list(self.key_buffer)
    
    def get_serial_number(self):
        return self.serial_number
