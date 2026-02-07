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


"""
Сборка итогового md-отчёта из JSON-файлов ClassificationReport.

Использование:
    python build_report.py reports/*.json -o report.md
    python build_report.py report1.json report2.json report3.json -o report.md

Каждый JSON-файл — результат анализа одной классификации по схеме ClassificationReport.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime


# ── Маппинг enum-значений на русский ────────────────────────────────────

AUTOMATION_POTENTIAL_RU = {
    "high": "🟢 Высокий",
    "medium": "🟡 Средний",
    "low": "🟠 Низкий",
    "none": "🔴 Нет",
}

COMPLEXITY_RU = {
    "simple": "Простой",
    "moderate": "Средний",
    "complex": "Сложный",
}

INTERACTION_TYPE_RU = {
    "informational": "Информационный",
    "action_request": "Запрос на действие",
    "diagnostics": "Диагностика",
    "consultation": "Консультация",
}

REPEATABILITY_RU = {
    "template": "Шаблонный",
    "frequent": "Частый",
    "rare": "Редкий",
}

LLM_ROLE_RU = {
    "closes": "Закрывает полностью",
    "assists": "Ассистирует оператору",
    "not_applicable": "Не применим",
}

PRIORITY_RU = {
    1: "🚀 Quick win",
    2: "⏳ Средний приоритет",
    3: "🔮 Долгосрочный",
}


# ── Вспомогательные функции ──────────────────────────────────────────────

def _ru(mapping: dict, key: str) -> str:
    return mapping.get(key, key)


def _bullet_list(items: list[str], indent: int = 0) -> str:
    prefix = "  " * indent
    return "\n".join(f"{prefix}- {item}" for item in items) if items else f"{prefix}- —"


def _numbered_list(items: list[str]) -> str:
    return "\n".join(f"{i}. {item}" for i, item in enumerate(items, 1)) if items else "1. —"


# ── Рендеринг блоков ─────────────────────────────────────────────────────

def render_period(period: dict) -> str:
    lines = []
    label = period["period_label"]
    total = period["total_requests"]

    lines.append(f"## Период: {label}")
    lines.append(f"")
    lines.append(f"**Всего запросов:** {total}")
    lines.append("")

    # Топ проблем
    lines.append("### Ключевые проблемы")
    lines.append("")
    lines.append(_bullet_list(period.get("top_issues", [])))
    lines.append("")

    # Системные проблемы
    if period.get("systemic_issues"):
        lines.append("### Системные проблемы")
        lines.append("")
        lines.append(_bullet_list(period["systemic_issues"]))
        lines.append("")

    # Аномалии
    if period.get("anomalies"):
        lines.append("### Аномалии")
        lines.append("")
        lines.append(_bullet_list(period["anomalies"]))
        lines.append("")

    # Аналитика
    lines.append("### Аналитика")
    lines.append("")
    lines.append(period.get("analytics_summary", "—"))
    lines.append("")

    # Таблица групп
    lines.append("### Группировка запросов")
    lines.append("")
    lines.append("| Группа | Кол-во | Доля | Повтор. | Сложность | Тип | Автоматизация |")
    lines.append("|--------|--------|------|---------|-----------|-----|---------------|")

    for g in period.get("groups", []):
        lines.append(
            f"| {g['group_name']} "
            f"| {g['request_count']} "
            f"| {g['share_percent']:.0f}% "
            f"| {_ru(REPEATABILITY_RU, g['repeatability'])} "
            f"| {_ru(COMPLEXITY_RU, g['complexity'])} "
            f"| {_ru(INTERACTION_TYPE_RU, g['interaction_type'])} "
            f"| {_ru(AUTOMATION_POTENTIAL_RU, g['automation_potential'])} |"
        )
    lines.append("")

    # Детали по каждой группе
    lines.append("<details>")
    lines.append("<summary><b>Детали по группам</b></summary>")
    lines.append("")

    for g in period.get("groups", []):
        lines.append(f"#### {g['group_name']}")
        lines.append("")
        lines.append(f"{g['description']}")
        lines.append("")
        lines.append(f"**Примеры запросов:**")
        lines.append("")
        lines.append(_bullet_list(g.get("example_requests", [])))
        lines.append("")
        lines.append(
            f"**Автоматизация ({_ru(AUTOMATION_POTENTIAL_RU, g['automation_potential'])}):** "
            f"{g.get('automation_comment', '—')}"
        )
        lines.append("")

    lines.append("</details>")
    lines.append("")

    return "\n".join(lines)


def render_comparison(comp: dict) -> str:
    lines = []
    lines.append("## Сравнение периодов")
    lines.append("")

    sections = [
        ("Появилось во втором периоде", "new_appeared"),
        ("Исчезло во втором периоде", "disappeared"),
        ("Рост", "growing"),
        ("Снижение", "declining"),
        ("Стабильные категории", "stable"),
    ]

    for title, key in sections:
        items = comp.get(key, [])
        if items:
            lines.append(f"**{title}:**")
            lines.append("")
            lines.append(_bullet_list(items))
            lines.append("")

    if comp.get("change_hypotheses"):
        lines.append("### Гипотезы изменений")
        lines.append("")
        lines.append(_numbered_list(comp["change_hypotheses"]))
        lines.append("")

    lines.append("### Анализ")
    lines.append("")
    lines.append(comp.get("comparison_summary", "—"))
    lines.append("")

    return "\n".join(lines)


def render_automation_map(amap: dict) -> str:
    lines = []
    lines.append("## Карта автоматизации")
    lines.append("")
    lines.append(
        f"**Общий потенциал покрытия LLM-агентом:** "
        f"{amap.get('total_automatable_percent', 0):.0f}%"
    )
    lines.append("")

    # Таблица
    lines.append("| Группа | Роль LLM | Покрытие | Приоритет |")
    lines.append("|--------|----------|----------|-----------|")

    for item in amap.get("items", []):
        lines.append(
            f"| {item['group_name']} "
            f"| {_ru(LLM_ROLE_RU, item['llm_role'])} "
            f"| {item['estimated_coverage_percent']:.0f}% "
            f"| {_ru(PRIORITY_RU, item.get('priority', 3))} |"
        )
    lines.append("")

    # Детали возможностей
    lines.append("<details>")
    lines.append("<summary><b>Возможности LLM по группам</b></summary>")
    lines.append("")

    for item in amap.get("items", []):
        if item.get("llm_capabilities"):
            lines.append(f"**{item['group_name']}:**")
            lines.append("")
            lines.append(_bullet_list(item["llm_capabilities"]))
            lines.append("")

    lines.append("</details>")
    lines.append("")

    # Quick wins и долгосрочные
    if amap.get("quick_wins"):
        lines.append("### 🚀 Quick wins (первая очередь)")
        lines.append("")
        lines.append(_numbered_list(amap["quick_wins"]))
        lines.append("")

    if amap.get("long_term"):
        lines.append("### 🔮 Долгосрочные задачи")
        lines.append("")
        lines.append(_numbered_list(amap["long_term"]))
        lines.append("")

    return "\n".join(lines)


def render_report(data: dict) -> str:
    """Рендерит один ClassificationReport в markdown."""
    lines = []

    name = data.get("classification_name", "Без названия")
    lines.append(f"# {name}")
    lines.append("")

    # Executive summary
    lines.append("> **Сводка**")
    lines.append(">")
    for paragraph in data.get("executive_summary", "—").split("\n"):
        lines.append(f"> {paragraph}")
    lines.append("")

    lines.append("---")
    lines.append("")

    # Периоды
    lines.append(render_period(data["period_1"]))
    lines.append("---")
    lines.append("")
    lines.append(render_period(data["period_2"]))
    lines.append("---")
    lines.append("")

    # Сравнение
    lines.append(render_comparison(data["comparison"]))
    lines.append("---")
    lines.append("")

    # Карта автоматизации
    lines.append(render_automation_map(data["automation_map"]))
    lines.append("---")
    lines.append("")

    # Выводы
    lines.append("## Выводы")
    lines.append("")
    lines.append(_numbered_list(data.get("conclusions", [])))
    lines.append("")

    # Рекомендации
    lines.append("## Рекомендации")
    lines.append("")
    lines.append(_numbered_list(data.get("recommendations", [])))
    lines.append("")

    return "\n".join(lines)


# ── Сводная таблица по всем классификациям ───────────────────────────────

def render_summary_table(reports: list[dict]) -> str:
    """Сводная таблица по всем классификациям — общий dashboard."""
    lines = []
    lines.append("# Сводная таблица по всем классификациям")
    lines.append("")
    lines.append(
        "| Классификация | Период 1 | Период 2 | Δ | "
        "Потенциал LLM | Quick wins |"
    )
    lines.append(
        "|---------------|----------|----------|---|"
        "---------------|-----------|"
    )

    for r in reports:
        name = r.get("classification_name", "—")
        p1 = r.get("period_1", {}).get("total_requests", 0)
        p2 = r.get("period_2", {}).get("total_requests", 0)

        if p1 > 0:
            delta = f"{((p2 - p1) / p1) * 100:+.0f}%"
        else:
            delta = "—"

        auto_pct = r.get("automation_map", {}).get("total_automatable_percent", 0)
        qw = ", ".join(r.get("automation_map", {}).get("quick_wins", [])[:2])
        if not qw:
            qw = "—"

        lines.append(
            f"| {name} | {p1} | {p2} | {delta} | {auto_pct:.0f}% | {qw} |"
        )

    lines.append("")
    return "\n".join(lines)


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Собрать md-отчёт из JSON-файлов ClassificationReport"
    )
    parser.add_argument(
        "files", nargs="+", type=Path,
        help="JSON-файлы с результатами анализа"
    )
    parser.add_argument(
        "-o", "--output", type=Path, default=Path("report.md"),
        help="Путь к итоговому md-файлу (default: report.md)"
    )
    parser.add_argument(
        "--no-summary", action="store_true",
        help="Не добавлять сводную таблицу"
    )
    args = parser.parse_args()

    reports = []
    for f in args.files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            reports.append(data)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"⚠️  Пропущен {f}: {e}", file=sys.stderr)

    if not reports:
        print("❌ Нет валидных JSON-файлов", file=sys.stderr)
        sys.exit(1)

    parts = []

    # Заголовок
    today = datetime.now().strftime("%d.%m.%Y")
    parts.append(f"# Аналитический отчёт Service Desk")
    parts.append(f"")
    parts.append(f"*Дата формирования: {today}*")
    parts.append(f"*Классификаций: {len(reports)}*")
    parts.append("")
    parts.append("---")
    parts.append("")

    # Сводная таблица
    if not args.no_summary and len(reports) > 1:
        parts.append(render_summary_table(reports))
        parts.append("---")
        parts.append("")

    # Отчёты по каждой классификации
    for r in reports:
        parts.append(render_report(r))
        parts.append("")
        parts.append("---")
        parts.append("")

    output_text = "\n".join(parts)
    args.output.write_text(output_text, encoding="utf-8")

    print(f"✅ Отчёт сохранён: {args.output}")
    print(f"   Классификаций: {len(reports)}")
    print(f"   Размер: {len(output_text):,} символов")


if __name__ == "__main__":
    main()
