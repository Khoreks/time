import pandas as pd
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict

class MetaClassManager:
    def __init__(self):
        self.next_meta_id = 1
        self.meta_classes = {}  # meta_class_id -> MetaClass
        self.current_mapping = {}  # (group, service, comp, view) -> meta_class_id
        self.clf_to_meta = {}  # clf_id -> meta_class_id

    class MetaClass:
        __slots__ = ['meta_id', 'current_clf', 'history_clfs', 'attributes']
        def __init__(self, meta_id: int, clf_id: int, attributes: Tuple):
            self.meta_id = meta_id
            self.current_clf = clf_id
            self.history_clfs = [clf_id]
            self.attributes = attributes  # (group, service, comp, view)

    def initialize_from_catalog(self, df: pd.DataFrame) -> None:
        """Инициализация метаклассов из исходного каталога"""
        grouped = df.groupby(['group_title', 'service_title', 'comp_title', 'view_title'])
        
        for attributes, group in grouped:
            clf_ids = group['clf_id'].unique()
            if len(clf_ids) > 1:
                raise ValueError(f"Multiple clf_id found for {attributes}")
            
            clf_id = clf_ids[0]
            meta_id = self.next_meta_id
            self.next_meta_id += 1
            
            meta_class = self.MetaClass(meta_id, clf_id, attributes)
            
            self.meta_classes[meta_id] = meta_class
            self.current_mapping[attributes] = meta_id
            self.clf_to_meta[clf_id] = meta_id

    def update_from_new_catalog(self, new_df: pd.DataFrame) -> pd.DataFrame:
        """Обновление метаклассов на основе нового каталога"""
        new_grouped = new_df.groupby(['group_title', 'service_title', 'comp_title', 'view_title'])
        new_attributes_map = {attrs: group['clf_id'].iloc[0] for attrs, group in new_grouped}

        # Поиск изменений
        changes = []
        current_attrs = set(self.current_mapping.keys())
        new_attrs = set(new_attributes_map.keys())

        # Обработка удаленных и измененных классов
        for attrs in current_attrs - new_attrs:
            meta_id = self.current_mapping[attrs]
            self.meta_classes[meta_id].current_clf = None

        # Обработка новых и измененных классов
        for attrs in new_attrs:
            new_clf = new_attributes_map[attrs]
            
            if attrs in self.current_mapping:
                meta_id = self.current_mapping[attrs]
                meta_class = self.meta_classes[meta_id]
                
                if meta_class.current_clf != new_clf:
                    meta_class.history_clfs.append(new_clf)
                    meta_class.current_clf = new_clf
                    self.clf_to_meta[new_clf] = meta_id
                    changes.append(('replaced', meta_id, attrs))
            else:
                # Новый метакласс
                meta_id = self.next_meta_id
                self.next_meta_id += 1
                
                meta_class = self.MetaClass(meta_id, new_clf, attrs)
                self.meta_classes[meta_id] = meta_class
                self.current_mapping[attrs] = meta_id
                self.clf_to_meta[new_clf] = meta_id
                changes.append(('created', meta_id, attrs))

        return pd.DataFrame(changes, columns=['change_type', 'meta_id', 'attributes'])

    def get_meta_class_info(self) -> pd.DataFrame:
        """Получение информации о метаклассах в виде DataFrame"""
        rows = []
        for meta in self.meta_classes.values():
            rows.append({
                'meta_class_id': meta.meta_id,
                'current_class_id': meta.current_clf,
                'history_class_ids': meta.history_clfs,
                'group_title': meta.attributes[0],
                'service_title': meta.attributes[1],
                'comp_title': meta.attributes[2],
                'view_title': meta.attributes[3]
            })
        return pd.DataFrame(rows)

    def get_meta_class_by_clf(self, clf_id: int) -> Optional[int]:
        """Получение meta_class_id по clf_id"""
        return self.clf_to_meta.get(clf_id)

