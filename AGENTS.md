# AGENTS.md — Yandex Wordstat Guide for AI Agents

**A toolkit for AI agents to collect Yandex search query statistics programmatically.**
Use this repo to gather Russian-language search semantics, find trending topics, and feed structured keyword data into LLMs for SEO content generation — all without the manual Wordstat UI.

## What this project is

Yandex Wordstat is the only source of real search volume data for the Russian-speaking internet (Runet). This project wraps the [Yandex Search API v2](https://yandex.cloud/ru/docs/search-api/) into Python scripts that an AI agent can invoke directly. The output is structured JSON — ready to pipe into DeepSeek, GPT, or Claude for content generation.

## Quick start for AI agents

### Prerequisites

```bash
# 1. Clone
git clone https://github.com/axelfreeman/yandex-wordstat-guide.git
cd yandex-wordstat-guide

# 2. Install deps
pip install -r requirements.txt   # only 'requests'

# 3. Set credentials
export WORDSTAT_API_KEY="AQVN..."       # Yandex Cloud API key
export WORDSTAT_FOLDER_ID="b1g..."      # 20-char folder ID — must be exactly 20 chars!
```

### Your first collection

```bash
python3 scripts/collect.py "ремонт квартир" "дизайн интерьера"
# → semantic_results.json with deduplicated phrases sorted by search volume
```

## What you can do with this

### 1. Collect search semantics (`scripts/collect.py`)

Takes seed phrases → expands each via `topRequests` API → deduplicates → sorts by volume.

```bash
python3 scripts/collect.py "keyword1" "keyword2" "keyword3"
```

**Output** (`semantic_results.json`):
```json
{
  "collected_at": "2026-08-11T14:30:00",
  "total_phrases": 171,
  "requests_used": 12,
  "results": [
    {"phrase": "ремонт квартир под ключ", "count": 12450, "source": "ремонт квартир"},
    {"phrase": "дизайн интерьера квартиры", "count": 6720, "source": "дизайн интерьера"}
  ]
}
```

### 2. Find explosive trends (`scripts/trending.py`)

Discovers phrases with ≥200% month-over-month growth. For each seed, collects top-15 related phrases, then pulls 6-month history via `dynamics` API.

```bash
python3 scripts/trending.py "нейросеть" "маркетинг" "AI"
# → trending.json with growth percentages and monthly history
```

**Output** (`trending.json`):
```json
{
  "collected": "2026-08-11T14:30:00",
  "total": 7,
  "results": [
    {
      "phrase": "нейросеть для видео",
      "avg_first_3": 1200,
      "last_month": 5800,
      "growth_pct": 383.3,
      "history": [{"date": "2026-03", "count": 1100}]
    }
  ]
}
```

### 3. Feed results into an LLM for content generation

```python
import json
data = json.load(open("semantic_results.json"))
prompt = f"Вот семантика по теме. Сгенерируй 10 SEO-страниц под эти запросы:\n{json.dumps(data['results'], ensure_ascii=False)}"
# → Send prompt to DeepSeek / GPT / Claude → HTML pages
```

## Architecture

```
yandex-wordstat-guide/
├── skill/SKILL.md           # Hermes Agent skill definition
├── scripts/
│   ├── collect.py           # Main semantic collector (topRequests → dedupe → sort)
│   └── trending.py          # Explosive growth finder (topRequests → dynamics → filter)
├── guide/
│   ├── oauth-setup.md       # How to get Yandex OAuth / API credentials
│   ├── quick-start.md       # Clone → keys → first result
│   └── pitfalls.md          # Rate limits, string numbers, folderId gotchas
├── examples/
│   └── sample_results.json  # Example output format
├── requirements.txt         # requests>=2.28
└── README.md
```

### API methods used

| Method | Cost | Purpose |
|--------|------|---------|
| `topRequests` | Paid | Expand a seed phrase into related queries with volumes |
| `dynamics` | Paid | Get monthly/weekly search volume history for a phrase |
| `regions` | Paid | Regional breakdown of search volume |
| `getRegionsTree` | **Free** | Get the region tree — does NOT count against quota, cache it |

## Critical constraints

| Constraint | Value | Notes |
|-----------|-------|-------|
| Requests per hour | **100** | Hard limit — `collect.py` stops at 90 (10% safety margin) |
| Delay between requests | **0.3s** | Built into both scripts |
| Max phrase length | 400 chars | API-side limit |
| Max phrases per request | 2,000 | API-side limit |
| Data window | 30 days | Wordstat data is always a trailing 30-day window |
| `folderId` length | **exactly 20 chars** | Copy-paste from UI often adds trailing space → 21 chars → error |
| Billing model | **Deposit** | Top up 500₽ (~$5), lasts 4-5 months. Unused funds don't expire. |

## Key pitfalls AI agents must handle

### 1. All numeric values are strings from the API
```python
# ❌ WRONG
total = r["count"] + other["count"]
# ✅ CORRECT
total = int(r["count"]) + int(other["count"])
```
Both `collect.py` and `trending.py` already handle this — don't break it.

### 2. folderId must be exactly 20 characters
```python
folder_id = os.getenv("WORDSTAT_FOLDER_ID").strip()
assert len(folder_id) == 20, f"folderId is {len(folder_id)} chars, expected 20"
```
Both scripts validate this on init and exit with a clear message if wrong.

### 3. Rate limit: 100/hour, not per-second
Error on hitting the limit:
```json
{"code": 8, "message": "rate quota limit exceed: allowed 100 requests"}
```
Strategy: max 90 requests per session, 0.3s sleep between calls. Never batch more than 90 in one run.

### 4. Dynamics date format
The `from_date`/`to_date` for `dynamics` must use the **last day** of the month (for monthly) or week (for weekly):
```python
# Monthly: last day of month
to_date = "2026-07-31T23:59:59Z"   # ✅
to_date = "2026-07-15T00:00:00Z"   # ❌ mid-month
```

### 5. getRegionsTree is free
Always cache the region tree — it's free and doesn't burn quota. The scripts don't use it by default but it's available if you need regional filtering.

## Common AI agent workflows

### Workflow 1: Build a semantic core for a new site
```
Agent: "Собери семантику по теме [topic] через Wordstat"
→ collect.py with 5-10 seed phrases
→ semantic_results.json with 200-500 phrases
→ Feed to LLM: "Сгруппируй эти запросы по кластерам и предложи структуру сайта"
→ Generate landing pages per cluster
```

### Workflow 2: Content calendar from trends
```
Agent: "Найди взрывные темы по [industry] за последние 6 месяцев"
→ trending.py with industry seeds
→ trending.json with growth percentages
→ Feed to LLM: "Напиши контент-план на месяц под эти растущие запросы"
→ Schedule articles
```

### Workflow 3: Competitor gap analysis
```
Agent: "Сравни нашу семантику с конкурентами"
→ collect.py on competitor brand terms + product categories
→ Compare with your own semantic core
→ LLM identifies gaps: "These queries competitor ranks for that you don't"
```

## Installation as a Hermes Agent skill

```bash
npx hermes skill install axelfreeman/yandex-wordstat-guide
```

Then tell your agent:
- "Собери семантику по теме [X] через Wordstat"
- "Покажи топ-20 запросов по [keyword]"
- "Найди тренды по [topic]"

## Environment variables

| Variable | Required | Source |
|----------|----------|--------|
| `WORDSTAT_API_KEY` | Yes | Yandex Cloud → Service Account → API Key |
| `WORDSTAT_FOLDER_ID` | Yes | Yandex Cloud → Folder ID (20 chars) |

See [guide/oauth-setup.md](guide/oauth-setup.md) for step-by-step credential setup.

## Author

[Axel Freeman](https://axelfreeman.ru) — AI-Native marketer. 40+ AI clients. Hermes Agent.

---

*When in doubt, read [guide/pitfalls.md](guide/pitfalls.md) — every known gotcha is documented there.*
