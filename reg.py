import re
from dataclasses import dataclass


@dataclass
class ListItem:
    level: int
    content: str
    original_marker: str


MARKER_PATTERNS = [
    (r'^(\d+\.\d+[.)]\s*)', 'nested_numeric'),  # 2.1.
    (r'^(\d+[.)]\s*)', 'numeric'),               # 1. или 1)
    (r'^([а-яА-Яa-zA-Z][.)]\s*)', 'alpha'),      # а) или a.
    (r'^([-•*●○]\s*)', 'bullet'),                # - * •
    (r'^(»\s*)', 'bullet'),                       # »
]


def extract_marker(text: str) -> tuple[str, str, str]:
    """Возвращает (маркер, контент, тип маркера)."""
    for pattern, marker_type in MARKER_PATTERNS:
        match = re.match(pattern, text)
        if match:
            marker = match.group(1)
            content = text[len(marker):].strip()
            return marker.strip(), content, marker_type
    return '', text, 'none'


def detect_level_from_marker(marker: str) -> int | None:
    """Уровень из составного маркера (2.1 -> level 1)."""
    match = re.match(r'^(\d+(?:\.\d+)+)', marker)
    if match:
        parts = match.group(1).split('.')
        return len(parts) - 1
    return None


def parse_list(text: str) -> list[ListItem]:
    lines = text.strip().split('\n')
    
    # Первый проход: собираем информацию
    parsed_lines = []
    for line in lines:
        if not line.strip():
            continue
        
        indent = len(line) - len(line.lstrip())
        clean = line.strip()
        marker, content, marker_type = extract_marker(clean)
        
        parsed_lines.append({
            'indent': indent,
            'marker': marker,
            'content': content,
            'marker_type': marker_type,
        })
    
    # Уникальные отступы -> уровни
    unique_indents = sorted(set(p['indent'] for p in parsed_lines))
    indent_to_level = {indent: i for i, indent in enumerate(unique_indents)}
    
    # Второй проход: определяем уровни
    items = []
    marker_type_stack = []  # Стек типов маркеров для отслеживания вложенности
    
    for i, p in enumerate(parsed_lines):
        level = 0
        
        # Приоритет 1: составной маркер (2.1.)
        level_from_marker = detect_level_from_marker(p['marker'])
        if level_from_marker is not None:
            level = level_from_marker
            
        # Приоритет 2: отступ
        elif p['indent'] > 0:
            level = indent_to_level[p['indent']]
            
        # Приоритет 3: смена типа маркера = вложенность
        elif p['marker_type'] != 'none':
            # Ищем предыдущий элемент с маркером на уровне 0
            prev_type = None
            for j in range(i - 1, -1, -1):
                if parsed_lines[j]['marker_type'] != 'none':
                    prev_type = parsed_lines[j]['marker_type']
                    prev_indent = parsed_lines[j]['indent']
                    break
            
            if prev_type and prev_type != p['marker_type'] and p['indent'] == 0:
                # Тип сменился: numeric -> bullet или bullet -> alpha и т.д.
                # Проверяем — это вложенность или новый список?
                
                # Смотрим вперёд: если потом вернётся старый тип — это вложенность
                returns_to_prev = False
                for j in range(i + 1, len(parsed_lines)):
                    if parsed_lines[j]['marker_type'] == prev_type and parsed_lines[j]['indent'] <= p['indent']:
                        returns_to_prev = True
                        break
                    if parsed_lines[j]['marker_type'] not in (p['marker_type'], 'none'):
                        break
                
                if returns_to_prev:
                    level = 1  # Это вложенный список
                else:
                    level = 0  # Это просто новый список с другим маркером
            else:
                level = 0
                
        # Приоритет 4: без маркера
        else:
            # Проверяем, есть ли после дочерние элементы
            has_children = False
            for j in range(i + 1, len(parsed_lines)):
                if parsed_lines[j]['indent'] > p['indent'] or (
                    parsed_lines[j]['marker_type'] != 'none' and 
                    parsed_lines[j]['indent'] >= p['indent']
                ):
                    has_children = True
                    break
                if parsed_lines[j]['indent'] < p['indent']:
                    break
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