# Пример использования
if __name__ == "__main__":
    # Создание исходного каталога
    initial_data = {
        'group_title': ['G1', 'G1', 'G2'],
        'service_title': ['S1', 'S1', 'S2'],
        'comp_title': ['C1', 'C1', 'C2'],
        'view_title': ['V1', 'V1', 'V2'],
        'clf_id': [123, 123, 456]
    }
    initial_df = pd.DataFrame(initial_data)

    # Инициализация менеджера
    manager = MetaClassManager()
    manager.initialize_from_catalog(initial_df)

    # Создание нового каталога с изменениями
    new_data = {
        'group_title': ['G1', 'G2', 'G3'],
        'service_title': ['S1', 'S2', 'S3'],
        'comp_title': ['C1', 'C2', 'C3'],
        'view_title': ['V1', 'V2', 'V3'],
        'clf_id': [321, 456, 789]
    }
    new_df = pd.DataFrame(new_data)

    # Обновление метаклассов
    changes = manager.update_from_new_catalog(new_df)
    print("Changes detected:")
    print(changes)

    # Получение текущего состояния метаклассов
    meta_info = manager.get_meta_class_info()
    print("\nMeta classes information:")
    print(meta_info)




import pandas as pd
import uuid
from datetime import datetime

class MetaClassManager:
    def __init__(self, meta_df: pd.DataFrame | None = None):
        if meta_df is None:
            self.meta_df = pd.DataFrame(columns=[
                "meta_class_id", "class_key", "service_title",
                "comp_title", "view_title", "active", "last_update"
            ])
        else:
            self.meta_df = meta_df

    def _make_class_key(self, row):
        return f"{row['service_id']}|{row['comp_id']}|{row['view_id']}"

    def update_from_catalog(self, catalog: pd.DataFrame):
        catalog = catalog.copy()
        catalog["class_key"] = catalog.apply(self._make_class_key, axis=1)

        for _, row in catalog.iterrows():
            mask = (
                (self.meta_df["service_title"] == row["service_title"]) &
                (self.meta_df["comp_title"] == row["comp_title"]) &
                (self.meta_df["view_title"] == row["view_title"])
            )

            if mask.any():
                # обновляем существующий метакласс
                self.meta_df.loc[mask, ["class_key", "active", "last_update"]] = [
                    row["class_key"], row["available"], datetime.now()
                ]
            else:
                # создаём новый метакласс
                self.meta_df.loc[len(self.meta_df)] = [
                    str(uuid.uuid4()), row["class_key"],
                    row["service_title"], row["comp_title"], row["view_title"],
                    row["available"], datetime.now()
                ]

        # пометить неактивные
        current_keys = set(catalog["class_key"])
        inactive_mask = ~self.meta_df["class_key"].isin(current_keys)
        self.meta_df.loc[inactive_mask, ["active", "last_update"]] = [False, datetime.now()]

        return self.meta_df



from __future__ import annotations
import pandas as pd
import uuid
from typing import List


