# 📊 Яндекс.Wordstat API — навык для AI-агентов

**Подключи Вордстат к своему AI-агенту и собирай поисковую семантику автоматом. Без интерфейса, без копипаста, без Excel.**

[![Hermes](https://img.shields.io/badge/Hermes_Agent-Skill-7C3AED?logo=robot&style=flat-square)](skill/SKILL.md)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&style=flat-square)]()
[![API](https://img.shields.io/badge/API-Яндекс.Поиск_v2-red?style=flat-square)](https://yandex.cloud/ru/docs/search-api/)
[![Stars](https://img.shields.io/github/stars/axelfreeman/yandex-wordstat-guide?style=flat-square)]()

```bash
npx hermes skill install axelfreeman/yandex-wordstat-guide
```

---

## Зачем это нужно

Яндекс.Вордстат — единственный источник реальной поисковой статистики рунета. Раньше чтобы собрать семантику нужно было сидеть в интерфейсе, копировать, вставлять в Excel. Дни работы.

**Через API вы получаете автоматический сбор через AI-агента.** 100 запросов в час, на выходе — структурированные данные которые можно сразу скормить нейросети для генерации контента.

```
Вы → Агент → Wordstat API → 500 фраз за час → DeepSeek → Готовые страницы
```

**Для кого:**
- Контекстологи и таргетологи — ежедневный мониторинг спроса
- SEO-специалисты — семантическое ядро за час вместо недели
- AI-маркетологи — данные для генерации страниц через LLM
- Владельцы бизнеса — понимание что реально ищут клиенты

## Установка

### Как навык для Hermes Agent

```bash
npx hermes skill install axelfreeman/yandex-wordstat-guide
```

### Как отдельный скрипт

```bash
git clone https://github.com/axelfreeman/yandex-wordstat-guide.git
cd yandex-wordstat-guide
pip install -r requirements.txt
cp .env.example .env  # вставьте свои ключи
```

### Для Claude Code / Cursor

Загрузите репозиторий как контекст. Скажите агенту: «Собери семантику по теме X через Wordstat API из skill/SKILL.md»

## Быстрый старт

### 1. Получить доступ

https://oauth.yandex.ru/ → создать приложение → права `search-api.webSearchUser`

Подробнее: [guide/oauth-setup.md](guide/oauth-setup.md)

### 2. Настроить ключи

```bash
export WORDSTAT_API_KEY="AQVN..."
export WORDSTAT_FOLDER_ID="b1g..."
```

### 3. Запустить сбор

```bash
python3 scripts/collect.py "ремонт квартир" "дизайн интерьера"
```

Результат — `semantic_results.json`:
```json
{
  "total_phrases": 171,
  "results": [
    {"phrase": "ремонт квартир под ключ", "shows": 12450},
    {"phrase": "дизайн интерьера квартиры", "shows": 6720}
  ]
}
```

### 4. Отправить в нейросеть

```python
data = json.load(open("semantic_results.json"))
prompt = f"Вот семантика. Сгенерируй 10 SEO-страниц под эти запросы:\n{data}"
# → DeepSeek API → HTML
```

## Структура

```
├── skill/SKILL.md           # Инструкция для AI-агента
├── scripts/collect.py       # Основной скрипт (python3 collect.py "ключ")
├── guide/
│   ├── oauth-setup.md       # OAuth: client_id, secret, токен
│   ├── quick-start.md       # От clone до первого результата
│   └── pitfalls.md          # Лимиты, строки вместо чисел, folderId
├── examples/
│   └── sample_results.json  # Пример выходных данных
├── .env.example             # Шаблон для ключей
└── requirements.txt         # requests
```

## Ограничения

| Что | Лимит |
|-----|-------|
| Запросов в час | 100 |
| Символов в фразе | 400 |
| Фраз в одном запросе | 2000 |
| Окно данных | 30 дней |

Все грабли: [guide/pitfalls.md](guide/pitfalls.md)

## Автор

[Axel Freeman](https://axelfreeman.ru) — AI-Native маркетолог. 40+ клиентов на AI. Hermes Agent.

---

*MIT License. Делайте что хотите, просто поставьте звезду.*
