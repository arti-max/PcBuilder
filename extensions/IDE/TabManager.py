import tkinter as tk
from tkinter import ttk, messagebox
import os

class TabManager:
    def __init__(self, parent, ide):
        self.parent = parent
        self.ide = ide
        self.tabs = {}  # {tab_id: {'file_path': path, 'modified': bool, 'content': str}}
        self.current_tab = None
        
        # Создание notebook для вкладок
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Стиль для вкладок
        self.setup_tab_style()
        
        # События
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Контекстное меню для вкладок
        self.create_context_menu()
        
        print("Менеджер вкладок инициализирован")
    
    def setup_tab_style(self):
        """Настройка стиля вкладок"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настройка цветов вкладок
        style.configure('TNotebook', background='#2b2b2b', borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background='#3c3c3c', 
                       foreground='white',
                       padding=[10, 5],
                       borderwidth=1)
        style.map('TNotebook.Tab',
                 background=[('selected', '#1e1e1e'), ('!selected', '#3c3c3c')],
                 foreground=[('selected', 'white'), ('!selected', '#cccccc')])
    
    def create_context_menu(self):
        """Создание контекстного меню для вкладок"""
        self.context_menu = tk.Menu(self.notebook, tearoff=0, bg='#3c3c3c', fg='white')
        self.context_menu.add_command(label="Закрыть", command=self.close_current_tab)
        self.context_menu.add_command(label="Закрыть остальные", command=self.close_other_tabs)
        self.context_menu.add_command(label="Закрыть все", command=self.close_all_tabs)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Показать в проводнике", command=self.show_in_explorer)
        
        # Привязка правой кнопки мыши
        self.notebook.bind("<Button-3>", self.show_context_menu)
    
    def add_tab(self, file_path=None, content="", title=None):
        """Добавление новой вкладки"""
        # Генерируем ID вкладки
        tab_id = f"tab_{len(self.tabs)}"
        
        # Создаем фрейм для содержимого вкладки
        tab_frame = tk.Frame(self.notebook, bg='#2b2b2b')
        
        # Создаем редактор для этой вкладки
        from Editor import CodeEditor
        editor = CodeEditor(tab_frame, self.ide)
        
        # ИСПРАВЛЕНИЕ: Применяем настройки к новому редактору
        if hasattr(self.ide, 'settings'):
            settings = self.ide.settings.load_settings()
            # Объединяем с расширенными настройками
            if hasattr(self.ide, 'advanced_settings'):
                settings = self.ide.advanced_settings.merge_with_settings(settings)
            editor.apply_settings(settings)
        
        # Устанавливаем содержимое
        if content:
            editor.set_content(content)
        else:
            # ИСПРАВЛЕНИЕ: Для пустого файла тоже нужна подсветка
            editor.clear()
        
        # Определяем заголовок вкладки
        if title:
            tab_title = title
        elif file_path:
            tab_title = os.path.basename(file_path)
        else:
            tab_title = f"Новый файл {len(self.tabs) + 1}"
        
        # Добавляем вкладку в notebook
        self.notebook.add(tab_frame, text=tab_title)
        
        # Сохраняем информацию о вкладке
        self.tabs[tab_id] = {
            'frame': tab_frame,
            'editor': editor,
            'file_path': file_path,
            'modified': False,
            'title': tab_title,
            'original_title': tab_title
        }
        
        # Переключаемся на новую вкладку
        self.notebook.select(tab_frame)
        self.current_tab = tab_id
        
        # Обновляем текущий редактор в IDE
        self.ide.editor = editor
        self.ide.current_file = file_path
        self.ide.is_modified = False
        
        # ИСПРАВЛЕНИЕ: Обновляем заголовок и статус
        self.ide.update_title()
        
        return tab_id
    
    def close_tab(self, tab_id):
        """Закрытие вкладки"""
        if tab_id not in self.tabs:
            return False
        
        tab_info = self.tabs[tab_id]
        
        # Проверяем несохраненные изменения
        if tab_info['modified']:
            result = messagebox.askyesnocancel(
                "Несохраненные изменения",
                f"Файл '{tab_info['title']}' был изменен.\nСохранить изменения?"
            )
            
            if result is None:  # Отмена
                return False
            elif result:  # Да - сохранить
                if not self.save_tab(tab_id):
                    return False
        
        # Удаляем вкладку
        self.notebook.forget(tab_info['frame'])
        del self.tabs[tab_id]
        
        # Если закрыли текущую вкладку, переключаемся на другую
        if self.current_tab == tab_id:
            if self.tabs:
                # Берем первую доступную вкладку
                next_tab_id = next(iter(self.tabs))
                self.switch_to_tab(next_tab_id)
            else:
                # Нет больше вкладок - создаем новую
                self.current_tab = None
                self.ide.editor = None
                self.add_tab()
        
        return True
    
    def close_current_tab(self):
        """Закрытие текущей вкладки"""
        if self.current_tab:
            self.close_tab(self.current_tab)
    
    def close_other_tabs(self):
        """Закрытие всех вкладок кроме текущей"""
        if not self.current_tab:
            return
        
        tabs_to_close = [tab_id for tab_id in self.tabs.keys() if tab_id != self.current_tab]
        
        for tab_id in tabs_to_close:
            if not self.close_tab(tab_id):
                break  # Прерываем если пользователь отменил закрытие
    
    def close_all_tabs(self):
        """Закрытие всех вкладок"""
        tabs_to_close = list(self.tabs.keys())
        
        for tab_id in tabs_to_close:
            if not self.close_tab(tab_id):
                break
    
    def switch_to_tab(self, tab_id):
        """Переключение на вкладку"""
        if tab_id not in self.tabs:
            return
        
        tab_info = self.tabs[tab_id]
        
        # Переключаем notebook
        self.notebook.select(tab_info['frame'])
        
        # Обновляем текущую вкладку
        self.current_tab = tab_id
        
        # Обновляем редактор в IDE
        self.ide.editor = tab_info['editor']
        self.ide.current_file = tab_info['file_path']
        self.ide.is_modified = tab_info['modified']
        
        # Обновляем заголовок IDE
        self.ide.update_title()
        
        # Обновляем навигатор меток
        if hasattr(self.ide, 'label_navigator'):
            self.ide.label_navigator.update_labels()
    
    def on_tab_changed(self, event):
        """Обработка смены вкладки"""
        try:
            # Получаем индекс выбранной вкладки
            selected_index = self.notebook.index(self.notebook.select())
            
            # Находим соответствующий tab_id
            for tab_id, tab_info in self.tabs.items():
                if self.notebook.index(tab_info['frame']) == selected_index:
                    self.switch_to_tab(tab_id)
                    break
        except tk.TclError:
            pass  # Ignore errors during tab switching
    
    def save_tab(self, tab_id):
        """Сохранение вкладки"""
        if tab_id not in self.tabs:
            return False
        
        tab_info = self.tabs[tab_id]
        
        if tab_info['file_path']:
            # Сохраняем существующий файл
            try:
                content = tab_info['editor'].get_content()
                with open(tab_info['file_path'], 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.set_tab_modified(tab_id, False)
                return True
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
                return False
        else:
            # Сохранить как...
            return self.save_tab_as(tab_id)
    
    def save_tab_as(self, tab_id):
        """Сохранение вкладки как..."""
        if tab_id not in self.tabs:
            return False
        
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            title="Сохранить как",
            defaultextension=".asm",
            filetypes=[("Assembly files", "*.asm"), ("All files", "*.*")]
        )
        
        if file_path:
            tab_info = self.tabs[tab_id]
            
            try:
                content = tab_info['editor'].get_content()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Обновляем информацию о вкладке
                tab_info['file_path'] = file_path
                new_title = os.path.basename(file_path)
                tab_info['title'] = new_title
                tab_info['original_title'] = new_title
                
                # Обновляем заголовок вкладки
                self.notebook.tab(tab_info['frame'], text=new_title)
                
                self.set_tab_modified(tab_id, False)
                return True
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
                return False
        
        return False
    
    def set_tab_modified(self, tab_id, modified):
        """Установка флага изменения вкладки"""
        if tab_id not in self.tabs:
            return
        
        tab_info = self.tabs[tab_id]
        tab_info['modified'] = modified
        
        # Обновляем заголовок вкладки
        title = tab_info['original_title']
        if modified:
            title += " *"
        
        tab_info['title'] = title
        self.notebook.tab(tab_info['frame'], text=title)
        
        # Если это текущая вкладка, обновляем IDE
        if tab_id == self.current_tab:
            self.ide.is_modified = modified
            self.ide.update_title()
    
    def open_file_in_new_tab(self, file_path):
        """Открытие файла в новой вкладке"""
        # Проверяем, не открыт ли уже этот файл
        for tab_id, tab_info in self.tabs.items():
            if tab_info['file_path'] == file_path:
                self.switch_to_tab(tab_id)
                return tab_id
        
        # Загружаем файл
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Создаем новую вкладку
            tab_id = self.add_tab(file_path, content)
            return tab_id
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")
            return None
    
    def show_context_menu(self, event):
        """Показ контекстного меню"""
        # Определяем, на какой вкладке был клик
        try:
            tab_index = self.notebook.tk.call(self.notebook._w, "identify", "tab", event.x, event.y)
            if tab_index != "":
                self.context_menu.post(event.x_root, event.y_root)
        except:
            pass
    
    def show_in_explorer(self):
        """Показ файла в проводнике"""
        if self.current_tab and self.tabs[self.current_tab]['file_path']:
            file_path = self.tabs[self.current_tab]['file_path']
            try:
                import subprocess
                import sys
                
                if sys.platform.startswith('win'):
                    subprocess.run(['explorer', '/select,', file_path])
                elif sys.platform.startswith('darwin'):
                    subprocess.run(['open', '-R', file_path])
                else:
                    subprocess.run(['xdg-open', os.path.dirname(file_path)])
            except:
                messagebox.showinfo("Информация", f"Файл: {file_path}")
    
    def get_current_tab_info(self):
        """Получение информации о текущей вкладке"""
        if self.current_tab:
            return self.tabs[self.current_tab]
        return None
