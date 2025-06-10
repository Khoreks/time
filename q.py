from collections import defaultdict

def aggregate_scores(titles, scores):
    # Словарь для хранения суммы и количества повторений
    score_dict = defaultdict(lambda: {'sum': 0, 'count': 0})
    
    # Собираем суммы и количество повторений
    for title, score in zip(titles, scores):
        score_dict[title]['sum'] += score
        score_dict[title]['count'] += 1
    
    # Вычисляем среднее для каждого title
    aggregated = {
        title: score_data['sum'] / score_data['count']
        for title, score_data in score_dict.items()
    }
    
    return aggregated
