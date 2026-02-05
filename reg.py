from pydantic import BaseModel, Field
from enum import Enum


class ParsingConfidence(str, Enum):
    HIGH = "high"        # Уверен в разметке
    MEDIUM = "medium"    # Есть небольшие сомнения
    LOW = "low"          # Требуется ручная проверка


class Function(BaseModel):
    """Конкретная функция/действие в рамках задачи."""
    text: str = Field(description="Текст функции")
    original_marker: str | None = Field(default=None, description="Исходный маркер (-, *, 1. и т.д.)")


class Task(BaseModel):
    """Задача с возможными подфункциями."""
    text: str = Field(description="Текст задачи")
    functions: list[Function] = Field(default_factory=list, description="Список функций в рамках задачи")
    original_marker: str | None = Field(default=None, description="Исходный маркер")


class ParsedResponsibilities(BaseModel):
    """Результат парсинга обязанностей вакансии."""
    
    tasks: list[Task] = Field(description="Список задач")
    
    confidence: ParsingConfidence = Field(description="Уверенность в парсинге")
    confidence_issues: list[str] = Field(
        default_factory=list, 
        description="Причины сниженной уверенности"
    )
    
    is_valid_structure: bool = Field(
        description="Текст имеет структуру списка обязанностей"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "tasks": [
                    {
                        "text": "Контролирует",
                        "functions": [
                            {"text": "Работу подчиненных", "original_marker": "*"},
                            {"text": "Сохранность имущества", "original_marker": "*"}
                        ],
                        "original_marker": "1."
                    },
                    {
                        "text": "Составляет отчётность",
                        "functions": [],
                        "original_marker": "2."
                    }
                ],
                "confidence": "high",
                "confidence_issues": [],
                "is_valid_structure": True
            }
        }


# === ПРОМПТ ДЛЯ LLM ===

PROMPT_TEMPLATE = """Распарси обязанности вакансии в структурированный формат.

Структура:
- Task (задача) — основной пункт обязанностей
- Function (функция) — конкретное действие в рамках задачи (вложенный пункт)

Правила:
1. Максимум 2 уровня: задачи и функции внутри них
2. Если пункт заканчивается на ":" — скорее всего дальше идут функции
3. Если вложенности нет — functions = []
4. confidence = "low" если: структура неоднозначна, непонятно что задача/функция

Верни JSON по схеме:
{{
  "tasks": [
    {{
      "text": "текст задачи (без маркера)",
      "functions": [
        {{"text": "текст функции", "original_marker": "- или * или null"}}
      ],
      "original_marker": "1. или * или null"
    }}
  ],
  "confidence": "high" | "medium" | "low",
  "confidence_issues": ["причина если не high"],
  "is_valid_structure": true | false
}}

Текст обязанностей:
{text}

JSON:"""


# === ИСПОЛЬЗОВАНИЕ ===

def parse_responsibilities(text: str) -> ParsedResponsibilities:
    """Парсит обязанности через LLM."""
    
    prompt = PROMPT_TEMPLATE.format(text=text)
    response = call_llm(prompt)  # твой вызов
    
    data = json.loads(response)
    return ParsedResponsibilities(**data)


# === ПРИМЕР ===

text = """1. Контролирует:
* Работу подчиненных
* Сохранность имущества
2. Составляет отчётность
3. Взаимодействует с подрядчиками:
- Ведёт переговоры
- Согласовывает договоры"""

result = parse_responsibilities(text)

print(f"Уверенность: {result.confidence}")
print(f"Валидная структура: {result.is_valid_structure}")
print()

for i, task in enumerate(result.tasks, 1):
    print(f"{i}. {task.text}")
    for func in task.functions:
        print(f"   - {func.text}")
```

**Вывод:**
```
Уверенность: high
Валидная структура: True

1. Контролирует
   - Работу подчиненных
   - Сохранность имущества
2. Составляет отчётность
3. Взаимодействует с подрядчиками
   - Ведёт переговоры
   - Согласовывает договоры
