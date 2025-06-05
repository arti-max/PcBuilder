import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import time
import threading

# Установка UTF-8 для Windows консоли
if sys.platform.startswith('win'):
    os.system('chcp 65001 >nul')

# Добавляем пути для импорта модулей
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Импорт модулей IDE
from Settings import SettingsManager
from AdvancedSettings import AdvancedSettings
from Editor import CodeEditor
from TabManager import TabManager
from LabelNavigator import LabelNavigator
from FileManager import FileManager
from ImportManager import ImportManager
from CompileDialogs import CompileDialog
from Compiler import CompilerIntegration

class PCBuilderIDE:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PC Builder IDE - Assembly Development Environment")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Инициализация компонентов
        self.settings = SettingsManager()
        self.file_manager = FileManager(self)
        self.import_manager = ImportManager(self)
        self.compiler = CompilerIntegration(self)
        
        # Переменные состояния
        self.current_file = None
        self.is_modified = False
        self.editor = None
        
        # Создание интерфейса
        self.create_menu()
        self.create_toolbar()
        self.create_main_layout()
        self.create_status_bar()
        
        # Привязка событий
        self.bind_events()
        
        # Загрузка настроек
        self.load_settings()
        
        # Автосохранение
        self.setup_autosave()
        
        # Проверка доступности ассемблера
        self.check_assembler_availability()
        
        print("🚀 PC Builder IDE запущена")
        print("📁 Рабочая директория:", os.getcwd())
    
    def create_menu(self):
        """Создание главного меню"""
        menubar = tk.Menu(self.root, bg='#3c3c3c', fg='white')
        self.root.config(menu=menubar)
        
        # Файл
        file_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новый (Ctrl+N)", command=self.new_file)
        file_menu.add_command(label="Открыть (Ctrl+O)", command=self.open_file)
        file_menu.add_command(label="Сохранить (Ctrl+S)", command=self.save_file)
        file_menu.add_command(label="Сохранить как...", command=self.save_file_as)
        file_menu.add_separator()
        
        # Последние файлы
        self.recent_menu = tk.Menu(file_menu, tearoff=0, bg='#3c3c3c', fg='white')
        file_menu.add_cascade(label="Последние файлы", menu=self.recent_menu)
        self.update_recent_files_menu()
        
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.on_closing)
        
        # Правка
        edit_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Отменить (Ctrl+Z)", command=self.undo)
        edit_menu.add_command(label="Повторить (Ctrl+Y)", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать (Ctrl+X)", command=self.cut)
        edit_menu.add_command(label="Копировать (Ctrl+C)", command=self.copy)
        edit_menu.add_command(label="Вставить (Ctrl+V)", command=self.paste)
        edit_menu.add_separator()
        edit_menu.add_command(label="Выделить всё (Ctrl+A)", command=self.select_all)
        edit_menu.add_separator()
        edit_menu.add_command(label="Найти (Ctrl+F)", command=self.find_text)
        edit_menu.add_command(label="Заменить (Ctrl+H)", command=self.replace_text)
        
        # Вид
        view_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="Вид", menu=view_menu)
        
        # Подменю для режима редактора
        editor_mode_menu = tk.Menu(view_menu, tearoff=0, bg='#3c3c3c', fg='white')
        view_menu.add_cascade(label="Режим редактора", menu=editor_mode_menu)
        editor_mode_menu.add_command(label="Обычный режим", command=lambda: self.set_editor_mode("normal"))
        editor_mode_menu.add_command(label="Полноэкранный режим", command=lambda: self.set_editor_mode("fullscreen"))
        editor_mode_menu.add_command(label="Режим без отвлечений", command=lambda: self.set_editor_mode("distraction_free"))
        
        view_menu.add_separator()
        
        # Подменю для отображения панелей
        panels_menu = tk.Menu(view_menu, tearoff=0, bg='#3c3c3c', fg='white')
        view_menu.add_cascade(label="Панели", menu=panels_menu)
        
        self.show_toolbar_var = tk.BooleanVar(value=True)
        panels_menu.add_checkbutton(label="Панель инструментов", 
                                  variable=self.show_toolbar_var,
                                  command=self.toggle_toolbar)
        
        self.show_statusbar_var = tk.BooleanVar(value=True)
        panels_menu.add_checkbutton(label="Строка состояния", 
                                  variable=self.show_statusbar_var,
                                  command=self.toggle_statusbar)
        
        self.show_navigator_var = tk.BooleanVar(value=True)
        panels_menu.add_checkbutton(label="Навигатор меток", 
                                  variable=self.show_navigator_var,
                                  command=self.toggle_navigator)
        
        # Сборка
        build_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="Сборка", menu=build_menu)
        build_menu.add_command(label="Компилировать в BIN (F5)", command=self.compile_to_bin)
        build_menu.add_command(label="Компилировать в TAPE (F6)", command=self.compile_to_tape)
        build_menu.add_command(label="Компилировать в оба формата (F7)", command=self.compile_all)
        build_menu.add_separator()
        build_menu.add_command(label="Остановить компиляцию", command=self.stop_compilation)
        build_menu.add_separator()
        build_menu.add_command(label="Показать результаты компиляции", command=self.show_last_compile_results)
        
        # Инструменты
        tools_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="Инструменты", menu=tools_menu)
        tools_menu.add_command(label="Импортировать TAPE файл...", command=self.import_tape)
        tools_menu.add_command(label="Экспортировать в TAPE...", command=self.export_to_tape)
        tools_menu.add_separator()
        tools_menu.add_command(label="Проверить синтаксис", command=self.check_syntax)
        tools_menu.add_command(label="Форматировать код", command=self.format_code)
        tools_menu.add_separator()
        tools_menu.add_command(label="Открыть терминал", command=self.open_terminal)
        
        # Настройки
        settings_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="Настройки", menu=settings_menu)
        settings_menu.add_command(label="Настройки IDE", command=self.open_settings)
        settings_menu.add_command(label="Выбрать компилятор", command=self.select_compiler)
        settings_menu.add_separator()
        settings_menu.add_command(label="Настройки редактора", command=self.editor_settings)
        settings_menu.add_command(label="Настройки цветовой схемы", command=self.color_scheme_settings)
        
        # Справка
        help_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="Справка по IDE", command=self.show_ide_help)
        help_menu.add_command(label="Инструкции процессора", command=self.show_instructions)
        help_menu.add_command(label="Пример программы", command=self.show_example)
        help_menu.add_separator()
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def create_toolbar(self):
        """Создание панели инструментов"""
        self.toolbar = tk.Frame(self.root, bg='#3c3c3c', height=40)
        self.toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Кнопки
        buttons = [
            ("📄", "Новый", self.new_file),
            ("📂", "Открыть", self.open_file),
            ("💾", "Сохранить", self.save_file),
            ("|", "", None),
            ("▶️", "Компилировать (BIN)", self.compile_to_bin),
            ("📼", "Компилировать (TAPE)", self.compile_to_tape),
            ("|", "", None),
            ("🔍", "Найти", self.find_text),
            ("🔧", "Настройки", self.open_settings),
        ]
        
        for icon, tooltip, command in buttons:
            if icon == "|":
                # Разделитель
                separator = tk.Frame(self.toolbar, bg='#555555', width=2, height=30)
                separator.pack(side=tk.LEFT, padx=5)
            else:
                btn = tk.Button(self.toolbar, text=icon, bg='#4c4c4c', fg='white',
                              border=0, relief='flat', width=3, height=1,
                              command=command if command else None)
                btn.pack(side=tk.LEFT, padx=2, pady=5)
                
                # Tooltip
                if tooltip:
                    self.create_tooltip(btn, tooltip)
    
    def create_main_layout(self):
        """Создание основного макета"""
        # Главная панель
        self.main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg='#2b2b2b',
                                       sashrelief=tk.RAISED, sashwidth=3)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая панель - редактор
        self.left_frame = tk.Frame(self.main_paned, bg='#2b2b2b')
        
        # Система вкладок
        self.tab_manager = TabManager(self.left_frame, self)
        
        # Правая панель - навигация и инструменты
        self.right_frame = tk.Frame(self.main_paned, bg='#2b2b2b', width=300)
        
        # Навигатор меток
        self.label_navigator = LabelNavigator(self.right_frame, self)
        
        # Добавляем панели
        self.main_paned.add(self.left_frame, minsize=600)
        self.main_paned.add(self.right_frame, minsize=250)
    
    def create_status_bar(self):
        """Создание строки состояния"""
        self.status_bar = tk.Frame(self.root, bg='#3c3c3c', height=25)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Статус файла
        self.status_file = tk.Label(self.status_bar, text="Готов", 
                                   bg='#3c3c3c', fg='white', anchor=tk.W)
        self.status_file.pack(side=tk.LEFT, padx=5)
        
        # Позиция курсора
        self.status_cursor = tk.Label(self.status_bar, text="Строка: 1, Столбец: 1",
                                     bg='#3c3c3c', fg='white')
        self.status_cursor.pack(side=tk.RIGHT, padx=5)
        
        # Кодировка
        self.status_encoding = tk.Label(self.status_bar, text="UTF-8",
                                       bg='#3c3c3c', fg='white')
        self.status_encoding.pack(side=tk.RIGHT, padx=5)
    
    def create_tooltip(self, widget, text):
        """Создание всплывающей подсказки"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, bg='#ffffcc', fg='black',
                           relief='solid', borderwidth=1)
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def bind_events(self):
        """Привязка горячих клавиш"""
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Control-f>', lambda e: self.find_text())
        self.root.bind('<Control-h>', lambda e: self.replace_text())
        self.root.bind('<F5>', lambda e: self.compile_to_bin())
        self.root.bind('<F6>', lambda e: self.compile_to_tape())
        self.root.bind('<F7>', lambda e: self.compile_all())
        
        # Обработка закрытия
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_settings(self):
        """Загрузка настроек"""
        settings = self.settings.load_settings()
        self.apply_settings(settings)
    
    def apply_settings(self, settings):
        """Применение настроек"""
        appearance = settings.get('appearance', {})
        
        if not appearance.get('show_toolbar', True):
            self.toolbar.pack_forget()
            self.show_toolbar_var.set(False)
        
        if not appearance.get('show_status_bar', True):
            self.status_bar.pack_forget()
            self.show_statusbar_var.set(False)
        
    def setup_autosave(self):
        """Настройка автосохранения"""
        auto_save = self.settings.get_setting('editor', 'auto_save', False)
        
        if auto_save:
            interval = self.settings.get_setting('editor', 'auto_save_interval', 5) * 60 * 1000
            self.schedule_autosave(interval)

    
    def schedule_autosave(self, interval):
        """Планирование автосохранения"""
        def autosave():
            if self.is_modified and self.current_file:
                self.save_file()
            self.root.after(interval, autosave)
        
        self.root.after(interval, autosave)
    
    def check_assembler_availability(self):
        """Проверка доступности ассемблера"""
        if hasattr(self, 'compiler'):
            assembler_path = self.compiler.get_assembler_path()
            if assembler_path:
                rel_path = os.path.relpath(assembler_path, os.getcwd())
                self.update_status(f"Ассемблер: {rel_path}")
            else:
                self.update_status("Ассемблер не найден! Проверьте настройки.")
                self.root.after(1000, self.prompt_select_assembler)
    
    def prompt_select_assembler(self):
        """Предложение выбрать ассемблер"""
        result = messagebox.askyesno(
            "Ассемблер не найден",
            "Ассемблер PC Builder не найден.\n\nХотите выбрать его вручную?"
        )
        
        if result:
            self.select_compiler()
    
    # === Файловые операции ===
    
    def new_file(self):
        """Создание нового файла"""
        if hasattr(self, 'tab_manager') and self.tab_manager:
            self.tab_manager.add_tab()
            self.update_status("Новый файл создан")
    
    def open_file(self):
        """Открытие файла"""
        file_path = filedialog.askopenfilename(
            title="Открыть файл ассемблера",
            filetypes=[("Assembly files", "*.asm"), ("All files", "*.*")]
        )
        
        if file_path:
            if hasattr(self, 'tab_manager') and self.tab_manager:
                tab_id = self.tab_manager.open_file_in_new_tab(file_path)
                if tab_id:
                    self.update_status(f"Файл открыт: {os.path.basename(file_path)}")
                    self.add_to_recent_files(file_path)
    
    def save_file(self):
        """Сохранение файла"""
        if hasattr(self, 'tab_manager') and self.tab_manager and self.tab_manager.current_tab:
            if self.tab_manager.save_tab(self.tab_manager.current_tab):
                filename = os.path.basename(self.current_file) if self.current_file else "файл"
                self.update_status(f"Файл сохранен: {filename}")
                return True
        return False
    
    def save_file_as(self):
        """Сохранение файла как..."""
        if hasattr(self, 'tab_manager') and self.tab_manager and self.tab_manager.current_tab:
            if self.tab_manager.save_tab_as(self.tab_manager.current_tab):
                filename = os.path.basename(self.current_file) if self.current_file else "файл"
                self.update_status(f"Файл сохранен как: {filename}")
                if self.current_file:
                    self.add_to_recent_files(self.current_file)
                return True
        return False
    
    def add_to_recent_files(self, file_path):
        """Добавление файла в список последних"""
        settings = self.settings.load_settings()
        recent_files = settings.get('recent_files', [])
        
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        recent_files.insert(0, file_path)
        recent_files = recent_files[:10]
        
        settings['recent_files'] = recent_files
        self.settings.save_settings(settings)
        self.update_recent_files_menu()
    
    def update_recent_files_menu(self):
        """Обновление меню последних файлов"""
        self.recent_menu.delete(0, tk.END)
        
        settings = self.settings.load_settings()
        recent_files = settings.get('recent_files', [])
        
        if recent_files:
            for file_path in recent_files:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    self.recent_menu.add_command(
                        label=filename,
                        command=lambda path=file_path: self.open_recent_file(path)
                    )
            
            self.recent_menu.add_separator()
            self.recent_menu.add_command(label="Очистить список", command=self.clear_recent_files)
        else:
            self.recent_menu.add_command(label="Нет последних файлов", state=tk.DISABLED)
    
    def open_recent_file(self, file_path):
        """Открытие последнего файла"""
        if os.path.exists(file_path):
            if hasattr(self, 'tab_manager') and self.tab_manager:
                tab_id = self.tab_manager.open_file_in_new_tab(file_path)
                if tab_id:
                    self.update_status(f"Файл открыт: {os.path.basename(file_path)}")
        else:
            messagebox.showerror("Ошибка", f"Файл не найден:\n{file_path}")
    
    def clear_recent_files(self):
        """Очистка списка последних файлов"""
        settings = self.settings.load_settings()
        settings['recent_files'] = []
        self.settings.save_settings(settings)
        self.update_recent_files_menu()
    
    # === Операции редактирования ===
    
    def undo(self):
        """Отмена"""
        if self.editor:
            self.editor.undo()
    
    def redo(self):
        """Повтор"""
        if self.editor:
            self.editor.redo()
    
    def cut(self):
        """Вырезать"""
        if self.editor:
            try:
                self.editor.text_widget.event_generate("<<Cut>>")
            except:
                pass
    
    def copy(self):
        """Копировать"""
        if self.editor:
            try:
                self.editor.text_widget.event_generate("<<Copy>>")
            except:
                pass
    
    def paste(self):
        """Вставить"""
        if self.editor:
            try:
                self.editor.text_widget.event_generate("<<Paste>>")
            except:
                pass
    
    def select_all(self):
        """Выделить всё"""
        if self.editor:
            try:
                self.editor.text_widget.tag_add("sel", "1.0", "end")
                return "break"
            except:
                pass
    
    def find_text(self):
        """Поиск текста"""
        if self.editor:
            self.editor.show_find_dialog()
    
    def replace_text(self):
        """Замена текста"""
        if self.editor:
            self.editor.show_replace_dialog()
    
    # === Компиляция ===
    
    def compile_to_bin(self):
        """Компиляция в BIN"""
        if not self.current_file:
            if not self.save_file():
                return
                
        dialog = CompileDialog(self.root, "bin")
        result = dialog.show()
        
        if result:
            if self.is_modified:
                self.save_file()
            
            self.compiler.compile_file(
                self.current_file, 
                "bin", 
                output_path=result.get('output_dir')
            )
    
    def compile_to_tape(self):
        """Компиляция в TAPE"""
        if not self.current_file:
            if not self.save_file():
                return
                
        # Открываем диалог настроек компиляции
        dialog = CompileDialog(self.root, "tape")
        result = dialog.show()
        
        if result:
            # Автосохранение перед компиляцией
            if self.is_modified:
                self.save_file()
            
            # ИСПРАВЛЕНИЕ: Передаем параметры правильно
            self.compiler.compile_file(
                self.current_file, 
                "tape",
                output_path=result.get('output_path'),
                metadata=result.get('metadata')
            )
    
    def compile_all(self):
        """Компиляция в оба формата"""
        if not self.current_file:
            if not self.save_file():
                return
        
        # Автосохранение перед компиляцией
        if self.is_modified:
            self.save_file()
        
        # ИСПРАВЛЕНИЕ: Упрощенный вызов
        self.compiler.compile_file(self.current_file, "both")
    
    def stop_compilation(self):
        """Остановка компиляции"""
        if hasattr(self, 'compiler'):
            self.compiler.stop_compilation()
    
    def show_last_compile_results(self):
        """Показ результатов последней компиляции"""
        messagebox.showinfo("Информация", "Результаты компиляции пока не реализованы")
    
    # === Инструменты ===
    
    def import_tape(self):
        """Импорт TAPE файла"""
        messagebox.showinfo("Информация", "Импорт TAPE файлов пока не реализован")
    
    def export_to_tape(self):
        """Экспорт в TAPE"""
        self.compile_to_tape()
    
    def check_syntax(self):
        """Проверка синтаксиса"""
        messagebox.showinfo("Информация", "Проверка синтаксиса пока не реализована")
    
    def format_code(self):
        """Форматирование кода"""
        messagebox.showinfo("Информация", "Форматирование кода пока не реализовано")
    
    def open_terminal(self):
        """Открытие терминала"""
        try:
            import subprocess
            
            if sys.platform.startswith('win'):
                subprocess.Popen('cmd.exe', cwd=os.getcwd())
            elif sys.platform.startswith('darwin'):
                subprocess.Popen(['open', '-a', 'Terminal', '.'], cwd=os.getcwd())
            else:
                subprocess.Popen(['x-terminal-emulator'], cwd=os.getcwd())
        except:
            messagebox.showerror("Ошибка", "Не удалось открыть терминал")
    
    # === Настройки ===
    
    def open_settings(self):
        """Открытие настроек"""
        self.settings.show_settings_dialog(self.root)
    
    def open_advanced_settings(self):
        """Открытие расширенных настроек"""
        self.advanced_settings.show_settings_dialog(self.root)
    
    def select_compiler(self):
        """Выбор компилятора"""
        file_path = filedialog.askopenfilename(
            title="Выбрать файл компилятора",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            self.settings.set_setting('compiler', 'path', file_path)
            self.update_status(f"Компилятор: {os.path.basename(file_path)}")
    
    def editor_settings(self):
        """Настройки редактора"""
        self.settings.show_settings_dialog(self.root)
    
    def color_scheme_settings(self):
        """Настройки цветовой схемы"""
        self.settings.show_settings_dialog(self.root)
    
    # === Справка ===
    
    def show_ide_help(self):
        """Показ справки по IDE"""
        help_text = """
