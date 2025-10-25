import asyncio
import pandas as pd
from openai import AsyncOpenAI
from typing import AsyncGenerator, List

async def llm_client(prompt: str, api_url: str, api_key: str = "EMPTY"):
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=api_url
    )
    response = await client.chat.completions.create(
        model="your_model_name",  # Укажите имя модели, если нужно
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.7
    )
    return response.choices[0].message.content

async def batch_generator(df: pd.DataFrame, batch_size: int, queue: asyncio.Queue, num_workers: int):
    """Асинхронный генератор батчей — кладет батчи в очередь"""
    batches = (df.iloc[i:i + batch_size] for i in range(0, len(df), batch_size))
    for batch in batches:
        await queue.put(batch)
    # Отправляем сигнал о завершении (None)
    for _ in range(num_workers):
        await queue.put(None)  # Сигнал для остановки

async def process_batch_and_add_result(batch, llm_client_func, api_url: str):
    """Обработка одного батча"""
    results = []
    for idx, row in batch.iterrows():
        prompt = row.get("text", "")
        result = await llm_client_func(prompt, api_url)
        results.append(result)
    return results

async def worker(queue: asyncio.Queue, llm_client_func, api_url: str, results_queue: asyncio.Queue):
    """Рабочий процесс: берет батч из очереди, обрабатывает, кладет результат в другую очередь"""
    while True:
        batch = await queue.get()
        if batch is None:  # Сигнал остановки
            break
        results = await process_batch_and_add_result(batch, llm_client_func, api_url)
        await results_queue.put(results)
        queue.task_done()

async def process_dataframe_async_streaming(
    df: pd.DataFrame,
    llm_client_func,
    api_urls: List[str],
    batch_size: int = 10,
    max_batches_in_queue: int = 4
):
    """
    Обработка датафрейма с асинхронной генерацией батчей и буфером
    """
    # Очередь для батчей
    batch_queue = asyncio.Queue(maxsize=max_batches_in_queue)
    # Очередь для результатов
    results_queue = asyncio.Queue()

    # Запускаем генератор батчей
    batch_gen_task = asyncio.create_task(
        batch_generator(df, batch_size, batch_queue, len(api_urls))
    )

    # Запускаем рабочие задачи (по числу API)
    workers = [
        asyncio.create_task(worker(batch_queue, llm_client_func, api_url, results_queue))
        for api_url in api_urls
    ]

    all_results = []
    # Считываем результаты по мере готовности
    for _ in range(len(api_urls)):
        while len([t for t in workers if not t.done()]) > 0 or not results_queue.empty():
            try:
                result_batch = await asyncio.wait_for(results_queue.get(), timeout=1.0)
                all_results.extend(result_batch)
            except asyncio.TimeoutError:
                continue

    # Ждем завершения всех задач
    await batch_gen_task
    for w in workers:
        await w

    return all_results
