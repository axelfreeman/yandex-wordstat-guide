---
name: wordstat-collector
description: "Яндекс.Вордстат через API. Автоматический сбор поисковой семантики для AI-агента. 100 запросов/час."
version: 2.0.0
install: "npx hermes skill install axelfreeman/yandex-wordstat-guide"
requires:
  env: [WORDSTAT_API_KEY, WORDSTAT_FOLDER_ID]
  apis: [yandex-search-api]
---

# Wordstat Collector

## Что делает

Собирает поисковую статистику Яндекса через API и возвращает структурированные данные. Агент может использовать их для генерации SEO-страниц, рекламных кампаний и контент-планов.

## Команды для агента

```
«Собери семантику по теме [тема] через Wordstat»
«Покажи топ-20 запросов по [ключ]»
«Сгенерируй SEO-страницы на основе семантики из semantic_results.json»
```

## Переменные

```bash
WORDSTAT_API_KEY     # API-ключ Яндекс.Облака
WORDSTAT_FOLDER_ID   # ID каталога (20 символов)
```

## Скрипт

`scripts/collect.py` — принимает список seed-фраз, возвращает JSON с фразами и частотами.

```bash
python3 scripts/collect.py "фраза1" "фраза2"
```

## Лимиты

- 100 запросов в час
- 0.3 sec между запросами
- Не больше 90 запросов за сессию (запас 10%)

## Питфоллы

- Все числа приходят строками → `int(count)`
- folderId ровно 20 символов → `.strip()`
- Дата для dynamics — последний день месяца/недели
