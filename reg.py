import re
from dataclasses import dataclass


@dataclass
class ListItem:
    level: int
    content: str
    original_marker: str


MARKER_PATTERNS = [
    r'^(\d+\.\d+[.)]\s*)',        # 2.1. или 2.1)
    r'^(\d+[.)]\s*)',              # 1. или 1)
    r'^([а-яА-Яa-zA-Z][.)]\s*)',   # а) или a.
    r'^([-•*●○]\s*)',              # - * •
    r'^(»\s*)',                     # »
]


def extract_marker(text: str) -> tuple[str, str]:
    for pattern in MARKER_PATTERNS:
        match = re.match(pattern, text)
        if match:
            marker = match.group(1)
            content = text[len(marker):].strip()
            return marker.strip(), content
    return '', text


def detect_level_from_marker(marker: str) -> int | None:
    """Определяет уровень по самому маркеру (например 2.1 = уровень 1)."""
    # Маркер типа 2.1. или 3.2.1.
    match = re.match(r'^(\d+(?:\.\d+)+)', marker)
    if match:
        parts = match.group(1).split('.')
        return len(parts) - 1  # 2.1 -> уровень 1, 2.1.3 -> уровень 2
    return None


def parse_list(text: str) -> list[ListItem]:
    lines = text.strip().split('\n')
    items = []
    
    # Собираем информацию о всех строках
    parsed_lines = []
    for line in lines:
        if not line.strip():
            continue
        
        indent = len(line) - len(line.lstrip())
        clean = line.strip()
        marker, content = extract_marker(clean)
        
        parsed_lines.append({
            'indent': indent,
            'marker': marker,
            'content': content,
            'has_marker': bool(marker)
        })
    
    # Определяем уникальные отступы для маппинга на уровни
    unique_indents = sorted(set(p['indent'] for p in parsed_lines))
    indent_to_level = {indent: i for i, indent in enumerate(unique_indents)}
    
    # Строим элементы
    for i, p in enumerate(parsed_lines):
        # Приоритет 1: уровень из самого маркера (2.1. -> level 1)
        level_from_marker = detect_level_from_marker(p['marker'])
        if level_from_marker is not None:
            level = level_from_marker
        
        # Приоритет 2: уровень по отступу
        elif p['indent'] > 0:
            level = indent_to_level[p['indent']]
        
        # Приоритет 3: без маркера + следующий с маркером = заголовок
        elif not p['has_marker']:
            # Проверяем, есть ли после этой строки пункты с маркерами/отступами
            has_children = False
            for j in range(i + 1, len(parsed_lines)):
                if parsed_lines[j]['indent'] > p['indent'] or parsed_lines[j]['has_marker']:
                    has_children = True
                    break
                if parsed_lines[j]['indent'] <= p['indent'] and not parsed_lines[j]['has_marker']:
                    break
            
            level = 0  # Заголовок всегда level 0
            
        else:
            level = 0
        
        items.append(ListItem(
            level=level,
            content=p['content'],
            original_marker=p['marker']
        ))
    
    return items


def renumber(items: list[ListItem]) -> list[tuple[str, str]]:
    result = []
    counters = [0] * 10
    
    for item in items:
        level = item.level
        counters[level] += 1
        
        for i in range(level + 1, len(counters)):
            counters[i] = 0
        
        number_parts = [str(counters[i]) for i in range(level + 1)]
        number = '.'.join(number_parts) + '.'
        
        result.append((number, item.content))
    
    return result


def format_list(text: str) -> str:
    items = parse_list(text)
    numbered = renumber(items)
    
    lines = []
    for number, content in numbered:
        depth = number.count('.') - 1
        indent = '  ' * depth
        lines.append(f"{indent}{number} {content}")
    
    return '\n'.join(lines)


# === ТЕСТЫ ===
test1 = """1. Определить цели проекта и собрать исходные требования.
2. Разработать архитектуру решения:
 2.1. Выбрать технологический стек и инструменты.
 2.2. Спроектировать взаимодействие компонентов системы.
3. Реализовать MVP и провести первичное тестирование."""

test2 = """Разработать архитектуру решения:
 - Выбрать технологический стек и инструменты.
 - Спроектировать взаимодействие компонентов системы."""

test3 = """* Определить цели проекта и собрать исходные требования.
* Разработать архитектуру решения:
 Выбрать технологический стек и инструменты.
 Спроектировать взаимодействие компонентов системы.
* Реализовать MVP и провести первичное тестирование."""

for i, test in enumerate([test1, test2, test3], 1):
    print(f"=== TEST {i} ===")
    print("Вход:")
    print(test)
    print("\nВыход:")
    print(format_list(test))
    print("\n")