PC Builder IDE - Справка

=== Горячие клавиши ===
Ctrl+N - Новый файл
Ctrl+O - Открыть файл
Ctrl+S - Сохранить файл
Ctrl+F - Найти
Ctrl+H - Заменить
F5 - Компилировать в BIN
F6 - Компилировать в TAPE
F7 - Компилировать в оба формата

=== Особенности IDE ===
• Поддержка вкладок для работы с несколькими файлами
• Подсветка синтаксиса ассемблера
• Автодополнение команд и регистров
• Навигация по меткам
• Интеграция с компилятором
• Резервное копирование
• Импорт файлов
"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Справка по IDE")
        help_window.geometry("600x500")
        help_window.configure(bg='#2b2b2b')
        
        text_widget = tk.Text(help_window, bg='#1e1e1e', fg='white',
                             font=('Consolas', 11), padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        text_widget.insert('1.0', help_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_instructions(self):
        """Показ справки по инструкциям"""
        messagebox.showinfo("Информация", "Справка по инструкциям в разработке")
    
    def show_example(self):
        """Показ примера программы"""
        example = """; Пример программы для PC Builder
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
    
    ; Простой цикл
    mov a, 10
loop:
    dec a
    cmp a, 0
    jne loop
    
    hlt
"""
        
        if hasattr(self, 'tab_manager') and self.tab_manager:
            tab_id = self.tab_manager.add_tab(title="Пример", content=example)
            self.update_status("Пример программы загружен")
    
    def show_about(self):
        """О программе"""
        messagebox.showinfo("О программе", 
                           "PC Builder IDE v1.0\n\n"
                           "Интегрированная среда разработки\n"
                           "для 8-битного процессора PC Builder\n\n"
                           "Создано для проекта PC Builder\n"
                           "github.com/arti-max/PcBuilder")
    
    # === Управление видом ===
    
    def set_editor_mode(self, mode):
        """Установка режима редактора"""
        if mode == "normal":
            if hasattr(self, 'fullscreen_state'):
                self.root.attributes('-fullscreen', False)
                del self.fullscreen_state
            self.update_status("Обычный режим")
        
        elif mode == "fullscreen":
            self.fullscreen_state = True
            self.root.attributes('-fullscreen', True)
            self.update_status("Полноэкранный режим (Esc для выхода)")
            self.root.bind('<Escape>', lambda e: self.set_editor_mode("normal"))
        
        elif mode == "distraction_free":
            self.toolbar.pack_forget()
            self.status_bar.pack_forget()
            if self.right_frame in self.main_paned.panes():
                self.main_paned.forget(self.right_frame)
            self.update_status("Режим без отвлечений")
    
    def toggle_toolbar(self):
        """Переключение видимости панели инструментов"""
        if self.show_toolbar_var.get():
            self.toolbar.pack(fill=tk.X, pady=(0, 5), before=self.main_paned)
        else:
            self.toolbar.pack_forget()
    
    def toggle_statusbar(self):
        """Переключение видимости строки состояния"""
        if self.show_statusbar_var.get():
            self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        else:
            self.status_bar.pack_forget()
    
    def toggle_navigator(self):
        """Переключение видимости навигатора"""
        if self.show_navigator_var.get():
            if self.right_frame not in self.main_paned.panes():
                self.main_paned.add(self.right_frame, minsize=250)
        else:
            if self.right_frame in self.main_paned.panes():
                self.main_paned.forget(self.right_frame)
    
    # === Утилиты ===
    
    def update_title(self):
        """Обновление заголовка окна"""
        title = "PC Builder IDE"
        if self.current_file:
            filename = os.path.basename(self.current_file)
            title += f" - {filename}"
        
        if self.is_modified:
            title += " *"
        
        self.root.title(title)
    
    def update_status(self, message):
        """Обновление строки состояния"""
        self.status_file.config(text=message)
        print(f"📝 {message}")
    
    def update_cursor_position(self, line, column):
        """Обновление позиции курсора"""
        self.status_cursor.config(text=f"Строка: {line}, Столбец: {column}")
    
    def set_modified(self, modified=True):
        """Установка флага изменения"""
        self.is_modified = modified
        self.update_title()
        
        if hasattr(self, 'tab_manager') and self.tab_manager and self.tab_manager.current_tab:
            self.tab_manager.set_tab_modified(self.tab_manager.current_tab, modified)
        
        if modified and hasattr(self, 'label_navigator'):
            self.label_navigator.update_labels()
    
    def on_closing(self):
        """Обработка закрытия приложения"""
        # Проверяем несохраненные изменения во всех вкладках
        if hasattr(self, 'tab_manager') and self.tab_manager:
            for tab_id, tab_info in self.tab_manager.tabs.items():
                if tab_info['modified']:
                    self.tab_manager.switch_to_tab(tab_id)
                    if not self.tab_manager.close_tab(tab_id):
                        return  # Пользователь отменил закрытие
        
        print("👋 PC Builder IDE закрыта")
        self.root.destroy()
    
    def run(self):
        """Запуск IDE"""
        self.root.mainloop()

if __name__ == "__main__":
    ide = PCBuilderIDE()
    ide.run()
