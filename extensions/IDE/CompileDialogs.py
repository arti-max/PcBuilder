import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class CompileDialog:
    def __init__(self, parent, compile_type="bin"):
        self.parent = parent
        self.compile_type = compile_type
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Компиляция в {compile_type.upper()}")
        self.dialog.geometry("500x400")
        self.dialog.configure(bg='#2b2b2b')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрируем диалог
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self.create_widgets()
        
    def create_widgets(self):
        """Создание виджетов диалога"""
        main_frame = tk.Frame(self.dialog, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        if self.compile_type == "tape":
            self.create_tape_widgets(main_frame)
        else:
            self.create_bin_widgets(main_frame)
        
        # Кнопки
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(button_frame, text="Отмена", bg='#4c4c4c', fg='white',
                 border=0, relief='flat', command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        
        tk.Button(button_frame, text="Компилировать", bg='#0e639c', fg='white',
                 border=0, relief='flat', command=self.compile).pack(side=tk.RIGHT)
    
    def create_tape_widgets(self, parent):
        """Виджеты для компиляции в TAPE"""
        # Заголовок
        title_label = tk.Label(parent, text="Создание TAPE кассеты", 
                              bg='#2b2b2b', fg='white', font=('Consolas', 14, 'bold'))
        title_label.pack(anchor='w', pady=(0, 20))
        
        # Имя кассеты
        tk.Label(parent, text="Название кассеты:", bg='#2b2b2b', fg='white').pack(anchor='w', pady=(0, 5))
        self.name_var = tk.StringVar(value="Untitled Program")
        name_entry = tk.Entry(parent, textvariable=self.name_var, bg='#3c3c3c', fg='white',
                             insertbackground='white', font=('Consolas', 10))
        name_entry.pack(fill=tk.X, pady=(0, 15))
        name_entry.focus_set()
        
        # Автор
        tk.Label(parent, text="Автор:", bg='#2b2b2b', fg='white').pack(anchor='w', pady=(0, 5))
        self.author_var = tk.StringVar(value="PC Builder IDE")
        author_entry = tk.Entry(parent, textvariable=self.author_var, bg='#3c3c3c', fg='white',
                               insertbackground='white', font=('Consolas', 10))
        author_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Описание
        tk.Label(parent, text="Описание:", bg='#2b2b2b', fg='white').pack(anchor='w', pady=(0, 5))
        self.description_text = tk.Text(parent, height=4, bg='#3c3c3c', fg='white',
                                       insertbackground='white', font=('Consolas', 10))
        self.description_text.pack(fill=tk.X, pady=(0, 15))
        self.description_text.insert('1.0', "Программа для PC Builder")
        
        # Путь сохранения
        tk.Label(parent, text="Путь сохранения:", bg='#2b2b2b', fg='white').pack(anchor='w', pady=(0, 5))
        
        path_frame = tk.Frame(parent, bg='#2b2b2b')
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.output_path_var = tk.StringVar(value="tapes/program.tape")
        path_entry = tk.Entry(path_frame, textvariable=self.output_path_var, bg='#3c3c3c', fg='white',
                             insertbackground='white', font=('Consolas', 10))
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(path_frame, text="...", bg='#4c4c4c', fg='white', border=0,
                 command=self.browse_tape_path).pack(side=tk.RIGHT, padx=(5, 0))
    
    def create_bin_widgets(self, parent):
        """Виджеты для компиляции в BIN"""
        # Заголовок
        title_label = tk.Label(parent, text="Создание BIN файлов", 
                              bg='#2b2b2b', fg='white', font=('Consolas', 14, 'bold'))
        title_label.pack(anchor='w', pady=(0, 20))
        
        # Путь сохранения
        tk.Label(parent, text="Папка сохранения:", bg='#2b2b2b', fg='white').pack(anchor='w', pady=(0, 5))
        
        path_frame = tk.Frame(parent, bg='#2b2b2b')
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.output_path_var = tk.StringVar(value="bios")
        path_entry = tk.Entry(path_frame, textvariable=self.output_path_var, bg='#3c3c3c', fg='white',
                             insertbackground='white', font=('Consolas', 10))
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(path_frame, text="...", bg='#4c4c4c', fg='white', border=0,
                 command=self.browse_bin_path).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Дополнительные опции
        options_frame = tk.LabelFrame(parent, text="Опции", bg='#2b2b2b', fg='white')
        options_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.overwrite_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Перезаписать существующие файлы",
                      variable=self.overwrite_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=10, pady=5)
        
        self.create_backup_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Создать резервную копию",
                      variable=self.create_backup_var, bg='#2b2b2b', fg='white',
                      selectcolor='#3c3c3c').pack(anchor='w', padx=10, pady=5)
    
    def browse_tape_path(self):
        """Выбор пути для TAPE файла"""
        filename = filedialog.asksaveasfilename(
            title="Сохранить TAPE как",
            defaultextension=".tape",
            filetypes=[("TAPE files", "*.tape"), ("All files", "*.*")]
        )
        if filename:
            self.output_path_var.set(filename)
    
    def browse_bin_path(self):
        """Выбор папки для BIN файлов"""
        dirname = filedialog.askdirectory(title="Выберите папку для сохранения")
        if dirname:
            self.output_path_var.set(dirname)
    
    def compile(self):
        """Компиляция с параметрами"""
        if self.compile_type == "tape":
            # Проверяем обязательные поля
            if not self.name_var.get().strip():
                messagebox.showerror("Ошибка", "Введите название кассеты")
                return
            
            self.result = {
                'type': 'tape',
                'metadata': {
                    'name': self.name_var.get().strip(),
                    'author': self.author_var.get().strip(),
                    'description': self.description_text.get('1.0', 'end-1c').strip()
                },
                'output_path': self.output_path_var.get().strip()
            }
        else:
            
            self.result = {
                'type': 'bin',
                'output_dir': self.output_path_var.get().strip(),
                'overwrite': self.overwrite_var.get(),
                'create_backup': self.create_backup_var.get()
            }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Отмена"""
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        """Показ диалога и возврат результата"""
        self.dialog.wait_window()
        return self.result
