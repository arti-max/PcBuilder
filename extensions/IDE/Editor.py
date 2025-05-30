import tkinter as tk
from tkinter import ttk, messagebox
import re
from SyntaxHighlighter import SyntaxHighlighter
from Autocomplete import AutocompleteManager

class CodeEditor:
    def __init__(self, parent, ide):
        self.parent = parent
        self.ide = ide
        
        # Создание основного фрейма
        self.main_frame = tk.Frame(parent, bg='#2b2b2b')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создание виджетов
        self.create_widgets()
        
        # Система подсветки синтаксиса
        self.syntax_highlighter = SyntaxHighlighter(self.text_widget)
        
        # Система автодополнения
        self.autocomplete = AutocompleteManager(self.text_widget, ide)
        
        # Привязка событий
        self.bind_events()
        
        # История отмены
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo = 100
        
        print("Редактор кода инициализирован")
    
    def create_widgets(self):
        """Создание виджетов редактора"""
        # Фрейм для номеров строк и текста
        editor_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Номера строк с фиксированной шириной
        self.line_numbers = tk.Text(editor_frame, width=5, padx=5, takefocus=0,
                                border=0, state='disabled', wrap='none',
                                bg='#3c3c3c', fg='#888888',
                                font=('Consolas', 11), cursor='arrow')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Разделитель между номерами строк и текстом
        separator = tk.Frame(editor_frame, bg='#555555', width=1)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Основной текстовый виджет с отступом
        self.text_widget = tk.Text(editor_frame, wrap='none', undo=True,
                                bg='#1e1e1e', fg='#ffffff',
                                insertbackground='#ffffff',
                                selectbackground='#264f78',
                                font=('Consolas', 11),
                                tabs=('1c', '2c', '3c', '4c'),
                                padx=10)
        
        # ИСПРАВЛЕНИЕ: Создаем скроллбары с правильной привязкой
        self.v_scrollbar = tk.Scrollbar(editor_frame, orient=tk.VERTICAL)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.h_scrollbar = tk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # ИСПРАВЛЕНИЕ: Правильная настройка связи скроллбаров
        self.text_widget.config(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )
        self.v_scrollbar.config(command=self.synchronized_scroll)
        self.h_scrollbar.config(command=self.text_widget.xview)
        
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Привязка событий для синхронизации
        self.bind_sync_events()

    def synchronized_scroll(self, *args):
        """Синхронизированная прокрутка текста и номеров строк"""
        # Прокручиваем основной текст
        self.text_widget.yview(*args)
        # Синхронизируем номера строк
        self.line_numbers.yview(*args)
        
    def bind_sync_events(self):
        """Привязка событий для синхронизации"""
        # Обновление при изменении содержимого
        self.text_widget.bind('<KeyPress>', self.on_content_change)
        self.text_widget.bind('<KeyRelease>', self.on_content_change)
        self.text_widget.bind('<Button-1>', self.on_content_change)
        self.text_widget.bind('<ButtonRelease-1>', self.on_content_change)
        
        # ИСПРАВЛЕНИЕ: Правильная обработка колеса мыши
        self.text_widget.bind('<MouseWheel>', self.on_mousewheel)
        self.line_numbers.bind('<MouseWheel>', self.on_mousewheel)
        
        # Синхронизация при прокрутке
        self.text_widget.bind('<Configure>', self.on_text_configure)
    
    def on_text_scroll(self, *args):
        """ИСПРАВЛЕННАЯ обработка прокрутки текста"""
        # Обновляем скроллбар
        if hasattr(self, 'v_scrollbar'):
            self.v_scrollbar.set(*args)
        
        # ИСПРАВЛЕНИЕ: Немедленная синхронизация номеров строк
        self.sync_line_numbers_scroll()
        
        # Возвращаем значение для скроллбара
        return args
    
    def on_scrollbar_move(self, *args):
        """ИСПРАВЛЕННАЯ обработка движения скроллбара"""
        # Прокручиваем текст
        self.text_widget.yview(*args)
        # Синхронизируем номера строк
        self.sync_line_numbers_scroll()

    def update_scrollbar_and_sync(self):
        """Обновление скроллбара и синхронизация"""
        try:
            # Получаем текущую позицию прокрутки
            top, bottom = self.text_widget.yview()
            
            # Обновляем скроллбар
            self.v_scrollbar.set(top, bottom)
            
            # Синхронизируем номера строк
            self.line_numbers.yview_moveto(top)
            
        except tk.TclError:
            pass
    
    def on_mousewheel(self, event):
        """ИСПРАВЛЕННАЯ обработка колеса мыши"""
        # Вычисляем количество строк для прокрутки
        delta = -1 * (event.delta // 120)
        
        # Прокручиваем текст и получаем новую позицию
        self.text_widget.yview_scroll(delta, "units")
        
        # ИСПРАВЛЕНИЕ: Обновляем скроллбар и синхронизируем номера строк
        self.update_scrollbar_and_sync()
        
        return "break"
    
    def sync_line_numbers_scroll(self):
        """ИСПРАВЛЕННАЯ синхронизация прокрутки номеров строк"""
        try:
            # Получаем текущую позицию прокрутки текста
            text_top, text_bottom = self.text_widget.yview()
            
            # Применяем ту же прокрутку к номерам строк
            self.line_numbers.yview_moveto(text_top)
            
        except tk.TclError:
            pass  # Игнорируем ошибки во время обновления
    
    def on_content_change(self, event=None):
        """Обработка изменения содержимого"""
        # Планируем обновление номеров строк
        self.text_widget.after_idle(self.update_line_numbers)
        self.text_widget.after_idle(self.update_cursor_info)
        self.text_widget.after_idle(self.sync_line_numbers_scroll)
    
    def on_text_configure(self, event=None):
        """Обработка изменения конфигурации текста"""
        self.text_widget.after_idle(self.sync_line_numbers_scroll)
    
    def update_line_numbers(self):
        """УЛУЧШЕННОЕ обновление номеров строк"""
        try:
            # Получаем количество строк в тексте
            line_count = int(self.text_widget.index('end-1c').split('.')[0])
            
            # Генерируем номера строк с правильным выравниванием
            line_numbers_text = '\n'.join(f"{i:>4}" for i in range(1, line_count + 1))
            
            # Обновляем виджет номеров строк
            self.line_numbers.config(state='normal')
            self.line_numbers.delete('1.0', 'end')
            self.line_numbers.insert('1.0', line_numbers_text)
            self.line_numbers.config(state='disabled')
            
            # Синхронизируем прокрутку
            self.sync_line_numbers_scroll()
            
        except (tk.TclError, ValueError):
            pass  # Игнорируем ошибки при обновлении
    
    def update_cursor_info(self, event=None):
        """Обновление информации о курсоре"""
        try:
            cursor_pos = self.text_widget.index(tk.INSERT)
            line, column = cursor_pos.split('.')
            self.ide.update_cursor_position(int(line), int(column) + 1)
        except:
            pass
    
    def bind_events(self):
        """Привязка событий"""
        # Отслеживание изменений
        self.text_widget.bind('<<Modified>>', self.on_text_modified)
        self.text_widget.bind('<Control-z>', self.undo)
        self.text_widget.bind('<Control-y>', self.redo)
        
        # Автоотступ
        self.text_widget.bind('<Return>', self.auto_indent)
        self.text_widget.bind('<Tab>', self.handle_tab)
        self.text_widget.bind('<Shift-Tab>', self.handle_shift_tab)
    
    def on_text_modified(self, event):
        """Обработка изменения текста"""
        if self.text_widget.edit_modified():
            self.ide.set_modified(True)
            self.text_widget.edit_modified(False)
    
    def auto_indent(self, event):
        """Автоматический отступ"""
        # Получаем текущую строку
        current_line = self.text_widget.get('insert linestart', 'insert')
        
        # Вычисляем отступ
        indent = ''
        for char in current_line:
            if char in ' \t':
                indent += char
            else:
                break
        
        # Добавляем дополнительный отступ после меток или директив
        stripped_line = current_line.strip()
        if stripped_line.endswith(':') or stripped_line.startswith('#'):
            indent += '    '  # 4 пробела
        
        # Вставляем новую строку с отступом
        self.text_widget.insert('insert', f'\n{indent}')
        return 'break'
    
    def handle_tab(self, event):
        """Обработка табуляции"""
        try:
            sel_start = self.text_widget.index('sel.first')
            sel_end = self.text_widget.index('sel.last')
            
            start_line = int(sel_start.split('.')[0])
            end_line = int(sel_end.split('.')[0])
            
            for line_num in range(start_line, end_line + 1):
                self.text_widget.insert(f'{line_num}.0', '    ')
            
            return 'break'
        except tk.TclError:
            self.text_widget.insert('insert', '    ')
            return 'break'
    
    def handle_shift_tab(self, event):
        """Обработка Shift+Tab"""
        try:
            sel_start = self.text_widget.index('sel.first')
            sel_end = self.text_widget.index('sel.last')
            
            start_line = int(sel_start.split('.')[0])
            end_line = int(sel_end.split('.')[0])
            
            for line_num in range(start_line, end_line + 1):
                line_start = f'{line_num}.0'
                line_text = self.text_widget.get(line_start, f'{line_num}.end')
                
                spaces_to_remove = 0
                for char in line_text[:4]:
                    if char == ' ':
                        spaces_to_remove += 1
                    else:
                        break
                
                if spaces_to_remove > 0:
                    self.text_widget.delete(line_start, f'{line_num}.{spaces_to_remove}')
            
            return 'break'
        except tk.TclError:
            return 'break'
    
    def save_undo_state(self):
        """Сохранение состояния для отмены"""
        content = self.text_widget.get('1.0', 'end-1c')
        cursor_pos = self.text_widget.index('insert')
        
        self.undo_stack.append((content, cursor_pos))
        
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack.pop(0)
        
        self.redo_stack.clear()
    
    def undo(self, event=None):
        """Отмена действия"""
        if self.undo_stack:
            current_content = self.text_widget.get('1.0', 'end-1c')
            current_cursor = self.text_widget.index('insert')
            self.redo_stack.append((current_content, current_cursor))
            
            content, cursor_pos = self.undo_stack.pop()
            self.set_content(content)
            self.text_widget.mark_set('insert', cursor_pos)
            
            return 'break'
    
    def redo(self, event=None):
        """Повтор действия"""
        if self.redo_stack:
            current_content = self.text_widget.get('1.0', 'end-1c')
            current_cursor = self.text_widget.index('insert')
            self.undo_stack.append((current_content, current_cursor))
            
            content, cursor_pos = self.redo_stack.pop()
            self.set_content(content)
            self.text_widget.mark_set('insert', cursor_pos)
            
            return 'break'
    
    def get_content(self):
        """Получение содержимого редактора"""
        return self.text_widget.get('1.0', 'end-1c')
    
    def set_content(self, content):
        """Установка содержимого редактора"""
        self.text_widget.delete('1.0', 'end')
        self.text_widget.insert('1.0', content)
        self.syntax_highlighter.highlight_syntax()
        self.update_line_numbers()
    
    def clear(self):
        """Очистка редактора"""
        self.text_widget.delete('1.0', 'end')
        self.update_line_numbers()
    
    def apply_settings(self, settings):
        """Применение настроек"""
        editor_settings = settings.get('editor', {})
        theme_settings = settings.get('theme', {})
        
        # Шрифт
        font_family = editor_settings.get('font_family', 'Consolas')
        font_size = editor_settings.get('font_size', 11)
        font = (font_family, font_size)
        
        self.text_widget.config(font=font)
        self.line_numbers.config(font=font)
        
        # Цвета
        bg_color = theme_settings.get('background', '#1e1e1e')
        fg_color = theme_settings.get('foreground', '#ffffff')
        
        self.text_widget.config(bg=bg_color, fg=fg_color)
        self.line_numbers.config(bg='#3c3c3c', fg='#888888')
        
        # Обновляем подсветку синтаксиса
        self.syntax_highlighter.update_colors(theme_settings)
        self.syntax_highlighter.highlight_syntax()
        
        # Размер табуляции
        tab_width = editor_settings.get('tab_width', 4)
        tabs = tuple(f'{i}c' for i in range(tab_width, tab_width * 20, tab_width))
        self.text_widget.config(tabs=tabs)
    
    def goto_line(self, line_number):
        """Переход к строке"""
        self.text_widget.mark_set('insert', f'{line_number}.0')
        self.text_widget.see('insert')
        self.text_widget.focus_set()


class FindDialog:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.create_dialog()
    
    def create_dialog(self):
        """Создание диалога поиска"""
        self.dialog = tk.Toplevel()
        self.dialog.title("Поиск")
        self.dialog.geometry("400x120")
        self.dialog.configure(bg='#2b2b2b')
        self.dialog.transient(self.text_widget.winfo_toplevel())
        
        # Поле поиска
        tk.Label(self.dialog, text="Найти:", bg='#2b2b2b', fg='white').pack(anchor='w', padx=10, pady=5)
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(self.dialog, textvariable=self.search_var,
                               bg='#3c3c3c', fg='white', insertbackground='white')
        search_entry.pack(fill='x', padx=10, pady=5)
        search_entry.focus_set()
        
        # Кнопки
        button_frame = tk.Frame(self.dialog, bg='#2b2b2b')
        button_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(button_frame, text="Найти далее", bg='#0e639c', fg='white',
                 border=0, command=self.find_next).pack(side='left', padx=(0, 5))
        
        tk.Button(button_frame, text="Найти назад", bg='#4c4c4c', fg='white',
                 border=0, command=self.find_previous).pack(side='left', padx=(0, 5))
        
        tk.Button(button_frame, text="Закрыть", bg='#4c4c4c', fg='white',
                 border=0, command=self.dialog.destroy).pack(side='right')
        
        # Привязка Enter
        search_entry.bind('<Return>', lambda e: self.find_next())
        
        self.last_search = None
        self.last_index = '1.0'
    
    def find_next(self):
        """Поиск вперед"""
        search_text = self.search_var.get()
        if not search_text:
            return
        
        # Если новый поиск, начинаем с текущей позиции
        if search_text != self.last_search:
            self.last_index = self.text_widget.index('insert')
            self.last_search = search_text
        
        # Ищем текст
        pos = self.text_widget.search(search_text, self.last_index, 'end')
        if pos:
            # Выделяем найденный текст
            end_pos = f"{pos}+{len(search_text)}c"
            self.text_widget.tag_remove('sel', '1.0', 'end')
            self.text_widget.tag_add('sel', pos, end_pos)
            self.text_widget.mark_set('insert', end_pos)
            self.text_widget.see(pos)
            
            self.last_index = end_pos
        else:
            # Не найдено, начинаем с начала
            self.last_index = '1.0'
            messagebox.showinfo("Поиск", f"Текст '{search_text}' не найден")
    
    def find_previous(self):
        """Поиск назад"""
        search_text = self.search_var.get()
        if not search_text:
            return
        
        current_pos = self.text_widget.index('insert')
        pos = self.text_widget.search(search_text, current_pos, '1.0', backwards=True)
        
        if pos:
            end_pos = f"{pos}+{len(search_text)}c"
            self.text_widget.tag_remove('sel', '1.0', 'end')
            self.text_widget.tag_add('sel', pos, end_pos)
            self.text_widget.mark_set('insert', pos)
            self.text_widget.see(pos)
        else:
            messagebox.showinfo("Поиск", f"Текст '{search_text}' не найден")

class ReplaceDialog:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.create_dialog()
    
    def create_dialog(self):
        """Создание диалога замены"""
        self.dialog = tk.Toplevel()
        self.dialog.title("Найти и заменить")
        self.dialog.geometry("400x180")
        self.dialog.configure(bg='#2b2b2b')
        self.dialog.transient(self.text_widget.winfo_toplevel())
        
        # Поле поиска
        tk.Label(self.dialog, text="Найти:", bg='#2b2b2b', fg='white').pack(anchor='w', padx=10, pady=5)
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(self.dialog, textvariable=self.search_var,
                               bg='#3c3c3c', fg='white', insertbackground='white')
        search_entry.pack(fill='x', padx=10, pady=5)
        
        # Поле замены
        tk.Label(self.dialog, text="Заменить на:", bg='#2b2b2b', fg='white').pack(anchor='w', padx=10, pady=5)
        
        self.replace_var = tk.StringVar()
        replace_entry = tk.Entry(self.dialog, textvariable=self.replace_var,
                                bg='#3c3c3c', fg='white', insertbackground='white')
        replace_entry.pack(fill='x', padx=10, pady=5)
        
        # Кнопки
        button_frame = tk.Frame(self.dialog, bg='#2b2b2b')
        button_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(button_frame, text="Найти", bg='#4c4c4c', fg='white',
                 border=0, command=self.find_next).pack(side='left', padx=(0, 5))
        
        tk.Button(button_frame, text="Заменить", bg='#0e639c', fg='white',
                 border=0, command=self.replace_current).pack(side='left', padx=(0, 5))
        
        tk.Button(button_frame, text="Заменить всё", bg='#b5651d', fg='white',
                 border=0, command=self.replace_all).pack(side='left', padx=(0, 5))
        
        tk.Button(button_frame, text="Закрыть", bg='#4c4c4c', fg='white',
                 border=0, command=self.dialog.destroy).pack(side='right')
        
        search_entry.focus_set()
    
    def find_next(self):
        """Поиск следующего вхождения"""
        search_text = self.search_var.get()
        if not search_text:
            return
        
        current_pos = self.text_widget.index('insert')
        pos = self.text_widget.search(search_text, current_pos, 'end')
        
        if pos:
            end_pos = f"{pos}+{len(search_text)}c"
            self.text_widget.tag_remove('sel', '1.0', 'end')
            self.text_widget.tag_add('sel', pos, end_pos)
            self.text_widget.mark_set('insert', end_pos)
            self.text_widget.see(pos)
        else:
            messagebox.showinfo("Поиск", f"Текст '{search_text}' не найден")
    
    def replace_current(self):
        """Замена текущего выделения"""
        try:
            # Проверяем, есть ли выделение
            sel_start = self.text_widget.index('sel.first')
            sel_end = self.text_widget.index('sel.last')
            
            # Заменяем выделенный текст
            self.text_widget.delete(sel_start, sel_end)
            self.text_widget.insert(sel_start, self.replace_var.get())
            
            # Ищем следующее вхождение
            self.find_next()
            
        except tk.TclError:
            # Нет выделения, просто ищем
            self.find_next()
    
    def replace_all(self):
        """Замена всех вхождений"""
        search_text = self.search_var.get()
        replace_text = self.replace_var.get()
        
        if not search_text:
            return
        
        content = self.text_widget.get('1.0', 'end-1c')
        count = content.count(search_text)
        
        if count > 0:
            new_content = content.replace(search_text, replace_text)
            self.text_widget.delete('1.0', 'end')
            self.text_widget.insert('1.0', new_content)
            
            messagebox.showinfo("Замена", f"Заменено {count} вхождений")
        else:
            messagebox.showinfo("Замена", f"Текст '{search_text}' не найден")
