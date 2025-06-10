import re

def has_chinese_characters(text):
    pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002b73f\U0002b740-\U0002b81f\U0002b820-\U0002ceaf]')
    return bool(pattern.search(text))

# Пример использования
text1 = "Hello 你好世界!"
text2 = "No Chinese here."

print(has_chinese_characters(text1))  # True
print(has_chinese_characters(text2))  # False
