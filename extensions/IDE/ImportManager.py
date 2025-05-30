import os
import re
import tkinter as tk
from tkinter import messagebox

class ImportManager:
    def __init__(self, ide):
        self.ide = ide
        self.import_patterns = [
            r'#include\s+"([^"]+)"',      # #include "file.asm"
            r'#import\s+"([^"]+)"',       # #import "file.asm"  
            r';@import\s+([^\s;]+)',      # ;@import file.asm
        ]
        
    def find_imports(self, content, file_path=None):
        """Поиск импортов в коде"""
        imports = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern in self.import_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    import_path = match.group(1)
                    
                    # Разрешаем относительный путь
                    if file_path and not os.path.isabs(import_path):
                        base_dir = os.path.dirname(file_path)
                        full_path = os.path.join(base_dir, import_path)
                    else:
                        full_path = import_path
                    
                    imports.append({
                        'path': import_path,
                        'full_path': os.path.normpath(full_path),
                        'line': line_num,
                        'pattern': match.group(0),
                        'exists': os.path.exists(full_path) if full_path else False
                    })
        
        return imports
    
    def resolve_imports(self, content, file_path):
        """Разрешение импортов и создание объединенного кода"""
        imports = self.find_imports(content, file_path)
        
        if not imports:
            return content, []
        
        # Проверяем существование файлов
        missing_files = [imp for imp in imports if not imp['exists']]
        if missing_files:
            self.show_missing_files_dialog(missing_files)
            return content, imports
        
        # Создаем объединенный код
        merged_content = self.create_merged_content(content, imports, file_path)
        return merged_content, imports
    
    def create_merged_content(self, main_content, imports, main_file_path):
        """Создание объединенного содержимого"""
        processed_files = set()
        merged_lines = []
        
        # Обрабатываем основной файл
        main_lines = main_content.split('\n')
        
        for line in main_lines:
            # Проверяем, является ли строка импортом
            is_import_line = False
            for pattern in self.import_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    is_import_line = True
                    break
            
            if is_import_line:
                # Заменяем импорт на комментарий
                merged_lines.append(f"; {line.strip()} (resolved by IDE)")
            else:
                merged_lines.append(line)
        
        # Добавляем импортированные файлы в конец
        merged_lines.append("")
        merged_lines.append("; === IMPORTED FILES ===")
        
        for import_info in imports:
            if import_info['full_path'] not in processed_files:
                try:
                    with open(import_info['full_path'], 'r', encoding='utf-8') as f:
                        import_content = f.read()
                    
                    merged_lines.append(f"\n; === From {import_info['path']} ===")
                    
                    # Рекурсивно обрабатываем импорты в импортированном файле
                    resolved_import, _ = self.resolve_imports(import_content, import_info['full_path'])
                    
                    # Удаляем директивы org из импортированных файлов
                    import_lines = resolved_import.split('\n')
                    for import_line in import_lines:
                        if not import_line.strip().lower().startswith('#org'):
                            merged_lines.append(import_line)
                    
                    merged_lines.append(f"; === End of {import_info['path']} ===")
                    processed_files.add(import_info['full_path'])
                    
                except Exception as e:
                    merged_lines.append(f"; ERROR: Could not import {import_info['path']}: {e}")
        
        return '\n'.join(merged_lines)
    
    def show_missing_files_dialog(self, missing_files):
        """Показ диалога о недостающих файлах"""
        message = "Не найдены следующие импортируемые файлы:\n\n"
        for file_info in missing_files:
            message += f"• {file_info['path']} (строка {file_info['line']})\n"
        
        message += "\nКомпиляция будет выполнена без разрешения импортов."
        
        messagebox.showwarning("Недостающие импорты", message)
    
    def insert_import_directive(self, file_path):
        """Вставка директивы импорта в текущий файл"""
        if not self.ide.current_file:
            messagebox.showwarning("Предупреждение", "Сначала сохраните текущий файл")
            return
        
        # Вычисляем относительный путь
        try:
            current_dir = os.path.dirname(self.ide.current_file)
            rel_path = os.path.relpath(file_path, current_dir)
            
            # Создаем директиву импорта
            import_directive = f'#include "{rel_path}"\n'
            
            # Вставляем в начало файла (после директив org)
            current_content = self.ide.editor.get_content()
            lines = current_content.split('\n')
            
            insert_line = 0
            # Ищем место для вставки после org директив
            for i, line in enumerate(lines):
                if line.strip().lower().startswith('#org'):
                    insert_line = i + 1
                elif line.strip() and not line.strip().startswith(';'):
                    break
            
            lines.insert(insert_line, import_directive)
            new_content = '\n'.join(lines)
            
            self.ide.editor.set_content(new_content)
            self.ide.set_modified(True)
            
            self.ide.update_status(f"Добавлен импорт: {rel_path}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить импорт: {e}")
