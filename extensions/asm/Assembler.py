import os
import sys
import argparse
from datetime import datetime
from Lexer import Lexer
from Parser import Parser
from Compiler import Compiler, TapeFormat

class Assembler:
    def __init__(self):
        self.lexer = None
        self.parser = None
        self.compiler = Compiler()
    
    def assemble_file(self, filename, output_type="bin", output_path=None, metadata=None):
        """
        Ассемблирует файл с выбором типа вывода
        
        Args:
            filename: Путь к файлу .asm
            output_type: "bin", "tape", "both"
            output_path: Путь для сохранения (опционально)
            metadata: Метаданные для TAPE файла
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Файл не найден: {filename}")
        
        with open(filename, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        return self.assemble_string(source_code, output_type, output_path, metadata)
    
    def assemble_string(self, source_code, output_type="bin", output_path=None, metadata=None):
        """
        Ассемблирует строку с кодом
        
        Args:
            source_code: Исходный код на ассемблере
            output_type: "bin", "tape", "both" 
            output_path: Путь для сохранения
            metadata: Метаданные для TAPE файла
        """
        print(" Начало ассемблирования...")
        
        # Лексический анализ
        print(" Лексический анализ...")
        self.lexer = Lexer(source_code)
        tokens = self.lexer.tokenize()
        print(f"   Найдено токенов: {len(tokens)}")
        
        # Синтаксический анализ
        print("  Синтаксический анализ...")
        self.parser = Parser(tokens)
        statements = self.parser.parse()
        print(f"   Найдено инструкций: {len(statements)}")
        
        # Компиляция
        print("  Компиляция...")
        binary_data = self.compiler.compile(statements)
        print(f"   Размер кода: {len(binary_data)} байт")
        
        if self.compiler.org_address != 0:
            print(f"   Адрес загрузки: 0x{self.compiler.org_address:04X}")
        
        # Сохранение результата
        results = {}
        
        if output_type in ["bin", "both"]:
            print(" Сохранение BIN файлов...")
            self.compiler.save_to_files(binary_data, output_path)
            results["bin"] = binary_data
            print(f"    BIN файлы сохранены в {output_path}/")
        
        if output_type in ["tape", "both"]:
            print(" Создание TAPE файла...")
            
            # Подготовка метаданных
            if metadata is None:
                metadata = {
                    'name': 'Assembled Program',
                    'author': 'PC Builder',
                    'description': 'Auto-generated'
                }
            
            # Определение пути для TAPE файла
            if output_path is None:
                os.makedirs("asm/tapes", exist_ok=True)
                tape_path = "asm/tapes/program.tape"
            else:
                tape_path = output_path
                if not tape_path.endswith('.tape'):
                    tape_path += '.tape'
            
            tape_data = self.compiler.save_to_tape(binary_data, tape_path, metadata)
            results["tape"] = {"path": tape_path, "data": tape_data}
            print(f"    TAPE файл сохранен: {tape_path}")
        
        print(" Ассемблирование завершено успешно!")
        return results
    
    def get_program_info(self, binary_data):
        """Возвращает информацию о программе"""
        info = {
            "size": len(binary_data),
            "load_address": self.compiler.org_address,
            "machine_code": [f"0x{b:02X}" for b in binary_data[:20]]  # Первые 20 байт
        }
        
        if len(binary_data) > 20:
            info["machine_code"].append("...")
        
        return info

def create_metadata_from_args(args):
    """Создает метаданные из аргументов командной строки"""
    return {
        'name': args.name or 'Assembled Program',
        'author': args.author or 'PC Builder',
        'description': args.description or f'Assembled on {datetime.now().strftime("%Y-%m-%d %H:%M")}'
    }

def main():
    """Основная функция с поддержкой командной строки"""
    parser = argparse.ArgumentParser(
        description='PC Builder Assembler - Ассемблер для 8-битного процессора',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python assembler.py program.asm                    # Компиляция в BIN
  python assembler.py program.asm --tape             # Компиляция в TAPE
  python assembler.py program.asm --both             # Компиляция в BIN и TAPE
  python assembler.py program.asm --tape --name "My Program" --author "Developer"
  python assembler.py --interactive                  # Интерактивный режим
        """
    )
    
    parser.add_argument('input', nargs='?', help='Входной файл .asm')
    parser.add_argument('--tape', action='store_true', help='Компилировать в TAPE файл')
    parser.add_argument('--both', action='store_true', help='Компилировать в BIN и TAPE')
    parser.add_argument('--output', '-o', help='Путь для сохранения файла')
    parser.add_argument('--name', help='Название программы (для TAPE)')
    parser.add_argument('--author', help='Автор программы (для TAPE)')
    parser.add_argument('--description', help='Описание программы (для TAPE)')
    parser.add_argument('--interactive', '-i', action='store_true', help='Интерактивный режим')
    parser.add_argument('--info', action='store_true', help='Показать информацию о программе')
    
    args = parser.parse_args()
    
    assembler = Assembler()
    
    # Интерактивный режим
    if args.interactive:
        print("🎮 Интерактивный режим ассемблера PC Builder")
        print("Введите код на ассемблере (Ctrl+D для завершения):")
        print("=" * 50)
        
        try:
            source_lines = []
            while True:
                try:
                    line = input()
                    if line.strip() == "EOF":
                        break
                    source_lines.append(line)
                except EOFError:
                    break
            
            source_code = "\n".join(source_lines)
            
            if source_code.strip():
                print("\n" + "=" * 50)
                metadata = {
                    'name': 'Interactive Program',
                    'author': 'Interactive User',
                    'description': f'Created interactively on {datetime.now().strftime("%Y-%m-%d %H:%M")}'
                }
                
                results = assembler.assemble_string(source_code, "both", None, metadata)
                
                if args.info and "bin" in results:
                    info = assembler.get_program_info(results["bin"])
                    print(f"\n Информация о программе:")
                    print(f"   Размер: {info['size']} байт")
                    print(f"   Адрес загрузки: 0x{info['load_address']:04X}")
                    print(f"   Машинный код: {' '.join(info['machine_code'])}")
            else:
                print(" Код не введен")
                
        except KeyboardInterrupt:
            print("\n Прервано пользователем")
            return
        except Exception as e:
            print(f" Ошибка: {e}")
            return
    
    # Обычный режим
    elif args.input:
        try:
            # Определение типа вывода
            if args.both:
                output_type = "both"
            elif args.tape:
                output_type = "tape"
            else:
                output_type = "bin"
            
            # Создание метаданных
            metadata = create_metadata_from_args(args) if output_type in ["tape", "both"] else None
            
            # Ассемблирование
            results = assembler.assemble_file(args.input, output_type, args.output, metadata)
            
            # Показ информации
            if args.info and "bin" in results:
                info = assembler.get_program_info(results["bin"])
                print(f"\n Информация о программе:")
                print(f"   Размер: {info['size']} байт")
                print(f"   Адрес загрузки: 0x{info['load_address']:04X}")
                print(f"   Машинный код: {' '.join(info['machine_code'])}")
            
        except Exception as e:
            print(f" Ошибка: {e}")
            sys.exit(1)
    
    else:
        parser.print_help()