class MetaClassManager:
    """
    Шаг 1. Инициализация метаклассов по активным комбинациям каталога.

    Вход: DataFrame catalog с колонками:
      ['group_title','service_title','service_id','comp_title','comp_id',
       'view_title','view_id','type_title','creation_date','last_modified_date','available']

    Результат: self.meta_df с колонками:
      ['uuid', 'title', 'nested_classes', 'available']

    Определения:
      - class_key = f"{service_id}|{comp_id}|{view_id}"
      - title      = f"{service_title}|{comp_title}|{view_title}"
      - nested_classes: List[str] из class_key, сгруппированных по title
      - available: True для созданных на шаге 1 (инициализация только по активным)

    Деталь: UUID детерминирован по title через uuid5, чтобы переинициализация
            давала те же meta-id при неизменном названии.
    """

    META_COLUMNS = ["uuid", "title", "nested_classes", "available"]

    def __init__(self, meta_df: pd.DataFrame | None = None) -> None:
        if meta_df is None:
            self.meta_df = pd.DataFrame(columns=self.META_COLUMNS)
        else:
            # нормализуем порядок и наличие колонок
            for c in self.META_COLUMNS:
                if c not in meta_df.columns:
                    meta_df[c] = pd.NA
            self.meta_df = meta_df[self.META_COLUMNS].copy()

    @staticmethod
    def _class_key(row: pd.Series) -> str:
        return f"{row['service_id']}|{row['comp_id']}|{row['view_id']}"

    @staticmethod
    def _title(row: pd.Series) -> str:
        return f"{row['service_title']}|{row['comp_title']}|{row['view_title']}"

    @staticmethod
    def _uuid_for_title(title: str) -> str:
        # детерминированный UUID по названию метакласса
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"meta:{title}"))

    def init_active(self, catalog: pd.DataFrame) -> pd.DataFrame:
        """Создать метаклассы для всех активных комбинаций каталога.

        Возвращает обновлённый self.meta_df.
        """
        required_cols = {
            'service_title', 'comp_title', 'view_title',
            'service_id', 'comp_id', 'view_id', 'available'
        }
        missing = required_cols - set(catalog.columns)
        if missing:
            raise ValueError(f"Отсутствуют колонки в catalog: {sorted(missing)}")

        # фильтруем только активные строки
        active = catalog[catalog['available'] == True].copy()  # noqa: E712
        if active.empty:
            # очистка и возврат пустой таблицы в корректном формате
            self.meta_df = pd.DataFrame(columns=self.META_COLUMNS)
            return self.meta_df

        # подготовим вспомогательные поля
        active['class_key'] = active.apply(self._class_key, axis=1)
        active['title'] = active.apply(self._title, axis=1)

        # группируем по названию метакласса
        grouped = (
            active.groupby('title')['class_key']
            .apply(list)
            .reset_index(name='nested_classes')
        )

        # формируем мета-таблицу
        meta = pd.DataFrame({
            'uuid': grouped['title'].apply(self._uuid_for_title),
            'title': grouped['title'],
            'nested_classes': grouped['nested_classes'],
            'available': True,
        })

        # сохраняем как текущее состояние
        self.meta_df = meta[self.META_COLUMNS].copy()
        return self.meta_df


# --------------------------
# Пример использования (док-тест)
# --------------------------
if __name__ == "__main__":
    data = [
        {
            'group_title': 'Comm', 'service_title': 'Skype', 'service_id': 1,
            'comp_title': 'Base', 'comp_id': 10, 'view_title': 'Default', 'view_id': 100,
            'type_title': 'app', 'creation_date': '2025-01-01', 'last_modified_date': '2025-01-02',
            'available': True,
        },
        {
            'group_title': 'Comm', 'service_title': 'Skype', 'service_id': 13,
            'comp_title': 'Base', 'comp_id': 10, 'view_title': 'Default', 'view_id': 100,
            'type_title': 'app', 'creation_date': '2025-01-10', 'last_modified_date': '2025-01-11',
            'available': True,
        },
        {
            'group_title': 'Comm', 'service_title': 'Skype для конференций', 'service_id': 14,
            'comp_title': 'Base', 'comp_id': 10, 'view_title': 'Default', 'view_id': 100,
            'type_title': 'app', 'creation_date': '2025-01-20', 'last_modified_date': '2025-01-21',
            'available': False,
        },
    ]
    catalog_df = pd.DataFrame(data)

    mgr = MetaClassManager()
    meta_df = mgr.init_active(catalog_df)
    print(meta_df)




from __future__ import annotations
import pandas as pd
import uuid
from typing import List


