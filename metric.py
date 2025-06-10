import numpy as np
from scipy import stats
from sklearn.preprocessing import MinMaxScaler

class AdvancedMetricMerger:
    def __init__(self, metric1_direction='lower_worse', metric2_direction='lower_better',
                 border_effect_strength=0.5, outlier_threshold=3.0):
        """
        :param metric1_direction: направление первой метрики ('lower_worse' или 'lower_better')
        :param metric2_direction: направление второй метрики
        :param border_effect_strength: сила влияния пограничных значений (0-1)
        :param outlier_threshold: порог для определения выбросов (в сигмах)
        """
        self.metric1_dir = metric1_direction
        self.metric2_dir = metric2_direction
        self.border_strength = border_effect_strength
        self.outlier_thresh = outlier_threshold
        self.scaler = MinMaxScaler()
        
    def _prepare_metrics(self, metric1, metric2):
        """Нормализация и приведение метрик к единому направлению"""
        # Приводим обе метрики к направлению "чем меньше, тем лучше"
        if self.metric1_dir == 'lower_worse':
            metric1_norm = 1 - np.array(metric1)
        else:
            metric1_norm = np.array(metric1)
            
        if self.metric2_dir == 'lower_worse':
            metric2_norm = 1 - np.array(metric2)
        else:
            metric2_norm = np.array(metric2)
            
        return metric1_norm, metric2_norm
    
    def _calculate_border_effects(self, values):
        """Вычисление пограничных эффектов с использованием сигмоидной функции"""
        # Используем сигмоиду для определения "близости к границе"
        border_proximity = 1 / (1 + np.exp(-10*(values - 0.5)))
        border_effect = border_proximity * self.border_strength + (1 - self.border_strength)
        return border_effect
    
    def _detect_outliers(self, values):
        """Обнаружение выбросов с использованием z-оценок"""
        z_scores = np.abs(stats.zscore(values))
        return z_scores > self.outlier_thresh
    
    def _calculate_adaptive_weights(self, metric1, metric2):
        """Адаптивные веса на основе статистических свойств метрик"""
        # Веса на основе дисперсии (чем больше дисперсия, тем меньше вес)
        var1, var2 = np.var(metric1), np.var(metric2)
        weight1 = 1 / (1 + var1)
        weight2 = 1 / (1 + var2)
        
        # Нормализация весов
        total = weight1 + weight2
        return weight1/total, weight2/total
    
    def combine_metrics(self, metric1, metric2):
        """Комбинирование метрик с учетом пограничных эффектов и статистики"""
        # Подготовка метрик
        m1, m2 = self._prepare_metrics(metric1, metric2)
        
        # Вычисление пограничных эффектов
        m1_border = self._calculate_border_effects(m1)
        m2_border = self._calculate_border_effects(m2)
        
        # Обнаружение выбросов
        m1_outliers = self._detect_outliers(m1)
        m2_outliers = self._detect_outliers(m2)
        
        # Адаптивные веса
        w1, w2 = self._calculate_adaptive_weights(m1, m2)
        
        # Комбинирование с учетом всех факторов
        combined = (
            w1 * m1 * m1_border * np.where(m1_outliers, 1.5, 1.0) + 
            w2 * m2 * m2_border * np.where(m2_outliers, 1.5, 1.0)
        )
        
        # Нормализация к [0, 1]
        combined_normalized = self.scaler.fit_transform(combined.reshape(-1, 1)).flatten()
        
        return combined_normalized

# Пример использования
if __name__ == "__main__":
    # Генерация тестовых данных
    np.random.seed(42)
    metric1 = np.random.beta(2, 5, 100)  # метрика где "чем меньше, тем хуже"
    metric2 = np.random.beta(5, 2, 100)  # метрика где "чем меньше, тем лучше"
    
    # Создание и применение комбинатора
    merger = AdvancedMetricMerger(border_effect_strength=0.7, outlier_threshold=2.5)
    combined_metric = merger.combine_metrics(metric1, metric2)
    
    # Визуализация
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(12, 6))
    plt.scatter(metric1, metric2, c=combined_metric, cmap='viridis')
    plt.colorbar(label='Combined Metric')
    plt.xlabel('Metric 1 (lower=worse)')
    plt.ylabel('Metric 2 (lower=better)')
    plt.title('Advanced Metric Combination')
    plt.show()
