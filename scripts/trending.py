#!/usr/bin/env python3
"""Поиск взрывных тематик — фразы с резким ростом в этом месяце."""
import json, os, sys, time, urllib.request
from datetime import datetime, timedelta

class TrendingFinder:
    def __init__(self):
        self.key = os.getenv("WORDSTAT_API_KEY", "").strip()
        self.folder = os.getenv("WORDSTAT_FOLDER_ID", "").strip()
        if not self.key or not self.folder:
            print("export WORDSTAT_API_KEY='...' WORDSTAT_FOLDER_ID='...'")
            sys.exit(1)
        self.requests = 0
    
    def _api(self, method, body):
        """API call with error handling."""
        if self.requests >= 85:
            return {"results": []}
        body["folderId"] = self.folder
        req = urllib.request.Request(
            f"https://searchapi.api.cloud.yandex.net/v2/wordstat/{method}",
            data=json.dumps(body).encode(),
            headers={"Authorization": f"Api-Key {self.key}", "Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                self.requests += 1
                return json.loads(r.read())
        except Exception as e:
            return {"results": []}
    
    def find(self, seeds, threshold=200):
        """Find phrases with growth >= threshold%."""
        print(f"Searching {len(seeds)} seeds, threshold {threshold}%\n")
        trends = []
        
        # Calculate dates
        today = datetime.now()
        from_month = today.month - 5
        from_year = today.year
        if from_month <= 0:
            from_month += 12
            from_year -= 1
        from_str = f"{from_year}-{from_month:02d}-01T00:00:00Z"
        
        if today.month == 1:
            to_dt = datetime(today.year - 1, 12, 31)
        else:
            to_dt = datetime(today.year, today.month, 1) - timedelta(days=1)
        to_str = to_dt.strftime("%Y-%m-%d") + "T23:59:59Z"
        
        for seed in seeds:
            if self.requests >= 80:
                break
            
            print(f"[{self.requests+1}] {seed}")
            top = self._api("topRequests", {"phrase": seed, "numPhrases": 15})
            time.sleep(0.3)
            
            phrases = [p["phrase"] for p in top.get("results", [])[:10]]
            if not phrases:
                continue
            
            for phrase in phrases:
                if self.requests >= 80:
                    break
                
                dyn = self._api("dynamics", {
                    "phrase": phrase,
                    "period": "PERIOD_MONTHLY",
                    "from_date": from_str,
                    "to_date": to_str,
                })
                time.sleep(0.3)
                
                points = dyn.get("results", [])
                if len(points) < 4:
                    continue
                
                first3 = points[:3]
                last1 = points[-1]
                
                avg = sum(int(p["count"]) for p in first3) / 3
                cur = int(last1["count"])
                
                if avg == 0:
                    continue
                
                growth = ((cur - avg) / avg) * 100
                
                if growth >= threshold:
                    t = {
                        "phrase": phrase,
                        "avg_first_3": int(avg),
                        "last_month": cur,
                        "growth_pct": round(growth, 1),
                        "history": [{"date": p["date"][:7], "count": int(p["count"])} for p in points]
                    }
                    trends.append(t)
                    print(f"  +{growth:.0f}%  {phrase}: {int(avg):,} -> {cur:,}")
        
        return sorted(trends, key=lambda x: x["growth_pct"], reverse=True)
    
    def save(self, trends, fname="trending.json"):
        out = {"collected": datetime.now().isoformat(), "total": len(trends), "requests": self.requests, "results": trends}
        with open(fname, "w") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"\nSaved: {fname} ({len(trends)} trends)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 trending.py 'topic1' 'topic2' ...")
        print("Example: python3 trending.py 'AI' 'marketing' 'design'")
        sys.exit(1)
    f = TrendingFinder()
    trends = f.find(sys.argv[1:])
    f.save(trends)
    if trends:
        print(f"\nTop trends:")
        for i, t in enumerate(trends[:10], 1):
            print(f"  {i}. +{t['growth_pct']}%  {t['phrase']}")
    else:
        print("\nNo explosive growth detected. Try other topics.")
