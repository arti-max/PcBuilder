import pygame
import os
import time
import threading
import numpy as np
from tkinter import filedialog, messagebox
import tkinter as tk
from datetime import datetime
from api.Device import Device

class TapeFormat:
    """Формат TAPE файла"""
    TAPE_SIZE = 2048  # 2KB максимальный размер
    HEADER_SIZE = 128  # Размер заголовка
    
    @staticmethod
    def create_tape_file(data, metadata):
        """Создает TAPE файл с заголовком и данными"""
        # Создаем заголовок
        header = bytearray(TapeFormat.HEADER_SIZE)
        
        # Магическое число для идентификации TAPE файла
        header[0:4] = b'TAPE'
        
        # Версия формата
        header[4] = 1
        header[5] = 0
        
        # Размер данных (2 байта)
        data_size = len(data)
        header[6] = (data_size >> 8) & 0xFF
        header[7] = data_size & 0xFF
        
        # Время создания (4 байта Unix timestamp)
        timestamp = int(time.time())
        header[8] = (timestamp >> 24) & 0xFF
        header[9] = (timestamp >> 16) & 0xFF
        header[10] = (timestamp >> 8) & 0xFF
        header[11] = timestamp & 0xFF
        
        # Название кассеты (32 байта)
        name = metadata.get('name', 'Untitled')[:31]
        name_bytes = name.encode('utf-8')
        header[12:12+len(name_bytes)] = name_bytes
        
        # Автор (32 байта)
        author = metadata.get('author', 'Unknown')[:31]
        author_bytes = author.encode('utf-8')
        header[44:44+len(author_bytes)] = author_bytes
        
        # Описание (32 байта)
        description = metadata.get('description', '')[:31]
        desc_bytes = description.encode('utf-8')
        header[76:76+len(desc_bytes)] = desc_bytes
        
        # Контрольная сумма заголовка
        checksum = sum(header[:-4]) & 0xFFFF
        header[124] = (checksum >> 8) & 0xFF
        header[125] = checksum & 0xFF
        
        # Создаем полный файл
        tape_data = bytearray(TapeFormat.TAPE_SIZE)
        tape_data[:TapeFormat.HEADER_SIZE] = header
        
        # Копируем данные программы
        data_start = TapeFormat.HEADER_SIZE
        if len(data) > TapeFormat.TAPE_SIZE - TapeFormat.HEADER_SIZE:
            raise ValueError(f"Программа слишком большая: {len(data)} байт, максимум {TapeFormat.TAPE_SIZE - TapeFormat.HEADER_SIZE}")
        
        tape_data[data_start:data_start+len(data)] = data
        
        # Остальное место заполняется нулями (NOP)
        return tape_data
    
    @staticmethod
    def read_tape_file(tape_data):
        """Читает TAPE файл и возвращает заголовок и данные"""
        if len(tape_data) < TapeFormat.HEADER_SIZE:
            raise ValueError("Неверный размер TAPE файла")
        
        header = tape_data[:TapeFormat.HEADER_SIZE]
        
        # Проверяем магическое число
        if header[0:4] != b'TAPE':
            raise ValueError("Не является TAPE файлом")
        
        # Извлекаем информацию из заголовка
        version = (header[4], header[5])
        data_size = (header[6] << 8) | header[7]
        timestamp = (header[8] << 24) | (header[9] << 16) | (header[10] << 8) | header[11]
        
        name = header[12:44].decode('utf-8').rstrip('\x00')
        author = header[44:76].decode('utf-8').rstrip('\x00')
        description = header[76:108].decode('utf-8').rstrip('\x00')
        
        # Проверяем контрольную сумму
        stored_checksum = (header[124] << 8) | header[125]
        calculated_checksum = sum(header[:-4]) & 0xFFFF
        
        if stored_checksum != calculated_checksum:
            print("Предупреждение: Неверная контрольная сумма заголовка")
        
        metadata = {
            'version': version,
            'data_size': data_size,
            'timestamp': timestamp,
            'creation_date': datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            'name': name,
            'author': author,
            'description': description
        }
        
        # Извлекаем данные программы
        data_start = TapeFormat.HEADER_SIZE
        program_data = tape_data[data_start:data_start+data_size] if data_size > 0 else bytearray()
        
        return metadata, program_data

