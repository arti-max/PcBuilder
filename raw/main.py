import os
import sys
import pygame
from cpu.Cpu import Cpu
from ram.Ram0 import Ram0
from api.Api import DeviceManager, auto_discover_devices

def load_boot_files(ram):
    boot_dir = "boot"
    if not os.path.exists(boot_dir):
        return 0
        
    boot_files = sorted([f for f in os.listdir(boot_dir) if f.endswith(".bin") and f.split(".")[0].isdigit()])
    boot_files = [f for f in boot_files if int(f.split(".")[0]) <= 1]
    
    if not boot_files:
        return 0
    
    start_address = 0x00FF
    current_address = start_address
    
    for boot_file in boot_files:
        file_path = os.path.join(boot_dir, boot_file)
        with open(file_path, "rb") as f:
            data = f.read()
            for byte in data:
                ram.write(current_address, byte)
                current_address += 1
    
    return start_address

def main():
    # Инициализация pygame
    pygame.init()
    
    # Создаем окно для устройств
    canvas_width, canvas_height = 800, 600
    canvas = pygame.display.set_mode((canvas_width, canvas_height))
    pygame.display.set_caption("PC Builder - Devices Canvas")
    clock = pygame.time.Clock()
    
    # Проверка наличия чипа CPU
    try:
        cpu = Cpu()
    except Exception as e:
        print(f"Ошибка инициализации CPU: {e}")
        sys.exit(1)
    
    # Проверка наличия хотя бы одного чипа RAM
    ram = Ram0()
    cpu.set_ram(ram)
    
    # Инициализация системы устройств
    device_manager = DeviceManager(canvas)
    
    # Автоматическое обнаружение устройств
    discovered_devices = auto_discover_devices()
    for device_name, device_class in discovered_devices.items():
        device_manager.register_device_class(device_name, device_class)
    
    # Загружаем устройства из конфигурации портов
    for port, device_name in device_manager.ports_config.items():
        if device_name and device_name in discovered_devices:
            try:
                device_manager.connect_device(int(port), device_name)
            except Exception as e:
                print(f"Ошибка подключения {device_name} к порту {port}: {e}")
    
    # Подключаем device_manager к CPU
    cpu.set_device_manager(device_manager)
    
    # Загрузка boot файлов
    start_address = load_boot_files(ram) if os.path.exists("boot") else 0
    
    # Основной цикл
    cpu.run(start=start_address)
    
    while cpu.running:
        cpu.step()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cpu.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                device_manager.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                device_manager.handle_key_down(event)
                if event.key == pygame.K_r:
                    print("запуск CPU...")
                    cpu.run(start=start_address)
            elif event.type == pygame.KEYUP:
                device_manager.handle_key_up(event)
        
        # Обновляем устройства
        device_manager.update_all()
        
        # Очищаем экран
        canvas.fill((32, 32, 32))  # Темно-серый фон
        
        # Рисуем устройства
        device_manager.draw_all()
        
        # Обновляем экран
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
    
    pygame.quit()
    print(cpu.registers)

if __name__ == "__main__":
    main()
