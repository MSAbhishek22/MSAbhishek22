#!/usr/bin/env python3
"""Fetch MSAbhishek22's public contribution calendar (no token needed —
GitHub serves it as public HTML) and write data/contributions.json."""
import json, re, sys, urllib.request
from datetime import date, timedelta

USER = "MSAbhishek22"
url = f"https://github.com/users/{USER}/contributions"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

days = {}
for m in re.finditer(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d)"', html):
    days[m.group(1)] = int(m.group(2))
# counts per day (for stats) appear in tool-tip text like "3 contributions on ..."
counts = {}
for m in re.finditer(r'(\d+|No) contributions? on [A-Za-z]+ (\d{1,2}), (\d{4})', html):
    pass  # tooltip format varies; level grid is the reliable source

if not days:
    sys.exit("no contribution days parsed — GitHub markup changed?")

dates = sorted(days)
# streaks computed on levels > 0
streak = longest = 0
prev = None
for d in dates:
    cur = date.fromisoformat(d)
    if days[d] > 0:
        streak = streak + 1 if prev and (cur - prev).days == 1 else 1
        longest = max(longest, streak)
    else:
        streak = 0
    prev = cur
# current streak: count back from the latest date with the run still alive
cur_streak = 0
d = date.fromisoformat(dates[-1])
by = {date.fromisoformat(k): v for k, v in days.items()}
if by.get(d, 0) == 0:
    d -= timedelta(days=1)
while by.get(d, 0) > 0:
    cur_streak += 1
    d -= timedelta(days=1)

active = sum(1 for v in days.values() if v > 0)
out = {
    "user": USER,
    "days": days,
    "first": dates[0],
    "last": dates[-1],
    "active_days": active,
    "total_days": len(dates),
    "current_streak": cur_streak,
    "longest_streak": longest,
}
with open("data/contributions.json", "w") as f:
    json.dump(out, f, indent=1)
print(f"OK {len(dates)} days, active {active}, streak {cur_streak}, longest {longest}")
