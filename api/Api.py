import pygame
import json
import os
from api.Device import Device

class DeviceManager:
    def __init__(self, canvas):
        self.canvas = canvas
        self.devices = {}  # port -> device instance
        self.device_classes = {}  # device_name -> device class
        self.ports_config = self.load_ports_config()
        
    def load_ports_config(self):
        """Загружает конфигурацию портов"""
        config_path = "devices/ports.json"
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Создаем базовый конфиг портов
            default_ports = {
                "1": None,
                "2": None,
                "3": None,
                "4": None,
                "5": None
            }
            self.save_ports_config(default_ports)
            return default_ports
    
    def save_ports_config(self, config=None):
        """Сохраняет конфигурацию портов"""
        if config is None:
            config = self.ports_config
        
        os.makedirs("devices", exist_ok=True)
        with open("devices/ports.json", 'w') as f:
            json.dump(config, f, indent=4)
    
    def register_device_class(self, device_name, device_class):
        """Регистрирует класс устройства"""
        self.device_classes[device_name] = device_class
    
    def connect_device(self, port, device_name):
        """Подключает устройство к порту"""
        if device_name not in self.device_classes:
            raise ValueError(f"Неизвестное устройство: {device_name}")
        
        # Создаем экземпляр устройства
        device_class = self.device_classes[device_name]
        device = device_class(self.canvas)
        
        # Подключаем к порту
        self.devices[port] = device
        self.ports_config[str(port)] = device_name
        self.save_ports_config()
        
        print(f"Устройство {device_name} подключено к порту {port}")
    
    def disconnect_device(self, port):
        """Отключает устройство от порта"""
        if port in self.devices:
            del self.devices[port]
        self.ports_config[str(port)] = None
        self.save_ports_config()
    
    def get_device(self, port):
        """Возвращает устройство по порту"""
        return self.devices.get(port)
    
    def update_all(self):
        """Обновляет все устройства"""
        for device in self.devices.values():
            device.update()
    
    def draw_all(self):
        """Рисует все устройства"""
        for device in self.devices.values():
            device.render_to_canvas()
    
    def handle_click(self, mouse_pos):
        """Обрабатывает клики по устройствам"""
        for device in self.devices.values():
            device.on_click(mouse_pos)
    
    def handle_key_down(self, event):
        """Обрабатывает нажатие клавиши для всех устройств"""
        for device in self.devices.values():
            if device.accepts_keyboard_input:
                device.on_key_down(event)
    
    def handle_key_up(self, event):
        """Обрабатывает отпускание клавиши для всех устройств"""
        for device in self.devices.values():
            if device.accepts_keyboard_input:
                device.on_key_up(event)
    
    def device_in(self, port, value):
        """Отправляет данные устройству (out инструкция процессора)"""
        device = self.get_device(port)
        if device:
            device.device_in(value)
        else:
            print(f"Нет устройства на порту {port}")
    
    def device_out(self, port):
        """Получает данные от устройства (in инструкция процессора)"""
        device = self.get_device(port)
        if device:
            return device.device_out()
        else:
            print(f"Нет устройства на порту {port}")
            return 0

def auto_discover_devices():
    """Автоматически находит и регистрирует устройства"""
    devices_dir = "devices"
    if not os.path.exists(devices_dir):
        return {}
    
    discovered = {}
    
    for filename in os.listdir(devices_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            device_name = filename[:-3]  # убираем .py
            try:
                # Динамически импортируем модуль
                module = __import__(f"devices.{device_name}", fromlist=[device_name])
                device_class = getattr(module, device_name)
                
                # Проверяем, что это наследник Device
                if issubclass(device_class, Device):
                    discovered[device_name] = device_class
                    print(f"Найдено устройство: {device_name}")
            except (ImportError, AttributeError) as e:
                print(f"Ошибка загрузки устройства {device_name}: {e}")
    
    return discovered
