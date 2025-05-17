import pandas as pd


def get_balanced_sample(df, limits, priority_system='system_1'):
    """
    Генерирует сбалансированную выборку с учетом приоритетов

    Параметры:
    df - исходный DataFrame
    limits - словарь с ограничениями {'clf_1': 5000, 'clf_2': 1000, 'clf_3': 100}
    priority_system - система с высшим приоритетом

    Возвращает:
    DataFrame сбалансированной выборки
    """
    # Создаем копию, чтобы не менять исходный df
    result_sample = pd.DataFrame(columns=df.columns)
    temp_df = df.copy()

    # Сортируем весь датафрейм по приоритетам
    temp_df['priority'] = temp_df['system'].apply(lambda x: 0 if x == priority_system else 1)
    temp_df = temp_df.sort_values(['priority', 'creation_date'], ascending=[True, False])

    # Обрабатываем каждый уровень классификации от верхнего к нижнему
    for level in ['clf_1', 'clf_2', 'clf_3']:
        if level not in limits:
            continue

        # Для каждого уникального значения в уровне классификации
        for clf_value in temp_df[level].unique():
            # Выбираем записи с текущим значением классификации
            mask = temp_df[level] == clf_value

            # Если это самый верхний уровень, берем из всего датафрейма
            if level == 'clf_1':
                current_group = temp_df[mask]
            else:
                # Для вложенных уровней берем только из уже отобранных записей
                parent_level = f'clf_{int(level.split("_")[1]) - 1}'
                parent_values = result_sample[parent_level].unique()
                current_group = temp_df[mask & temp_df[parent_level].isin(parent_values)]

            # Ограничиваем количество записей
            limited_group = current_group.head(limits[level])

            # Добавляем в результат
            result_sample = pd.concat([result_sample, limited_group])

            # Удаляем уже отобранные записи из временного датафрейма
            temp_df = temp_df.drop(limited_group.index)

    # Удаляем дубликаты (если запись попала в несколько групп)
    result_sample = result_sample.drop_duplicates()

    return result_sample.reset_index(drop=True)


# Пример использования
# Создаем тестовый DataFrame (в вашем случае используйте свой)
data = {
    'system': ['system_1', 'system_2', 'system_1', 'system_3'] * 1000,
    'content': ['text'] * 4000,
    'clf_1': ['IT', 'HR', 'IT', 'Finance'] * 1000,
    'clf_2': ['PC', 'Hiring', 'Network', 'Accounting'] * 1000,
    'clf_3': ['Recovery', 'Application', 'Setup', 'Payment'] * 1000,
    'creation_date': pd.date_range(end='2023-01-01', periods=4000)
}

df = pd.DataFrame(data)

# Задаем ограничения
limits = {
    'clf_1': 5000,
    'clf_2': 1000,
    'clf_3': 100
}

# Получаем сбалансированную выборку
balanced_sample = get_balanced_sample(df, limits)

# Проверяем количество записей для каждого уровня
print("Количество записей по clf_1:")
print(balanced_sample['clf_1'].value_counts())
print("\nКоличество записей по clf_2:")
print(balanced_sample['clf_2'].value_counts())
print("\nКоличество записей по clf_3:")
print(balanced_sample['clf_3'].value_counts())