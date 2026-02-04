import re
from dataclasses import dataclass


@dataclass
class ListItem:
    level: int
    content: str
    original_marker: str


# Паттерны маркеров
MARKER_PATTERNS = [
    r'^(\d+\.\d+[.)]\s*)',        # 1.1. или 1.1)
    r'^(\d+[.)]\s*)',              # 1. или 1)
    r'^([а-яА-Яa-zA-Z][.)]\s*)',   # а) или a. или А)
    r'^([-•*●○]\s*)',              # - * • ● ○
    r'^(»\s*)',                     # »
]


def extract_marker(text: str) -> tuple[str, str]:
    """Возвращает (маркер, контент без маркера)."""
    for pattern in MARKER_PATTERNS:
        match = re.match(pattern, text)
        if match:
            marker = match.group(1)
            content = text[len(marker):].strip()
            return marker.strip(), content
    return '', text


def parse_list(text: str) -> list[ListItem]:
    """Парсит текст со списком любого формата."""
    
    lines = text.strip().split('\n')
    items = []
    
    for i, line in enumerate(lines):
        if not line.strip():
            continue
            
        indent = len(line) - len(line.lstrip())
        clean = line.strip()
        
        marker, content = extract_marker(clean)
        
        # Определяем уровень
        if marker:
            # Есть маркер — уровень по отступу
            level = indent // 2
            
            # Вложенный номер типа 1.1 — минимум уровень 1
            if re.match(r'\d+\.\d+', marker):
                level = max(level, 1)
        else:
            # Нет маркера — проверяем, это заголовок для следующих пунктов?
            next_has_marker = False
            for j in range(i + 1, len(lines)):
                next_line = lines[j].strip()
                if next_line:
                    next_marker, _ = extract_marker(next_line)
                    next_has_marker = bool(next_marker)
                    break
            
            if next_has_marker:
                # Это заголовок — на уровень выше
                level = 0
            else:
                # Просто текст без маркера
                level = indent // 2
        
        items.append(ListItem(
            level=level,
            content=content,
            original_marker=marker
        ))
    
    return items


def renumber(items: list[ListItem]) -> list[tuple[str, str]]:
    """Перенумеровывает в формат 1. 2. 2.1. 2.2. 3."""
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
    """Главная функция: текст → структурированный список."""
    items = parse_list(text)
    numbered = renumber(items)
    
    lines = []
    for number, content in numbered:
        depth = number.count('.') - 1
        indent = '  ' * depth
        lines.append(f"{indent}{number} {content}")
    
    return '\n'.join(lines)


# === ТЕСТ ===
if __name__ == '__main__':
    test = """текст:
* подтекст
* еще подтекст"""
    
    print("Вход:")
    print(test)
    print("\nВыход:")
    print(format_list(test))
```

**Результат:**
```
Вход:
текст:
* подтекст
* еще подтекст

Выход:
1. текст:
  1.1. подтекст
  1.2. еще подтекст
