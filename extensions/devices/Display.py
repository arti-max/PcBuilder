import pygame
import time
from api.Device import Device

class Display(Device):
    def __init__(self, canvas):
        super().__init__(canvas, "Display")
        
        # Параметры дисплея (увеличенные)
        self.display_width = 32
        self.display_height = 32
        self.pixel_size = self.config.get("pixel_size", 16)
        self.gap_size = self.config.get("gap_size", 2)
        
        # ИСПРАВЛЕННЫЕ цвета для лучшей видимости
        self.pixel_on_color = self.config.get("pixel_on_color", [0, 255, 80])     # Яркий зеленый
        self.pixel_off_color = self.config.get("pixel_off_color", [0, 60, 30])   # ВИДИМЫЙ темно-зеленый
        self.background_color = self.config.get("background_color", [10, 10, 10]) # Почти черный
        self.border_color = self.config.get("border_color", [50, 100, 50])
        self.scan_color = self.config.get("scan_color", [0, 150, 255])
        self.frame_color = self.config.get("frame_color", [20, 60, 20])
        
        # Размеры дисплея
        self.display_area_width = (self.pixel_size + self.gap_size) * self.display_width + self.gap_size
        self.display_area_height = (self.pixel_size + self.gap_size) * self.display_height + self.gap_size
        
        # Кнопки
        self.button_width = 80
        self.button_height = 40
        self.button_gap = 10
        
        # Общие размеры устройства
        self.frame_thickness = 8
        self.total_width = self.display_area_width + self.button_width + self.button_gap * 3 + self.frame_thickness * 2
        self.total_height = max(self.display_area_height, (self.button_height + self.button_gap) * 3) + self.frame_thickness * 2
        
        self.width = self.total_width
        self.height = self.total_height
        self.surface = pygame.Surface((self.width, self.height))
        
        # Буферы пикселей
        self.pixel_buffer = [[0 for _ in range(self.display_width)] for _ in range(self.display_height)]
        self.displayed_buffer = [[0 for _ in range(self.display_width)] for _ in range(self.display_height)]
        self.update_state = [[0 for _ in range(self.display_width)] for _ in range(self.display_height)]
        
        # ИСПРАВЛЕННАЯ система обновления - убираем мерцание
        self.scan_mode = self.config.get("scan_mode", "line_scan")
        self.refresh_modes = {
            "instant": {"rate": 0, "method": self._update_instant},
            "line_scan": {"rate": 0.01, "method": self._update_line_scan},
            "block_scan": {"rate": 0.08, "method": self._update_block_scan},
            "column_scan": {"rate": 0.05, "method": self._update_column_scan},
            "quad_scan": {"rate": 0.15, "method": self._update_quad_scan},
            "pixel_scan": {"rate": 0.005, "method": self._update_pixel_scan}
        }
        
        self.current_mode = self.refresh_modes[self.scan_mode]
        self.last_refresh_time = time.time()
        self.last_fade_time = time.time()
        
        # Состояние сканирования
        self.scan_position = 0
        self.scan_complete = True
        
        # Входящие данные
        self.input_mode = "idle"
        self.temp_x = 0
        self.temp_y = 0
        
        # Оптимизация отрисовки
        self.dirty_rects = []
        self.need_full_redraw = True
        
        # Кнопки состояние
        self.button_states = {
            "reset": False,
            "invert": False
        }
        self.button_press_times = {}
        
        # ИСПРАВЛЕННЫЕ предварительно созданные поверхности
        self.pixel_surfaces = self._create_pixel_surfaces()
        
        # Шрифт для кнопок
        pygame.font.init()
        self.button_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 16)
        
    def _create_pixel_surfaces(self):
        """ИСПРАВЛЕННАЯ версия - создает простые, но видимые пиксели"""
        surfaces = {}
        
        # Простые прямоугольные пиксели без сложного градиента
        surfaces['on'] = pygame.Surface((self.pixel_size, self.pixel_size))
        surfaces['on'].fill(self.pixel_on_color)
        pygame.draw.rect(surfaces['on'], [c//3 for c in self.pixel_on_color], 
                        (0, 0, self.pixel_size, self.pixel_size), 1)
        
        surfaces['off'] = pygame.Surface((self.pixel_size, self.pixel_size))
        surfaces['off'].fill(self.pixel_off_color)  # Темно-зеленый, но ВИДИМЫЙ
        pygame.draw.rect(surfaces['off'], [c//2 for c in self.pixel_off_color], 
                        (0, 0, self.pixel_size, self.pixel_size), 1)
        
        # Пиксели в процессе обновления (слегка ярче)
        bright_on = [min(255, c + 30) for c in self.pixel_on_color]
        bright_off = [min(255, c + 10) for c in self.pixel_off_color]
        
        surfaces['on_updating'] = pygame.Surface((self.pixel_size, self.pixel_size))
        surfaces['on_updating'].fill(bright_on)
        # pygame.draw.rect(surfaces['on_updating'], [50, 100, 50], 
        #                 (0, 0, self.pixel_size, self.pixel_size), 2)  # Белая рамка
        
        surfaces['off_updating'] = pygame.Surface((self.pixel_size, self.pixel_size))
        surfaces['off_updating'].fill(bright_off)
        # pygame.draw.rect(surfaces['off_updating'], [50, 100, 50], 
        #                 (0, 0, self.pixel_size, self.pixel_size), 2)  # Белая рамка
        
        # Недавно обновленные пиксели (слегка подсвечены)
        fade_on = [min(255, c + 10) for c in self.pixel_on_color]
        fade_off = [min(255, c + 5) for c in self.pixel_off_color]
        
        surfaces['on_recent'] = pygame.Surface((self.pixel_size, self.pixel_size))
        surfaces['on_recent'].fill(fade_on)
        # pygame.draw.rect(surfaces['on_recent'], [100, 200, 100], 
        #                 (0, 0, self.pixel_size, self.pixel_size), 1)
        
        surfaces['off_recent'] = pygame.Surface((self.pixel_size, self.pixel_size))
        surfaces['off_recent'].fill(fade_off)
        # pygame.draw.rect(surfaces['off_recent'], [50, 150, 50], 
        #                 (0, 0, self.pixel_size, self.pixel_size), 1)
        
        return surfaces
    
    def get_default_config(self):
        config = super().get_default_config()
        config.update({
            "pixel_size": 16,
            "gap_size": 2,
            "pixel_on_color": [0, 255, 80],
            "pixel_off_color": [0, 80, 30],
            "background_color": [10, 10, 10],
            "border_color": [100, 100, 100],
            "scan_color": [0, 150, 255],
            "frame_color": [60, 60, 60],
            "scan_mode": "line_scan",
            "width": 400,
            "height": 320,
            "x": 30,
            "y": 10,
            "serial_number": 0x4f
        })
        return config
    
    def get_button_rect(self, button_name):
        """Возвращает прямоугольник кнопки"""
        button_x = self.frame_thickness + self.display_area_width + self.button_gap
        
        if button_name == "reset":
            button_y = self.frame_thickness + self.button_gap
        elif button_name == "invert":
            button_y = self.frame_thickness + self.button_gap * 2 + self.button_height
        else:
            return None
            
        return pygame.Rect(button_x, button_y, self.button_width, self.button_height)
    
    def handle_click(self, local_x, local_y):
        """Обрабатывает клик по дисплею или кнопкам"""
        # Проверяем клики по кнопкам
        reset_rect = self.get_button_rect("reset")
        invert_rect = self.get_button_rect("invert")
        
        if reset_rect and reset_rect.collidepoint(local_x, local_y):
            self.press_button("reset")
            return
        
        if invert_rect and invert_rect.collidepoint(local_x, local_y):
            self.press_button("invert")
            return
        
        # Для отладки - клик по пикселю
        display_x = local_x - self.frame_thickness - self.gap_size
        display_y = local_y - self.frame_thickness - self.gap_size
        
        if display_x >= 0 and display_y >= 0:
            click_x = display_x // (self.pixel_size + self.gap_size)
            click_y = display_y // (self.pixel_size + self.gap_size)
            
            if 0 <= click_x < self.display_width and 0 <= click_y < self.display_height:
                self.pixel_buffer[click_y][click_x] = 1 - self.pixel_buffer[click_y][click_x]
                print(f"Пиксель ({click_x}, {click_y}) {'включен' if self.pixel_buffer[click_y][click_x] else 'выключен'}")
    
    def press_button(self, button_name):
        """Нажатие кнопки"""
        self.button_states[button_name] = True
        self.button_press_times[button_name] = time.time()
        
        if button_name == "reset":
            self.reset_display()
            print("Display: RESET - экран очищен")
        elif button_name == "invert":
            self.invert_display()
            print("Display: INVERT - экран инвертирован")
    
    def reset_display(self):
        """Очищает дисплей"""
        for y in range(self.display_height):
            for x in range(self.display_width):
                self.pixel_buffer[y][x] = 0
        self.need_full_redraw = True
    
    def invert_display(self):
        """Инвертирует все пиксели дисплея"""
        for y in range(self.display_height):
            for x in range(self.display_width):
                self.pixel_buffer[y][x] = 1 - self.pixel_buffer[y][x]
        self.need_full_redraw = True
    
    def _draw_button(self, button_name, rect):
        """Рисует кнопку"""
        if self.button_states.get(button_name, False):
            button_color = [100, 100, 150]
            text_color = [255, 255, 255]
            border_color = [150, 150, 200]
        else:
            button_color = [70, 70, 70]
            text_color = [200, 200, 200]
            border_color = [120, 120, 120]
        
        pygame.draw.rect(self.surface, button_color, rect)
        pygame.draw.rect(self.surface, border_color, rect, 2)
        
        text = self.button_font.render(button_name.upper(), True, text_color)
        text_rect = text.get_rect(center=rect.center)
        self.surface.blit(text, text_rect)
    
    def update(self):
        """ИСПРАВЛЕННАЯ версия обновления - убираем лишнее мерцание"""
        current_time = time.time()
        refresh_rate = self.current_mode["rate"]
        
        if refresh_rate == 0 or current_time - self.last_refresh_time >= refresh_rate:
            self.last_refresh_time = current_time
            
            if self.scan_complete:
                self.scan_complete = False
                self.scan_position = 0
            
            self.current_mode["method"]()
        
        if current_time - self.last_fade_time >= 0.3:
            self.last_fade_time = current_time
            self._fade_update_effects()
        
        buttons_to_release = []
        for button_name, press_time in self.button_press_times.items():
            if current_time - press_time > 0.2:
                buttons_to_release.append(button_name)
        
        for button_name in buttons_to_release:
            self.button_states[button_name] = False
            del self.button_press_times[button_name]
    
    def draw(self):
        """ИСПРАВЛЕННАЯ отрисовка"""
        self.surface.fill([40, 40, 40])
        
        outer_rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(self.surface, self.frame_color, outer_rect)
        pygame.draw.rect(self.surface, [100, 100, 100], outer_rect, 3)
        
        display_rect = pygame.Rect(
            self.frame_thickness - 2, 
            self.frame_thickness - 2, 
            self.display_area_width + 4, 
            self.display_area_height + 4
        )
        pygame.draw.rect(self.surface, [80, 80, 80], display_rect)
        pygame.draw.rect(self.surface, self.border_color, display_rect, 2)
        
        display_inner_rect = pygame.Rect(
            self.frame_thickness, 
            self.frame_thickness, 
            self.display_area_width, 
            self.display_area_height
        )
        pygame.draw.rect(self.surface, self.background_color, display_inner_rect)
        
        for y in range(self.display_height):
            for x in range(self.display_width):
                self._draw_pixel(x, y)
        
        self.need_full_redraw = False
        self.dirty_rects.clear()
        
        reset_rect = self.get_button_rect("reset")
        invert_rect = self.get_button_rect("invert")
        
        if reset_rect:
            self._draw_button("reset", reset_rect)
        if invert_rect:
            self._draw_button("invert", invert_rect)
        
        label_text = self.small_font.render("16x16 DISPLAY", True, [150, 150, 150])
        label_rect = label_text.get_rect()
        label_rect.centerx = self.frame_thickness + self.display_area_width // 2
        label_rect.y = self.height - 20
        self.surface.blit(label_text, label_rect)
        
        mode_text = self.small_font.render(f"MODE: {self.scan_mode.upper()}", True, [120, 120, 120])
        mode_rect = mode_text.get_rect()
        mode_rect.x = self.frame_thickness + self.display_area_width + self.button_gap
        mode_rect.y = self.height - 40
        self.surface.blit(mode_text, mode_rect)
    
    def _draw_pixel(self, x, y):
        """ИСПРАВЛЕННАЯ отрисовка пикселя"""
        pixel_x = self.frame_thickness + self.gap_size + x * (self.pixel_size + self.gap_size)
        pixel_y = self.frame_thickness + self.gap_size + y * (self.pixel_size + self.gap_size)
        
        pixel_value = self.displayed_buffer[y][x]
        update_state = self.update_state[y][x]
        
        if update_state == 1:
            surface_key = 'on_updating' if pixel_value else 'off_updating'
        elif update_state == 2:
            surface_key = 'on_recent' if pixel_value else 'off_recent'
        else:
            surface_key = 'on' if pixel_value else 'off'
        
        surface = self.pixel_surfaces[surface_key]
        self.surface.blit(surface, (pixel_x, pixel_y))
    
    def _mark_updating(self, pixels):
        """Отмечает пиксели как обновляющиеся"""
        for x, y in pixels:
            if 0 <= x < self.display_width and 0 <= y < self.display_height:
                self.update_state[y][x] = 1
    
    def _fade_update_effects(self):
        """МЯГКОЕ затухание эффектов обновления"""
        for y in range(self.display_height):
            for x in range(self.display_width):
                if self.update_state[y][x] == 1:
                    self.update_state[y][x] = 2
                elif self.update_state[y][x] == 2:
                    self.update_state[y][x] = 0
    
    def _update_instant(self):
        updating_pixels = []
        for y in range(self.display_height):
            for x in range(self.display_width):
                if self.displayed_buffer[y][x] != self.pixel_buffer[y][x]:
                    self.displayed_buffer[y][x] = self.pixel_buffer[y][x]
                    updating_pixels.append((x, y))
        if updating_pixels:
            self._mark_updating(updating_pixels)
        self.scan_complete = True
        return True
    
    def _update_line_scan(self):
        if self.scan_position >= self.display_height:
            self.scan_position = 0
            self.scan_complete = True
            return True
        
        y = self.scan_position
        updating_pixels = [(x, y) for x in range(self.display_width)]
        self._mark_updating(updating_pixels)
        
        changed_pixels = []
        for x in range(self.display_width):
            if self.displayed_buffer[y][x] != self.pixel_buffer[y][x]:
                self.displayed_buffer[y][x] = self.pixel_buffer[y][x]
                changed_pixels.append((x, y))
        
        self.scan_position += 1
        return len(changed_pixels) > 0
    
    def _update_column_scan(self):
        if self.scan_position >= self.display_width:
            self.scan_position = 0
            self.scan_complete = True
            return True
        
        x = self.scan_position
        updating_pixels = [(x, y) for y in range(self.display_height)]
        self._mark_updating(updating_pixels)
        
        changed_pixels = []
        for y in range(self.display_height):
            if self.displayed_buffer[y][x] != self.pixel_buffer[y][x]:
                self.displayed_buffer[y][x] = self.pixel_buffer[y][x]
                changed_pixels.append((x, y))
        
        self.scan_position += 1
        return len(changed_pixels) > 0
    
    def _update_block_scan(self):
        blocks_per_row = (self.display_width + 3) // 4
        total_blocks = blocks_per_row * ((self.display_height + 3) // 4)
        
        if self.scan_position >= total_blocks:
            self.scan_position = 0
            self.scan_complete = True
            return True
        
        block_x = (self.scan_position % blocks_per_row) * 4
        block_y = (self.scan_position // blocks_per_row) * 4
        
        updating_pixels = []
        for dy in range(4):
            for dx in range(4):
                x, y = block_x + dx, block_y + dy
                if x < self.display_width and y < self.display_height:
                    updating_pixels.append((x, y))
        
        self._mark_updating(updating_pixels)
        
        changed_pixels = []
        for dy in range(4):
            for dx in range(4):
                x, y = block_x + dx, block_y + dy
                if x < self.display_width and y < self.display_height:
                    if self.displayed_buffer[y][x] != self.pixel_buffer[y][x]:
                        self.displayed_buffer[y][x] = self.pixel_buffer[y][x]
                        changed_pixels.append((x, y))
        
        self.scan_position += 1
        return len(changed_pixels) > 0
    
    def _update_quad_scan(self):
        quadrants = [(0, 0, 8, 8), (8, 0, 8, 8), (0, 8, 8, 8), (8, 8, 8, 8)]
        if self.scan_position >= len(quadrants):
            self.scan_position = 0
            self.scan_complete = True
            return True
        
        start_x, start_y, width, height = quadrants[self.scan_position]
        updating_pixels = []
        
        for y in range(start_y, min(start_y + height, self.display_height)):
            for x in range(start_x, min(start_x + width, self.display_width)):
                updating_pixels.append((x, y))
        
        self._mark_updating(updating_pixels)
        
        changed_pixels = []
        for y in range(start_y, min(start_y + height, self.display_height)):
            for x in range(start_x, min(start_x + width, self.display_width)):
                if self.displayed_buffer[y][x] != self.pixel_buffer[y][x]:
                    self.displayed_buffer[y][x] = self.pixel_buffer[y][x]
                    changed_pixels.append((x, y))
        
        self.scan_position += 1
        return len(changed_pixels) > 0
    
    def _update_pixel_scan(self):
        if self.scan_position >= self.display_width * self.display_height:
            self.scan_position = 0
            self.scan_complete = True
            return True
        
        x = self.scan_position % self.display_width
        y = self.scan_position // self.display_width
        
        self._mark_updating([(x, y)])
        
        changed = False
        if self.displayed_buffer[y][x] != self.pixel_buffer[y][x]:
            self.displayed_buffer[y][x] = self.pixel_buffer[y][x]
            changed = True
        
        self.scan_position += 1
        return changed
    
    def set_scan_mode(self, mode):
        """Изменяет режим сканирования"""
        if mode in self.refresh_modes:
            self.scan_mode = mode
            self.current_mode = self.refresh_modes[mode]
            self.scan_position = 0
            self.scan_complete = True
            self.update_config("scan_mode", mode)
            
            for y in range(self.display_height):
                for x in range(self.display_width):
                    self.update_state[y][x] = 0
            self.need_full_redraw = True
            
            print(f"Display: режим сканирования '{mode}'")
    
    def device_in(self, value):
        """Получает команды от процессора"""
        self._last_command = value
        
        if self.input_mode == "idle":
            if value == 0x4f:
                print(f"Display: запрос серийного номера")
                return
            elif value == 0xAA:
                self.reset_display()
                print("Display: RESET команда от процессора")
                return
            elif value == 0xBB:
                self.invert_display()
                print("Display: INVERT команда от процессора")
                return
            
            self.temp_x = value & 0x0F
            self.input_mode = "receiving_y"
        elif self.input_mode == "receiving_y":
            self.temp_y = value & 0x0F
            self.input_mode = "receiving_state"
        elif self.input_mode == "receiving_state":
            state = 1 if (value & 0x01) else 0
            if 0 <= self.temp_x < self.display_width and 0 <= self.temp_y < self.display_height:
                self.pixel_buffer[self.temp_y][self.temp_x] = state
            self.input_mode = "idle"
    
    def device_out(self):
        """Отправляет данные процессору"""
        if hasattr(self, '_last_command') and self._last_command == 0x4f:
            self._last_command = None
            serial_number = self.config.get("serial_number", 0x4f)
            print(f"Display: отправлен серийный номер 0x{serial_number:02X}")
            return serial_number
        else:
            return 0
    
    def instant_update(self):
        """Мгновенное обновление всего экрана"""
        old_mode = self.scan_mode
        self.set_scan_mode("instant")
        self.update()
        self.set_scan_mode(old_mode)
        print("Display: принудительное мгновенное обновление")