class MetaClassManager:
    """
    Шаги реализации:
    1. Инициализация метаклассов по активным комбинациям каталога.
    2. Обработка неактивных комбинаций: если неактивная комбинация отсутствует
       в nested_classes, пытаемся найти метакласс по title.
    """

    META_COLUMNS = ["uuid", "title", "nested_classes", "available"]

    def __init__(self, meta_df: pd.DataFrame | None = None) -> None:
        if meta_df is None:
            self.meta_df = pd.DataFrame(columns=self.META_COLUMNS)
        else:
            for c in self.META_COLUMNS:
                if c not in meta_df.columns:
                    meta_df[c] = pd.NA
            self.meta_df = meta_df[self.META_COLUMNS].copy()

    @staticmethod
    def _class_key(row: pd.Series) -> str:
        return f"{row['service_id']}|{row['comp_id']}|{row['view_id']}"

    @staticmethod
    def _title(row: pd.Series) -> str:
        return f"{row['service_title']}|{row['comp_title']}|{row['view_title']}"

    @staticmethod
    def _uuid_for_title(title: str) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"meta:{title}"))

    def init_active(self, catalog: pd.DataFrame) -> pd.DataFrame:
        required_cols = {
            'service_title', 'comp_title', 'view_title',
            'service_id', 'comp_id', 'view_id', 'available'
        }
        missing = required_cols - set(catalog.columns)
        if missing:
            raise ValueError(f"Отсутствуют колонки в catalog: {sorted(missing)}")

        active = catalog[catalog['available'] == True].copy()  # noqa: E712
        if active.empty:
            self.meta_df = pd.DataFrame(columns=self.META_COLUMNS)
            return self.meta_df

        active['class_key'] = active.apply(self._class_key, axis=1)
        active['title'] = active.apply(self._title, axis=1)

        grouped = (
            active.groupby('title')['class_key']
            .apply(list)
            .reset_index(name='nested_classes')
        )

        meta = pd.DataFrame({
            'uuid': grouped['title'].apply(self._uuid_for_title),
            'title': grouped['title'],
            'nested_classes': grouped['nested_classes'],
            'available': True,
        })

        self.meta_df = meta[self.META_COLUMNS].copy()
        return self.meta_df

    def handle_inactive(self, catalog: pd.DataFrame) -> pd.DataFrame:
        """
        Обработка неактивных комбинаций.
        Если комбинация отсутствует в nested_classes, но title совпадает с
        существующим метаклассом, то добавляем комбинацию туда.
        """
        inactive = catalog[catalog['available'] == False].copy()  # noqa: E712
        if inactive.empty:
            return self.meta_df

        inactive['class_key'] = inactive.apply(self._class_key, axis=1)
        inactive['title'] = inactive.apply(self._title, axis=1)

        for _, row in inactive.iterrows():
            title = row['title']
            class_key = row['class_key']

            mask = self.meta_df['title'] == title
            if mask.any():
                # добавляем class_key, если его там ещё нет
                nested = self.meta_df.loc[mask, 'nested_classes'].iloc[0]
                if class_key not in nested:
                    new_nested = nested + [class_key]
                    self.meta_df.loc[mask, 'nested_classes'] = [new_nested]
            else:
                # если такого title нет вообще — создаём новый метакласс (неактивный)
                self.meta_df.loc[len(self.meta_df)] = [
                    self._uuid_for_title(title),
                    title,
                    [class_key],
                    False
                ]

        return self.meta_df


# --------------------------
# Пример использования (док-тест)
# --------------------------
if __name__ == "__main__":
    data = [
        {
            'group_title': 'Comm', 'service_title': 'Skype', 'service_id': 1,
            'comp_title': 'Base', 'comp_id': 10, 'view_title': 'Default', 'view_id': 100,
            'type_title': 'app', 'creation_date': '2025-01-01', 'last_modified_date': '2025-01-02',
            'available': True,
        },
        {
            'group_title': 'Comm', 'service_title': 'Skype', 'service_id': 13,
            'comp_title': 'Base', 'comp_id': 10, 'view_title': 'Default', 'view_id': 100,
            'type_title': 'app', 'creation_date': '2025-01-10', 'last_modified_date': '2025-01-11',
            'available': False,
        },
        {
            'group_title': 'Comm', 'service_title': 'Skype для конференций', 'service_id': 14,
            'comp_title': 'Base', 'comp_id': 10, 'view_title': 'Default', 'view_id': 100,
            'type_title': 'app', 'creation_date': '2025-01-20', 'last_modified_date': '2025-01-21',
            'available': False,
        },
    ]
    catalog_df = pd.DataFrame(data)

    mgr = MetaClassManager()
    mgr.init_active(catalog_df)
    meta_df = mgr.handle_inactive(catalog_df)
    print(meta_df)


for _, row in inactive.iterrows():
    title = row['title']
    class_key = row['class_key']

    mask = self.meta_df['title'] == title
    if mask.any():
        idx = self.meta_df.index[mask][0]  # индекс совпадения
        nested = self.meta_df.at[idx, 'nested_classes']
        if class_key not in nested:
            new_nested = nested + [class_key]
            self.meta_df.at[idx, 'nested_classes'] = new_nested
    else:
        # если такого title нет вообще — создаём новый метакласс (неактивный)
        self.meta_df.loc[len(self.meta_df)] = [
            self._uuid_for_title(title),
            title,
            [class_key],
            False
        ]
