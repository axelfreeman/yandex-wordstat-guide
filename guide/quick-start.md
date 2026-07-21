# Быстрый старт

## 1. Клонировать репозиторий

```bash
git clone https://github.com/axelfreeman/yandex-wordstat-guide.git
cd yandex-wordstat-guide
```

## 2. Установить ключи

```bash
export WORDSTAT_API_KEY="AQVN..."      # из Яндекс.Облака
export WORDSTAT_FOLDER_ID="b1g..."     # ID каталога
```

## 3. Запустить сбор

```bash
python3 scripts/wordstat_collector.py "ремонт квартир" "дизайн интерьера"
```

Результат: `semantic_results.json` со списком запросов.

## 4. Скормить нейросети

```bash
# Отправить результаты в DeepSeek
python3 -c "
import json
data = json.load(open('semantic_results.json'))
prompt = f'Вот семантика по теме. Сгенерируй 5 SEO-страниц: {data}'
# → отправить prompt в DeepSeek API
"
```
