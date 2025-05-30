import tkinter as tk
from tkinter import ttk, colorchooser, filedialog
import json
import os

class AdvancedSettings:
    def __init__(self, ide):
        self.ide = ide
        
        # Дополнительные настройки
        self.advanced_settings = {
            'editor': {
                'auto_save': False,
                'auto_save_interval': 5,  # минуты
                'highlight_matching_brackets': True,
                'highlight_current_line': True,
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
            'compiler': {
                'output_dir': 'bios',
                'tape_dir': 'extensions/asm/tapes',
                'error_reporting': True,
                'warnings_as_errors': False,
                'verbose_output': False,
                'optimize': True,
                'auto_run_after_compile': False
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
            }
        }
    
    def merge_with_settings(self, settings):
        """Объединение с основными настройками"""
        if 'advanced' not in settings:
            settings['advanced'] = self.advanced_settings.copy()
        else:
            # Объединяем настройки, сохраняя пользовательские значения
            for section, options in self.advanced_settings.items():
                if section not in settings['advanced']:
                    settings['advanced'][section] = options.copy()
                else:
                    for option, value in options.items():
                        if option not in settings['advanced'][section]:
                            settings['advanced'][section][option] = value
        
        return settings
    
    def load_settings(self):
        """Загрузка настроек"""
        settings = self.ide.settings.load_settings()
        return self.merge_with_settings(settings)
    
    def save_settings(self, settings):
        """Сохранение настроек"""
        self.ide.settings.save_settings(settings)
    
    def show_settings_dialog(self, parent):
        """Показ диалога расширенных настроек"""
        dialog = AdvancedSettingsDialog(parent, self)
        dialog.show()
    
    def get_setting(self, section, key, default=None):
        """Получение конкретной настройки"""
        settings = self.load_settings()
        return settings.get('advanced', {}).get(section, {}).get(key, default)
    
    def set_setting(self, section, key, value):
        """Установка конкретной настройки"""
        settings = self.load_settings()
        if 'advanced' not in settings:
            settings['advanced'] = {}
        if section not in settings['advanced']:
            settings['advanced'][section] = {}
        
        settings['advanced'][section][key] = value
        self.save_settings(settings)

class AdvancedSettingsDialog:
    def __init__(self, parent, settings_manager):
        self.parent = parent
        self.settings_manager = settings_manager
        self.settings = settings_manager.load_settings()
        
        # Создание окна
        self.window = tk.Toplevel(parent)
        self.window.title("Расширенные настройки")
        self.window.geometry("700x600")
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
        self.create_compiler_tab()
        self.create_appearance_tab()
        self.create_keyboard_tab()
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
        
        # Автосохранение
        autosave_frame = tk.LabelFrame(frame, text="Автосохранение", bg='#2b2b2b', fg='white')
        autosave_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.auto_save_var = tk.BooleanVar(value=self.get_advanced_setting('editor', 'auto_save', False))
        tk.Checkbutton(autosave_frame, text="Включить автосохранение",
                      variable=self.auto_save_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        interval_frame = tk.Frame(autosave_frame, bg='#2b2b2b')
        interval_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(interval_frame, text="Интервал (минуты):", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        
        self.auto_save_interval_var = tk.IntVar(value=self.get_advanced_setting('editor', 'auto_save_interval', 5))
        interval_spin = tk.Spinbox(interval_frame, from_=1, to=30, textvariable=self.auto_save_interval_var,
                                  bg='#3c3c3c', fg='white', width=5)
        interval_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        # Подсветка и отображение
        highlight_frame = tk.LabelFrame(frame, text="Подсветка и отображение", bg='#2b2b2b', fg='white')
        highlight_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.highlight_brackets_var = tk.BooleanVar(value=self.get_advanced_setting('editor', 'highlight_matching_brackets', True))
        tk.Checkbutton(highlight_frame, text="Подсвечивать парные скобки",
                      variable=self.highlight_brackets_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.highlight_line_var = tk.BooleanVar(value=self.get_advanced_setting('editor', 'highlight_current_line', True))
        tk.Checkbutton(highlight_frame, text="Подсвечивать текущую строку",
                      variable=self.highlight_line_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.show_whitespace_var = tk.BooleanVar(value=self.get_advanced_setting('editor', 'show_whitespace', False))
        tk.Checkbutton(highlight_frame, text="Показывать пробельные символы",
                      variable=self.show_whitespace_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.show_indentation_guides_var = tk.BooleanVar(value=self.get_advanced_setting('editor', 'show_indentation_guides', True))
        tk.Checkbutton(highlight_frame, text="Показывать направляющие отступов",
                      variable=self.show_indentation_guides_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        # Дополнительные настройки
        extra_frame = tk.LabelFrame(frame, text="Дополнительно", bg='#2b2b2b', fg='white')
        extra_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.code_folding_var = tk.BooleanVar(value=self.get_advanced_setting('editor', 'code_folding', True))
        tk.Checkbutton(extra_frame, text="Сворачивание кода",
                      variable=self.code_folding_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.smooth_scrolling_var = tk.BooleanVar(value=self.get_advanced_setting('editor', 'smooth_scrolling', True))
        tk.Checkbutton(extra_frame, text="Плавная прокрутка",
                      variable=self.smooth_scrolling_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.parameter_hints_var = tk.BooleanVar(value=self.get_advanced_setting('editor', 'show_parameter_hints', True))
        tk.Checkbutton(extra_frame, text="Показывать подсказки параметров",
                      variable=self.parameter_hints_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
    
    def create_compiler_tab(self):
        """Вкладка настроек компилятора"""
        frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(frame, text="Компилятор")
        
        # Директории вывода
        output_frame = tk.LabelFrame(frame, text="Директории вывода", bg='#2b2b2b', fg='white')
        output_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # BIN директория
        bin_frame = tk.Frame(output_frame, bg='#2b2b2b')
        bin_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(bin_frame, text="Директория BIN файлов:", bg='#2b2b2b', fg='white').pack(anchor='w')
        
        bin_path_frame = tk.Frame(bin_frame, bg='#2b2b2b')
        bin_path_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.output_dir_var = tk.StringVar(value=self.get_advanced_setting('compiler', 'output_dir', 'bios'))
        bin_entry = tk.Entry(bin_path_frame, textvariable=self.output_dir_var, bg='#3c3c3c', fg='white')
        bin_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(bin_path_frame, text="...", bg='#4c4c4c', fg='white', border=0,
                 command=self.browse_bin_dir).pack(side=tk.RIGHT, padx=(5, 0))
        
        # TAPE директория
        tape_frame = tk.Frame(output_frame, bg='#2b2b2b')
        tape_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(tape_frame, text="Директория TAPE файлов:", bg='#2b2b2b', fg='white').pack(anchor='w')
        
        tape_path_frame = tk.Frame(tape_frame, bg='#2b2b2b')
        tape_path_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.tape_dir_var = tk.StringVar(value=self.get_advanced_setting('compiler', 'tape_dir', 'extensions/asm/tapes'))
        tape_entry = tk.Entry(tape_path_frame, textvariable=self.tape_dir_var, bg='#3c3c3c', fg='white')
        tape_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(tape_path_frame, text="...", bg='#4c4c4c', fg='white', border=0,
                 command=self.browse_tape_dir).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Опции компиляции
        options_frame = tk.LabelFrame(frame, text="Опции компиляции", bg='#2b2b2b', fg='white')
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.error_reporting_var = tk.BooleanVar(value=self.get_advanced_setting('compiler', 'error_reporting', True))
        tk.Checkbutton(options_frame, text="Подробный вывод ошибок",
                      variable=self.error_reporting_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.warnings_as_errors_var = tk.BooleanVar(value=self.get_advanced_setting('compiler', 'warnings_as_errors', False))
        tk.Checkbutton(options_frame, text="Считать предупреждения ошибками",
                      variable=self.warnings_as_errors_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.verbose_output_var = tk.BooleanVar(value=self.get_advanced_setting('compiler', 'verbose_output', False))
        tk.Checkbutton(options_frame, text="Подробный вывод процесса компиляции",
                      variable=self.verbose_output_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.optimize_var = tk.BooleanVar(value=self.get_advanced_setting('compiler', 'optimize', True))
        tk.Checkbutton(options_frame, text="Оптимизировать код",
                      variable=self.optimize_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        # Автозапуск
        run_frame = tk.LabelFrame(frame, text="Автозапуск", bg='#2b2b2b', fg='white')
        run_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.auto_run_var = tk.BooleanVar(value=self.get_advanced_setting('compiler', 'auto_run_after_compile', False))
        tk.Checkbutton(run_frame, text="Автоматически запускать после компиляции",
                      variable=self.auto_run_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
    
    def create_appearance_tab(self):
        """Вкладка настроек внешнего вида"""
        frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(frame, text="Внешний вид")
        
        # Интерфейс
        interface_frame = tk.LabelFrame(frame, text="Интерфейс", bg='#2b2b2b', fg='white')
        interface_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.show_status_bar_var = tk.BooleanVar(value=self.get_advanced_setting('appearance', 'show_status_bar', True))
        tk.Checkbutton(interface_frame, text="Показывать строку состояния",
                      variable=self.show_status_bar_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.show_toolbar_var = tk.BooleanVar(value=self.get_advanced_setting('appearance', 'show_toolbar', True))
        tk.Checkbutton(interface_frame, text="Показывать панель инструментов",
                      variable=self.show_toolbar_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        # Редактор
        editor_frame = tk.LabelFrame(frame, text="Редактор", bg='#2b2b2b', fg='white')
        editor_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.show_line_numbers_var = tk.BooleanVar(value=self.get_advanced_setting('appearance', 'show_line_numbers', True))
        tk.Checkbutton(editor_frame, text="Показывать номера строк",
                      variable=self.show_line_numbers_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.show_scrollbars_var = tk.BooleanVar(value=self.get_advanced_setting('appearance', 'show_scrollbars', True))
        tk.Checkbutton(editor_frame, text="Показывать полосы прокрутки",
                      variable=self.show_scrollbars_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        # Анимации
        animations_frame = tk.LabelFrame(frame, text="Анимации", bg='#2b2b2b', fg='white')
        animations_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.tool_window_animations_var = tk.BooleanVar(value=self.get_advanced_setting('appearance', 'tool_window_animations', True))
        tk.Checkbutton(animations_frame, text="Анимации окон инструментов",
                      variable=self.tool_window_animations_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        # Масштаб
        zoom_frame = tk.LabelFrame(frame, text="Масштаб редактора", bg='#2b2b2b', fg='white')
        zoom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        zoom_level_frame = tk.Frame(zoom_frame, bg='#2b2b2b')
        zoom_level_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(zoom_level_frame, text="Уровень масштаба (%):", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        
        self.zoom_level_var = tk.IntVar(value=self.get_advanced_setting('appearance', 'editor_zoom_level', 100))
        zoom_spin = tk.Spinbox(zoom_level_frame, from_=50, to=200, textvariable=self.zoom_level_var,
                               bg='#3c3c3c', fg='white', width=5)
        zoom_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        # Сбросить кнопка
        tk.Button(zoom_level_frame, text="Сбросить", bg='#4c4c4c', fg='white', border=0,
                 command=lambda: self.zoom_level_var.set(100)).pack(side=tk.LEFT, padx=(5, 0))
    
    def create_keyboard_tab(self):
        """Вкладка настроек клавиатуры"""
        frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(frame, text="Клавиатура")
        
        # Эмуляция Vim
        vim_frame = tk.LabelFrame(frame, text="Режимы редактирования", bg='#2b2b2b', fg='white')
        vim_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.vim_emulation_var = tk.BooleanVar(value=self.get_advanced_setting('keyboard', 'use_vim_emulation', False))
        tk.Checkbutton(vim_frame, text="Использовать эмуляцию Vim",
                      variable=self.vim_emulation_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        # Горячие клавиши
        shortcuts_frame = tk.LabelFrame(frame, text="Горячие клавиши", bg='#2b2b2b', fg='white')
        shortcuts_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # TODO: Добавить настройку горячих клавиш
    
    def create_project_tab(self):
        """Вкладка настроек проекта"""
        frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(frame, text="Проект")
        
        # Директории проекта
        dir_frame = tk.LabelFrame(frame, text="Директории проекта", bg='#2b2b2b', fg='white')
        dir_frame.pack(fill=tk.X, padx=5, pady=5)
        
        assembly_dir_frame = tk.Frame(dir_frame, bg='#2b2b2b')
        assembly_dir_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(assembly_dir_frame, text="Директория ассемблерного кода:", bg='#2b2b2b', fg='white').pack(anchor='w')
        
        asm_path_frame = tk.Frame(assembly_dir_frame, bg='#2b2b2b')
        asm_path_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.assembly_dir_var = tk.StringVar(value=self.get_advanced_setting('project', 'default_assembly_directory', 'extensions/asm/code'))
        asm_entry = tk.Entry(asm_path_frame, textvariable=self.assembly_dir_var, bg='#3c3c3c', fg='white')
        asm_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(asm_path_frame, text="...", bg='#4c4c4c', fg='white', border=0,
                 command=self.browse_asm_dir).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Опции проекта
        options_frame = tk.LabelFrame(frame, text="Опции проекта", bg='#2b2b2b', fg='white')
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.auto_detect_files_var = tk.BooleanVar(value=self.get_advanced_setting('project', 'auto_detect_files', True))
        tk.Checkbutton(options_frame, text="Автоматически определять файлы проекта",
                      variable=self.auto_detect_files_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.auto_open_last_var = tk.BooleanVar(value=self.get_advanced_setting('project', 'auto_open_last_project', True))
        tk.Checkbutton(options_frame, text="Автоматически открывать последний проект",
                      variable=self.auto_open_last_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        # Кодировка
        encoding_frame = tk.Frame(options_frame, bg='#2b2b2b')
        encoding_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(encoding_frame, text="Кодировка по умолчанию:", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        
        self.encoding_var = tk.StringVar(value=self.get_advanced_setting('project', 'default_encoding', 'utf-8'))
        encodings = ['utf-8', 'cp1251', 'ascii', 'iso-8859-1', 'latin-1']
        encoding_combo = ttk.Combobox(encoding_frame, textvariable=self.encoding_var, values=encodings, width=10)
        encoding_combo.pack(side=tk.LEFT, padx=(5, 0))
    
    def create_backup_tab(self):
        """Вкладка настроек резервного копирования"""
        frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(frame, text="Резервные копии")
        
        # Настройки резервного копирования
        backup_frame = tk.LabelFrame(frame, text="Резервное копирование", bg='#2b2b2b', fg='white')
        backup_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.create_backups_var = tk.BooleanVar(value=self.get_advanced_setting('backup', 'create_backups', True))
        tk.Checkbutton(backup_frame, text="Создавать резервные копии",
                      variable=self.create_backups_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.include_timestamp_var = tk.BooleanVar(value=self.get_advanced_setting('backup', 'include_timestamp', True))
        tk.Checkbutton(backup_frame, text="Включать временную метку в имя файла",
                      variable=self.include_timestamp_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        # Директория резервных копий
        dir_frame = tk.Frame(backup_frame, bg='#2b2b2b')
        dir_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(dir_frame, text="Директория резервных копий:", bg='#2b2b2b', fg='white').pack(anchor='w')
        
        backup_path_frame = tk.Frame(dir_frame, bg='#2b2b2b')
        backup_path_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.backup_dir_var = tk.StringVar(value=self.get_advanced_setting('backup', 'backup_directory', '.backups'))
        backup_entry = tk.Entry(backup_path_frame, textvariable=self.backup_dir_var, bg='#3c3c3c', fg='white')
        backup_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Максимальное количество файлов
        max_files_frame = tk.Frame(backup_frame, bg='#2b2b2b')
        max_files_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(max_files_frame, text="Максимальное количество файлов:", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        
        self.max_backup_files_var = tk.IntVar(value=self.get_advanced_setting('backup', 'max_backup_files', 10))
        max_files_spin = tk.Spinbox(max_files_frame, from_=1, to=100, textvariable=self.max_backup_files_var,
                                   bg='#3c3c3c', fg='white', width=5)
        max_files_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        # Интервал автосохранения
        interval_frame = tk.Frame(backup_frame, bg='#2b2b2b')
        interval_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(interval_frame, text="Интервал резервного копирования (минуты):", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        
        self.backup_interval_var = tk.IntVar(value=self.get_advanced_setting('backup', 'backup_interval', 10))
        interval_spin = tk.Spinbox(interval_frame, from_=1, to=60, textvariable=self.backup_interval_var,
                                  bg='#3c3c3c', fg='white', width=5)
        interval_spin.pack(side=tk.LEFT, padx=(5, 0))
    
    def create_import_tab(self):
        """Вкладка настроек импорта"""
        frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(frame, text="Импорт")
        
        # Настройки импорта
        import_frame = tk.LabelFrame(frame, text="Настройки импорта", bg='#2b2b2b', fg='white')
        import_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.resolve_imports_var = tk.BooleanVar(value=self.get_advanced_setting('import', 'resolve_imports', True))
        tk.Checkbutton(import_frame, text="Разрешать импорты при компиляции",
                      variable=self.resolve_imports_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.recursive_imports_var = tk.BooleanVar(value=self.get_advanced_setting('import', 'recursive_imports', True))
        tk.Checkbutton(import_frame, text="Разрешать рекурсивные импорты",
                      variable=self.recursive_imports_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.create_import_cache_var = tk.BooleanVar(value=self.get_advanced_setting('import', 'create_import_cache', True))
        tk.Checkbutton(import_frame, text="Создавать кэш импортов",
                      variable=self.create_import_cache_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        self.detect_circular_imports_var = tk.BooleanVar(value=self.get_advanced_setting('import', 'detect_circular_imports', True))
        tk.Checkbutton(import_frame, text="Определять циклические импорты",
                      variable=self.detect_circular_imports_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=5, pady=2)
        
        # Директории импорта
        dirs_frame = tk.LabelFrame(frame, text="Директории импорта", bg='#2b2b2b', fg='white')
        dirs_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Список директорий
        self.import_dirs_listbox = tk.Listbox(dirs_frame, bg='#1e1e1e', fg='white',
                                             selectbackground='#0e639c', font=('Consolas', 10))
        self.import_dirs_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Загружаем директории
        import_dirs = self.get_advanced_setting('import', 'import_dirs', [])
        for dir_path in import_dirs:
            self.import_dirs_listbox.insert(tk.END, dir_path)
        
        # Кнопки управления
        buttons_frame = tk.Frame(dirs_frame, bg='#2b2b2b')
        buttons_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        tk.Button(buttons_frame, text="Добавить...", bg='#4c4c4c', fg='white', border=0,
                 command=self.add_import_dir).pack(fill=tk.X, pady=(0, 5))
        
        tk.Button(buttons_frame, text="Удалить", bg='#4c4c4c', fg='white', border=0,
                 command=self.remove_import_dir).pack(fill=tk.X)
    
    def add_import_dir(self):
        """Добавление директории импорта"""
        dir_path = filedialog.askdirectory(title="Выберите директорию для импорта")
        if dir_path:
            self.import_dirs_listbox.insert(tk.END, dir_path)
    
    def remove_import_dir(self):
        """Удаление директории импорта"""
        selection = self.import_dirs_listbox.curselection()
        if selection:
            self.import_dirs_listbox.delete(selection[0])
    
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
    
    def get_advanced_setting(self, section, key, default=None):
        """Получение расширенной настройки"""
        return self.settings.get('advanced', {}).get(section, {}).get(key, default)
    
    def reset_to_defaults(self):
        """Сброс к настройкам по умолчанию"""
        self.settings['advanced'] = self.settings_manager.advanced_settings.copy()
        self.window.destroy()
        self.show()
    
    def save_and_close(self):
        """Сохранение и закрытие"""
        # Сохраняем настройки редактора
        self.settings.setdefault('advanced', {}).setdefault('editor', {})
        self.settings['advanced']['editor']['auto_save'] = self.auto_save_var.get()
        self.settings['advanced']['editor']['auto_save_interval'] = self.auto_save_interval_var.get()
        self.settings['advanced']['editor']['highlight_matching_brackets'] = self.highlight_brackets_var.get()
        self.settings['advanced']['editor']['highlight_current_line'] = self.highlight_line_var.get()
        self.settings['advanced']['editor']['show_whitespace'] = self.show_whitespace_var.get()
        self.settings['advanced']['editor']['show_indentation_guides'] = self.show_indentation_guides_var.get()
        self.settings['advanced']['editor']['code_folding'] = self.code_folding_var.get()
        self.settings['advanced']['editor']['smooth_scrolling'] = self.smooth_scrolling_var.get()
        self.settings['advanced']['editor']['show_parameter_hints'] = self.parameter_hints_var.get()
        
        # Сохраняем настройки компилятора
        self.settings.setdefault('advanced', {}).setdefault('compiler', {})
        self.settings['advanced']['compiler']['output_dir'] = self.output_dir_var.get()
        self.settings['advanced']['compiler']['tape_dir'] = self.tape_dir_var.get()
        self.settings['advanced']['compiler']['error_reporting'] = self.error_reporting_var.get()
        self.settings['advanced']['compiler']['warnings_as_errors'] = self.warnings_as_errors_var.get()
        self.settings['advanced']['compiler']['verbose_output'] = self.verbose_output_var.get()
        self.settings['advanced']['compiler']['optimize'] = self.optimize_var.get()
        self.settings['advanced']['compiler']['auto_run_after_compile'] = self.auto_run_var.get()
        
        # Сохраняем настройки внешнего вида
        self.settings.setdefault('advanced', {}).setdefault('appearance', {})
        self.settings['advanced']['appearance']['show_status_bar'] = self.show_status_bar_var.get()
        self.settings['advanced']['appearance']['show_toolbar'] = self.show_toolbar_var.get()
        self.settings['advanced']['appearance']['show_line_numbers'] = self.show_line_numbers_var.get()
        self.settings['advanced']['appearance']['show_scrollbars'] = self.show_scrollbars_var.get()
        self.settings['advanced']['appearance']['tool_window_animations'] = self.tool_window_animations_var.get()
        self.settings['advanced']['appearance']['editor_zoom_level'] = self.zoom_level_var.get()
        
        # Сохраняем настройки клавиатуры
        self.settings.setdefault('advanced', {}).setdefault('keyboard', {})
        self.settings['advanced']['keyboard']['use_vim_emulation'] = self.vim_emulation_var.get()
        
        # Сохраняем настройки проекта
        self.settings.setdefault('advanced', {}).setdefault('project', {})
        self.settings['advanced']['project']['default_assembly_directory'] = self.assembly_dir_var.get()
        self.settings['advanced']['project']['auto_detect_files'] = self.auto_detect_files_var.get()
        self.settings['advanced']['project']['auto_open_last_project'] = self.auto_open_last_var.get()
        self.settings['advanced']['project']['default_encoding'] = self.encoding_var.get()
        
        # Сохраняем настройки резервного копирования
        self.settings.setdefault('advanced', {}).setdefault('backup', {})
        self.settings['advanced']['backup']['create_backups'] = self.create_backups_var.get()
        self.settings['advanced']['backup']['backup_directory'] = self.backup_dir_var.get()
        self.settings['advanced']['backup']['max_backup_files'] = self.max_backup_files_var.get()
        self.settings['advanced']['backup']['backup_interval'] = self.backup_interval_var.get()
        self.settings['advanced']['backup']['include_timestamp'] = self.include_timestamp_var.get()
        
        # Сохраняем настройки импорта
        self.settings.setdefault('advanced', {}).setdefault('import', {})
        self.settings['advanced']['import']['resolve_imports'] = self.resolve_imports_var.get()
        self.settings['advanced']['import']['recursive_imports'] = self.recursive_imports_var.get()
        self.settings['advanced']['import']['create_import_cache'] = self.create_import_cache_var.get()
        self.settings['advanced']['import']['detect_circular_imports'] = self.detect_circular_imports_var.get()
        
        # Сохраняем директории импорта
        import_dirs = list(self.import_dirs_listbox.get(0, tk.END))
        self.settings['advanced']['import']['import_dirs'] = import_dirs
        
        # Сохраняем настройки
        self.settings_manager.save_settings(self.settings)
        
        self.window.destroy()
    
    def cancel(self):
        """Отмена"""
        self.window.destroy()
    
    def show(self):
        """Показ диалога"""
        self.window.wait_window()
