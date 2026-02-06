from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────────────

class AutomationPotential(str, Enum):
    """Потенциал автоматизации группы запросов LLM-агентом."""
    HIGH = "high"          # Полностью закрывается LLM
    MEDIUM = "medium"      # LLM ассистирует оператору
    LOW = "low"            # Минимальная помощь LLM
    NONE = "none"          # Только человек

class RequestComplexity(str, Enum):
    """Сложность типичного запроса в группе."""
    SIMPLE = "simple"          # Шаблонный, не требует экспертизы
    MODERATE = "moderate"      # Требует контекста или нескольких шагов
    COMPLEX = "complex"        # Требует глубокой экспертизы / эскалации

class InteractionType(str, Enum):
    """Тип взаимодействия с пользователем."""
    INFORMATIONAL = "informational"    # FAQ, статус, справка
    ACTION_REQUEST = "action_request"  # Сделай что-то (доступ, настройка)
    DIAGNOSTICS = "diagnostics"        # Диагностика / troubleshooting
    CONSULTATION = "consultation"      # Консультация, требует обсуждения

class Repeatability(str, Enum):
    """Повторяемость запросов в группе."""
    TEMPLATE = "template"    # Шаблонные, повторяются регулярно
    FREQUENT = "frequent"    # Встречаются часто, но с вариациями
    RARE = "rare"            # Единичные / уникальные случаи


# ── Группировка запросов ─────────────────────────────────────────────────

class RequestGroup(BaseModel):
    """Группа однотипных запросов внутри периода."""

    group_name: str = Field(
        description="Краткое название группы запросов"
    )
    description: str = Field(
        description="Описание: что объединяет запросы в этой группе"
    )
    example_requests: list[str] = Field(
        description="2-3 характерных примера запросов из группы"
    )
    request_count: int = Field(
        description="Количество запросов в группе"
    )
    share_percent: float = Field(
        description="Доля группы от общего числа запросов в периоде (%)"
    )

    # Разметка для автоматизации
    repeatability: Repeatability = Field(
        description="Повторяемость запросов"
    )
    complexity: RequestComplexity = Field(
        description="Сложность типичного запроса"
    )
    interaction_type: InteractionType = Field(
        description="Тип взаимодействия"
    )
    automation_potential: AutomationPotential = Field(
        description="Потенциал автоматизации LLM-агентом"
    )
    automation_comment: str = Field(
        description=(
            "Пояснение: почему такой уровень автоматизации, "
            "что именно может делать LLM-агент для этой группы"
        )
    )


# ── Аналитика периода ───────────────────────────────────────────────────

class PeriodAnalysis(BaseModel):
    """Полный анализ одного периода."""

    period_label: str = Field(
        description="Название периода, например '2020-2023'"
    )
    total_requests: int = Field(
        description="Общее количество запросов в периоде"
    )

    groups: list[RequestGroup] = Field(
        description="Группы запросов с разметкой"
    )

    top_issues: list[str] = Field(
        description="Топ-3 самых частых / значимых проблем"
    )
    systemic_issues: list[str] = Field(
        description="Системные (повторяющиеся) проблемы периода"
    )
    anomalies: list[str] = Field(
        description="Аномалии, нетипичные всплески, выбросы"
    )

    analytics_summary: str = Field(
        description=(
            "Развёрнутый аналитический текст по периоду: "
            "ключевые наблюдения, паттерны, характеристика нагрузки. "
            "3-5 абзацев."
        )
    )


# ── Сравнение периодов ──────────────────────────────────────────────────

class PeriodComparison(BaseModel):
    """Сравнительный анализ двух периодов."""

    new_appeared: list[str] = Field(
        description="Типы запросов, которые появились только во втором периоде"
    )
    disappeared: list[str] = Field(
        description="Типы запросов, которые исчезли во втором периоде"
    )
    growing: list[str] = Field(
        description="Категории с ростом количества / доли"
    )
    declining: list[str] = Field(
        description="Категории со снижением количества / доли"
    )
    stable: list[str] = Field(
        description="Стабильные категории без значимых изменений"
    )
    change_hypotheses: list[str] = Field(
        description=(
            "Гипотезы: почему произошли изменения "
            "(оргизменения, новые системы, удалёнка и т.д.)"
        )
    )

    comparison_summary: str = Field(
        description=(
            "Развёрнутый аналитический текст сравнения периодов: "
            "тренды, динамика, ключевые сдвиги. 2-4 абзаца."
        )
    )


# ── Карта автоматизации ─────────────────────────────────────────────────

class AutomationMapItem(BaseModel):
    """Элемент карты автоматизации."""

    group_name: str = Field(
        description="Название группы запросов"
    )
    llm_role: str = Field(
        description=(
            "Что именно делает LLM-агент: "
            "'closes' — закрывает полностью, "
            "'assists' — помогает оператору, "
            "'not_applicable' — не участвует"
        )
    )
    llm_capabilities: list[str] = Field(
        description="Конкретные действия LLM-агента для этой группы"
    )
    estimated_coverage_percent: float = Field(
        description="Оценка % запросов группы, которые LLM может покрыть"
    )
    priority: int = Field(
        description="Приоритет внедрения (1 = quick win, 2 = средний, 3 = долгосрочный)"
    )


