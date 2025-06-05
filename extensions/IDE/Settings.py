import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
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
                'highlight_current_line': True,
                'auto_save': False,
                'auto_save_interval': 5,  # минуты
                'highlight_matching_brackets': True,
                'show_whitespace': False,
                'virtual_space': False,
                'smooth_scrolling': True,
                'code_folding': True,
                'show_gutter_icons': True,
                'show_indentation_guides': True,
                'show_parameter_hints': True,
                'auto_import': True,
                'show_line_endings': False
            },
            'theme': {
                'name': 'VS Code Dark',
                'background': '#1e1e1e',
                'foreground': '#ffffff',
                'keyword_color': '#569cd6',
                'register_color': '#9cdcfe',
                'comment_color': '#6a9955',
                'string_color': '#ce9178',
                'number_color': '#b5cea8',
                'label_color': '#dcdcaa',
                'directive_color': '#c586c0',
                'operator_color': '#d4d4d4',
                'error_color': '#f44747',
                'address_color': '#4fc1ff',
                'current_line': '#2d2d2d',
                'selection': '#264f78'
            },
            'compiler': {
                'path': '',  # Автоматический поиск
                'default_output': 'bin',
                'auto_save_before_compile': True,
                'output_dir': 'bios',
                'tape_dir': 'extensions/asm/tapes',
                'error_reporting': True,
                'warnings_as_errors': False,
                'verbose_output': False,
                'optimize': True,
                'auto_run_after_compile': False
            },
            'autocomplete': {
                'enabled': True,
                'case_sensitive': False,
                'min_chars': 1,
                'show_descriptions': True,
                'auto_insert_templates': True
            },
            'appearance': {
                'show_status_bar': True,
                'show_toolbar': True,
                'show_line_numbers': True,
                'show_scrollbars': True,
                'use_native_file_dialogs': True,
                'tool_window_animations': True,
                'editor_zoom_level': 100
            },
            'keyboard': {
                'use_vim_emulation': False,
                'show_keybindings_popup': True,
                'keyboard_shortcuts': {}
            },
            'terminal': {
                'font_family': 'Consolas',
                'font_size': 11,
                'background_color': '#1E1E1E',
                'foreground_color': '#CCCCCC',
                'buffer_size': 1000,
                'use_system_shell': True
            },
            'project': {
                'default_assembly_directory': 'extensions/asm/code',
                'search_depth': 3,
                'auto_detect_files': True,
                'default_encoding': 'utf-8',
                'auto_open_last_project': True
            },
            'backup': {
                'create_backups': True,
                'backup_directory': '.backups',
                'max_backup_files': 10,
                'backup_interval': 10,  # минуты
                'include_timestamp': True
            },
            'import': {
                'resolve_imports': True,
                'recursive_imports': True,
                'create_import_cache': True,
                'detect_circular_imports': True,
                'import_dirs': []
            },
            'navigator': {
                'auto_update': True,
                'group_by_type': True,
                'show_line_numbers': True,
                'expand_groups': True
            },
            'window': {
                'width': 1200,
                'height': 800,
                'remember_size': True,
                'remember_position': True,
                'last_x': 100,
                'last_y': 100
            },
            'recent_files': []
        }
    
    def load_settings(self):
        """Загрузка настроек из файла"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
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
        self.window.geometry("800x700")
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
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Стиль для notebook
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#2b2b2b')
        style.configure('TNotebook.Tab', background='#3c3c3c', foreground='white')
        
        # Создание вкладок
        self.create_editor_tab()
        self.create_theme_tab()
        self.create_compiler_tab()
        self.create_autocomplete_tab()
        self.create_appearance_tab()
        self.create_project_tab()
        self.create_backup_tab()
        self.create_import_tab()
        
        # Кнопки
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(button_frame, text="По умолчанию", bg='#4c4c4c', fg='white',
                 border=0, relief='flat', command=self.reset_to_defaults).pack(side=tk.LEFT)
        
        tk.Button(button_frame, text="Отмена", bg='#4c4c4c', fg='white',
                 border=0, relief='flat', command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        
        tk.Button(button_frame, text="Применить", bg='#0e639c', fg='white',
                 border=0, relief='flat', command=self.save_and_close).pack(side=tk.RIGHT)
    
    def create_editor_tab(self):
        """Вкладка настроек редактора"""
        frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(frame, text="Редактор")
        
        # Шрифт
        font_frame = tk.LabelFrame(frame, text="Шрифт", bg='#2b2b2b', fg='white')
        font_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(font_frame, text="Семейство:", bg='#2b2b2b', fg='white').grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.font_family_var = tk.StringVar(value=self.settings['editor']['font_family'])
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_family_var,
                                 values=['Consolas', 'Courier New', 'Monaco', 'Menlo', 'DejaVu Sans Mono'])
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
        
        # Автосохранение
        autosave_frame = tk.LabelFrame(frame, text="Автосохранение", bg='#2b2b2b', fg='white')
        autosave_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.auto_save_var = tk.BooleanVar(value=self.settings['editor']['auto_save'])
        tk.Checkbutton(autosave_frame, text="Включить автосохранение",
                      variable=self.auto_save_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        interval_frame = tk.Frame(autosave_frame, bg='#2b2b2b')
        interval_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(interval_frame, text="Интервал (минуты):", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        self.auto_save_interval_var = tk.IntVar(value=self.settings['editor']['auto_save_interval'])
        interval_spin = tk.Spinbox(interval_frame, from_=1, to=30, textvariable=self.auto_save_interval_var,
                                  bg='#3c3c3c', fg='white', width=5)
        interval_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        # Опции редактора
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
        
        self.highlight_brackets_var = tk.BooleanVar(value=self.settings['editor']['highlight_matching_brackets'])
        tk.Checkbutton(options_frame, text="Подсветка парных скобок", variable=self.highlight_brackets_var,
                      bg='#2b2b2b', fg='white', selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.show_whitespace_var = tk.BooleanVar(value=self.settings['editor']['show_whitespace'])
        tk.Checkbutton(options_frame, text="Показывать пробельные символы", variable=self.show_whitespace_var,
                      bg='#2b2b2b', fg='white', selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
    
    def create_theme_tab(self):
        """Вкладка темы"""
        frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(frame, text="Тема")
        
        colors_frame = tk.LabelFrame(frame, text="Цвета", bg='#2b2b2b', fg='white')
        colors_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Список цветов для настройки
        color_settings = [
            ('background', 'Фон редактора'),
            ('foreground', 'Основной текст'),
            ('keyword_color', 'Ключевые слова'),
            ('register_color', 'Регистры'),
            ('comment_color', 'Комментарии'),
            ('string_color', 'Строки'),
            ('number_color', 'Числа'),
            ('label_color', 'Метки'),
            ('directive_color', 'Директивы'),
            ('current_line', 'Текущая строка'),
            ('selection', 'Выделение')
        ]
        
        self.color_vars = {}
        for i, (key, label) in enumerate(color_settings):
            tk.Label(colors_frame, text=f"{label}:", bg='#2b2b2b', fg='white').grid(row=i, column=0, sticky='w', padx=5, pady=2)
            
            self.color_vars[key] = tk.StringVar(value=self.settings['theme'][key])
            color_frame = tk.Frame(colors_frame, bg='#2b2b2b')
            color_frame.grid(row=i, column=1, padx=5, pady=2, sticky='w')
            
            color_display = tk.Frame(color_frame, bg=self.settings['theme'][key], width=30, height=20, relief='solid', bd=1)
            color_display.pack(side=tk.LEFT, padx=(0, 5))
            
            tk.Button(color_frame, text="Выбрать", bg='#4c4c4c', fg='white', border=0,
                     command=lambda k=key, d=color_display: self.choose_color(k, d)).pack(side=tk.LEFT)
        
        # Предустановленные темы
        themes_frame = tk.LabelFrame(frame, text="Предустановленные темы", bg='#2b2b2b', fg='white')
        themes_frame.pack(fill=tk.X, padx=5, pady=5)
        
        theme_buttons = [
            ("VS Code Dark", self.apply_vscode_dark_theme),
            ("VS Code Light", self.apply_vscode_light_theme),
            ("Sublime Text", self.apply_sublime_theme),
            ("Atom Dark", self.apply_atom_dark_theme)
        ]
        
        for i, (name, command) in enumerate(theme_buttons):
            tk.Button(themes_frame, text=name, bg='#4c4c4c', fg='white', border=0,
                     command=command).grid(row=i//2, column=i%2, padx=5, pady=2, sticky='ew')
        
        themes_frame.grid_columnconfigure(0, weight=1)
        themes_frame.grid_columnconfigure(1, weight=1)
    
    def create_compiler_tab(self):
        """Вкладка компилятора"""
        frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(frame, text="Компилятор")
        
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
        
        # Директории вывода
        output_frame = tk.LabelFrame(frame, text="Директории вывода", bg='#2b2b2b', fg='white')
        output_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # BIN директория
        tk.Label(output_frame, text="Директория BIN файлов:", bg='#2b2b2b', fg='white').pack(anchor='w', padx=5, pady=2)
        
        bin_path_frame = tk.Frame(output_frame, bg='#2b2b2b')
        bin_path_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.output_dir_var = tk.StringVar(value=self.settings['compiler']['output_dir'])
        bin_entry = tk.Entry(bin_path_frame, textvariable=self.output_dir_var, bg='#3c3c3c', fg='white')
        bin_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(bin_path_frame, text="...", bg='#4c4c4c', fg='white', border=0,
                 command=self.browse_bin_dir).pack(side=tk.RIGHT, padx=(5, 0))
        
        # TAPE директория
        tk.Label(output_frame, text="Директория TAPE файлов:", bg='#2b2b2b', fg='white').pack(anchor='w', padx=5, pady=2)
        
        tape_path_frame = tk.Frame(output_frame, bg='#2b2b2b')
        tape_path_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.tape_dir_var = tk.StringVar(value=self.settings['compiler']['tape_dir'])
        tape_entry = tk.Entry(tape_path_frame, textvariable=self.tape_dir_var, bg='#3c3c3c', fg='white')
        tape_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(tape_path_frame, text="...", bg='#4c4c4c', fg='white', border=0,
                 command=self.browse_tape_dir).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Опции компиляции
        options_frame = tk.LabelFrame(frame, text="Опции", bg='#2b2b2b', fg='white')
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(options_frame, text="Формат по умолчанию:", bg='#2b2b2b', fg='white').grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.default_output_var = tk.StringVar(value=self.settings['compiler']['default_output'])
        output_combo = ttk.Combobox(options_frame, textvariable=self.default_output_var,
                                   values=['bin', 'tape', 'both'])
        output_combo.grid(row=0, column=1, padx=5, pady=2, sticky='w')
        
        self.auto_save_compile_var = tk.BooleanVar(value=self.settings['compiler']['auto_save_before_compile'])
        tk.Checkbutton(options_frame, text="Автосохранение перед компиляцией",
                      variable=self.auto_save_compile_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').grid(row=1, column=0, columnspan=2, sticky='w', padx=5, pady=2)
        
        self.error_reporting_var = tk.BooleanVar(value=self.settings['compiler']['error_reporting'])
        tk.Checkbutton(options_frame, text="Подробный вывод ошибок",
                      variable=self.error_reporting_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').grid(row=2, column=0, columnspan=2, sticky='w', padx=5, pady=2)
        
        self.optimize_var = tk.BooleanVar(value=self.settings['compiler']['optimize'])
        tk.Checkbutton(options_frame, text="Оптимизировать код",
                      variable=self.optimize_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').grid(row=3, column=0, columnspan=2, sticky='w', padx=5, pady=2)
    
    def create_autocomplete_tab(self):
        """Вкладка автодополнения"""
        frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(frame, text="Автодополнение")
        
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
        
        self.show_descriptions_var = tk.BooleanVar(value=self.settings['autocomplete']['show_descriptions'])
        tk.Checkbutton(autocomplete_frame, text="Показывать описания",
                      variable=self.show_descriptions_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.auto_insert_templates_var = tk.BooleanVar(value=self.settings['autocomplete']['auto_insert_templates'])
        tk.Checkbutton(autocomplete_frame, text="Автоматически вставлять шаблоны",
                      variable=self.auto_insert_templates_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        tk.Label(autocomplete_frame, text="Минимум символов для вызова:", bg='#2b2b2b', fg='white').pack(anchor='w', padx=5, pady=(10, 2))
        self.min_chars_var = tk.IntVar(value=self.settings['autocomplete']['min_chars'])
        min_chars_spin = tk.Spinbox(autocomplete_frame, from_=1, to=5, textvariable=self.min_chars_var,
                                   bg='#3c3c3c', fg='white', width=10)
        min_chars_spin.pack(anchor='w', padx=5, pady=2)
    
    def create_appearance_tab(self):
        """Вкладка внешнего вида"""
        frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(frame, text="Внешний вид")
        
        # Интерфейс
        interface_frame = tk.LabelFrame(frame, text="Интерфейс", bg='#2b2b2b', fg='white')
        interface_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.show_status_bar_var = tk.BooleanVar(value=self.settings['appearance']['show_status_bar'])
        tk.Checkbutton(interface_frame, text="Показывать строку состояния",
                      variable=self.show_status_bar_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.show_toolbar_var = tk.BooleanVar(value=self.settings['appearance']['show_toolbar'])
        tk.Checkbutton(interface_frame, text="Показывать панель инструментов",
                      variable=self.show_toolbar_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.show_scrollbars_var = tk.BooleanVar(value=self.settings['appearance']['show_scrollbars'])
        tk.Checkbutton(interface_frame, text="Показывать полосы прокрутки",
                      variable=self.show_scrollbars_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        # Масштаб
        zoom_frame = tk.LabelFrame(frame, text="Масштаб", bg='#2b2b2b', fg='white')
        zoom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        zoom_level_frame = tk.Frame(zoom_frame, bg='#2b2b2b')
        zoom_level_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(zoom_level_frame, text="Уровень масштаба (%):", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        
        self.zoom_level_var = tk.IntVar(value=self.settings['appearance']['editor_zoom_level'])
        zoom_spin = tk.Spinbox(zoom_level_frame, from_=50, to=200, textvariable=self.zoom_level_var,
                              bg='#3c3c3c', fg='white', width=5)
        zoom_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        tk.Button(zoom_level_frame, text="Сбросить", bg='#4c4c4c', fg='white', border=0,
                 command=lambda: self.zoom_level_var.set(100)).pack(side=tk.LEFT, padx=(5, 0))
    
    def create_project_tab(self):
        """Вкладка настроек проекта"""
        frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(frame, text="Проект")
        
        # Директории проекта
        dir_frame = tk.LabelFrame(frame, text="Директории проекта", bg='#2b2b2b', fg='white')
        dir_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(dir_frame, text="Директория ассемблерного кода:", bg='#2b2b2b', fg='white').pack(anchor='w', padx=5, pady=2)
        
        asm_path_frame = tk.Frame(dir_frame, bg='#2b2b2b')
        asm_path_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.assembly_dir_var = tk.StringVar(value=self.settings['project']['default_assembly_directory'])
        asm_entry = tk.Entry(asm_path_frame, textvariable=self.assembly_dir_var, bg='#3c3c3c', fg='white')
        asm_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(asm_path_frame, text="...", bg='#4c4c4c', fg='white', border=0,
                 command=self.browse_asm_dir).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Опции проекта
        options_frame = tk.LabelFrame(frame, text="Опции проекта", bg='#2b2b2b', fg='white')
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.auto_detect_files_var = tk.BooleanVar(value=self.settings['project']['auto_detect_files'])
        tk.Checkbutton(options_frame, text="Автоматически определять файлы проекта",
                      variable=self.auto_detect_files_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.auto_open_last_var = tk.BooleanVar(value=self.settings['project']['auto_open_last_project'])
        tk.Checkbutton(options_frame, text="Автоматически открывать последний проект",
                      variable=self.auto_open_last_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        # Кодировка
        encoding_frame = tk.Frame(options_frame, bg='#2b2b2b')
        encoding_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(encoding_frame, text="Кодировка по умолчанию:", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        
        self.encoding_var = tk.StringVar(value=self.settings['project']['default_encoding'])
        encodings = ['utf-8', 'cp1251', 'ascii', 'iso-8859-1', 'latin-1']
        encoding_combo = ttk.Combobox(encoding_frame, textvariable=self.encoding_var, values=encodings, width=10)
        encoding_combo.pack(side=tk.LEFT, padx=(5, 0))
    
    def create_backup_tab(self):
        """Вкладка настроек резервного копирования"""
        frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(frame, text="Резервные копии")
        
        backup_frame = tk.LabelFrame(frame, text="Резервное копирование", bg='#2b2b2b', fg='white')
        backup_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.create_backups_var = tk.BooleanVar(value=self.settings['backup']['create_backups'])
        tk.Checkbutton(backup_frame, text="Создавать резервные копии",
                      variable=self.create_backups_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.include_timestamp_var = tk.BooleanVar(value=self.settings['backup']['include_timestamp'])
        tk.Checkbutton(backup_frame, text="Включать временную метку в имя файла",
                      variable=self.include_timestamp_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        # Директория резервных копий
        tk.Label(backup_frame, text="Директория резервных копий:", bg='#2b2b2b', fg='white').pack(anchor='w', padx=5, pady=2)
        
        backup_path_frame = tk.Frame(backup_frame, bg='#2b2b2b')
        backup_path_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.backup_dir_var = tk.StringVar(value=self.settings['backup']['backup_directory'])
        backup_entry = tk.Entry(backup_path_frame, textvariable=self.backup_dir_var, bg='#3c3c3c', fg='white')
        backup_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Максимальное количество файлов
        max_files_frame = tk.Frame(backup_frame, bg='#2b2b2b')
        max_files_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(max_files_frame, text="Максимальное количество файлов:", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        
        self.max_backup_files_var = tk.IntVar(value=self.settings['backup']['max_backup_files'])
        max_files_spin = tk.Spinbox(max_files_frame, from_=1, to=100, textvariable=self.max_backup_files_var,
                                   bg='#3c3c3c', fg='white', width=5)
        max_files_spin.pack(side=tk.LEFT, padx=(5, 0))
    
    def create_import_tab(self):
        """Вкладка настроек импорта"""
        frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(frame, text="Импорт")
        
        import_frame = tk.LabelFrame(frame, text="Настройки импорта", bg='#2b2b2b', fg='white')
        import_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.resolve_imports_var = tk.BooleanVar(value=self.settings['import']['resolve_imports'])
        tk.Checkbutton(import_frame, text="Разрешать импорты при компиляции",
                      variable=self.resolve_imports_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.recursive_imports_var = tk.BooleanVar(value=self.settings['import']['recursive_imports'])
        tk.Checkbutton(import_frame, text="Разрешать рекурсивные импорты",
                      variable=self.recursive_imports_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.create_import_cache_var = tk.BooleanVar(value=self.settings['import']['create_import_cache'])
        tk.Checkbutton(import_frame, text="Создавать кэш импортов",
                      variable=self.create_import_cache_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.detect_circular_imports_var = tk.BooleanVar(value=self.settings['import']['detect_circular_imports'])
        tk.Checkbutton(import_frame, text="Определять циклические импорты",
                      variable=self.detect_circular_imports_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
    
    # === Методы для работы с цветами и темами ===
    
    def choose_color(self, key, display_widget):
        """Выбор цвета"""
        color = colorchooser.askcolor(color=self.color_vars[key].get())[1]
        if color:
            self.color_vars[key].set(color)
            display_widget.configure(bg=color)
    
    def apply_vscode_dark_theme(self):
        """Применение темы VS Code Dark"""
        colors = {
            'background': '#1e1e1e',
            'foreground': '#ffffff',
            'keyword_color': '#569cd6',
            'register_color': '#9cdcfe',
            'comment_color': '#6a9955',
            'string_color': '#ce9178',
            'number_color': '#b5cea8',
            'label_color': '#dcdcaa',
            'directive_color': '#c586c0',
            'current_line': '#2d2d2d',
            'selection': '#264f78'
        }
        self.apply_theme(colors)
    
    def apply_vscode_light_theme(self):
        """Применение темы VS Code Light"""
        colors = {
            'background': '#ffffff',
            'foreground': '#000000',
            'keyword_color': '#0000ff',
            'register_color': '#001080',
            'comment_color': '#008000',
            'string_color': '#a31515',
            'number_color': '#098658',
            'label_color': '#795e26',
            'directive_color': '#af00db',
            'current_line': '#f3f3f3',
            'selection': '#add6ff'
        }
        self.apply_theme(colors)
    
    def apply_sublime_theme(self):
        """Применение темы Sublime Text"""
        colors = {
            'background': '#272822',
            'foreground': '#f8f8f2',
            'keyword_color': '#f92672',
            'register_color': '#66d9ef',
            'comment_color': '#75715e',
            'string_color': '#e6db74',
            'number_color': '#ae81ff',
            'label_color': '#a6e22e',
            'directive_color': '#f92672',
            'current_line': '#3e3d32',
            'selection': '#49483e'
        }
        self.apply_theme(colors)
    
    def apply_atom_dark_theme(self):
        """Применение темы Atom Dark"""
        colors = {
            'background': '#282c34',
            'foreground': '#abb2bf',
            'keyword_color': '#c678dd',
            'register_color': '#61afef',
            'comment_color': '#5c6370',
            'string_color': '#98c379',
            'number_color': '#d19a66',
            'label_color': '#e06c75',
            'directive_color': '#c678dd',
            'current_line': '#2c323c',
            'selection': '#3e4451'
        }
        self.apply_theme(colors)
    
    def apply_theme(self, colors):
        """Применение темы"""
        for key, color in colors.items():
            if key in self.color_vars:
                self.color_vars[key].set(color)
                # Найдем соответствующий виджет отображения цвета
                # Это упрощенная версия, можно улучшить
                pass
    
    # === Методы для обзора файлов ===
    
    def browse_compiler(self):
        """Выбор файла компилятора"""
        file_path = filedialog.askopenfilename(
            title="Выбрать файл ассемблера",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                rel_path = os.path.relpath(file_path, os.path.dirname(__file__))
                self.compiler_path_var.set(rel_path)
            except:
                self.compiler_path_var.set(file_path)
    
    def browse_bin_dir(self):
        """Выбор директории для BIN файлов"""
        dir_path = filedialog.askdirectory(title="Выберите директорию для BIN файлов")
        if dir_path:
            self.output_dir_var.set(dir_path)
    
    def browse_tape_dir(self):
        """Выбор директории для TAPE файлов"""
        dir_path = filedialog.askdirectory(title="Выберите директорию для TAPE файлов")
        if dir_path:
            self.tape_dir_var.set(dir_path)
    
    def browse_asm_dir(self):
        """Выбор директории для ассемблерного кода"""
        dir_path = filedialog.askdirectory(title="Выберите директорию для ассемблерного кода")
        if dir_path:
            self.assembly_dir_var.set(dir_path)
    
    # === Основные методы диалога ===
    
    def reset_to_defaults(self):
        """Сброс к настройкам по умолчанию"""
        self.settings = self.settings_manager.default_settings.copy()
        self.window.destroy()
        self.show()
    
    def save_and_close(self):
        """Сохранение и закрытие"""
        try:
            # Собираем настройки из виджетов
            
            # Редактор
            self.settings['editor']['font_family'] = self.font_family_var.get()
            self.settings['editor']['font_size'] = self.font_size_var.get()
            self.settings['editor']['tab_width'] = self.tab_width_var.get()
            self.settings['editor']['line_numbers'] = self.line_numbers_var.get()
            self.settings['editor']['word_wrap'] = self.word_wrap_var.get()
            self.settings['editor']['auto_indent'] = self.auto_indent_var.get()
            self.settings['editor']['highlight_current_line'] = self.highlight_line_var.get()
            self.settings['editor']['auto_save'] = self.auto_save_var.get()
            self.settings['editor']['auto_save_interval'] = self.auto_save_interval_var.get()
            self.settings['editor']['highlight_matching_brackets'] = self.highlight_brackets_var.get()
            self.settings['editor']['show_whitespace'] = self.show_whitespace_var.get()
            
            # Цвета темы
            for key, var in self.color_vars.items():
                self.settings['theme'][key] = var.get()
            
            # Компилятор
            self.settings['compiler']['path'] = self.compiler_path_var.get()
            self.settings['compiler']['default_output'] = self.default_output_var.get()
            self.settings['compiler']['auto_save_before_compile'] = self.auto_save_compile_var.get()
            self.settings['compiler']['output_dir'] = self.output_dir_var.get()
            self.settings['compiler']['tape_dir'] = self.tape_dir_var.get()
            self.settings['compiler']['error_reporting'] = self.error_reporting_var.get()
            self.settings['compiler']['optimize'] = self.optimize_var.get()
            
            # Автодополнение
            self.settings['autocomplete']['enabled'] = self.autocomplete_enabled_var.get()
            self.settings['autocomplete']['case_sensitive'] = self.case_sensitive_var.get()
            self.settings['autocomplete']['min_chars'] = self.min_chars_var.get()
            self.settings['autocomplete']['show_descriptions'] = self.show_descriptions_var.get()
            self.settings['autocomplete']['auto_insert_templates'] = self.auto_insert_templates_var.get()
            
            # Внешний вид
            self.settings['appearance']['show_status_bar'] = self.show_status_bar_var.get()
            self.settings['appearance']['show_toolbar'] = self.show_toolbar_var.get()
            self.settings['appearance']['show_scrollbars'] = self.show_scrollbars_var.get()
            self.settings['appearance']['editor_zoom_level'] = self.zoom_level_var.get()
            
            # Проект
            self.settings['project']['default_assembly_directory'] = self.assembly_dir_var.get()
            self.settings['project']['auto_detect_files'] = self.auto_detect_files_var.get()
            self.settings['project']['auto_open_last_project'] = self.auto_open_last_var.get()
            self.settings['project']['default_encoding'] = self.encoding_var.get()
            
            # Резервные копии
            self.settings['backup']['create_backups'] = self.create_backups_var.get()
            self.settings['backup']['backup_directory'] = self.backup_dir_var.get()
            self.settings['backup']['max_backup_files'] = self.max_backup_files_var.get()
            self.settings['backup']['include_timestamp'] = self.include_timestamp_var.get()
            
            # Импорт
            self.settings['import']['resolve_imports'] = self.resolve_imports_var.get()
            self.settings['import']['recursive_imports'] = self.recursive_imports_var.get()
            self.settings['import']['create_import_cache'] = self.create_import_cache_var.get()
            self.settings['import']['detect_circular_imports'] = self.detect_circular_imports_var.get()
            
            # Сохраняем
            if self.settings_manager.save_settings(self.settings):
                self.window.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить настройки")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении настроек: {e}")
    
    def cancel(self):
        """Отмена"""
        self.window.destroy()
    
    def show(self):
        """Показ диалога"""
        self.window.wait_window()
