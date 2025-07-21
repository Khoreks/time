from datetime import datetime, timezone, timedelta

# Исходное время без часового пояса (наивное)
dt_naive = datetime(2023, 12, 31, 23, 59, 59, 999999)
print("Наивное время:", dt_naive)  # 2023-12-31 23:59:59.999999

# Создаем временную зону UTC+7
tz_utc_plus_7 = timezone(timedelta(hours=7))

# Вариант 1: Просто добавить пояс (если время УЖЕ подразумевалось как UTC+7)
dt_with_tz = dt_naive.replace(tzinfo=tz_utc_plus_7)
print("Время с UTC+7:", dt_with_tz)  # 2023-12-31 23:59:59.999999+07:00

# Вариант 2: Если время было в UTC, конвертируем в UTC+7
dt_utc = dt_naive.replace(tzinfo=timezone.utc)  # Сначала считаем его UTC
dt_converted = dt_utc.astimezone(tz_utc_plus_7)  # Переводим в UTC+7
print("Конвертированное время:", dt_converted)  # 2024-01-01 06:59:59.999999+07:00