class AutomationMap(BaseModel):
    """Карта автоматизации с оценкой эффекта."""

    items: list[AutomationMapItem] = Field(
        description="Элементы карты по каждой группе запросов"
    )
    total_automatable_percent: float = Field(
        description="Общий % запросов, потенциально покрываемых LLM-агентом"
    )
    quick_wins: list[str] = Field(
        description="Группы для первоочередного внедрения (быстрый эффект)"
    )
    long_term: list[str] = Field(
        description="Группы, требующие значительной подготовки"
    )


# ── Итоговый отчёт ──────────────────────────────────────────────────────

class ClassificationReport(BaseModel):
    """
    Полный отчёт по одной классификации запросов Service Desk.
    Это корневая модель — именно её передавать как response_format.
    """

    classification_name: str = Field(
        description="Название классификации (категории) запросов"
    )

    executive_summary: str = Field(
        description=(
            "Краткая сводка для руководства: "
            "ключевые цифры, главные выводы, рекомендации. 1-2 абзаца."
        )
    )

    period_1: PeriodAnalysis = Field(
        description="Анализ первого периода (2020-2023)"
    )
    period_2: PeriodAnalysis = Field(
        description="Анализ второго периода (2024-2025)"
    )

    comparison: PeriodComparison = Field(
        description="Сравнение двух периодов"
    )

    automation_map: AutomationMap = Field(
        description="Карта автоматизации LLM-агентом"
    )

    conclusions: list[str] = Field(
        description="Общие выводы (3-5 пунктов)"
    )
    recommendations: list[str] = Field(
        description="Рекомендации по развитию поддержки и внедрению LLM (3-5 пунктов)"
    )



# System prompt

Ты — аналитик службы технической поддержки. Твоя задача — провести глубокий анализ запросов из Service Desk для принятия решений о развитии поддержки и внедрении LLM-агента.

## Контекст

Компания рассматривает внедрение LLM-агента, который будет:
- Полностью закрывать часть запросов пользователей (FAQ, типовые инструкции, статусы)
- Помогать операторам в режиме чата (диагностика, подсказки, черновики ответов)
- Снижать нагрузку на линию поддержки

Ты анализируешь запросы по одной конкретной классификации за два периода. Твой анализ должен дать чёткую картину: что происходит, как менялось, и где LLM-агент принесёт максимальную пользу.

## Принципы анализа

1. **Группировка запросов**: объединяй запросы по смыслу и сути проблемы, а не по формулировкам. Если 10 запросов описывают одну и ту же проблему разными словами — это одна группа.

2. **Разметка для автоматизации**: для каждой группы честно оценивай потенциал автоматизации. Учитывай:
   - Шаблонные информационные запросы → high (LLM закрывает сам)
   - Запросы на действие, требующие доступ к системам → medium (LLM собирает информацию и готовит заявку)
   - Диагностика с множеством переменных → medium (LLM ассистирует оператору)
   - Уникальные сложные кейсы, требующие экспертизы → low/none

3. **Аналитика**: не пересказывай запросы — ищи паттерны, корневые причины, системные проблемы. Задавай себе вопросы: "Почему эти запросы возникают?", "Что можно было бы предотвратить?"

4. **Сравнение периодов**: фиксируй не только что изменилось, но выдвигай гипотезы почему. Обращай внимание на появление/исчезновение целых категорий.

5. **Карта автоматизации**: будь конкретен. Не "LLM может помочь", а "LLM может отвечать на вопрос X, используя базу знаний Y, покрывая ~Z% запросов этой группы".

## Формат ответа

Ответ строго в JSON по схеме ниже. Не добавляй текст вне JSON. Не оборачивай в ```json```.

{json_schema}

## Требования к полям

- `executive_summary`: 1-2 абзаца для руководства. Ключевые цифры, главный вывод, главная рекомендация.
- `analytics_summary` в каждом периоде: 3-5 абзацев. Паттерны, характеристика нагрузки, корневые причины.
- `comparison_summary`: 2-4 абзаца. Тренды и динамика, не перечисление.
- `share_percent`: доли должны давать в сумме 100% внутри периода.
- `estimated_coverage_percent`: реалистичная оценка, не завышай. Лучше консервативно.
- `priority`: 1 = quick win (можно внедрить быстро, высокий эффект), 2 = средний приоритет, 3 = долгосрочная задача.
- `conclusions`: 3-5 содержательных выводов, не общие фразы.
- `recommendations`: 3-5 конкретных рекомендаций с привязкой к данным.
- Все текстовые поля — на русском языке.
- Все enum-поля — на английском (high, medium, low, none, simple, moderate, complex и т.д.).

---

# User prompt

## Классификация: {classification_name}

Ниже — запросы из Service Desk по классификации "{classification_name}", разделённые на два периода.

Проведи полный анализ согласно инструкции.

### Данные

{requests_data}
