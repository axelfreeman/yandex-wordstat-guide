#!/usr/bin/env python3
"""
Поиск взрывных тематик: фразы которые никто не искал, а в этом месяце — рост.
Использование: python3 trending.py "широкая тема"
"""
import json, os, sys, time, urllib.request
from datetime import datetime, timedelta

class TrendingFinder:
    def __init__(self):
        self.key = os.getenv("WORDSTAT_API_KEY", "").strip()
        self.folder = os.getenv("WORDSTAT_FOLDER_ID", "").strip()
        
        if not self.key or not self.folder:
            print("❌ export WORDSTAT_API_KEY='...' WORDSTAT_FOLDER_ID='...'")
            sys.exit(1)
        
        self.requests = 0
    
    def _call(self, method, body):
        body["folderId"] = self.folder
        req = urllib.request.Request(
            f"https://searchapi.api.cloud.yandex.net/v2/wordstat/{method}",
            data=json.dumps(body).encode(),
            headers={"Authorization": f"Api-Key {self.key}", "Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            self.requests += 1
            return json.loads(r.read())
    
    def find_trending(self, seeds, threshold_pct=200):
        """
        Находит фразы с резким ростом.
        threshold_pct: минимальный рост в % (200 = в 3 раза больше)
        """
        print(f"🔍 Ищем взрывные темы за последние 6 месяцев")
        print(f"   Порог роста: {threshold_pct}%\n")
        
        trending = []
        
        for seed in seeds:
            if self.requests >= 85:
                break
            
            # Шаг 1: собрать топ-фразы по seed
            print(f"[{self.requests+1}] {seed}")
            top = self._call("topRequests", {"phrase": seed, "numPhrases": 20})
            time.sleep(0.3)
            
            phrases = [p["phrase"] for p in top.get("results", [])[:10]]
            if not phrases:
                continue
            
            # Шаг 2: запросить динамику для топ-10 фраз
            today = datetime.now()
            to_date = today.replace(day=1) - timedelta(days=1)  # последний день прошлого месяца
            to_date = to_date.replace(day=min(28, to_date.day))  # фикс февраля
            from_date = (to_date - timedelta(days=180)).replace(day=1)
            
            dyn = self._call("dynamics", {
                "phrases": phrases,
                "period": "PERIOD_MONTHLY",
                "fromDate": from_date.strftime("%Y-%m-%d"),
                "toDate": to_date.strftime("%Y-%m-%d")
            })
            time.sleep(0.3)
            
            for result in dyn.get("results", []):
                points = result.get("points", [])
                if len(points) < 3:
                    continue
                
                # Считаем рост: среднее первых месяцев vs последний месяц
                first_half = points[:len(points)//2]
                last_month = points[-1]
                
                avg_early = sum(int(p["count"]) for p in first_half) / max(len(first_half), 1)
                current = int(last_month["count"])
                
                if avg_early == 0:
                    continue
                
                growth = ((current - avg_early) / avg_early) * 100
                
                if growth >= threshold_pct:
                    trend = {
                        "phrase": result["phrase"],
                        "avg_early": int(avg_early),
                        "current": current,
                        "growth_pct": round(growth, 1),
                        "history": [{"date": p["date"], "count": int(p["count"])} for p in points]
                    }
                    trending.append(trend)
                    print(f"  🚀 {result['phrase']}: {int(avg_early)} → {current} (+{growth:.0f}%)")
        
        return sorted(trending, key=lambda x: x["growth_pct"], reverse=True)
    
    def save(self, trends, filename="trending_topics.json"):
        output = {
            "collected_at": datetime.now().isoformat(),
            "total_trends": len(trends),
            "requests_used": self.requests,
            "results": trends
        }
        with open(filename, "w") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\n✅ {filename}: {len(trends)} растущих тем")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python3 trending.py 'тема1' 'тема2' ...")
        print("Пример: python3 trending.py 'нейросеть' 'маркетинг' 'ремонт'")
        sys.exit(1)
    
    finder = TrendingFinder()
    trends = finder.find_trending(sys.argv[1:], threshold_pct=200)
    finder.save(trends)
    
    if trends:
        print(f"\n📈 Топ-5 взрывных тем:")
        for i, t in enumerate(trends[:5], 1):
            print(f"  {i}. {t['phrase']}: {t['avg_early']} → {t['current']} (+{t['growth_pct']}%)")
    else:
        print("\n😴 Пока ничего взрывного. Попробуйте другие темы.")