# Примеры для быстрого тестирования
def run_examples():
    """Запуск примеров для тестирования"""
    assembler = Assembler()
    
    # Пример 1: Простая программа очистки
    cleanup_program = """
#org 0x0300
jmp main

main:
    ; Очистка 8-битных регистров
    xor a, a
    xor b, b
    xor c, c
    xor d, d
    
    ; Инициализация стека
    mov sp, 0xFF
    mov bp, 0xFF
    mov ss, 0x00
    
    ; Тестовая программа
    mov a, 0xEE
    hlt
"""
    
    # Пример 2: Работа с дисплеем
    display_program = """
#org 0x0300
jmp main

main:
    ; Очистка регистров
    xor a, a
    xor b, b
    xor c, c
    xor d, d
    
    ; Рисуем крест на дисплее
    mov a, 2        ; Порт дисплея
    mov b, 8        ; X центр
    out a, b
    mov b, 8        ; Y центр
    out a, b
    mov b, 1        ; Включить пиксель
    out a, b
    
    hlt
"""
    
    print("🧪 Тестирование примеров...")
    
    try:
        # Тест программы очистки
        print("\n  Тест программы очистки:")
        results1 = assembler.assemble_string(cleanup_program, "both", "asm/tapes/cleanup.tape", {
            'name': 'Cleanup Program',
            'author': 'PC Builder Examples',
            'description': 'Example program showing register cleanup'
        })
        
        # Тест программы дисплея
        print("\n  Тест программы дисплея:")
        results2 = assembler.assemble_string(display_program, "both", "asm/tapes/display_test.tape", {
            'name': 'Display Test',
            'author': 'PC Builder Examples', 
            'description': 'Example program drawing on display'
        })
        
        print("\n Все примеры успешно ассемблированы!")
        
    except Exception as e:
        print(f" Ошибка в примерах: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        run_examples()
    else:
        main()
