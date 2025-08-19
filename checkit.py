import json
from pathlib import Path


def process_dictionary(
        file_path: str,
        sort_by: str = "key",  # "key" или "value"
        remove_empty_duplicates: bool = True,
        modify_original: bool = True,
) -> tuple[list, dict]:
    """
    Обрабатывает JSON-словарь в формате [{key: value}, ...]:
    - Сортирует записи: сначала с описаниями, потом без
    - Удаляет дубликаты (с опциями для пустых значений)
    - Сохраняет в формате: один объект на строку
    - Возвращает обработанные данные и статистику
    """
    # Загрузка данных
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("JSON должен быть массивом объектов [{key: value}, ...].")

    # Инициализация статистики
    stats = {
        "total_entries": len(data),
        "duplicates_found": 0,
        "duplicates_removed": 0,
        "entries_with_value": 0,
        "entries_without_value": 0,
    }

    # Обработка дубликатов и разделение записей
    unique_entries = {}
    duplicates_report = {}
    entries_with_value = []
    entries_without_value = []

    for entry in data:
        if not isinstance(entry, dict) or len(entry) != 1:
            raise ValueError("Каждый объект должен содержать одну пару key:value.")

        key, value = next(iter(entry.items()))

        if key in unique_entries:
            stats["duplicates_found"] += 1
            duplicates_report.setdefault(key, []).append(value)
            if remove_empty_duplicates and not value:
                stats["duplicates_removed"] += 1
                continue
            # Оставляем первое непустое значение
            if unique_entries[key]:
                continue
        unique_entries[key] = value

        # Разделяем записи по наличию значения
        if value:
            entries_with_value.append({key: value})
        else:
            entries_without_value.append({key: value})

    # Сортировка
    def sort_key(item):
        key, value = next(iter(item.items()))
        return key.lower() if sort_by == "key" else str(value).lower()

    entries_with_value.sort(key=sort_key)
    entries_without_value.sort(key=sort_key)

    # Итоговый список (сначала с значениями, потом без)
    result = entries_with_value + entries_without_value
    stats["entries_with_value"] = len(entries_with_value)
    stats["entries_without_value"] = len(entries_without_value)

    # Сохранение в формате с переносами строк
    if modify_original:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("[\n")
            for i, entry in enumerate(result):
                json.dump(entry, f, ensure_ascii=False)
                if i < len(result) - 1:
                    f.write(",\n")
                else:
                    f.write("\n")
            f.write("]")

    # Отчет о дубликатах
    if duplicates_report:
        print("⚠ Найдены дубликаты ключей:")
        for key, values in duplicates_report.items():
            print(f"   - Ключ: '{key}'")
            for i, val in enumerate(values, 1):
                print(f"     {i}. Значение: {repr(val)}")

    return result, stats


if __name__ == "__main__":
    # Конфигурация
    CONFIG = {
        "file_path": "dictionary.json",
        "sort_by": "key",  # "key" или "value"
        "remove_empty_duplicates": True,
        "modify_original": True,
    }

    # Запуск обработки
    try:
        processed_data, stats = process_dictionary(**CONFIG)

        # Вывод статистики
        print("\n📊 Статистика:")
        print(f"  Всего записей: {stats['total_entries']}")
        print(f"  Дубликатов найдено: {stats['duplicates_found']}")
        print(f"  Дубликатов удалено: {stats['duplicates_removed']}")
        print(f"  Записей с описаниями: {stats['entries_with_value']}")
        print(f"  Записей без описаний: {stats['entries_without_value']}")
        print(f"  Итого сохранено: {len(processed_data)}")

        print("\n✅ Файл успешно обработан!" if CONFIG["modify_original"] else "✅ Данные обработаны (файл не изменён)")

    except Exception as e:
        print(f"❌ Ошибка: {e}")