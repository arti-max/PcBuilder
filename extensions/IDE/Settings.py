import tkinter as tk
from tkinter import ttk, colorchooser, filedialog
import json
import os

class SettingsManager:
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        self.default_settings = {
            'editor': {
                'font_family': 'Consolas',
                'font_size': 11,
                'tab_width': 4,
                'line_numbers': True,
                'word_wrap': False,
                'auto_indent': True,
                'highlight_current_line': True
            },
            'theme': {
                'background': '#1e1e1e',
                'foreground': '#ffffff',
                'keyword_color': '#569cd6',
                'comment_color': '#6a9955',
                'string_color': '#ce9178',
                'number_color': '#b5cea8',
                'label_color': '#dcdcaa',
                'current_line': '#2d2d2d'
            },
            'compiler': {
                'path': '../asm/Assembler.py',
                'default_output': 'bin',
                'auto_save_before_compile': True
            },
            'autocomplete': {
                'enabled': True,
                'case_sensitive': False,
                'min_chars': 1
            }
        }
    
    def load_settings(self):
        """Загрузка настроек из файла"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # Объединяем с настройками по умолчанию
                return self._merge_settings(self.default_settings, settings)
            else:
                return self.default_settings.copy()
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
            return self.default_settings.copy()
    
    def save_settings(self, settings):
        """Сохранение настроек в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
            return False
    
    def _merge_settings(self, default, user):
        """Объединение настроек пользователя с настройками по умолчанию"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        return result
    
    def get_setting(self, section, key, default=None):
        """Получение конкретной настройки"""
        settings = self.load_settings()
        return settings.get(section, {}).get(key, default)
    
    def set_setting(self, section, key, value):
        """Установка конкретной настройки"""
        settings = self.load_settings()
        if section not in settings:
            settings[section] = {}
        settings[section][key] = value
        self.save_settings(settings)
    
    def show_settings_dialog(self, parent):
        """Показ диалога настроек"""
        dialog = SettingsDialog(parent, self)
        dialog.show()

class SettingsDialog:
    def __init__(self, parent, settings_manager):
        self.parent = parent
        self.settings_manager = settings_manager
        self.settings = settings_manager.load_settings()
        
        # Создание окна
        self.window = tk.Toplevel(parent)
        self.window.title("Настройки IDE")
        self.window.geometry("600x500")
        self.window.configure(bg='#2b2b2b')
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """Создание виджетов диалога"""
        # Главный контейнер
        main_frame = tk.Frame(self.window, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook для вкладок
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Стиль для notebook
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#2b2b2b')
        style.configure('TNotebook.Tab', background='#3c3c3c', foreground='white')
        
        # Вкладки
        self.create_editor_tab(notebook)
        self.create_theme_tab(notebook)
        self.create_compiler_tab(notebook)
        self.create_autocomplete_tab(notebook)
        
        # Кнопки
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(button_frame, text="По умолчанию", bg='#4c4c4c', fg='white',
                 border=0, relief='flat', command=self.reset_to_defaults).pack(side=tk.LEFT)
        
        tk.Button(button_frame, text="Отмена", bg='#4c4c4c', fg='white',
                 border=0, relief='flat', command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        
        tk.Button(button_frame, text="OK", bg='#0e639c', fg='white',
                 border=0, relief='flat', command=self.save_and_close).pack(side=tk.RIGHT)
    
    def create_editor_tab(self, notebook):
        """Вкладка настроек редактора"""
        frame = tk.Frame(notebook, bg='#2b2b2b')
        notebook.add(frame, text="Редактор")
        
        # Шрифт
        font_frame = tk.LabelFrame(frame, text="Шрифт", bg='#2b2b2b', fg='white')
        font_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(font_frame, text="Семейство:", bg='#2b2b2b', fg='white').grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.font_family_var = tk.StringVar(value=self.settings['editor']['font_family'])
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_family_var,
                                 values=['Consolas', 'Courier New', 'Monaco', 'Menlo'])
        font_combo.grid(row=0, column=1, padx=5, pady=2)
        
        tk.Label(font_frame, text="Размер:", bg='#2b2b2b', fg='white').grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.font_size_var = tk.IntVar(value=self.settings['editor']['font_size'])
        size_spin = tk.Spinbox(font_frame, from_=8, to=24, textvariable=self.font_size_var,
                              bg='#3c3c3c', fg='white', width=10)
        size_spin.grid(row=1, column=1, padx=5, pady=2)
        
        # Отступы
        indent_frame = tk.LabelFrame(frame, text="Отступы", bg='#2b2b2b', fg='white')
        indent_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(indent_frame, text="Размер табуляции:", bg='#2b2b2b', fg='white').grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.tab_width_var = tk.IntVar(value=self.settings['editor']['tab_width'])
        tab_spin = tk.Spinbox(indent_frame, from_=2, to=8, textvariable=self.tab_width_var,
                             bg='#3c3c3c', fg='white', width=10)
        tab_spin.grid(row=0, column=1, padx=5, pady=2)
        
        # Опции
        options_frame = tk.LabelFrame(frame, text="Опции", bg='#2b2b2b', fg='white')
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.line_numbers_var = tk.BooleanVar(value=self.settings['editor']['line_numbers'])
        tk.Checkbutton(options_frame, text="Номера строк", variable=self.line_numbers_var,
                      bg='#2b2b2b', fg='white', selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.word_wrap_var = tk.BooleanVar(value=self.settings['editor']['word_wrap'])
        tk.Checkbutton(options_frame, text="Перенос слов", variable=self.word_wrap_var,
                      bg='#2b2b2b', fg='white', selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.auto_indent_var = tk.BooleanVar(value=self.settings['editor']['auto_indent'])
        tk.Checkbutton(options_frame, text="Автоотступ", variable=self.auto_indent_var,
                      bg='#2b2b2b', fg='white', selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.highlight_line_var = tk.BooleanVar(value=self.settings['editor']['highlight_current_line'])
        tk.Checkbutton(options_frame, text="Подсветка текущей строки", variable=self.highlight_line_var,
                      bg='#2b2b2b', fg='white', selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
    
    def create_theme_tab(self, notebook):
        """Вкладка темы"""
        frame = tk.Frame(notebook, bg='#2b2b2b')
        notebook.add(frame, text="Тема")
        
        colors_frame = tk.LabelFrame(frame, text="Цвета", bg='#2b2b2b', fg='white')
        colors_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Список цветов для настройки
        color_settings = [
            ('background', 'Фон'),
            ('foreground', 'Текст'),
            ('keyword_color', 'Ключевые слова'),
            ('comment_color', 'Комментарии'),
            ('string_color', 'Строки'),
            ('number_color', 'Числа'),
            ('label_color', 'Метки'),
            ('current_line', 'Текущая строка')
        ]
        
        self.color_vars = {}
        for i, (key, label) in enumerate(color_settings):
            tk.Label(colors_frame, text=f"{label}:", bg='#2b2b2b', fg='white').grid(row=i, column=0, sticky='w', padx=5, pady=2)
            
            self.color_vars[key] = tk.StringVar(value=self.settings['theme'][key])
            
            color_frame = tk.Frame(colors_frame, bg='#2b2b2b')
            color_frame.grid(row=i, column=1, padx=5, pady=2)
            
            color_display = tk.Frame(color_frame, bg=self.settings['theme'][key], width=30, height=20, relief='solid', bd=1)
            color_display.pack(side=tk.LEFT, padx=(0, 5))
            
            tk.Button(color_frame, text="Выбрать", bg='#4c4c4c', fg='white', border=0,
                     command=lambda k=key, d=color_display: self.choose_color(k, d)).pack(side=tk.LEFT)
    
    def create_compiler_tab(self, notebook):
        """Вкладка компилятора"""
        frame = tk.Frame(notebook, bg='#2b2b2b')
        notebook.add(frame, text="Компилятор")
        
        # Путь к компилятору
        path_frame = tk.LabelFrame(frame, text="Компилятор", bg='#2b2b2b', fg='white')
        path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(path_frame, text="Путь к ассемблеру:", bg='#2b2b2b', fg='white').pack(anchor='w', padx=5, pady=2)
        
        path_entry_frame = tk.Frame(path_frame, bg='#2b2b2b')
        path_entry_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.compiler_path_var = tk.StringVar(value=self.settings['compiler']['path'])
        path_entry = tk.Entry(path_entry_frame, textvariable=self.compiler_path_var,
                             bg='#3c3c3c', fg='white', insertbackground='white')
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(path_entry_frame, text="Обзор...", bg='#4c4c4c', fg='white', border=0,
                 command=self.browse_compiler).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Опции компиляции
        options_frame = tk.LabelFrame(frame, text="Опции", bg='#2b2b2b', fg='white')
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(options_frame, text="Формат по умолчанию:", bg='#2b2b2b', fg='white').grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.default_output_var = tk.StringVar(value=self.settings['compiler']['default_output'])
        output_combo = ttk.Combobox(options_frame, textvariable=self.default_output_var,
                                   values=['bin', 'tape', 'both'])
        output_combo.grid(row=0, column=1, padx=5, pady=2)
        
        self.auto_save_var = tk.BooleanVar(value=self.settings['compiler']['auto_save_before_compile'])
        tk.Checkbutton(options_frame, text="Автосохранение перед компиляцией",
                      variable=self.auto_save_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').grid(row=1, column=0, columnspan=2, sticky='w', padx=5, pady=2)
    
    def create_autocomplete_tab(self, notebook):
        """Вкладка автодополнения"""
        frame = tk.Frame(notebook, bg='#2b2b2b')
        notebook.add(frame, text="Автодополнение")
        
        autocomplete_frame = tk.LabelFrame(frame, text="Настройки автодополнения", bg='#2b2b2b', fg='white')
        autocomplete_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.autocomplete_enabled_var = tk.BooleanVar(value=self.settings['autocomplete']['enabled'])
        tk.Checkbutton(autocomplete_frame, text="Включить автодополнение",
                      variable=self.autocomplete_enabled_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.case_sensitive_var = tk.BooleanVar(value=self.settings['autocomplete']['case_sensitive'])
        tk.Checkbutton(autocomplete_frame, text="Учитывать регистр",
                      variable=self.case_sensitive_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        tk.Label(autocomplete_frame, text="Минимум символов для вызова:", bg='#2b2b2b', fg='white').pack(anchor='w', padx=5, pady=(10, 2))
        self.min_chars_var = tk.IntVar(value=self.settings['autocomplete']['min_chars'])
        min_chars_spin = tk.Spinbox(autocomplete_frame, from_=1, to=5, textvariable=self.min_chars_var,
                                   bg='#3c3c3c', fg='white', width=10)
        min_chars_spin.pack(anchor='w', padx=5, pady=2)
    
    def choose_color(self, key, display_widget):
        """Выбор цвета"""
        color = colorchooser.askcolor(color=self.color_vars[key].get())[1]
        if color:
            self.color_vars[key].set(color)
            display_widget.configure(bg=color)
    
    def browse_compiler(self):
        """Выбор файла компилятора"""
        file_path = filedialog.askopenfilename(
            title="Выбрать файл ассемблера",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if file_path:
            # Делаем путь относительным
            try:
                rel_path = os.path.relpath(file_path, os.path.dirname(__file__))
                self.compiler_path_var.set(rel_path)
            except:
                self.compiler_path_var.set(file_path)
    
    def reset_to_defaults(self):
        """Сброс к настройкам по умолчанию"""
        self.settings = self.settings_manager.default_settings.copy()
        self.window.destroy()
        self.show()
    
    def save_and_close(self):
        """Сохранение и закрытие"""
        # Собираем настройки из виджетов
        self.settings['editor']['font_family'] = self.font_family_var.get()
        self.settings['editor']['font_size'] = self.font_size_var.get()
        self.settings['editor']['tab_width'] = self.tab_width_var.get()
        self.settings['editor']['line_numbers'] = self.line_numbers_var.get()
        self.settings['editor']['word_wrap'] = self.word_wrap_var.get()
        self.settings['editor']['auto_indent'] = self.auto_indent_var.get()
        self.settings['editor']['highlight_current_line'] = self.highlight_line_var.get()
        
        # Цвета темы
        for key, var in self.color_vars.items():
            self.settings['theme'][key] = var.get()
        
        # Компилятор
        self.settings['compiler']['path'] = self.compiler_path_var.get()
        self.settings['compiler']['default_output'] = self.default_output_var.get()
        self.settings['compiler']['auto_save_before_compile'] = self.auto_save_var.get()
        
        # Автодополнение
        self.settings['autocomplete']['enabled'] = self.autocomplete_enabled_var.get()
        self.settings['autocomplete']['case_sensitive'] = self.case_sensitive_var.get()
        self.settings['autocomplete']['min_chars'] = self.min_chars_var.get()
        
        # Сохраняем
        if self.settings_manager.save_settings(self.settings):
            self.window.destroy()
        else:
            tk.messagebox.showerror("Ошибка", "Не удалось сохранить настройки")
    
    def cancel(self):
        """Отмена"""
        self.window.destroy()
    
    def show(self):
        """Показ диалога"""
        self.window.wait_window()
