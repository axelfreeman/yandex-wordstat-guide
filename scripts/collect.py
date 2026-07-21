#!/usr/bin/env python3
"""
Wordstat Collector — сбор поисковой семантики для AI-агентов.
Использование: python3 wordstat_collector.py "ключевая фраза"
"""
import json, os, sys, time, urllib.request
from pathlib import Path
from datetime import datetime

class WordstatCollector:
    def __init__(self):
        self.key = os.getenv("WORDSTAT_API_KEY", "").strip()
        self.folder = os.getenv("WORDSTAT_FOLDER_ID", "").strip()
        
        if not self.key or not self.folder:
            print("❌ Установите переменные окружения:")
            print("   export WORDSTAT_API_KEY='AQVN...'")
            print("   export WORDSTAT_FOLDER_ID='b1g...'")
            sys.exit(1)
        
        if len(self.folder) != 20:
            print(f"❌ folderId должен быть ровно 20 символов. Сейчас: {len(self.folder)}")
            sys.exit(1)
        
        self.results = {}
        self.requests_made = 0
        self.max_requests = 90  # запас 10% от лимита 100/час
        
    def _call(self, method, body):
        if self.requests_made >= self.max_requests:
            raise RuntimeError(f"Достигнут лимит {self.max_requests} запросов/час")
        
        body["folderId"] = self.folder
        req = urllib.request.Request(
            f"https://searchapi.api.cloud.yandex.net/v2/wordstat/{method}",
            data=json.dumps(body).encode(),
            headers={
                "Authorization": f"Api-Key {self.key}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                self.requests_made += 1
                return json.loads(r.read())
        except Exception as e:
            print(f"  ⚠️ Ошибка запроса: {e}")
            return {"results": []}
    
    def expand_seed(self, phrase, num=100):
        """Расширить seed-фразу → список вложенных запросов."""
        print(f"  [{self.requests_made+1}] {phrase}... ", end="", flush=True)
        data = self._call("topRequests", {
            "phrase": phrase,
            "numPhrases": num
        })
        count = len(data.get("results", []))
        total = data.get("totalCount", "0")
        print(f"{count} фраз (всего: {int(total):,})")
        return data.get("results", [])
    
    def collect(self, seeds, num_per_seed=100):
        """Основной цикл сбора."""
        print(f"\n📊 Сбор семантики: {len(seeds)} seed-фраз (до {self.max_requests} запросов)")
        print(f"   Начало: {datetime.now().strftime('%H:%M:%S')}\n")
        
        for seed in seeds:
            if self.requests_made >= self.max_requests - 5:
                break
            
            results = self.expand_seed(seed, num_per_seed)
            self.results[seed] = results
            time.sleep(0.3)
        
        # Дедупликация
        unique = {}
        for seed, phrases in self.results.items():
            for p in phrases:
                phrase = p["phrase"].strip()
                count = int(p.get("count", 0))
                if phrase not in unique or unique[phrase]["count"] < count:
                    unique[phrase] = {"count": count, "source": seed}
        
        # Сортировка по убыванию
        sorted_phrases = sorted(unique.items(), key=lambda x: x[1]["count"], reverse=True)
        
        return sorted_phrases
    
    def save(self, phrases, filename="semantic_results.json"):
        """Сохранить результаты."""
        output = {
            "collected_at": datetime.now().isoformat(),
            "total_phrases": len(phrases),
            "requests_used": self.requests_made,
            "results": [
                {"phrase": p, "count": c["count"], "source": c["source"]}
                for p, c in phrases
            ]
        }
        Path(filename).write_text(json.dumps(output, ensure_ascii=False, indent=2))
        total_shows = sum(c["count"] for _, c in phrases)
        print(f"\n✅ Сохранено: {filename}")
        print(f"   Уникальных фраз: {len(phrases)}")
        print(f"   Суммарный спрос: {total_shows:,} показов/мес")
        print(f"   Использовано запросов: {self.requests_made}/{self.max_requests}")
        return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python3 wordstat_collector.py 'фраза1' ['фраза2' ...]")
        print("Пример: python3 wordstat_collector.py 'ремонт квартир' 'дизайн интерьера'")
        sys.exit(1)
    
    collector = WordstatCollector()
    seeds = sys.argv[1:]
    
    phrases = collector.collect(seeds)
    collector.save(phrases)
    
    # Топ-10
    print("\n📈 Топ-10 запросов:")
    for i, (phrase, data) in enumerate(phrases[:10], 1):
        print(f"  {i:>2}. {data['count']:>8,}  {phrase}")
