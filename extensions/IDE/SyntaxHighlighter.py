import tkinter as tk
import re

class SyntaxHighlighter:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        
        # Настройка тегов для подсветки
        self.setup_tags()
        
        # Паттерны для подсветки
        self.setup_patterns()
        
        print("🎨 Подсветка синтаксиса инициализирована")
        
    def force_highlight(self):
        """Принудительная подсветка синтаксиса"""
        self.text_widget.after_idle(self.highlight_syntax)
    
    def setup_tags(self):
        """Настройка тегов для подсветки"""
        # Цвета по умолчанию (тема VS Code Dark)
        self.colors = {
            'keyword': '#569cd6',      # Голубой для ключевых слов
            'register': '#9cdcfe',     # Светло-голубой для регистров
            'number': '#b5cea8',       # Зеленый для чисел
            'string': '#ce9178',       # Оранжевый для строк
            'comment': '#6a9955',      # Зеленый для комментариев
            'label': '#dcdcaa',        # Желтый для меток
            'directive': '#c586c0',    # Розовый для директив
            'operator': '#d4d4d4',     # Белый для операторов
            'error': '#f44747',        # Красный для ошибок
            'address': '#4fc1ff',      # Синий для адресов
        }
        
        # Создаем теги
        for tag_name, color in self.colors.items():
            self.text_widget.tag_configure(tag_name, foreground=color)
        
        # Специальные стили
        self.text_widget.tag_configure('bold', font=('Consolas', 11, 'bold'))
        self.text_widget.tag_configure('italic', font=('Consolas', 11, 'italic'))
    
    def setup_patterns(self):
        """Настройка паттернов для подсветки"""
        # Инструкции процессора
        self.instructions = [
            'nop', 'mov', 'ld', 'add', 'sub', 'xor', 'or', 'and', 'not',
            'cmp', 'jmp', 'je', 'jne', 'shl', 'shr', 'call', 'ret',
            'in', 'out', 'ldm', 'stm', 'hlt', 'push', 'pop', 'inc', 'dec'
        ]
        
        # Регистры
        self.registers = ['a', 'b', 'c', 'd', 'ip', 'ir', 'sp', 'bp', 'ss']
        
        # Создаем скомпилированные регулярные выражения
        self.patterns = [
            # Комментарии (самый высокий приоритет)
            (r';.*$', 'comment'),
            
            # Директивы
            (r'#\w+', 'directive'),
            
            # Метки (слово с двоеточием)
            (r'^\s*([a-zA-Z_\.][a-zA-Z0-9_\.]*)\s*:', 'label'),
            
            # Шестнадцатеричные числа
            (r'\b0[xX][0-9a-fA-F]+\b', 'number'),
            
            # Двоичные числа
            (r'\b0[bB][01]+\b', 'number'),
            
            # Десятичные числа
            (r'\b\d+\b', 'number'),
            
            # Адресация памяти
            (r'\[[^\]]+\]', 'address'),
            
            # Инструкции (создаем паттерн динамически)
            (r'\b(?:' + '|'.join(self.instructions) + r')\b', 'keyword'),
            
            # Регистры (создаем паттерн динамически)
            (r'\b(?:' + '|'.join(self.registers) + r')\b', 'register'),
            
            # Операторы
            (r'[+\-*/=<>!&|^~]', 'operator'),
            
            # Запятые и скобки
            (r'[,\(\)\[\]]', 'operator'),
        ]
        
        # Компилируем регулярные выражения
        self.compiled_patterns = []
        for pattern, tag in self.patterns:
            try:
                compiled_pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                self.compiled_patterns.append((compiled_pattern, tag))
            except re.error as e:
                print(f"Ошибка компиляции паттерна {pattern}: {e}")
    
    def highlight_syntax(self):
        """Основная функция подсветки синтаксиса"""
        try:
            # Получаем весь текст
            content = self.text_widget.get('1.0', 'end-1c')
            
            # Удаляем все существующие теги
            for tag_name in self.colors.keys():
                self.text_widget.tag_remove(tag_name, '1.0', 'end')
            
            # ИСПРАВЛЕНИЕ: Проверяем, есть ли текст для подсветки
            if not content.strip():
                return
            
            # Применяем подсветку построчно для лучшей производительности
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                if line.strip():  # Подсвечиваем только непустые строки
                    self.highlight_line(line_num, line)
        
        except tk.TclError:
            # Игнорируем ошибки во время обновления виджета
            pass
        
    def highlight_line(self, line_num, line_content):
        """Подсветка одной строки"""
        line_start = f'{line_num}.0'
        
        # Применяем каждый паттерн
        for pattern, tag in self.compiled_patterns:
            for match in pattern.finditer(line_content):
                start_col = match.start()
                end_col = match.end()
                
                start_pos = f'{line_num}.{start_col}'
                end_pos = f'{line_num}.{end_col}'
                
                # Для меток берем только группу 1 (имя метки)
                if tag == 'label' and match.groups():
                    label_start = match.start(1)
                    label_end = match.end(1)
                    start_pos = f'{line_num}.{label_start}'
                    end_pos = f'{line_num}.{label_end}'
                
                self.text_widget.tag_add(tag, start_pos, end_pos)
        
        # Специальная обработка для контекстно-зависимых элементов
        self.highlight_context_dependent(line_num, line_content)
    
    def highlight_context_dependent(self, line_num, line_content):
        """Подсветка контекстно-зависимых элементов"""
        # Подсветка ошибок синтаксиса
        self.highlight_syntax_errors(line_num, line_content)
        
        # Подсветка неиспользуемых меток
        self.highlight_unused_labels(line_num, line_content)
    
    def highlight_syntax_errors(self, line_num, line_content):
        """Подсветка синтаксических ошибок"""
        line = line_content.strip()
        
        # Пропускаем комментарии и пустые строки
        if line.startswith(';') or not line:
            return
        
        # Проверяем базовые ошибки
        errors = []
        
        # Недопустимые символы в начале строки
        if re.match(r'^\s*[0-9]', line) and ':' not in line:
            errors.append("Строка не может начинаться с цифры")
        
        # Неправильное использование скобок
        brackets = line.count('[') - line.count(']')
        if brackets != 0:
            errors.append("Несбалансированные скобки")
        
        # Если есть ошибки, подсвечиваем всю строку
        if errors:
            start_pos = f'{line_num}.0'
            end_pos = f'{line_num}.end'
            self.text_widget.tag_add('error', start_pos, end_pos)
    
    def highlight_unused_labels(self, line_num, line_content):
        """Подсветка неиспользуемых меток (упрощенная версия)"""
        # Эта функция может быть расширена для анализа всего кода
        pass
    
    def update_colors(self, theme_settings):
        """Обновление цветовой схемы"""
        # Обновляем цвета из настроек
        color_mapping = {
            'keyword': theme_settings.get('keyword_color', '#569cd6'),
            'register': theme_settings.get('register_color', '#9cdcfe'),
            'number': theme_settings.get('number_color', '#b5cea8'),
            'string': theme_settings.get('string_color', '#ce9178'),
            'comment': theme_settings.get('comment_color', '#6a9955'),
            'label': theme_settings.get('label_color', '#dcdcaa'),
            'directive': theme_settings.get('directive_color', '#c586c0'),
            'operator': theme_settings.get('operator_color', '#d4d4d4'),
            'error': theme_settings.get('error_color', '#f44747'),
            'address': theme_settings.get('address_color', '#4fc1ff'),
        }
        
        # Применяем новые цвета
        for tag_name, color in color_mapping.items():
            if tag_name in self.colors:
                self.colors[tag_name] = color
                self.text_widget.tag_configure(tag_name, foreground=color)
    
    def add_custom_pattern(self, pattern, tag_name, color):
        """Добавление пользовательского паттерна"""
        try:
            compiled_pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            self.compiled_patterns.append((compiled_pattern, tag_name))
            
            # Создаем новый тег если его нет
            if tag_name not in self.colors:
                self.colors[tag_name] = color
                self.text_widget.tag_configure(tag_name, foreground=color)
            
            print(f"Добавлен пользовательский паттерн: {pattern} -> {tag_name}")
        except re.error as e:
            print(f"Ошибка добавления паттерна {pattern}: {e}")
    
    def remove_custom_pattern(self, pattern):
        """Удаление пользовательского паттерна"""
        self.compiled_patterns = [
            (p, t) for p, t in self.compiled_patterns 
            if p.pattern != pattern
        ]
    
    def get_syntax_info(self, position):
        """Получение информации о синтаксисе в указанной позиции"""
        # Получаем все теги в указанной позиции
        tags = self.text_widget.tag_names(position)
        
        syntax_info = {
            'position': position,
            'tags': list(tags),
            'type': None,
            'description': ''
        }
        
        # Определяем тип элемента
        if 'keyword' in tags:
            syntax_info['type'] = 'instruction'
            syntax_info['description'] = 'Инструкция процессора'
        elif 'register' in tags:
            syntax_info['type'] = 'register'
            syntax_info['description'] = 'Регистр процессора'
        elif 'number' in tags:
            syntax_info['type'] = 'number'
            syntax_info['description'] = 'Числовое значение'
        elif 'label' in tags:
            syntax_info['type'] = 'label'
            syntax_info['description'] = 'Метка'
        elif 'directive' in tags:
            syntax_info['type'] = 'directive'
            syntax_info['description'] = 'Директива ассемблера'
        elif 'comment' in tags:
            syntax_info['type'] = 'comment'
            syntax_info['description'] = 'Комментарий'
        elif 'address' in tags:
            syntax_info['type'] = 'address'
            syntax_info['description'] = 'Адресация памяти'
        
        return syntax_info
    
    def highlight_matching_brackets(self, position):
        """Подсветка соответствующих скобок"""
        # Получаем символ в указанной позиции
        char = self.text_widget.get(position)
        
        if char in '[](){}':
            # Ищем соответствующую скобку
            matching_pos = self.find_matching_bracket(position, char)
            
            if matching_pos:
                # Подсвечиваем обе скобки
                self.text_widget.tag_remove('matching_bracket', '1.0', 'end')
                self.text_widget.tag_add('matching_bracket', position)
                self.text_widget.tag_add('matching_bracket', matching_pos)
                self.text_widget.tag_configure('matching_bracket', 
                                             background='#555555', foreground='#ffffff')
    
    def find_matching_bracket(self, position, bracket):
        """Поиск соответствующей скобки"""
        bracket_pairs = {'[': ']', '(': ')', '{': '}', ']': '[', ')': '(', '}': '{'}
        matching_bracket = bracket_pairs.get(bracket)
        
        if not matching_bracket:
            return None
        
        # Определяем направление поиска
        if bracket in '[({':
            direction = 1  # Ищем вперед
            start_pos = f"{position}+1c"
            end_pos = 'end'
        else:
            direction = -1  # Ищем назад
            start_pos = f"{position}-1c"
            end_pos = '1.0'
        
        # Простой поиск (без учета вложенности для краткости)
        content = self.text_widget.get(start_pos, end_pos)
        
        for i, char in enumerate(content):
            if char == matching_bracket:
                if direction == 1:
                    return f"{position}+{i+1}c"
                else:
                    return f"{position}-{len(content)-i}c"
        
        return None
