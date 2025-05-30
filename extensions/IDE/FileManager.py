import os
import shutil
import re
from tkinter import messagebox

class FileManager:
    def __init__(self, ide):
        self.ide = ide
        self.project_root = self.find_project_root()
        self.imports_cache = {}
        
        print(f"📁 Файловый менеджер инициализирован")
        print(f"📂 Корень проекта: {self.project_root}")
    
    def find_project_root(self):
        """Поиск корня проекта PC Builder"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Поднимаемся вверх до корня проекта
        while current_dir != os.path.dirname(current_dir):
            # Ищем характерные файлы/папки проекта
            if (os.path.exists(os.path.join(current_dir, 'cpu')) and
                os.path.exists(os.path.join(current_dir, 'devices')) and
                os.path.exists(os.path.join(current_dir, 'api'))):
                return current_dir
            current_dir = os.path.dirname(current_dir)
        
        # Если не найден, возвращаем текущую директорию
        return os.getcwd()
    
    def resolve_imports(self, file_path):
        """Разрешение импортов в файле и создание объединенного файла"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        # Создаем временную директорию для объединенных файлов
        temp_dir = os.path.join(os.path.dirname(file_path), '.temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Читаем основной файл
        with open(file_path, 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        # Ищем директивы импорта
        imports = self.find_imports(main_content)
        
        if not imports:
            # Нет импортов, возвращаем оригинальный файл
            return file_path
        
        # Создаем объединенный файл
        merged_file = os.path.join(temp_dir, f"merged_{os.path.basename(file_path)}")
        
        try:
            self.create_merged_file(file_path, merged_file, imports)
            print(f"📦 Создан объединенный файл: {merged_file}")
            return merged_file
        except Exception as e:
            print(f"❌ Ошибка создания объединенного файла: {e}")
            return file_path
    
    def find_imports(self, content):
        """Поиск директив импорта в коде"""
        imports = []
        
        # Паттерны для поиска импортов (можно расширить)
        import_patterns = [
            r'#include\s+"([^"]+)"',      # #include "file.asm"
            r'#import\s+"([^"]+)"',       # #import "file.asm"
            r';import\s+([^\s;]+)',       # ;import file.asm
        ]
        
        for pattern in import_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                import_path = match.group(1)
                imports.append({
                    'path': import_path,
                    'line': content[:match.start()].count('\n') + 1,
                    'full_match': match.group(0)
                })
        
        return imports
    
    def create_merged_file(self, main_file, output_file, imports):
        """Создание объединенного файла"""
        main_dir = os.path.dirname(main_file)
        
        # Читаем основной файл
        with open(main_file, 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        # Собираем содержимое всех импортируемых файлов
        imported_contents = []
        processed_files = set()  # Для предотвращения циклических импортов
        
        for import_info in imports:
            import_path = import_info['path']
            
            # Разрешаем относительный путь
            if not os.path.isabs(import_path):
                full_import_path = os.path.join(main_dir, import_path)
            else:
                full_import_path = import_path
            
            # Нормализуем путь
            full_import_path = os.path.normpath(full_import_path)
            
            # Проверяем на циклические импорты
            if full_import_path in processed_files:
                print(f"⚠️ Пропущен циклический импорт: {import_path}")
                continue
            
            # Читаем импортируемый файл
            if os.path.exists(full_import_path):
                try:
                    with open(full_import_path, 'r', encoding='utf-8') as f:
                        import_content = f.read()
                    
                    # Рекурсивно обрабатываем импорты в импортируемом файле
                    nested_imports = self.find_imports(import_content)
                    if nested_imports:
                        # Создаем временный файл для вложенных импортов
                        temp_file = os.path.join(os.path.dirname(output_file), 
                                               f"temp_{os.path.basename(full_import_path)}")
                        self.create_merged_file(full_import_path, temp_file, nested_imports)
                        
                        with open(temp_file, 'r', encoding='utf-8') as f:
                            import_content = f.read()
                        
                        # Удаляем временный файл
                        os.remove(temp_file)
                    
                    # Удаляем директивы импорта из импортируемого файла
                    import_content = self.remove_import_directives(import_content)
                    
                    imported_contents.append({
                        'path': import_path,
                        'content': import_content,
                        'comment': f"; === Импортировано из {import_path} ===\n"
                    })
                    
                    processed_files.add(full_import_path)
                    
                except Exception as e:
                    print(f"❌ Ошибка чтения файла {full_import_path}: {e}")
            else:
                print(f"⚠️ Файл не найден: {full_import_path}")
        
        # Создаем объединенный файл
        with open(output_file, 'w', encoding='utf-8') as f:
            # Записываем заголовок
            f.write("; ===================================================\n")
            f.write("; Автоматически созданный объединенный файл\n")
            f.write(f"; Основной файл: {os.path.basename(main_file)}\n")
            f.write(f"; Импортов: {len(imported_contents)}\n")
            f.write("; ===================================================\n\n")
            
            # Записываем основной файл (без директив импорта)
            main_content_clean = self.remove_import_directives(main_content)
            f.write(main_content_clean)
            
            # Записываем импортированные файлы
            for import_info in imported_contents:
                f.write(f"\n\n{import_info['comment']}")
                f.write(import_info['content'])
                f.write(f"\n; === Конец импорта {import_info['path']} ===\n")
    
    def remove_import_directives(self, content):
        """Удаление директив импорта из содержимого"""
        lines = content.split('\n')
        filtered_lines = []
        
        import_patterns = [
            r'#include\s+"[^"]+"',
            r'#import\s+"[^"]+"',
            r';import\s+\S+',
        ]
        
        for line in lines:
            is_import = False
            for pattern in import_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    is_import = True
                    break
            
            if not is_import:
                filtered_lines.append(line)
            else:
                # Заменяем директиву импорта на комментарий
                filtered_lines.append(f"; {line.strip()} (удалено при объединении)")
        
        return '\n'.join(filtered_lines)
    
    def cleanup_temp_files(self):
        """Очистка временных файлов"""
        temp_dirs = []
        
        # Ищем временные директории
        if hasattr(self.ide, 'current_file') and self.ide.current_file:
            file_dir = os.path.dirname(self.ide.current_file)
            temp_dir = os.path.join(file_dir, '.temp')
            if os.path.exists(temp_dir):
                temp_dirs.append(temp_dir)
        
        # Удаляем временные файлы
        for temp_dir in temp_dirs:
            try:
                shutil.rmtree(temp_dir)
                print(f"🗑️ Удалена временная директория: {temp_dir}")
            except Exception as e:
                print(f"⚠️ Не удалось удалить временную директорию {temp_dir}: {e}")
    
    def create_project_template(self, project_path, project_name):
        """Создание шаблона проекта"""
        try:
            # Создаем структуру директорий
            os.makedirs(project_path, exist_ok=True)
            
            # Создаем основные папки
            folders = ['src', 'include', 'build', 'docs']
            for folder in folders:
                os.makedirs(os.path.join(project_path, folder), exist_ok=True)
            
            # Создаем основной файл
            main_file = os.path.join(project_path, 'src', 'main.asm')
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(f"""; {project_name} - Главный файл
; Создано: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#org 0x0300
jmp main

main:
    ; Очистка регистров
    xor a, a
    xor b, b
    xor c, c
    xor d, d
    
    ; Инициализация стека
    mov sp, 0xFF
    mov bp, 0xFF
    mov ss, 0x00
    
    ; TODO: Добавьте свой код здесь
    
    hlt

; === Функции проекта ===

; TODO: Добавьте свои функции

; === Данные проекта ===

; TODO: Добавьте свои данные
""")
            
            # Создаем файл README
            readme_file = os.path.join(project_path, 'README.md')
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(f"""# {project_name}

Проект для PC Builder - 8-битного компьютерного симулятора.

## Структура проекта

- `src/` - Исходные файлы ассемблера
- `include/` - Подключаемые файлы
- `build/` - Скомпилированные файлы
- `docs/` - Документация

## Сборка

Используйте PC Builder IDE для компиляции проекта.

## Описание

TODO: Опишите ваш проект
""")
            
            print(f"✅ Создан шаблон проекта: {project_path}")
            return main_file
            
        except Exception as e:
            print(f"❌ Ошибка создания проекта: {e}")
            return None
    
    def find_asm_files(self, directory):
        """Поиск всех .asm файлов в директории"""
        asm_files = []
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.asm'):
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, directory)
                        asm_files.append({
                            'name': file,
                            'path': full_path,
                            'relative_path': rel_path,
                            'size': os.path.getsize(full_path)
                        })
        except Exception as e:
            print(f"❌ Ошибка поиска файлов: {e}")
        
        return asm_files
    
    def backup_file(self, file_path):
        """Создание резервной копии файла"""
        if not os.path.exists(file_path):
            return None
        
        try:
            # Создаем папку для бэкапов
            backup_dir = os.path.join(os.path.dirname(file_path), '.backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            # Генерируем имя бэкапа с timestamp
            timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.basename(file_path)
            backup_name = f"{filename}.{timestamp}.bak"
            backup_path = os.path.join(backup_dir, backup_name)
            
            # Копируем файл
            shutil.copy2(file_path, backup_path)
            
            print(f"💾 Создан бэкап: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"❌ Ошибка создания бэкапа: {e}")
            return None
    
    def get_file_info(self, file_path):
        """Получение информации о файле"""
        if not os.path.exists(file_path):
            return None
        
        try:
            stat = os.stat(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Подсчет статистики
            lines = content.split('\n')
            code_lines = 0
            comment_lines = 0
            empty_lines = 0
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    empty_lines += 1
                elif stripped.startswith(';'):
                    comment_lines += 1
                else:
                    code_lines += 1
            
            # Поиск меток и функций
            labels = len(re.findall(r'^\s*([a-zA-Z_\.][a-zA-Z0-9_\.]*)\s*:', content, re.MULTILINE))
            
            return {
                'path': file_path,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'lines_total': len(lines),
                'lines_code': code_lines,
                'lines_comments': comment_lines,
                'lines_empty': empty_lines,
                'labels_count': labels,
                'encoding': 'utf-8'
            }
            
        except Exception as e:
            print(f"❌ Ошибка получения информации о файле: {e}")
            return None
