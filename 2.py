import pandas as pd
import numpy as np
from sklearn.utils import resample


def balance_dataset_with_normal_dist(
        df: pd.DataFrame,
        target_column: str = 'label',
        len_column: str = 'len',
        n_samples: int = 1000,
        sigma_coeff: float = 1.0,
        random_state: int = 42,
        drop_small_classes: bool = True,
) -> pd.DataFrame:
    """
    Балансирует датасет, выбирая `n_samples` из классов с избытком данных,
    используя нормальное распределение по длине (len), чтобы отсеивать выбросы.

    Параметры:
    ----------
    df : pd.DataFrame
        Входной датафрейм.
    target_column : str, default='label'
        Название колонки с метками классов.
    len_column : str, default='len'
        Название колонки с длинами семплов.
    n_samples : int, default=1000
        Максимальное количество семплов на класс.
    sigma_coeff : float, default=1.0
        Коэффициент стандартного отклонения для отсечения выбросов.
        Чем больше, тем шире диапазон допустимых длин.
    random_state : int, default=42
        Seed для воспроизводимости.
    drop_small_classes : bool, default=True
        Удалять ли классы с числом семплов < 2.

    Возвращает:
    -----------
    pd.DataFrame
        Сбалансированный датафрейм.
    """
    np.random.seed(random_state)

    # Удаляем классы с < 2 семплами (если нужно)
    if drop_small_classes:
        valid_classes = df[target_column].value_counts()[df[target_column].value_counts() >= 2].index
        df = df[df[target_column].isin(valid_classes)].copy()

    # Разделяем датафрейм по классам
    classes = df[target_column].unique()
    balanced_dfs = []

    for cls in classes:
        class_df = df[df[target_column] == cls].copy()
        n_class_samples = len(class_df)

        # Если в классе <= n_samples, берем все
        if n_class_samples <= n_samples:
            balanced_dfs.append(class_df)
            continue

        # Вычисляем среднюю длину и стандартное отклонение
        mean_len = class_df[len_column].mean()
        std_len = class_df[len_column].std()

        # Генерируем веса на основе нормального распределения
        weights = np.exp(-0.5 * ((class_df[len_column] - mean_len) / (sigma_coeff * std_len)) ** 2)
        weights /= weights.sum()  # Нормализуем

        # Выбираем n_samples семплов с учетом весов
        selected_indices = np.random.choice(
            class_df.index,
            size=n_samples,
            replace=False,
            p=weights,
        )
        selected_df = class_df.loc[selected_indices]
        balanced_dfs.append(selected_df)

    # Объединяем и перемешиваем
    balanced_df = pd.concat(balanced_dfs, ignore_index=True)
    return balanced_df.sample(frac=1, random_state=random_state)