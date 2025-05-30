import tkinter as tk
from tkinter import ttk
import re

class LabelNavigator:
    def __init__(self, parent, ide):
        self.parent = parent
        self.ide = ide
        self.labels = []
        
        # Создание основного фрейма
        self.main_frame = tk.LabelFrame(parent, text="Навигация по меткам", 
                                       bg='#2b2b2b', fg='white', font=('Consolas', 10))
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Поле поиска
        search_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(search_frame, text="🔍", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                    bg='#3c3c3c', fg='white', insertbackground='white',
                                    font=('Consolas', 9))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.search_var.trace('w', self.filter_labels)
        
        # Дерево меток
        tree_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Стиль для Treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background='#1e1e1e', foreground='white',
                       fieldbackground='#1e1e1e', borderwidth=0)
        style.configure('Treeview.Heading', background='#3c3c3c', foreground='white',
                       borderwidth=1, relief='flat')
        style.map('Treeview', background=[('selected', '#0e639c')])
        
        # Создание Treeview
        self.tree = ttk.Treeview(tree_frame, height=15, selectmode='extended')
        self.tree.heading('#0', text='Метки и функции', anchor='w')
        self.tree.column('#0', width=200, minwidth=150)
        
        # Скроллбар для дерева
        scrollbar = tk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение виджетов
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # События
        self.tree.bind('<Double-1>', self.goto_label)
        self.tree.bind('<Return>', self.goto_label)
        
        # Контекстное меню
        self.context_menu = tk.Menu(self.tree, tearoff=0, bg='#3c3c3c', fg='white')
        self.context_menu.add_command(label="Перейти к метке", command=self.goto_selected_label)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Копировать имя", command=self.copy_label_name)
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # Обновляем метки
        self.update_labels()
        
        print("🧭 Навигатор меток инициализирован")
    
    def update_labels(self):
        """Обновление списка меток"""
        if not hasattr(self.ide, 'editor') or not self.ide.editor:
            return
        
        content = self.ide.editor.get_content()
        self.labels = self.parse_labels(content)
        self.populate_tree()
    
    def parse_labels(self, content):
        """Парсинг меток из кода"""
        labels = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            original_line = line
            line = line.strip()
            
            # Пропускаем комментарии
            if line.startswith(';') or not line:
                continue
            
            # Убираем комментарии в конце строки
            if ';' in line:
                line = line.split(';')[0].strip()
            
            # Ищем метки (слово с двоеточием)
            if ':' in line:
                label_part = line.split(':')[0].strip()
                
                # Проверяем, что это действительно метка
                if (label_part and 
                    not any(char in label_part for char in ['[', ']', ' ', '\t']) and
                    not label_part.startswith('#')):
                    
                    label_type = self.determine_label_type(label_part, original_line)
                    labels.append({
                        'name': label_part,
                        'line': line_num,
                        'type': label_type,
                        'full_line': original_line.strip()
                    })
            
            # Ищем директивы
            elif line.startswith('#'):
                directive_match = re.match(r'#(\w+)', line)
                if directive_match:
                    directive_name = directive_match.group(1)
                    labels.append({
                        'name': f"#{directive_name}",
                        'line': line_num,
                        'type': 'directive',
                        'full_line': original_line.strip()
                    })
        
        return labels
    
    def determine_label_type(self, label_name, full_line):
        """Определение типа метки"""
        if label_name.startswith('.'):
            return 'local'
        elif any(keyword in full_line.lower() for keyword in ['main', 'start', 'begin']):
            return 'main'
        elif any(keyword in full_line.lower() for keyword in ['loop', 'repeat']):
            return 'loop'
        elif any(keyword in full_line.lower() for keyword in ['end', 'exit', 'return']):
            return 'end'
        elif any(keyword in full_line.lower() for keyword in ['data', 'table', 'buffer']):
            return 'data'
        else:
            return 'function'
    
    def populate_tree(self):
        """Заполнение дерева метками"""
        # Очищаем дерево
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.labels:
            # Показываем сообщение, если меток нет
            self.tree.insert('', 'end', text='📝 Метки не найдены', values=('',))
            return
        
        # Группируем метки по типам
        grouped_labels = {}
        for label in self.labels:
            label_type = label['type']
            if label_type not in grouped_labels:
                grouped_labels[label_type] = []
            grouped_labels[label_type].append(label)
        
        # Иконки для типов
        type_icons = {
            'main': '🏠',
            'function': '⚙️',
            'loop': '🔄',
            'local': '📍',
            'data': '📊',
            'directive': '📝',
            'end': '🏁'
        }
        
        # Названия групп
        type_names = {
            'main': 'Главные функции',
            'function': 'Функции',
            'loop': 'Циклы',
            'local': 'Локальные метки',
            'data': 'Данные',
            'directive': 'Директивы',
            'end': 'Завершающие метки'
        }
        
        # Порядок отображения групп
        type_order = ['directive', 'main', 'function', 'loop', 'data', 'local', 'end']
        
        for label_type in type_order:
            if label_type in grouped_labels:
                type_icon = type_icons.get(label_type, '•')
                type_name = type_names.get(label_type, label_type.title())
                
                # Создаем группу
                group_item = self.tree.insert('', 'end', 
                                             text=f'{type_icon} {type_name} ({len(grouped_labels[label_type])})',
                                             values=('group',), open=True)
                
                # Добавляем метки в группу
                for label in grouped_labels[label_type]:
                    item_text = f"  {label['name']} (строка {label['line']})"
                    self.tree.insert(group_item, 'end', text=item_text, 
                                   values=(label['line'], label['name']))
    
    def filter_labels(self, *args):
        """Фильтрация меток по поиску"""
        search_text = self.search_var.get().lower()
        
        if not search_text:
            self.populate_tree()
            return
        
        # Фильтруем метки
        filtered_labels = []
        for label in self.labels:
            if search_text in label['name'].lower():
                filtered_labels.append(label)
        
        # Очищаем дерево
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not filtered_labels:
            self.tree.insert('', 'end', text=f'🔍 Ничего не найдено для "{search_text}"', values=('',))
            return
        
        # Показываем отфильтрованные результаты
        search_item = self.tree.insert('', 'end', 
                                      text=f'🔍 Результаты поиска ({len(filtered_labels)})',
                                      values=('group',), open=True)
        
        for label in filtered_labels:
            item_text = f"  {label['name']} (строка {label['line']})"
            self.tree.insert(search_item, 'end', text=item_text,
                           values=(label['line'], label['name']))
    
    def goto_label(self, event=None):
        """Переход к выбранной метке"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item)['values']
        
        if values and values[0] != 'group' and values[0]:
            try:
                line_number = int(values[0])
                self.ide.editor.goto_line(line_number)
                print(f"🎯 Переход к строке {line_number}")
            except (ValueError, IndexError):
                pass
    
    def goto_selected_label(self):
        """Переход к выбранной метке (из контекстного меню)"""
        self.goto_label()
    
    def copy_label_name(self):
        """Копирование имени метки в буфер обмена"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item)['values']
        
        if values and len(values) > 1:
            label_name = values[1]
            self.ide.root.clipboard_clear()
            self.ide.root.clipboard_append(label_name)
            self.ide.update_status(f"📋 Скопировано: {label_name}")
    
    def show_context_menu(self, event):
        """Показ контекстного меню"""
        # Выбираем элемент под курсором
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            # Проверяем, что это не группа
            values = self.tree.item(item)['values']
            if values and values[0] != 'group':
                self.context_menu.post(event.x_root, event.y_root)
    
    def highlight_label(self, label_name):
        """Подсветка метки в навигаторе"""
        # Ищем метку в дереве и выделяем её
        for item in self.tree.get_children():
            for child in self.tree.get_children(item):
                values = self.tree.item(child)['values']
                if values and len(values) > 1 and values[1] == label_name:
                    self.tree.selection_set(child)
                    self.tree.see(child)
                    break