class TapeLoader(Device):
    def __init__(self, canvas):
        super().__init__(canvas, "TapeLoader")
        
        self.serial_number = self.config.get("serial_number", 0x7a)
        
        # Размеры устройства
        self.device_width = self.config.get("device_width", 300)
        self.device_height = self.config.get("device_height", 200)
        self.frame_thickness = 8
        
        self.button_width = 70
        self.button_height = 30
        self.button_gap = 10
        
        self.width = self.device_width
        self.height = self.device_height
        self.surface = pygame.Surface((self.width, self.height))
        
        # Цветовая схема
        self.background_color = self.config.get("background_color", [40, 40, 40])
        self.frame_color = self.config.get("frame_color", [60, 60, 60])
        self.border_color = self.config.get("border_color", [100, 100, 100])
        self.tape_color = self.config.get("tape_color", [139, 69, 19])
        self.reel_color = self.config.get("reel_color", [80, 80, 80])
        self.led_on_color = self.config.get("led_on_color", [255, 0, 0])
        self.led_off_color = self.config.get("led_off_color", [60, 0, 0])
        self.text_color = self.config.get("text_color", [200, 200, 200])
        
        # Состояние кассеты
        self.tape_loaded = False
        self.tape_data = bytearray()
        self.tape_metadata = {}
        self.tape_filename = ""
        self.tape_position = 0
        self.tape_size = 0
        
        # Режимы работы
        self.mode = "STOP"
        self.playing = False
        self.recording = False
        
        # Состояние кнопок
        self.button_states = {
            "load": False,
            "eject": False
        }
        self.button_press_times = {}
        
        # Анимация ленты
        self.reel_rotation = 0
        self.last_animation_time = time.time()
        
        # НОВОЕ: Звуковая система
        self.sound_enabled = self._init_sound()
        self.current_sound = None
        self.sound_thread = None
        self.sound_stop_flag = False
        
        # Шрифты
        pygame.font.init()
        self.font = pygame.font.Font(None, 18)
        self.small_font = pygame.font.Font(None, 14)
        self.large_font = pygame.font.Font(None, 22)
        
    def _init_sound(self):
        """Инициализация звуковой системы"""
        try:
            if not pygame.get_init():
                return False
            
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            if pygame.mixer.get_init() is not None:
                print("TapeLoader: звуковая система инициализирована")
                return True
            else:
                print("TapeLoader: звук недоступен")
                return False
                
        except Exception as e:
            print(f"TapeLoader: ошибка инициализации звука: {e}")
            return False
    
    def generate_tape_sound(self, sound_type, duration=1.0):
        """Генерирует звуки кассетного магнитофона"""
        if not self.sound_enabled or pygame.mixer.get_init() is None:
            return None
        
        try:
            sample_rate = pygame.mixer.get_init()[0]
            frames = int(duration * sample_rate)
            
            # Генерируем разные звуки для разных режимов
            if sound_type == "play":
                # Тихий шум ленты + низкочастотное гудение
                noise = np.random.normal(0, 0.02, frames)  # Белый шум
                tape_hum = 0.05 * np.sin(2 * np.pi * 60 * np.linspace(0, duration, frames))  # 60Hz гудение
                wave_array = noise + tape_hum
                
            elif sound_type == "rewind":
                # Быстрый высокочастотный звук перемотки
                frequency = 1500 + 500 * np.sin(2 * np.pi * 2 * np.linspace(0, duration, frames))
                wave_array = 0.1 * np.sin(2 * np.pi * frequency * np.linspace(0, duration, frames))
                wave_array += np.random.normal(0, 0.05, frames)  # Добавляем шум
                
            elif sound_type == "fast_forward":
                # Средний звук быстрой перемотки
                frequency = 800 + 200 * np.sin(2 * np.pi * 3 * np.linspace(0, duration, frames))
                wave_array = 0.08 * np.sin(2 * np.pi * frequency * np.linspace(0, duration, frames))
                wave_array += np.random.normal(0, 0.03, frames)
                
            elif sound_type == "record":
                # Звук записи - похож на воспроизведение но с дополнительным шумом
                noise = np.random.normal(0, 0.03, frames)
                tape_hum = 0.04 * np.sin(2 * np.pi * 50 * np.linspace(0, duration, frames))
                motor_sound = 0.02 * np.sin(2 * np.pi * 120 * np.linspace(0, duration, frames))
                wave_array = noise + tape_hum + motor_sound
                
            elif sound_type == "load":
                # Звук вставки кассеты - механический клик
                click_envelope = np.exp(-10 * np.linspace(0, duration, frames))
                click_freq = 200 + 1000 * np.exp(-20 * np.linspace(0, duration, frames))
                wave_array = 0.3 * click_envelope * np.sin(2 * np.pi * click_freq * np.linspace(0, duration, frames))
                
            elif sound_type == "eject":
                # Звук извлечения кассеты
                click_envelope = np.exp(-8 * np.linspace(0, duration, frames))
                click_freq = 150 + 800 * np.exp(-15 * np.linspace(0, duration, frames))
                wave_array = 0.25 * click_envelope * np.sin(2 * np.pi * click_freq * np.linspace(0, duration, frames))
                
            else:
                # Тишина
                wave_array = np.zeros(frames)
            
            # Применяем огибающую для избежания щелчков
            fade_frames = int(0.01 * sample_rate)
            if fade_frames > 0 and len(wave_array) > fade_frames * 2:
                wave_array[:fade_frames] *= np.linspace(0, 1, fade_frames)
                wave_array[-fade_frames:] *= np.linspace(1, 0, fade_frames)
            
            # Ограничиваем амплитуду
            wave_array = np.clip(wave_array, -0.5, 0.5)
            
            # Конвертируем в 16-битный формат
            wave_array = (wave_array * 16383).astype(np.int16)
            
            # Создаем стерео звук
            stereo_wave = np.zeros((frames, 2), dtype=np.int16)
            stereo_wave[:, 0] = wave_array
            stereo_wave[:, 1] = wave_array
            
            return pygame.sndarray.make_sound(stereo_wave)
            
        except Exception as e:
            print(f"TapeLoader: ошибка генерации звука: {e}")
            return None
    
    def play_tape_sound(self, sound_type, duration=None):
        """Воспроизводит звук кассетного магнитофона"""
        if not self.sound_enabled:
            return
        
        self.stop_tape_sound()
        
        # Устанавливаем длительность по умолчанию для разных звуков
        if duration is None:
            if sound_type in ["load", "eject"]:
                duration = 0.3
            elif sound_type == "rewind":
                duration = 1.0
            else:
                duration = float('inf')  # Бесконечное воспроизведение для play/record
        
        self.sound_stop_flag = False
        self.sound_thread = threading.Thread(target=self._sound_playback_thread, args=(sound_type, duration))
        self.sound_thread.daemon = True
        self.sound_thread.start()
        
        print(f"TapeLoader: воспроизведение звука '{sound_type}'")
    
    def _sound_playback_thread(self, sound_type, duration):
        """Поток воспроизведения звука"""
        try:
            if duration == float('inf'):
                # Бесконечное воспроизведение для режимов play/record
                while not self.sound_stop_flag:
                    sound = self.generate_tape_sound(sound_type, 2.0)  # 2-секундные циклы
                    if sound and not self.sound_stop_flag:
                        sound.play()
                        time.sleep(2.0)
                    else:
                        break
            else:
                # Одноразовое воспроизведение
                sound = self.generate_tape_sound(sound_type, duration)
                if sound and not self.sound_stop_flag:
                    sound.play()
                    time.sleep(duration)
                    
        except Exception as e:
            print(f"TapeLoader: ошибка воспроизведения звука: {e}")
    
    def stop_tape_sound(self):
        """Останавливает воспроизведение звука"""
        self.sound_stop_flag = True
        
        if self.sound_enabled and pygame.mixer.get_init() is not None:
            try:
                pygame.mixer.stop()
            except:
                pass
        
        if self.sound_thread and self.sound_thread.is_alive():
            self.sound_thread.join(timeout=0.1)
    
    def get_default_config(self):
        config = super().get_default_config()
        config.update({
            "serial_number": 0x7a,
            "device_width": 300,
            "device_height": 200,
            "background_color": [40, 40, 40],
            "frame_color": [60, 60, 60],
            "border_color": [100, 100, 100],
            "tape_color": [139, 69, 19],
            "reel_color": [80, 80, 80],
            "led_on_color": [255, 0, 0],
            "led_off_color": [60, 0, 0],
            "text_color": [200, 200, 200],
            "width": 300,
            "height": 200,
            "x": 470,
            "y": 50
        })
        return config
    
    def get_button_rect(self, button_name):
        button_y = self.height - self.button_height - 15
        
        if button_name == "load":
            button_x = 20
        elif button_name == "eject":
            button_x = 20 + self.button_width + self.button_gap
        else:
            return None
        
        return pygame.Rect(button_x, button_y, self.button_width, self.button_height)
    
    def handle_click(self, local_x, local_y):
        load_rect = self.get_button_rect("load")
        eject_rect = self.get_button_rect("eject")
        
        if load_rect and load_rect.collidepoint(local_x, local_y):
            self.press_button("load")
            return
        
        if eject_rect and eject_rect.collidepoint(local_x, local_y):
            self.press_button("eject")
            return
    
    def press_button(self, button_name):
        self.button_states[button_name] = True
        self.button_press_times[button_name] = time.time()
        
        if button_name == "load":
            self.load_tape()
        elif button_name == "eject":
            self.eject_tape()
    
    def load_tape(self):
        """ОБНОВЛЕНО: Загружает TAPE файл со звуком"""
        if self.tape_loaded:
            print("TapeLoader: кассета уже загружена")
            return
        
        try:
            root = tk.Tk()
            root.withdraw()
            
            filename = filedialog.askopenfilename(
                title="Выберите TAPE файл",
                filetypes=[
                    ("TAPE files", "*.tape"),
                    ("All files", "*.*")
                ]
            )
            
            root.destroy()
            
            if filename:
                # НОВОЕ: Звук вставки кассеты
                self.play_tape_sound("load", 0.3)
                
                with open(filename, 'rb') as f:
                    tape_file_data = f.read()
                
                try:
                    self.tape_metadata, self.tape_data = TapeFormat.read_tape_file(tape_file_data)
                    self.tape_filename = self.tape_metadata['name']
                    self.tape_size = len(self.tape_data)
                    self.tape_position = 0
                    self.tape_loaded = True
                    self.mode = "STOP"
                    self.playing = False
                    self.recording = False
                    
                    print(f"TapeLoader: загружена кассета '{self.tape_filename}'")
                    print(f"Автор: {self.tape_metadata['author']}")
                    print(f"Описание: {self.tape_metadata['description']}")
                    print(f"Дата создания: {self.tape_metadata['creation_date']}")
                    print(f"Размер данных: {self.tape_size} байт")
                    
                except ValueError as e:
                    print(f"TapeLoader: ошибка чтения TAPE файла: {e}")
                    messagebox.showerror("Ошибка", f"Неверный формат TAPE файла:\n{e}")
            
        except Exception as e:
            print(f"TapeLoader: ошибка загрузки кассеты: {e}")
            messagebox.showerror("Ошибка", f"Ошибка загрузки файла:\n{e}")
    
    def eject_tape(self):
        """ОБНОВЛЕНО: Извлекает кассету со звуком"""
        if not self.tape_loaded:
            print("TapeLoader: нет загруженной кассеты")
            return
        
        # Останавливаем воспроизведение
        self.stop_tape_sound()
        
        # Сохраняем изменения
        if self.tape_data and self.tape_filename:
            try:
                root = tk.Tk()
                root.withdraw()
                
                save = messagebox.askyesno(
                    "Сохранить изменения?",
                    f"Сохранить изменения в кассете '{self.tape_filename}'?"
                )
                
                if save:
                    save_path = filedialog.asksaveasfilename(
                        title="Сохранить кассету как",
                        defaultextension=".tape",
                        filetypes=[("TAPE files", "*.tape")]
                    )
                    
                    if save_path:
                        self.tape_metadata['data_size'] = len(self.tape_data)
                        tape_file_data = TapeFormat.create_tape_file(self.tape_data, self.tape_metadata)
                        
                        with open(save_path, 'wb') as f:
                            f.write(tape_file_data)
                        print(f"TapeLoader: кассета сохранена как '{save_path}'")
                
                root.destroy()
                
            except Exception as e:
                print(f"TapeLoader: ошибка сохранения: {e}")
        
        # НОВОЕ: Звук извлечения кассеты
        self.play_tape_sound("eject", 0.3)
        
        # Очищаем состояние
        self.tape_data = bytearray()
        self.tape_metadata = {}
        self.tape_filename = ""
        self.tape_size = 0
        self.tape_position = 0
        self.tape_loaded = False
        self.mode = "STOP"
        self.playing = False
        self.recording = False
        
        print("TapeLoader: кассета извлечена")
    
    def update(self):
        """Обновляет состояние загрузчика"""
        current_time = time.time()
        
        # Обновление состояния кнопок
        buttons_to_release = []
        for button_name, press_time in self.button_press_times.items():
            if current_time - press_time > 0.2:
                buttons_to_release.append(button_name)
        
        for button_name in buttons_to_release:
            self.button_states[button_name] = False
            del self.button_press_times[button_name]
        
        # Анимация вращения катушек
        if self.tape_loaded and self.mode in ["PLAY", "RECORD", "REWIND", "FAST_FORWARD"]:
            if current_time - self.last_animation_time >= 0.1:
                if self.mode == "REWIND":
                    self.reel_rotation -= 30
                else:
                    self.reel_rotation += 15
                
                if self.reel_rotation >= 360:
                    self.reel_rotation = 0
                elif self.reel_rotation < 0:
                    self.reel_rotation = 360
                    
                self.last_animation_time = current_time
    
    def draw(self):
        """Рисует загрузчик кассет"""
        # Фон
        self.surface.fill(self.background_color)
        
        # Внешняя рамка
        outer_rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(self.surface, self.frame_color, outer_rect)
        pygame.draw.rect(self.surface, self.border_color, outer_rect, 3)
        
        # Внутренняя область
        inner_rect = pygame.Rect(
            self.frame_thickness,
            self.frame_thickness,
            self.width - self.frame_thickness * 2,
            self.height - self.frame_thickness * 2
        )
        pygame.draw.rect(self.surface, [35, 35, 35], inner_rect)
        
        # Рисуем кассетный отсек
        self._draw_tape_compartment()
        
        # Рисуем индикаторы
        self._draw_indicators()
        
        # Рисуем кнопки
        self._draw_buttons()
        
        # Лейбл устройства
        label_text = self.small_font.render("TAPE LOADER", True, [150, 150, 150])
        label_rect = label_text.get_rect()
        label_rect.centerx = self.width // 2
        label_rect.bottom = self.height - 3
        self.surface.blit(label_text, label_rect)
    
    def _draw_tape_compartment(self):
        """Рисует отсек для кассеты"""
        compartment_rect = pygame.Rect(
            self.frame_thickness + 10,
            self.frame_thickness + 10,
            self.width - self.frame_thickness * 2 - 20,
            70
        )
        
        # Фон отсека
        pygame.draw.rect(self.surface, [25, 25, 25], compartment_rect)
        pygame.draw.rect(self.surface, [80, 80, 80], compartment_rect, 2)
        
        if self.tape_loaded:
            self._draw_cassette(compartment_rect)
        else:
            empty_text = self.font.render("NO TAPE", True, [100, 100, 100])
            empty_rect = empty_text.get_rect(center=compartment_rect.center)
            self.surface.blit(empty_text, empty_rect)
    
    def _draw_cassette(self, compartment_rect):
        """Рисует кассету"""
        cassette_rect = pygame.Rect(
            compartment_rect.x + 8,
            compartment_rect.y + 8,
            compartment_rect.width - 16,
            compartment_rect.height - 16
        )
        
        # Корпус кассеты
        pygame.draw.rect(self.surface, [60, 60, 60], cassette_rect)
        pygame.draw.rect(self.surface, [100, 100, 100], cassette_rect, 1)
        
        # Катушки
        reel_radius = 12
        left_reel_center = (cassette_rect.x + 25, cassette_rect.center[1])
        right_reel_center = (cassette_rect.right - 25, cassette_rect.center[1])
        
        # Левая катушка
        pygame.draw.circle(self.surface, self.reel_color, left_reel_center, reel_radius)
        pygame.draw.circle(self.surface, [120, 120, 120], left_reel_center, reel_radius, 2)
        
        # Правая катушка
        pygame.draw.circle(self.surface, self.reel_color, right_reel_center, reel_radius)
        pygame.draw.circle(self.surface, [120, 120, 120], right_reel_center, reel_radius, 2)
        
        # Лента между катушками
        tape_rect = pygame.Rect(
            left_reel_center[0] + reel_radius,
            left_reel_center[1] - 2,
            right_reel_center[0] - left_reel_center[0] - reel_radius * 2,
            4
        )
        pygame.draw.rect(self.surface, self.tape_color, tape_rect)
        
        # Анимация вращения
        if self.mode in ["PLAY", "RECORD", "REWIND", "FAST_FORWARD"]:
            import math
            for i in range(4):
                angle = math.radians(self.reel_rotation + i * 90)
                start_x = left_reel_center[0] + math.cos(angle) * 6
                start_y = left_reel_center[1] + math.sin(angle) * 6
                end_x = left_reel_center[0] + math.cos(angle) * 10
                end_y = left_reel_center[1] + math.sin(angle) * 10
                pygame.draw.line(self.surface, [150, 150, 150], (start_x, start_y), (end_x, end_y), 1)
                
                start_x = right_reel_center[0] + math.cos(angle) * 6
                start_y = right_reel_center[1] + math.sin(angle) * 6
                end_x = right_reel_center[0] + math.cos(angle) * 10
                end_y = right_reel_center[1] + math.sin(angle) * 10
                pygame.draw.line(self.surface, [150, 150, 150], (start_x, start_y), (end_x, end_y), 1)
        
        # Название файла на кассете
        display_name = self.tape_filename
        if len(display_name) > 25:
            display_name = display_name[:22] + "..."
        
        name_text = self.small_font.render(display_name, True, [200, 200, 200])
        name_rect = name_text.get_rect()
        name_rect.centerx = cassette_rect.centerx
        name_rect.y = cassette_rect.y + 3
        self.surface.blit(name_text, name_rect)
    
    def _draw_indicators(self):
        """Рисует индикаторы состояния с НОВЫМ звуковым индикатором"""
        indicator_y = self.frame_thickness + 90
        
        # Статус
        status_text = self.font.render(f"MODE: {self.mode}", True, self.text_color)
        self.surface.blit(status_text, (self.frame_thickness + 15, indicator_y))
        
        # LED индикатор
        led_color = self.led_on_color if self.mode in ["PLAY", "RECORD"] else self.led_off_color
        led_center = (self.width - 25, indicator_y + 8)
        pygame.draw.circle(self.surface, led_color, led_center, 6)
        pygame.draw.circle(self.surface, [150, 150, 150], led_center, 6, 1)
        
        # НОВОЕ: Звуковой индикатор
        sound_indicator = "+" if self.sound_enabled and not self.sound_stop_flag else "-"
        sound_color = [0, 255, 0] if self.sound_enabled else [100, 100, 100]
        sound_text = self.small_font.render(sound_indicator, True, sound_color)
        self.surface.blit(sound_text, (self.width - 45, indicator_y + 3))
        
        # Позиция на ленте
        if self.tape_loaded:
            position_text = f"POS: {self.tape_position:04X}/{self.tape_size:04X}"
            pos_text_surface = self.small_font.render(position_text, True, self.text_color)
            self.surface.blit(pos_text_surface, (self.frame_thickness + 15, indicator_y + 18))
            
            # Прогресс бар
            if self.tape_size > 0:
                progress_width = 180
                progress_height = 6
                progress_x = self.frame_thickness + 15
                progress_y = indicator_y + 35
                
                progress_bg = pygame.Rect(progress_x, progress_y, progress_width, progress_height)
                pygame.draw.rect(self.surface, [50, 50, 50], progress_bg)
                pygame.draw.rect(self.surface, [100, 100, 100], progress_bg, 1)
                
                progress = min(self.tape_position / self.tape_size, 1.0) if self.tape_size > 0 else 0
                fill_width = int(progress_width * progress)
                if fill_width > 0:
                    fill_rect = pygame.Rect(progress_x, progress_y, fill_width, progress_height)
                    pygame.draw.rect(self.surface, [0, 150, 0], fill_rect)
    
    def _draw_buttons(self):
        """Рисует кнопки"""
        load_rect = self.get_button_rect("load")
        eject_rect = self.get_button_rect("eject")
        
        if load_rect:
            self._draw_button("LOAD", load_rect, "load")
        if eject_rect:
            self._draw_button("EJECT", eject_rect, "eject")
    
    def _draw_button(self, text, rect, button_name):
        """Рисует отдельную кнопку"""
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
        
        # 3D эффект
        if not self.button_states.get(button_name, False):
            pygame.draw.line(self.surface, [min(255, c + 30) for c in button_color], 
                           rect.topleft, rect.topright, 1)
            pygame.draw.line(self.surface, [min(255, c + 30) for c in button_color], 
                           rect.topleft, rect.bottomleft, 1)
            pygame.draw.line(self.surface, [max(0, c - 30) for c in button_color], 
                           rect.bottomleft, rect.bottomright, 1)
            pygame.draw.line(self.surface, [max(0, c - 30) for c in button_color], 
                           rect.topright, rect.bottomright, 1)
        
        text_surface = self.small_font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.surface.blit(text_surface, text_rect)
    
    def device_in(self, value):
        """ОБНОВЛЕННЫЙ протокол с звуками"""
        self._last_command = value
        
        if value == 0x7a:
            print("TapeLoader: запрос серийного номера")
            return
        
        elif value == 0x06:
            print(f"TapeLoader: проверка наличия кассеты - {'есть' if self.tape_loaded else 'нет'}")
            return
            
        elif value == 0x01:  # REWIND
            self.tape_position = 0
            self.mode = "REWIND"
            self.play_tape_sound("rewind", 1.0)  # НОВОЕ: Звук перемотки
            print("TapeLoader: перемотка в начало")
            return
            
        elif value == 0x02:  # PLAY
            if self.tape_loaded:
                self.mode = "PLAY"
                self.playing = True
                self.recording = False
                self.play_tape_sound("play")  # НОВОЕ: Звук воспроизведения
                print("TapeLoader: режим воспроизведения включен")
            else:
                print("TapeLoader: нет кассеты для воспроизведения")
            return
            
        elif value == 0x03:  # RECORD
            if self.tape_loaded:
                self.mode = "RECORD"
                self.recording = True
                self.playing = False
                self.play_tape_sound("record")  # НОВОЕ: Звук записи
                print("TapeLoader: режим записи включен")
            else:
                print("TapeLoader: нет кассеты для записи")
            return
            
        elif value == 0x04:  # STOP
            self.mode = "STOP"
            self.playing = False
            self.recording = False
            self.stop_tape_sound()  # НОВОЕ: Останавливаем звук
            print("TapeLoader: остановка")
            return
            
        elif value == 0x05:  # FAST_FORWARD
            if self.tape_loaded:
                self.mode = "FAST_FORWARD"
                self.tape_position = min(self.tape_size - 1, self.tape_position + 100)
                self.play_tape_sound("fast_forward", 0.5)  # НОВОЕ: Звук быстрой перемотки
                print(f"TapeLoader: быстрая перемотка, позиция: {self.tape_position}")
            return
        
        # Если в режиме записи - записываем байт
        if self.recording and self.tape_loaded:
            self._write_next_byte(value)
    
    def device_out(self):
        """Отправляет данные процессору"""
        if hasattr(self, '_last_command') and self._last_command == 0x7a:
            self._last_command = None
            print(f"TapeLoader: отправлен серийный номер 0x{self.serial_number:02X}")
            return self.serial_number
        
        elif hasattr(self, '_last_command') and self._last_command == 0x06:
            self._last_command = None
            status = 0x01 if self.tape_loaded else 0x00
            print(f"TapeLoader: статус кассеты: 0x{status:02X}")
            return status
        
        # Если в режиме воспроизведения - читаем следующий байт
        if self.playing and self.tape_loaded:
            return self._read_next_byte()
        
        return 0
    
    def _read_next_byte(self):
        """Читает следующий байт с кассеты"""
        if not self.tape_loaded or self.tape_position >= len(self.tape_data):
            print("TapeLoader: конец кассеты")
            self.stop_tape_sound()  # НОВОЕ: Останавливаем звук в конце
            return 0
        
        data = self.tape_data[self.tape_position]
        self.tape_position += 1
        print(f"TapeLoader: прочитан байт 0x{data:02X} с позиции {self.tape_position-1:04X}")
        return data
    
    def _write_next_byte(self, data):
        """Записывает следующий байт на кассету"""
        if not self.tape_loaded:
            return
        
        while len(self.tape_data) <= self.tape_position:
            self.tape_data.append(0)
        
        self.tape_data[self.tape_position] = data
        print(f"TapeLoader: записан байт 0x{data:02X} в позицию {self.tape_position:04X}")
        self.tape_position += 1
        self.tape_size = len(self.tape_data)
    
    def get_serial_number(self):
        return self.serial_number
