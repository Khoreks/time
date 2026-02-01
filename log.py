import argparse
import json
import unicodedata
from collections import defaultdict
from pathlib import Path


def get_char_language(char: str) -> str:
    """Определяет язык/категорию символа по Unicode"""
    
    code = ord(char)
    
    # ASCII (английский, цифры, базовая пунктуация)
    if code < 128:
        return "ascii"
    
    # Кириллица
    if 0x0400 <= code <= 0x04FF:  # Basic Cyrillic
        return "cyrillic"
    if 0x0500 <= code <= 0x052F:  # Cyrillic Supplement
        return "cyrillic"
    if 0x2DE0 <= code <= 0x2DFF:  # Cyrillic Extended-A
        return "cyrillic"
    if 0xA640 <= code <= 0xA69F:  # Cyrillic Extended-B
        return "cyrillic"
    if 0x1C80 <= code <= 0x1C8F:  # Cyrillic Extended-C
        return "cyrillic"
    
    # Расширенная латиница (европейские языки — оставляем)
    if 0x0080 <= code <= 0x00FF:  # Latin-1 Supplement (ñ, ü, ø и т.д.)
        return "latin_extended"
    if 0x0100 <= code <= 0x017F:  # Latin Extended-A
        return "latin_extended"
    if 0x0180 <= code <= 0x024F:  # Latin Extended-B
        return "latin_extended"
    if 0x1E00 <= code <= 0x1EFF:  # Latin Extended Additional
        return "latin_extended"
    
    # Общая пунктуация и символы (разрешаем)
    if 0x2000 <= code <= 0x206F:  # General Punctuation
        return "punctuation"
    if 0x2070 <= code <= 0x209F:  # Superscripts and Subscripts
        return "symbols"
    if 0x20A0 <= code <= 0x20CF:  # Currency Symbols (€, £, ¥)
        return "symbols"
    if 0x2100 <= code <= 0x214F:  # Letterlike Symbols
        return "symbols"
    if 0x2150 <= code <= 0x218F:  # Number Forms
        return "symbols"
    if 0x2190 <= code <= 0x21FF:  # Arrows
        return "symbols"
    if 0x2200 <= code <= 0x22FF:  # Mathematical Operators
        return "symbols"
    if 0x2300 <= code <= 0x23FF:  # Miscellaneous Technical
        return "symbols"
    if 0x2500 <= code <= 0x257F:  # Box Drawing
        return "symbols"
    if 0x2580 <= code <= 0x259F:  # Block Elements
        return "symbols"
    if 0x25A0 <= code <= 0x25FF:  # Geometric Shapes
        return "symbols"
    if 0x2600 <= code <= 0x26FF:  # Miscellaneous Symbols
        return "symbols"
    if 0x2700 <= code <= 0x27BF:  # Dingbats
        return "symbols"
    
    # Эмодзи (можно включить/исключить по желанию)
    if 0x1F300 <= code <= 0x1F9FF:  # Miscellaneous Symbols and Pictographs, Emoticons
        return "emoji"
    if 0x1FA00 <= code <= 0x1FAFF:  # Chess, symbols
        return "emoji"
    
    # Китайский
    if 0x4E00 <= code <= 0x9FFF:    # CJK Unified Ideographs
        return "chinese"
    if 0x3400 <= code <= 0x4DBF:    # CJK Extension A
        return "chinese"
    if 0x20000 <= code <= 0x2A6DF:  # CJK Extension B
        return "chinese"
    if 0x2A700 <= code <= 0x2B73F:  # CJK Extension C
        return "chinese"
    if 0x2B740 <= code <= 0x2B81F:  # CJK Extension D
        return "chinese"
    if 0x2B820 <= code <= 0x2CEAF:  # CJK Extension E
        return "chinese"
    if 0x2CEB0 <= code <= 0x2EBEF:  # CJK Extension F
        return "chinese"
    if 0x30000 <= code <= 0x3134F:  # CJK Extension G
        return "chinese"
    if 0xF900 <= code <= 0xFAFF:    # CJK Compatibility Ideographs
        return "chinese"
    if 0x3000 <= code <= 0x303F:    # CJK Punctuation
        return "chinese"
    if 0x31C0 <= code <= 0x31EF:    # CJK Strokes
        return "chinese"
    if 0x2F00 <= code <= 0x2FDF:    # Kangxi Radicals
        return "chinese"
    if 0x2E80 <= code <= 0x2EFF:    # CJK Radicals Supplement
        return "chinese"
    if 0x3100 <= code <= 0x312F:    # Bopomofo
        return "chinese"
    if 0x31A0 <= code <= 0x31BF:    # Bopomofo Extended
        return "chinese"
    
    # Японский (кроме кандзи, которые выше как китайский)
    if 0x3040 <= code <= 0x309F:    # Hiragana
        return "japanese"
    if 0x30A0 <= code <= 0x30FF:    # Katakana
        return "japanese"
    if 0x31F0 <= code <= 0x31FF:    # Katakana Phonetic Extensions
        return "japanese"
    if 0xFF65 <= code <= 0xFF9F:    # Halfwidth Katakana
        return "japanese"
    
    # Корейский
    if 0xAC00 <= code <= 0xD7AF:    # Hangul Syllables
        return "korean"
    if 0x1100 <= code <= 0x11FF:    # Hangul Jamo
        return "korean"
    if 0x3130 <= code <= 0x318F:    # Hangul Compatibility Jamo
        return "korean"
    if 0xA960 <= code <= 0xA97F:    # Hangul Jamo Extended-A
        return "korean"
    if 0xD7B0 <= code <= 0xD7FF:    # Hangul Jamo Extended-B
        return "korean"
    
    # Арабский
    if 0x0600 <= code <= 0x06FF:    # Arabic
        return "arabic"
    if 0x0750 <= code <= 0x077F:    # Arabic Supplement
        return "arabic"
    if 0x08A0 <= code <= 0x08FF:    # Arabic Extended-A
        return "arabic"
    if 0xFB50 <= code <= 0xFDFF:    # Arabic Presentation Forms-A
        return "arabic"
    if 0xFE70 <= code <= 0xFEFF:    # Arabic Presentation Forms-B
        return "arabic"
    
    # Иврит
    if 0x0590 <= code <= 0x05FF:    # Hebrew
        return "hebrew"
    if 0xFB00 <= code <= 0xFB4F:    # Hebrew Presentation Forms
        return "hebrew"
    
    # Тайский
    if 0x0E00 <= code <= 0x0E7F:
        return "thai"
    
    # Вьетнамский (часть Latin Extended)
    # уже покрыт latin_extended
    
    # Греческий
    if 0x0370 <= code <= 0x03FF:    # Greek and Coptic
        return "greek"
    if 0x1F00 <= code <= 0x1FFF:    # Greek Extended
        return "greek"
    
    # Армянский
    if 0x0530 <= code <= 0x058F:
        return "armenian"
    
    # Грузинский
    if 0x10A0 <= code <= 0x10FF:
        return "georgian"
    
    # Деванагари (хинди и др.)
    if 0x0900 <= code <= 0x097F:
        return "devanagari"
    
    # Fullwidth формы (часто китайская пунктуация)
    if 0xFF00 <= code <= 0xFFEF:
        return "fullwidth"
    
    # Private Use Area (иногда спец-токены)
    if 0xE000 <= code <= 0xF8FF:
        return "private_use"
    
    # Остальное
    return "other"


