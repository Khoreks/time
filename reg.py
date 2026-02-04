import re
from dataclasses import dataclass


@dataclass
class ListItem:
    level: int
    content: str
    original_marker: str


def parse_list(text: str) -> list[ListItem]:
    """Парсит текст со списком любого формата."""
    
    # Паттерны маркеров (порядок важен — от специфичных к общим)
    MARKER_PATTERNS = [
        r'^(\d+\.\d+[.)]\s*)',        # 1.1. или 1.1)
        r'^(\d+[.)]\s*)',              # 1. или 1)
        r'^([а-яА-Яa-zA-Z][.)]\s*)',   # а) или a. или А)
        r'^([-•*●○]\s*)',              # - * • ● ○
        r'^(»\s*)',                     # »
    ]
    
    lines = text.strip().split('\n')
    items = []
    
    for line in lines:
        if not line.strip():
            continue
            
        # Считаем отступ (для вложенности)
        indent = len(line) - len(line.lstrip())
        clean = line.strip()
        
        # Ищем маркер
        marker = ''
        content = clean
        
        for pattern in MARKER_PATTERNS:
            match = re.match(pattern, clean)
            if match:
                marker = match.group(1)
                content = clean[len(marker):].strip()
                break
        
        # Уровень вложенности: по отступу или по типу маркера
        level = calculate_level(indent, marker)
        
        items.append(ListItem(
            level=level,
            content=content,
            original_marker=marker.strip()
        ))
    
    return items


def calculate_level(indent: int, marker: str) -> int:
    """Определяет уровень вложенности."""
    # Базовый уровень по отступу
    level = indent // 2
    
    # Вложенный номер типа 1.1 — это уровень 1
    if re.match(r'\d+\.\d+', marker):
        level = max(level, 1)
    
    return level


def renumber(items: list[ListItem]) -> list[tuple[str, str]]:
    """Перенумеровывает в формат 1. 2. 2.1. 2.2. 3."""
    result = []
    counters = [0] * 10  # до 10 уровней вложенности
    
    for item in items:
        level = item.level
        
        # Увеличиваем счётчик текущего уровня
        counters[level] += 1
        
        # Сбрасываем счётчики более глубоких уровней
        for i in range(level + 1, len(counters)):
            counters[i] = 0
        
        # Формируем номер: 1. или 1.2. или 1.2.3.
        number_parts = [str(counters[i]) for i in range(level + 1)]
        number = '.'.join(number_parts) + '.'
        
        result.append((number, item.content))
    
    return result


def format_list(text: str) -> str:
    """Главная функция: текст → структурированный список."""
    items = parse_list(text)
    numbered = renumber(items)
    
    lines = []
    for number, content in numbered:
        # Отступ для визуализации вложенности
        depth = number.count('.') - 1
        indent = '  ' * depth
        lines.append(f"{indent}{number} {content}")
    
    return '\n'.join(lines)


# === ТЕСТИРУЕМ ===

if __name__ == '__main__':
    test_cases = [
        # Тест 1: Разные маркеры
        """
        1) Первый пункт
        2) Второй пункт
        а) подпункт а
        б) подпункт б
        3) Третий пункт
        """,
        
        # Тест 2: Буллеты с отступами
        """
        - Купить п
