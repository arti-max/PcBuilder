import pygame
from api.Device import Device

class Led(Device):
    def __init__(self, canvas):
        super().__init__(canvas, "Led")
        self.state = False  # Включен/выключен
        self.color_on = self.config.get("color_on", [255, 0, 0])  # Красный
        self.color_off = self.config.get("color_off", [64, 0, 0])  # Темно-красный
        
    def get_default_config(self):
        """Конфигурация по умолчанию для LED"""
        config = super().get_default_config()
        config.update({
            "x": 764,
            "y": 564,
            "color_on": [255, 0, 0],
            "color_off": [64, 0, 0],
            "width": 30,
            "height": 30
        })
        return config
    
    def update(self):
        """Обновляет состояние LED"""
        # LED не требует постоянного обновления
        pass
    
    def draw(self):
        """Рисует LED"""
        color = self.color_on if self.state else self.color_off
        self.surface.fill((32, 32, 32))  # Черный фон
        
        # Рисуем круглый LED
        center = (self.width // 2, self.height // 2)
        radius = min(self.width, self.height) // 2 - 2
        pygame.draw.circle(self.surface, color, center, radius)
        
        # Рисуем границу
        pygame.draw.circle(self.surface, [128, 128, 128], center, radius, 2)
    
    def handle_click(self, local_x, local_y):
        """Переключает LED при клике"""
        self.state = not self.state
        print(f"LED {'включен' if self.state else 'выключен'}")
    
    def device_in(self, value):
        """Получает команду от процессора"""
        self.state = bool(value & 0x01)  # Младший бит определяет состояние
        #print(f"LED получил команду: {value}, состояние: {'включен' if self.state else 'выключен'}")
    
    def device_out(self):
        """Отправляет состояние процессору"""
        return 0x01 if self.state else 0x00