def classify_token(token_str: str) -> tuple[str, set[str]]:
    """
    Классифицирует токен по содержащимся языкам.
    
    Returns:
        (основной_язык, множество_всех_языков_в_токене)
    """
    if not token_str:
        return "empty", set()
    
    languages = defaultdict(int)
    
    for char in token_str:
        lang = get_char_language(char)
        languages[lang] += 1
    
    # Определяем основной язык (по количеству символов)
    if languages:
        primary = max(languages.keys(), key=lambda k: languages[k])
    else:
        primary = "empty"
    
    return primary, set(languages.keys())


def is_token_allowed(token_str: str, allow_emoji: bool = True) -> tuple[bool, str]:
    """
    Проверяет, разрешён ли токен.
    
    Returns:
        (разрешён, причина)
    """
    if not token_str:
        return True, "empty"
    
    primary, all_langs = classify_token(token_str)
    
    # Разрешённые категории
    allowed = {
        "ascii",
        "cyrillic", 
        "latin_extended",
        "punctuation",
        "symbols",
        "private_use",  # спец-токены моделей
        "empty",
    }
    
    if allow_emoji:
        allowed.add("emoji")
    
    # Греческий часто используется в математике/науке
    allowed.add("greek")
    
    # Проверяем все языки в токене
    blocked_langs = all_langs - allowed
    
    if blocked_langs:
        return False, f"contains: {', '.join(sorted(blocked_langs))}"
    
    return True, "ok"


