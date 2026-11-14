#!/usr/bin/env python3
"""Render data/contributions.json as an animated SVG heatmap —
'THE LONG DRIVE': every box is a day he showed up.
M-blue ramp, diagonal reveal (CSS keyframes inside the SVG, plays once)."""
import json
from datetime import date, timedelta

PALETTE = ["#131a26", "#0d2f4d", "#16588e", "#2f7fc4", "#7eb6e8", "#eaf6ff"]
BOX, GAP = 13, 3
STEP = BOX + GAP
OX, OY = 34, 56          # origin (room for month labels + day letters)
W = OX + 53 * STEP + 6
H = OY + 7 * STEP + 44   # + footer

data = json.load(open("data/contributions.json"))
days = {date.fromisoformat(k): v for k, v in data["days"].items()}
last = date.fromisoformat(data["last"])
first = last - timedelta(days=363)
# align to the Sunday on/before `first`
start = first - timedelta(days=(first.weekday() + 1) % 7)

cells, months, seen_months = [], [], set()
d, col = start, 0
while d <= last:
    row = (d.weekday() + 1) % 7  # Sunday = 0
    if row == 0 and col > 0:
        pass
    lvl = days.get(d, 0)
    x, y = OX + col * STEP, OY + row * STEP
    delay = (col + row) * 18
    cells.append(
        f'<rect class="c" x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="3" '
        f'fill="{PALETTE[lvl]}" style="animation-delay:{delay}ms">'
        f'<title>{d.isoformat()} — level {lvl}</title></rect>')
    if d.month not in seen_months and d.day <= 7:
        months.append((x, d.strftime("%b")))
        seen_months.add(d.month)
    if row == 6:
        col += 1
    d += timedelta(days=1)

month_svg = "".join(
    f'<text x="{x}" y="{OY - 12}" class="m">{m}</text>' for x, m in months)
day_svg = "".join(
    f'<text x="6" y="{OY + i * STEP + 11}" class="m">{t}</text>'
    for i, t in [(1, "Mon"), (3, "Wed"), (5, "Fri")])
legend = "".join(
    f'<rect x="{W - 162 + i * STEP}" y="{H - 24}" width="{BOX}" height="{BOX}" rx="3" fill="{c}"/>'
    for i, c in enumerate(PALETTE[1:], start=1))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Contribution heatmap — the long drive">
<style>
  .bg {{ fill: #0a0f1a; }}
  .t {{ font: 700 15px ui-monospace, Menlo, monospace; fill: #eaf6ff; letter-spacing: 2px; }}
  .m {{ font: 10px ui-monospace, Menlo, monospace; fill: #5b6b82; }}
  .f {{ font: 12px ui-monospace, Menlo, monospace; fill: #9db8d6; }}
  .c {{ animation: drop .45s ease-out both; }}
  @keyframes drop {{ from {{ opacity: 0; transform: translateY(-7px); }} to {{ opacity: 1; transform: translateY(0); }} }}
</style>
<rect class="bg" width="{W}" height="{H}" rx="12"/>
<text x="{OX}" y="24" class="t">THE LONG DRIVE — every box is a day I showed up</text>
{month_svg}
{day_svg}
{''.join(cells)}
<text x="{OX}" y="{H - 12}" class="f">{data["active_days"]} active days in the last year · current streak {data["current_streak"]} · longest {data["longest_streak"]}</text>
<text x="{W - 180}" y="{H - 12}" class="f">Less</text>
{legend}
<text x="{W - 56}" y="{H - 12}" class="f">More</text>
</svg>
'''
open("assets/heatmap.svg", "w").write(svg)
print("OK assets/heatmap.svg", len(svg), "bytes")
