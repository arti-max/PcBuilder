import pygame
import json
import os
from abc import ABC, abstractmethod

class Device(ABC):
    def __init__(self, canvas, device_name):
        self.canvas = canvas
        self.device_name = device_name
        self.config = self.load_config()
        self.x = self.config.get("x", 0)
        self.y = self.config.get("y", 0)
        self.width = self.config.get("width", 50)
        self.height = self.config.get("height", 50)
        self.visible = self.config.get("visible", True)
        
        # Поддержка клавиатурного ввода
        self.accepts_keyboard_input = self.config.get("accepts_keyboard_input", False)
        
        # Создаем поверхность для рисования устройства
        self.surface = pygame.Surface((self.width, self.height))
        
    def load_config(self):
        """Загружает конфигурацию устройства"""
        config_path = f"devices/config/{self.device_name}.json"
        
        # Создаем папку config если её нет
        os.makedirs("devices/config", exist_ok=True)
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Создаем базовый конфиг
            default_config = self.get_default_config()
            self.save_config(default_config)
            return default_config
    
    def get_default_config(self):
        """Возвращает конфигурацию по умолчанию"""
        return {
            "x": 0,
            "y": 0,
            "width": 50,
            "height": 50,
            "visible": True,
            "accepts_keyboard_input": False
        }
    
    def save_config(self, config=None):
        """Сохраняет конфигурацию устройства"""
        if config is None:
            config = self.config
        
        config_path = f"devices/config/{self.device_name}.json"
        os.makedirs("devices/config", exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
    
    def update_config(self, key, value, save=True):
        """Обновляет значение в конфигурации"""
        self.config[key] = value
        if save:
            self.save_config()
    
    def get_rect(self):
        """Возвращает прямоугольник устройства"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    @abstractmethod
    def update(self):
        """Обновляет состояние устройства"""
        pass
    
    @abstractmethod
    def draw(self):
        """Рисует устройство на своей поверхности"""
        pass
    
    def render_to_canvas(self):
        """Отрисовывает устройство на канвасе"""
        if self.visible:
            self.draw()
            self.canvas.blit(self.surface, (self.x, self.y))
    
    def on_click(self, mouse_pos):
        """Обрабатывает клик мыши"""
        rect = self.get_rect()
        if rect.collidepoint(mouse_pos):
            self.handle_click(mouse_pos[0] - self.x, mouse_pos[1] - self.y)
    
    def handle_click(self, local_x, local_y):
        """Обрабатывает клик внутри устройства (переопределяется в наследниках)"""
        pass
    
    # Новые методы для клавиатурного ввода
    def on_key_down(self, event):
        """Обрабатывает нажатие клавиши (переопределяется в наследниках)"""
        if self.accepts_keyboard_input:
            self.handle_key_down(event)
    
    def on_key_up(self, event):
        """Обрабатывает отпускание клавиши (переопределяется в наследниках)"""
        if self.accepts_keyboard_input:
            self.handle_key_up(event)
    
    def handle_key_down(self, event):
        """Переопределяется в наследниках для обработки нажатия клавиши"""
        pass
    
    def handle_key_up(self, event):
        """Переопределяется в наследниках для обработки отпускания клавиши"""
        pass
    
    @abstractmethod
    def device_in(self, value):
        """Получает данные от процессора (out инструкция)"""
        pass
    
    @abstractmethod
    def device_out(self):
        """Отправляет данные процессору (in инструкция)"""
        pass