def analyze_tokenizer(model_name: str, allow_emoji: bool = True):
    """Анализирует vocabulary токенизатора"""
    
    from transformers import AutoTokenizer
    
    print(f"Загрузка токенизатора: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    
    vocab_size = tokenizer.vocab_size
    print(f"Размер словаря: {vocab_size:,}")
    
    # Получаем специальные токены
    special_tokens = set()
    if hasattr(tokenizer, 'all_special_tokens'):
        special_tokens = set(tokenizer.all_special_tokens)
    if hasattr(tokenizer, 'additional_special_tokens'):
        special_tokens.update(tokenizer.additional_special_tokens or [])
    
    special_token_ids = set()
    if hasattr(tokenizer, 'all_special_ids'):
        special_token_ids = set(tokenizer.all_special_ids)
    
    print(f"Специальных токенов: {len(special_tokens)}")
    
    # Анализируем каждый токен
    allowed_ids = []
    blocked_ids = []
    stats = defaultdict(int)
    blocked_examples = defaultdict(list)
    
    print("Анализ токенов...")
    
    for token_id in range(vocab_size):
        # Специальные токены всегда разрешены
        if token_id in special_token_ids:
            allowed_ids.append(token_id)
            stats["special"] += 1
            continue
        
        try:
            token_str = tokenizer.decode([token_id], skip_special_tokens=False)
        except Exception:
            # Если не можем декодировать — разрешаем (скорее всего спец-токен)
            allowed_ids.append(token_id)
            stats["decode_error"] += 1
            continue
        
        # Проверяем, входит ли в специальные токены по строке
        if token_str in special_tokens:
            allowed_ids.append(token_id)
            stats["special"] += 1
            continue
        
        is_allowed, reason = is_token_allowed(token_str, allow_emoji)
        
        if is_allowed:
            allowed_ids.append(token_id)
            stats["allowed"] += 1
        else:
            blocked_ids.append(token_id)
            stats["blocked"] += 1
            
            # Сохраняем примеры для отчёта
            primary, _ = classify_token(token_str)
            if len(blocked_examples[primary]) < 5:
                blocked_examples[primary].append((token_id, repr(token_str)))
    
    return {
        "model": model_name,
        "vocab_size": vocab_size,
        "allowed_ids": allowed_ids,
        "blocked_ids": blocked_ids,
        "stats": dict(stats),
        "blocked_examples": dict(blocked_examples),
    }


def print_report(result: dict):
    """Выводит отчёт по анализу"""
    
    print("\n" + "=" * 60)
    print("ОТЧЁТ")
    print("=" * 60)
    
    print(f"\nМодель: {result['model']}")
    print(f"Размер словаря: {result['vocab_size']:,}")
    print(f"\nРазрешено токенов: {len(result['allowed_ids']):,}")
    print(f"Заблокировано токенов: {len(result['blocked_ids']):,}")
    
    print(f"\nСтатистика:")
    for key, value in sorted(result['stats'].items()):
        print(f"  {key}: {value:,}")
    
    if result['blocked_examples']:
        print(f"\nПримеры заблокированных токенов по языкам:")
        for lang, examples in sorted(result['blocked_examples'].items()):
            print(f"\n  {lang}:")
            for token_id, token_repr in examples[:3]:
                print(f"    ID {token_id}: {token_repr}")


def main():
    parser = argparse.ArgumentParser(
        description="Анализ vocabulary модели для фильтрации по языку"
    )
    parser.add_argument(
        "model",
        help="Название модели или путь (например: Qwen/Qwen2.5-7B-Instruct)"
    )
    parser.add_argument(
        "--output", "-o",
        default="filtered_tokens.json",
        help="Файл для сохранения результатов (default: filtered_tokens.json)"
    )
    parser.add_argument(
        "--no-emoji",
        action="store_true",
        help="Блокировать эмодзи"
    )
    
    args = parser.parse_args()
    
    result = analyze_tokenizer(args.model, allow_emoji=not args.no_emoji)
    print_report(result)
    
    # Сохраняем результат
    output_path = Path(args.output)
    
    # Основной файл — только blocked_ids для процессора
    output_data = {
        "model": result["model"],
        "vocab_size": result["vocab_size"],
        "blocked_ids": result["blocked_ids"],
        "allowed_count": len(result["allowed_ids"]),
        "blocked_count": len(result["blocked_ids"]),
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Результат сохранён в: {output_path}")
    print(f"  (blocked_ids: {len(result['blocked_ids']):,} токенов)")
    
    # Опционально сохраняем полный отчёт
    full_report_path = output_path.with_suffix(".full.json")
    with open(full_report_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Полный отчёт: {full_report_path}")


if __name__ == "__main__":
    main()
