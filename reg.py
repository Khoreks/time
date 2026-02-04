import re
from dataclasses import dataclass


@dataclass
class ListItem:
    level: int
    content: str
    original_marker: str


MARKER_PATTERNS = [
    r'^(\d+\.\d+[.)]\s*)',
    r'^(\d+[.)]\s*)',
    r'^([а-яА-Яa-zA-Z][.)]\s*)',
    r'^([-•*●○]\s*)',
    r'^(»\s*)',
]


def extract_marker(text: str) -> tuple[str, str]:
    for pattern in MARKER_PATTERNS:
        match = re.match(pattern, text)
        if match:
            marker = match.group(1)
            content = text[len(marker):].strip()
            return marker.strip(), content
    return '', text


def parse_list(text: str) -> list[ListItem]:
    lines = text.strip().split('\n')
    items = []
    parent_level = -1  # Отслеживаем уровень последнего "заголовка"
    
    for i, line in enumerate(lines):
        if not line.strip():
            continue
            
        indent = len(line) - len(line.lstrip())
        clean = line.strip()
        
        marker, content = extract_marker(clean)
        
        print(f"DEBUG: '{clean}' | marker='{marker}' | indent={indent}")
        
        if not marker:
            # Нет маркера — это заголовок группы
            level = 0
            parent_level = level
        else:
            # Есть маркер — вложенный под последний заголовок
            if parent_level >= 0:
                level = parent_level + 1
            else:
                level = 0
        
        print(f"DEBUG: -> level={level}")
        
        items.append(ListItem(
            level=level,
            content=content,
            original_marker=marker
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


# ТЕСТ
test = """текст:
* подтекст
* еще подтекст"""

print("=== ВХОД ===")
print(test)
print("\n=== ПАРСИНГ ===")
result = format_list(test)
print("\n=== ВЫХОД ===")
print(result)
