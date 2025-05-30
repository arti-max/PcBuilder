import pygame
import time
import threading
import numpy as np
from api.Device import Device

class Buzzer(Device):
    def __init__(self, canvas):
        super().__init__(canvas, "Buzzer")
        
        self.serial_number = self.config.get("serial_number", 0x2F)
        
        # Размеры устройства
        self.device_width = self.config.get("device_width", 140)  # Немного увеличил
        self.device_height = self.config.get("device_height", 100)
        self.frame_thickness = 4
        
        self.width = self.device_width
        self.height = self.device_height
        self.surface = pygame.Surface((self.width, self.height))
        
        # Цветовая схема
        self.background_color = self.config.get("background_color", [40, 40, 40])
        self.frame_color = self.config.get("frame_color", [60, 60, 60])
        self.border_color = self.config.get("border_color", [100, 100, 100])
        self.speaker_color = self.config.get("speaker_color", [80, 80, 80])
        self.active_color = self.config.get("active_color", [255, 100, 100])
        self.text_color = self.config.get("text_color", [200, 200, 200])
        self.compose_color = self.config.get("compose_color", [100, 255, 100])  # Зеленый для композиции
        
        # Состояние звука
        self.is_playing = False
        self.current_pattern = None
        self.play_thread = None
        self.stop_flag = False
        
        # НОВОЕ: Система композиции мелодий
        self.compose_mode = False
        self.melody_buffer = []  # Список (частота, длительность)
        self.waiting_for_duration = False
        self.temp_frequency = 0
        self.current_melody = None
        
        # Анимация
        self.blink_state = False
        self.last_blink_time = time.time()
        self.animation_intensity = 0
        
        # Стандартные звуковые паттерны
        self.sound_patterns = {
            0x01: {"name": "BEEP", "pattern": [0.1], "repeat": 1},
            0x02: {"name": "ERROR", "pattern": [0.5], "repeat": 1},
            0x03: {"name": "DISPLAY", "pattern": [0.1, 0.1, 0.1], "repeat": 3},
            0x04: {"name": "KEYBOARD", "pattern": [0.1, 0.2, 0.1], "repeat": 2},
            0x05: {"name": "TAPE", "pattern": [0.05, 0.05, 0.05, 0.05], "repeat": 2},
            0x07: {"name": "CRITICAL", "pattern": [0.2, 0.1, 0.2, 0.1, 0.2], "repeat": 5},
        }
        
        # НОВОЕ: Предустановленные ноты (частоты в Hz)
        self.musical_notes = {
            # Октава 4
            60: 262,  # C4 (До)
            61: 277,  # C#4
            62: 294,  # D4 (Ре)
            63: 311,  # D#4
            64: 330,  # E4 (Ми)
            65: 349,  # F4 (Фа)
            66: 370,  # F#4
            67: 392,  # G4 (Соль)
            68: 415,  # G#4
            69: 440,  # A4 (Ля)
            70: 466,  # A#4
            71: 494,  # B4 (Си)
            # Октава 5
            72: 523,  # C5
            73: 554,  # C#5
            74: 587,  # D5
            75: 622,  # D#5
            76: 659,  # E5
            77: 698,  # F5
            78: 740,  # F#5
            79: 784,  # G5
            80: 831,  # G#5
            81: 880,  # A5
            82: 932,  # A#5
            83: 988,  # B5
            # Октава 6
            84: 1047, # C6
            85: 1109, # C#6
            86: 1175, # D6
            87: 1245, # D#6
            88: 1319, # E6
            89: 1397, # F6
            90: 1480, # F#6
            91: 1568, # G6
            92: 1661, # G#6
            93: 1760, # A6
            94: 1865, # A#6
            95: 1976, # B6
        }
        
        # Инициализация звука
        self.sound_enabled = self._init_sound()
        
        # Шрифты
        pygame.font.init()
        self.font = pygame.font.Font(None, 16)
        self.small_font = pygame.font.Font(None, 12)
        
    def _init_sound(self):
        """Инициализация звуковой системы"""
        try:
            if not pygame.get_init():
                return False
            
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            if pygame.mixer.get_init() is not None:
                print("Buzzer: звуковая система инициализирована")
                return True
            else:
                print("Buzzer: звук недоступен")
                return False
                
        except Exception as e:
            print(f"Buzzer: ошибка инициализации звука: {e}")
            return False
    
    def get_default_config(self):
        config = super().get_default_config()
        config.update({
            "serial_number": 0x2F,
            "device_width": 140,
            "device_height": 100,
            "background_color": [40, 40, 40],
            "frame_color": [60, 60, 60],
            "border_color": [100, 100, 100],
            "speaker_color": [80, 80, 80],
            "active_color": [255, 100, 100],
            "text_color": [200, 200, 200],
            "compose_color": [100, 255, 100],
            "width": 140,
            "height": 100,
            "x": 800,
            "y": 50
        })
        return config
    
    def generate_tone(self, frequency, duration):
        """ИСПРАВЛЕННАЯ генерация музыкального тона"""
        if not self.sound_enabled or pygame.mixer.get_init() is None:
            return None
        
        try:
            sample_rate = pygame.mixer.get_init()[0]
            frames = int(duration * sample_rate)
            
            # Проверяем минимальную длину
            if frames < 100:  # Минимум 100 сэмплов
                frames = 100
            
            # Генерируем синусоидальную волну
            time_array = np.linspace(0, duration, frames)
            wave_array = np.sin(2 * np.pi * frequency * time_array)
            
            # ИСПРАВЛЕННАЯ ADSR огибающая с проверкой размеров
            envelope = np.ones(frames)
            
            # Параметры огибающей (в сэмплах)
            attack_frames = min(int(0.01 * sample_rate), frames // 4)    # 10ms или 1/4 от общей длины
            decay_frames = min(int(0.05 * sample_rate), frames // 4)     # 50ms или 1/4 от общей длины  
            release_frames = min(int(0.1 * sample_rate), frames // 4)    # 100ms или 1/4 от общей длины
            sustain_level = 0.7
            
            # Проверяем, что есть место для всех фаз
            total_envelope_frames = attack_frames + decay_frames + release_frames
            if total_envelope_frames >= frames:
                # Упрощенная огибающая для очень коротких звуков
                fade_frames = max(1, frames // 10)
                envelope[:fade_frames] = np.linspace(0, 1, fade_frames)
                envelope[-fade_frames:] = np.linspace(1, 0, fade_frames)
            else:
                # Полная ADSR огибающая
                # Атака
                if attack_frames > 0:
                    envelope[:attack_frames] = np.linspace(0, 1, attack_frames)
                
                # Спад
                if decay_frames > 0:
                    decay_start = attack_frames
                    decay_end = attack_frames + decay_frames
                    envelope[decay_start:decay_end] = np.linspace(1, sustain_level, decay_frames)
                
                # Поддержка
                sustain_start = attack_frames + decay_frames
                sustain_end = frames - release_frames
                if sustain_end > sustain_start:
                    envelope[sustain_start:sustain_end] = sustain_level
                
                # Затухание
                if release_frames > 0:
                    envelope[-release_frames:] = np.linspace(sustain_level, 0, release_frames)
            
            # ПРОВЕРЯЕМ размеры перед применением огибающей
            if len(wave_array) != len(envelope):
                print(f"Buzzer: несоответствие размеров wave_array({len(wave_array)}) != envelope({len(envelope)})")
                # Подгоняем размеры
                min_length = min(len(wave_array), len(envelope))
                wave_array = wave_array[:min_length]
                envelope = envelope[:min_length]
            
            # Применяем огибающую
            wave_array = wave_array * envelope * 0.3  # Уменьшаем громкость
            
            # Ограничиваем амплитуду
            wave_array = np.clip(wave_array, -0.5, 0.5)
            
            # Конвертируем в 16-битный формат
            wave_array = (wave_array * 16383).astype(np.int16)
            
            # Создаем стерео звук
            stereo_wave = np.zeros((len(wave_array), 2), dtype=np.int16)
            stereo_wave[:, 0] = wave_array
            stereo_wave[:, 1] = wave_array
            
            return pygame.sndarray.make_sound(stereo_wave)
            
        except Exception as e:
            print(f"Buzzer: ошибка генерации тона: {e}")
            return None

    
    def play_melody(self, melody):
        """Воспроизводит мелодию"""
        if not melody:
            print("Buzzer: мелодия пуста")
            return
        
        self.stop_sound()
        self.current_melody = melody.copy()
        self.is_playing = True
        self.stop_flag = False
        
        print(f"Buzzer: воспроизведение мелодии из {len(melody)} нот")
        
        self.play_thread = threading.Thread(target=self._play_melody_thread, args=(melody,))
        self.play_thread.daemon = True
        self.play_thread.start()
    
    def _play_melody_thread(self, melody):
        """Поток воспроизведения мелодии"""
        try:
            for i, (frequency, duration_ms) in enumerate(melody):
                if self.stop_flag:
                    break
                
                self.animation_intensity = 1.0
                
                if frequency > 0:  # 0 = пауза
                    duration_sec = duration_ms / 1000.0
                    
                    if self.sound_enabled:
                        sound = self.generate_tone(frequency, duration_sec)
                        if sound and not self.stop_flag:
                            sound.play()
                            time.sleep(duration_sec)
                        else:
                            time.sleep(duration_sec)
                    else:
                        time.sleep(duration_sec)
                else:
                    # Пауза
                    time.sleep(duration_ms / 1000.0)
                
                # Короткая пауза между нотами
                if i < len(melody) - 1:
                    self.animation_intensity = 0.2
                    time.sleep(0.02)
                    
        except Exception as e:
            print(f"Buzzer: ошибка воспроизведения мелодии: {e}")
        finally:
            self.is_playing = False
            self.animation_intensity = 0.0
            self.current_melody = None
    
    def generate_beep_sound(self, frequency=800, duration=0.1):
        """Генерирует простой звуковой сигнал (для обратной совместимости)"""
        return self.generate_tone(frequency, duration)
    
    def play_pattern(self, pattern_id):
        """Воспроизводит стандартный звуковой паттерн"""
        if pattern_id not in self.sound_patterns:
            print(f"Buzzer: неизвестный паттерн 0x{pattern_id:02X}")
            return
        
        self.stop_sound()
        
        pattern = self.sound_patterns[pattern_id]
        self.current_pattern = pattern
        self.is_playing = True
        self.stop_flag = False
        
        print(f"Buzzer: воспроизведение паттерна '{pattern['name']}'")
        
        self.play_thread = threading.Thread(target=self._play_pattern_thread, args=(pattern,))
        self.play_thread.daemon = True
        self.play_thread.start()
    
    def _play_pattern_thread(self, pattern):
        """Поток воспроизведения стандартного паттерна"""
        try:
            for repeat in range(pattern["repeat"]):
                if self.stop_flag:
                    break
                
                for i, duration in enumerate(pattern["pattern"]):
                    if self.stop_flag:
                        break
                    
                    frequency = 800 + (i * 100)
                    self.animation_intensity = 1.0
                    
                    if self.sound_enabled:
                        try:
                            sound = self.generate_tone(frequency, duration)
                            if sound:
                                sound.play()
                        except Exception as e:
                            print(f"Buzzer: ошибка воспроизведения: {e}")
                    
                    time.sleep(duration)
                    
                    if i < len(pattern["pattern"]) - 1:
                        self.animation_intensity = 0.0
                        time.sleep(0.05)
                
                if repeat < pattern["repeat"] - 1:
                    self.animation_intensity = 0.0
                    time.sleep(0.3)
        
        except Exception as e:
            print(f"Buzzer: ошибка в потоке воспроизведения: {e}")
        finally:
            self.is_playing = False
            self.animation_intensity = 0.0
            self.current_pattern = None
    
    def stop_sound(self):
        """Останавливает воспроизведение"""
        self.stop_flag = True
        self.is_playing = False
        self.animation_intensity = 0.0
        
        if self.sound_enabled and pygame.mixer.get_init() is not None:
            try:
                pygame.mixer.stop()
            except:
                pass
        
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=0.1)
        
        print("Buzzer: воспроизведение остановлено")
    
    def update(self):
        """Обновляет состояние устройства"""
        current_time = time.time()
        
        # Обновляем анимацию мигания
        if self.is_playing:
            if current_time - self.last_blink_time >= 0.1:
                self.blink_state = not self.blink_state
                self.last_blink_time = current_time
            
            if self.animation_intensity > 0:
                self.animation_intensity = max(0, self.animation_intensity - 0.05)
        else:
            self.blink_state = False
            self.animation_intensity = 0
    
    def draw(self):
        """Рисует устройство"""
        # Фон
        self.surface.fill(self.background_color)
        
        # Внешняя рамка
        outer_rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(self.surface, self.frame_color, outer_rect)
        
        # Цвет рамки зависит от режима
        border_color = self.compose_color if self.compose_mode else self.border_color
        pygame.draw.rect(self.surface, border_color, outer_rect, 2)
        
        # Внутренняя область
        inner_rect = pygame.Rect(
            self.frame_thickness,
            self.frame_thickness,
            self.width - self.frame_thickness * 2,
            self.height - self.frame_thickness * 2
        )
        pygame.draw.rect(self.surface, [30, 30, 30], inner_rect)
        
        # Рисуем динамик
        self._draw_speaker()
        
        # Статус
        self._draw_status()
        
        # Лейбл устройства
        label_text = self.small_font.render("BUZZER", True, [150, 150, 150])
        label_rect = label_text.get_rect()
        label_rect.centerx = self.width // 2
        label_rect.bottom = self.height - 3
        self.surface.blit(label_text, label_rect)
    
    def _draw_speaker(self):
        """Рисует динамик"""
        center_x = self.width // 2
        center_y = self.height // 2 - 10
        
        # Основной корпус динамика
        speaker_rect = pygame.Rect(center_x - 20, center_y - 15, 40, 30)
        
        # Цвет зависит от состояния
        if self.is_playing and self.blink_state:
            speaker_color = [
                min(255, self.speaker_color[0] + int(self.animation_intensity * 175)),
                min(255, self.speaker_color[1] + int(self.animation_intensity * 20)),
                min(255, self.speaker_color[2] + int(self.animation_intensity * 20))
            ]
        elif self.compose_mode:
            speaker_color = [
                min(255, self.speaker_color[0] + 40),
                min(255, self.speaker_color[1] + 60),
                min(255, self.speaker_color[2] + 40)
            ]
        else:
            speaker_color = self.speaker_color
        
        pygame.draw.rect(self.surface, speaker_color, speaker_rect)
        pygame.draw.rect(self.surface, self.border_color, speaker_rect, 2)
        
        # Решетка динамика
        for i in range(3):
            for j in range(6):
                hole_x = speaker_rect.x + 8 + j * 4
                hole_y = speaker_rect.y + 8 + i * 4
                pygame.draw.circle(self.surface, [50, 50, 50], (hole_x, hole_y), 1)
        
        # Звуковые волны при воспроизведении
        if self.is_playing and self.animation_intensity > 0:
            wave_color = [
                int(255 * self.animation_intensity),
                int(100 * self.animation_intensity),
                int(100 * self.animation_intensity)
            ]
            
            for i in range(3):
                wave_x = speaker_rect.right + 5 + i * 3
                wave_y1 = center_y - (5 + i * 2)
                wave_y2 = center_y + (5 + i * 2)
                
                pygame.draw.arc(self.surface, wave_color, 
                               (wave_x - 5, wave_y1, 10, wave_y2 - wave_y1), 
                               -0.5, 0.5, 2)
    
    def _draw_status(self):
        """Рисует статус устройства"""
        status_y = self.height - 30
        
        if self.compose_mode:
            status_text = f"COMPOSE ({len(self.melody_buffer)} notes)"
            color = self.compose_color
        elif self.is_playing and self.current_pattern:
            status_text = f"{self.current_pattern['name']}"
            color = self.active_color
        elif self.is_playing and self.current_melody:
            status_text = "PLAYING MELODY"
            color = self.active_color
        elif not self.sound_enabled:
            status_text = "MUTE"
            color = [150, 150, 0]
        else:
            status_text = "READY"
            color = self.text_color
        
        text_surface = self.small_font.render(status_text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.centerx = self.width // 2
        text_rect.y = status_y
        self.surface.blit(text_surface, text_rect)
    
    def device_in(self, value):
        """РАСШИРЕННЫЙ протокол с поддержкой композиции"""
        self._last_command = value
        
        if value == 0x2F:  # Запрос серийного номера
            print("Buzzer: запрос серийного номера")
            return
        
        elif value == 0x06:  # Стоп
            self.stop_sound()
            return
        
        elif value == 0x08:  # Войти в режим композиции
            self.compose_mode = True
            self.melody_buffer.clear()
            self.waiting_for_duration = False
            self.stop_sound()
            print("Buzzer: режим композиции включен")
            return
        
        elif value == 0x09:  # Воспроизвести мелодию
            if self.melody_buffer:
                self.compose_mode = False
                self.play_melody(self.melody_buffer)
                print(f"Buzzer: воспроизведение мелодии из {len(self.melody_buffer)} нот")
            else:
                print("Buzzer: буфер мелодии пуст")
            return
        
        elif value == 0x0A:  # Очистить мелодию
            self.melody_buffer.clear()
            self.waiting_for_duration = False
            print("Buzzer: буфер мелодии очищен")
            return
        
        elif value == 0x0B:  # Выйти из режима композиции
            self.compose_mode = False
            self.waiting_for_duration = False
            print("Buzzer: режим композиции выключен")
            return
        
        # Режим композиции
        if self.compose_mode:
            if not self.waiting_for_duration:
                # Получаем ноту/частоту
                if value in self.musical_notes:
                    # Музыкальная нота (MIDI номер)
                    self.temp_frequency = self.musical_notes[value]
                    self.waiting_for_duration = True
                    print(f"Buzzer: нота {value} ({self.temp_frequency}Hz), ожидание длительности")
                elif value == 0:
                    # Пауза
                    self.temp_frequency = 0
                    self.waiting_for_duration = True
                    print("Buzzer: пауза, ожидание длительности")
                else:
                    # Произвольная частота (ограничиваем разумными пределами)
                    frequency = min(max(value * 10, 50), 5000)  # от 50Hz до 5kHz
                    self.temp_frequency = frequency
                    self.waiting_for_duration = True
                    print(f"Buzzer: частота {frequency}Hz, ожидание длительности")
            else:
                # Получаем длительность
                duration_ms = max(value * 10, 50)  # Минимум 50ms
                self.melody_buffer.append((self.temp_frequency, duration_ms))
                self.waiting_for_duration = False
                print(f"Buzzer: добавлена нота {self.temp_frequency}Hz, {duration_ms}ms")
            return
        
        # Стандартные паттерны
        elif value in self.sound_patterns:
            self.play_pattern(value)
            return
        
        else:
            print(f"Buzzer: неизвестная команда 0x{value:02X}")
    
    def device_out(self):
        """Отправляет данные процессору"""
        if hasattr(self, '_last_command') and self._last_command == 0x2F:
            self._last_command = None
            print(f"Buzzer: отправлен серийный номер 0x{self.serial_number:02X}")
            return self.serial_number
        
        # Возвращаем статус
        if self.compose_mode:
            status = 0x08 | (0x04 if self.waiting_for_duration else 0x00)
        elif self.is_playing:
            status = 0x01
        elif self.sound_enabled:
            status = 0x02
        else:
            status = 0x00
        
        return status
    
    def get_serial_number(self):
        return self.serial_number
