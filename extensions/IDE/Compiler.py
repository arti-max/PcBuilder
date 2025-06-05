import os
import sys
import re
import subprocess
import threading
from tkinter import messagebox

class CompilerIntegration:
    def __init__(self, ide):
        self.ide = ide
        self.is_compiling = False
        self.compile_thread = None
        
        # Путь к ассемблеру (с учетом реальной структуры)
        self.default_assembler_path = os.path.join('..', 'asm', 'Assembler.py')
        
        print("🔧 Интеграция компилятора инициализирована")
    
    def get_assembler_path(self):
        """Получение пути к ассемблеру"""
        # Сначала проверяем настройки
        settings = self.ide.settings.load_settings()
        custom_path = settings.get('compiler', {}).get('path', '')
        
        if custom_path and os.path.exists(custom_path):
            return custom_path
        
        # ИСПРАВЛЕННЫЕ пути с учетом реальной структуры проекта
        possible_paths = [
            # Относительно IDE (extensions/IDE/) -> extensions/asm/
            os.path.join(os.path.dirname(__file__), '..', 'asm', 'Assembler.py'),
            # Абсолютный путь от корня проекта
            os.path.join(os.path.dirname(__file__), '..', '..', 'extensions', 'asm', 'Assembler.py'),
            # Поиск в родительской директории
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 'extensions', 'asm', 'Assembler.py'),
        ]
        
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            print(f"🔍 Проверяем путь: {abs_path}")
            if os.path.exists(abs_path):
                print(f"✅ Найден ассемблер: {abs_path}")
                return abs_path
        
        # Если не найден, попробуем найти автоматически
        return self._find_assembler_automatically()
    
    def _find_assembler_automatically(self):
        """Автоматический поиск ассемблера"""
        # Начинаем поиск от текущей директории IDE
        current_dir = os.path.dirname(__file__)
        
        # Поднимаемся до корня проекта и ищем
        search_paths = [
            current_dir,
            os.path.join(current_dir, '..'),
            os.path.join(current_dir, '..', '..'),
            os.path.join(current_dir, '..', '..', '..'),
        ]
        
        for search_dir in search_paths:
            abs_search_dir = os.path.abspath(search_dir)
            print(f"🔍 Поиск в директории: {abs_search_dir}")
            
            # Ищем файл Assembler.py рекурсивно
            for root, dirs, files in os.walk(abs_search_dir):
                if 'Assembler.py' in files:
                    assembler_path = os.path.join(root, 'Assembler.py')
                    
                    # Проверяем, что это правильный ассемблер (есть рядом Lexer.py и Parser.py)
                    if (os.path.exists(os.path.join(root, 'Lexer.py')) and
                        os.path.exists(os.path.join(root, 'Parser.py'))):
                        print(f"🎯 Автоматически найден ассемблер: {assembler_path}")
                        return assembler_path
        
        print("❌ Ассемблер не найден")
        return None
    
    def compile_file(self, file_path, output_type="bin", output_path=None, metadata=None):
        """Компиляция файла"""
        if self.is_compiling:
            self.ide.update_status("⚠️ Компиляция уже выполняется")
            return

        assembler_path = self.get_assembler_path()
        if not assembler_path:
            messagebox.showerror("Ошибка", 
                            "Ассемблер не найден!\nУстановите путь в настройках.")
            return

        # Автосохранение если включено
        settings = self.ide.settings.load_settings()
        if settings.get('compiler', {}).get('auto_save_before_compile', True):
            if self.ide.is_modified:
                self.ide.save_file()

        # Обработка импортов
        try:
            processed_file = self.ide.file_manager.resolve_imports(file_path)
        except Exception as e:
            self.ide.update_status(f"❌ Ошибка обработки импортов: {e}")
            return

        # ИСПРАВЛЕНИЕ: Обработка выходных путей
        compile_params = {
            'file_path': processed_file,
            'output_type': output_type,
            'metadata': metadata,
            'output_path': output_path,
            'is_merged': file_path != processed_file
        }

        # Запуск компиляции в отдельном потоке
        self.is_compiling = True
        self.compile_thread = threading.Thread(
            target=self._compile_worker,
            args=(compile_params,)
        )
        self.compile_thread.daemon = True
        self.compile_thread.start()
    
    def _compile_worker(self, params):
        """Рабочий поток компиляции"""
        try:
            self.ide.update_status("🔧 Компиляция...")
            
            file_path = params['file_path']
            output_type = params['output_type']
            metadata = params['metadata']
            output_path = params['output_path']
            is_merged = params['is_merged']
            
            # Подготовка команды
            cmd = [sys.executable, self.get_assembler_path(), file_path]
            
            # ИСПРАВЛЕНИЕ: Обработка различных типов вывода
            if output_type == "tape":
                cmd.append("--tape")
                
                # Генерируем метаданные если не переданы
                if metadata is None:
                    filename = os.path.splitext(os.path.basename(file_path))[0]
                    metadata = {
                        'name': filename,
                        'author': 'PC Builder IDE',
                        'description': f'Compiled from {filename}'
                    }
                
                # Добавляем метаданные в команду
                if 'name' in metadata:
                    cmd.extend(['--name', metadata['name']])
                if 'author' in metadata:
                    cmd.extend(['--author', metadata['author']])
                if 'description' in metadata:
                    cmd.extend(['--description', metadata['description']])
                
                    
            elif output_type == "both":
                cmd.append("--both")
                
                # Для "both" тоже добавляем метаданные если есть
                if metadata:
                    if 'name' in metadata:
                        cmd.extend(['--name', metadata['name']])
                    if 'author' in metadata:
                        cmd.extend(['--author', metadata['author']])
                    if 'description' in metadata:
                        cmd.extend(['--description', metadata['description']])
            
            # Для BIN компиляции не добавляем специальные параметры
            # так как всегда создается 0.bin и опционально 1.bin
            cmd.extend(['--output', output_path])
            
            # Добавляем флаг для показа информации
            cmd.append("--info")
            
            # Выполняем компиляцию
            print(f"🚀 Выполнение команды: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(file_path)
            )
            
            # Обрабатываем результат в основном потоке
            self.ide.root.after(0, self._handle_compile_result, result, output_type, is_merged)
            
        except Exception as e:
            error_msg = f"❌ Ошибка компиляции: {e}"
            self.ide.root.after(0, self.ide.update_status, error_msg)
            self.ide.root.after(0, self._compilation_finished)
    
    def _handle_compile_result(self, result, output_type, is_merged):
        """Обработка результата компиляции"""
        try:
            if result.returncode == 0:
                # Успешная компиляция
                output_info = self._parse_compile_output(result.stdout)
                
                if output_type == "bin":
                    success_msg = "✅ BIN файлы созданы успешно"
                    if output_info:
                        success_msg += f" ({output_info})"
                    success_msg += " (0.bin и возможно 1.bin в папке bios/)"
                elif output_type == "tape":
                    success_msg = "✅ TAPE кассета создана успешно"
                    if output_info:
                        success_msg += f" ({output_info})"
                else:  # both
                    success_msg = "✅ BIN и TAPE файлы созданы успешно"
                    if output_info:
                        success_msg += f" ({output_info})"
                
                self.ide.update_status(success_msg)
                
                # Показываем подробную информацию
                if result.stdout:
                    self._show_compile_output("Результат компиляции", result.stdout, "info")
                
                # Очищаем временные файлы если использовались
                if is_merged:
                    self.ide.file_manager.cleanup_temp_files()
                    
            else:
                # Ошибка компиляции
                error_msg = "❌ Ошибка компиляции"
                if result.stderr:
                    error_msg += f": {result.stderr.strip()}"
                
                self.ide.update_status(error_msg)
                
                # Показываем ошибки
                error_output = result.stderr or result.stdout or "Неизвестная ошибка"
                self._show_compile_output("Ошибки компиляции", error_output, "error")
                
        except Exception as e:
            self.ide.update_status(f"❌ Ошибка обработки результата: {e}")
        finally:
            self._compilation_finished()
    
    def _parse_compile_output(self, output):
        """Парсинг вывода компилятора"""
        info = {}
        
        # Ищем размер программы
        size_match = re.search(r'Размер: (\d+) байт', output)
        if size_match:
            info['size'] = int(size_match.group(1))
        
        # Ищем адрес загрузки
        addr_match = re.search(r'Адрес загрузки: 0x([0-9A-Fa-f]+)', output)
        if addr_match:
            info['load_address'] = addr_match.group(1)
        
        # Формируем краткую информацию
        if info:
            parts = []
            if 'size' in info:
                parts.append(f"{info['size']} байт")
            if 'load_address' in info:
                parts.append(f"@0x{info['load_address']}")
            return ", ".join(parts)
        
        return None
    
    def _show_compile_output(self, title, content, output_type="info"):
        """Показ вывода компиляции"""
        import tkinter as tk
        from tkinter import scrolledtext
        
        # Создаем окно для вывода
        output_window = tk.Toplevel(self.ide.root)
        output_window.title(title)
        output_window.geometry("600x400")
        output_window.configure(bg='#2b2b2b')
        
        # Текстовое поле с прокруткой
        text_widget = scrolledtext.ScrolledText(
            output_window,
            bg='#1e1e1e' if output_type == "info" else '#2d1b1b',
            fg='#ffffff' if output_type == "info" else '#ff6b6b',
            insertbackground='white',
            font=('Consolas', 10),
            wrap=tk.WORD
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вставляем содержимое
        text_widget.insert('1.0', content)
        text_widget.config(state=tk.DISABLED)
        
        # Кнопка закрытия
        close_button = tk.Button(
            output_window,
            text="Закрыть",
            bg='#4c4c4c',
            fg='white',
            border=0,
            command=output_window.destroy
        )
        close_button.pack(pady=5)
        
        # Фокус на окне
        output_window.focus_set()
    
    def _compilation_finished(self):
        """Завершение компиляции"""
        self.is_compiling = False
        self.compile_thread = None
    
    def stop_compilation(self):
        """Остановка компиляции"""
        if self.is_compiling and self.compile_thread:
            # В Python сложно принудительно остановить поток
            # Здесь можно добавить механизм прерывания через флаги
            self.ide.update_status("⚠️ Попытка остановки компиляции...")
    
    def get_supported_formats(self):
        """Получение поддерживаемых форматов вывода"""
        return ["bin", "tape", "both"]
    
    def validate_file_before_compile(self, file_path):
        """Проверка файла перед компиляцией"""
        errors = []
        warnings = []
        
        if not os.path.exists(file_path):
            errors.append("Файл не существует")
            return errors, warnings
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Базовые проверки синтаксиса
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                stripped_line = line.strip()
                
                # Пропускаем комментарии и пустые строки
                if not stripped_line or stripped_line.startswith(';'):
                    continue
                
                # Проверка на неправильные символы
                if any(ord(char) > 127 for char in stripped_line):
                    warnings.append(f"Строка {line_num}: Не-ASCII символы")
                
                # Проверка балансировки скобок
                if stripped_line.count('[') != stripped_line.count(']'):
                    errors.append(f"Строка {line_num}: Несбалансированные скобки")
                
                # Проверка базового синтаксиса меток
                if ':' in stripped_line and not stripped_line.startswith('#'):
                    label_part = stripped_line.split(':')[0].strip()
                    if ' ' in label_part or '\t' in label_part:
                        errors.append(f"Строка {line_num}: Некорректное имя метки")
            
            # Проверка наличия главной функции или точки входа
            if '#org' not in content.lower() and 'main:' not in content.lower():
                warnings.append("Не найдена точка входа (#org или main:)")
                
        except Exception as e:
            errors.append(f"Ошибка чтения файла: {e}")
        
        return errors, warnings
    
    def get_compile_statistics(self):
        """Получение статистики компиляции"""
        # Здесь можно добавить сбор статистики компиляций
        return {
            'total_compilations': 0,
            'successful_compilations': 0,
            'failed_compilations': 0,
            'average_compile_time': 0
        }
