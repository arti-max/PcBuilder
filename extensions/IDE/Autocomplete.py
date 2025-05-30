import tkinter as tk
from tkinter import ttk
import re

class AutocompleteManager:
    def __init__(self, text_widget, ide):
        self.text_widget = text_widget
        self.ide = ide
        self.popup_window = None
        self.listbox = None
        self.current_suggestions = []
        
        # Словарь инструкций процессора
        self.instructions = {
            # Базовые команды
            'nop': {'args': 0, 'desc': 'Нет операции'},
            'mov': {'args': 2, 'desc': 'mov dst, src - Копирование данных'},
            'ld': {'args': 2, 'desc': 'ld reg, value - Загрузка значения'},
            'hlt': {'args': 0, 'desc': 'Остановка процессора'},
            
            # Арифметика
            'add': {'args': 2, 'desc': 'add reg1, reg2 - Сложение'},
            'sub': {'args': 2, 'desc': 'sub reg1, reg2 - Вычитание'},
            'inc': {'args': 1, 'desc': 'inc reg - Увеличение на 1'},
            'dec': {'args': 1, 'desc': 'dec reg - Уменьшение на 1'},
            
            # Логика
            'xor': {'args': 2, 'desc': 'xor reg1, reg2 - Исключающее ИЛИ'},
            'or': {'args': 2, 'desc': 'or reg1, reg2 - Логическое ИЛИ'},
            'and': {'args': 2, 'desc': 'and reg1, reg2 - Логическое И'},
            'not': {'args': 1, 'desc': 'not reg - Логическое НЕ'},
            'shl': {'args': 1, 'desc': 'shl reg - Сдвиг влево'},
            'shr': {'args': 1, 'desc': 'shr reg - Сдвиг вправо'},
            
            # Сравнение и переходы
            'cmp': {'args': 2, 'desc': 'cmp op1, op2 - Сравнение'},
            'jmp': {'args': 1, 'desc': 'jmp address - Безусловный переход'},
            'je': {'args': 1, 'desc': 'je address - Переход если равно'},
            'jne': {'args': 1, 'desc': 'jne address - Переход если не равно'},
            
            # Подпрограммы
            'call': {'args': 1, 'desc': 'call address - Вызов подпрограммы'},
            'ret': {'args': 0, 'desc': 'Возврат из подпрограммы'},
            'push': {'args': 1, 'desc': 'push reg - Положить в стек'},
            'pop': {'args': 1, 'desc': 'pop reg - Взять из стека'},
            
            # Память
            'ldm': {'args': 2, 'desc': 'ldm reg, [address] - Загрузка из памяти'},
            'stm': {'args': 2, 'desc': 'stm [address], reg - Сохранение в память'},
            
            # Устройства
            'in': {'args': 2, 'desc': 'in port, reg - Чтение с порта'},
            'out': {'args': 2, 'desc': 'out port, reg - Запись в порт'},
        }
        
        # Регистры
        self.registers = ['a', 'b', 'c', 'd', 'ip', 'ir', 'sp', 'bp', 'ss']
        
        # Директивы
        self.directives = ['#org', '#db']
        
        # Настройки
        self.min_chars = 1
        self.case_sensitive = False
        self.enabled = True
        
        print("🔮 Автодополнение инициализировано")
    
    def check_autocomplete(self):
        """Проверка необходимости показа автодополнения"""
        if not self.enabled:
            return
        
        # Получаем текущее слово
        current_word = self.get_current_word()
        
        if len(current_word) >= self.min_chars:
            suggestions = self.get_suggestions(current_word)
            
            if suggestions:
                self.show_popup(suggestions)
            else:
                self.hide_popup()
        else:
            self.hide_popup()
    
    def get_current_word(self):
        """Получение текущего слова под курсором"""
        try:
            # Получаем позицию курсора
            cursor_pos = self.text_widget.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            col = int(col)
            
            # Получаем текущую строку
            line_text = self.text_widget.get(f'{line}.0', f'{line}.end')
            
            # Находим границы слова
            start = col
            while start > 0 and (line_text[start-1].isalnum() or line_text[start-1] in '_#'):
                start -= 1
            
            end = col
            while end < len(line_text) and (line_text[end].isalnum() or line_text[end] in '_'):
                end += 1
            
            return line_text[start:col]
        except:
            return ""
    
    def get_suggestions(self, word):
        """Получение списка предложений"""
        suggestions = []
        
        if not self.case_sensitive:
            word = word.lower()
        
        # Инструкции
        for instruction, info in self.instructions.items():
            if instruction.startswith(word):
                suggestions.append({
                    'text': instruction,
                    'type': 'instruction',
                    'description': info['desc']
                })
        
        # Регистры
        for register in self.registers:
            if register.startswith(word):
                suggestions.append({
                    'text': register,
                    'type': 'register',
                    'description': f'Регистр {register.upper()}'
                })
        
        # Директивы
        for directive in self.directives:
            if directive.startswith(word):
                suggestions.append({
                    'text': directive,
                    'type': 'directive',
                    'description': f'Директива {directive}'
                })
        
        # Метки из кода
        labels = self.get_labels_from_code()
        for label in labels:
            if label.startswith(word):
                suggestions.append({
                    'text': label,
                    'type': 'label',
                    'description': f'Метка {label}'
                })
        
        return suggestions[:10]  # Ограничиваем количество
    
    def get_labels_from_code(self):
        """Извлечение меток из кода"""
        content = self.text_widget.get('1.0', 'end-1c')
        labels = []
        
        # Ищем метки (слово с двоеточием)
        for line in content.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith(';'):
                # Проверяем, что это метка, а не адресация памяти
                before_colon = line.split(':')[0].strip()
                if before_colon and not any(char in before_colon for char in ['[', ']', ' ', '\t']):
                    labels.append(before_colon)
        
        return labels
    
    def show_popup(self, suggestions):
        """Показ popup с предложениями"""
        self.current_suggestions = suggestions
        
        if self.popup_window:
            self.hide_popup()
        
        # Получаем позицию курсора на экране
        cursor_pos = self.text_widget.index(tk.INSERT)
        x, y, _, _ = self.text_widget.bbox(cursor_pos)
        
        # Преобразуем в абсолютные координаты
        abs_x = self.text_widget.winfo_rootx() + x
        abs_y = self.text_widget.winfo_rooty() + y + 20
        
        # Создаем popup окно
        self.popup_window = tk.Toplevel(self.text_widget)
        self.popup_window.wm_overrideredirect(True)
        self.popup_window.geometry(f"+{abs_x}+{abs_y}")
        self.popup_window.configure(bg='#2b2b2b', relief='solid', bd=1)
        
        # Создаем listbox
        self.listbox = tk.Listbox(self.popup_window, height=min(8, len(suggestions)),
                                 bg='#2b2b2b', fg='white', selectbackground='#0e639c',
                                 border=0, font=('Consolas', 10))
        self.listbox.pack()
        
        # Заполняем предложения
        for suggestion in suggestions:
            display_text = self.format_suggestion(suggestion)
            self.listbox.insert(tk.END, display_text)
        
        # Выбираем первый элемент
        if suggestions:
            self.listbox.selection_set(0)
        
        # Привязываем события
        self.listbox.bind('<Double-Button-1>', self.insert_suggestion)
        self.listbox.bind('<Return>', self.insert_suggestion)
        self.text_widget.bind('<Escape>', lambda e: self.hide_popup())
        self.text_widget.bind('<Down>', self.handle_down_arrow)
        self.text_widget.bind('<Up>', self.handle_up_arrow)
        self.text_widget.bind('<Tab>', self.insert_suggestion)
        
        # Фокус остается на тексте
        self.text_widget.focus_set()
    
    def format_suggestion(self, suggestion):
        """Форматирование предложения для отображения"""
        text = suggestion['text']
        type_icon = {
            'instruction': '⚙️',
            'register': '📋',
            'directive': '📝',
            'label': '🏷️'
        }.get(suggestion['type'], '•')
        
        return f"{type_icon} {text}"
    
    def hide_popup(self):
        """Скрытие popup"""
        if self.popup_window:
            self.popup_window.destroy()
            self.popup_window = None
            self.listbox = None
        
        # Убираем привязки
        self.text_widget.unbind('<Down>')
        self.text_widget.unbind('<Up>')
        self.text_widget.unbind('<Tab>')
    
    def handle_down_arrow(self, event):
        """Обработка стрелки вниз"""
        if self.listbox:
            current = self.listbox.curselection()
            if current:
                next_index = min(current[0] + 1, self.listbox.size() - 1)
            else:
                next_index = 0
            
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(next_index)
            self.listbox.see(next_index)
            return 'break'
    
    def handle_up_arrow(self, event):
        """Обработка стрелки вверх"""
        if self.listbox:
            current = self.listbox.curselection()
            if current:
                next_index = max(current[0] - 1, 0)
            else:
                next_index = 0
            
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(next_index)
            self.listbox.see(next_index)
            return 'break'
    
    def insert_suggestion(self, event=None):
        """Вставка выбранного предложения"""
        if not self.listbox or not self.current_suggestions:
            return
        
        selection = self.listbox.curselection()
        if not selection:
            return
        
        suggestion = self.current_suggestions[selection[0]]
        suggestion_text = suggestion['text']
        
        # Получаем текущее слово и заменяем его
        current_word = self.get_current_word()
        cursor_pos = self.text_widget.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        col = int(col)
        
        # Вычисляем позицию начала слова
        start_col = col - len(current_word)
        
        # Удаляем текущее слово и вставляем предложение
        self.text_widget.delete(f'{line}.{start_col}', f'{line}.{col}')
        self.text_widget.insert(f'{line}.{start_col}', suggestion_text)
        
        # Добавляем шаблон аргументов для инструкций
        if suggestion['type'] == 'instruction':
            self.insert_instruction_template(suggestion_text, suggestion)
        
        self.hide_popup()
        return 'break'
    
    def insert_instruction_template(self, instruction, info):
        """Вставка шаблона аргументов для инструкции"""
        templates = {
            'mov': ' a, b',
            'ld': ' a, 42',
            'add': ' a, b',
            'sub': ' a, b',
            'cmp': ' a, b',
            'jmp': ' label',
            'je': ' label',
            'jne': ' label',
            'call': ' function',
            'push': ' a',
            'pop': ' a',
            'inc': ' a',
            'dec': ' a',
            'in': ' port, reg',
            'out': ' port, reg',
            'ldm': ' a, [address]',
            'stm': ' [address], a',
            '#org': ' 0x0300',
            '#db': ' 0x00, 0x01'
        }
        
        template = templates.get(instruction, '')
        if template:
            # Вставляем шаблон и выделяем первый аргумент
            start_pos = self.text_widget.index(tk.INSERT)
            self.text_widget.insert(tk.INSERT, template)
            
            # Выделяем первый аргумент для быстрого редактирования
            if ' ' in template:
                first_arg_start = template.find(' ') + 1
                first_arg = template[first_arg_start:].split(',')[0].split(' ')[0]
                
                line, col = start_pos.split('.')
                col = int(col)
                
                arg_start = f'{line}.{col + first_arg_start}'
                arg_end = f'{line}.{col + first_arg_start + len(first_arg)}'
                
                self.text_widget.tag_add('sel', arg_start, arg_end)
                self.text_widget.mark_set(tk.INSERT, arg_end)
    
    def update_settings(self, settings):
        """Обновление настроек автодополнения"""
        autocomplete_settings = settings.get('autocomplete', {})
        self.enabled = autocomplete_settings.get('enabled', True)
        self.case_sensitive = autocomplete_settings.get('case_sensitive', False)
        self.min_chars = autocomplete_settings.get('min_chars', 1)
