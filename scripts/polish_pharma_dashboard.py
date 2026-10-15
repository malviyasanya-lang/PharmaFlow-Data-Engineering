"""Polish the existing 3-page PharmaFlow PBIR report layout, safely.
Only edits .Report; backs it up. Run with Power BI Desktop closed.
"""
from pathlib import Path
from datetime import datetime
import json, shutil, uuid

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / 'PharmaFlow_Dashboard.Report'
PAGES = REPORT / 'definition' / 'pages'
SCHEMA = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.13.0/schema.json'


def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p, obj): p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def textbox(text, x, y, width, height, font_size, z):
    name = uuid.uuid4().hex[:20]
    return {
        '$schema': SCHEMA, 'name': name,
        'position': {'x': x, 'y': y, 'z': z, 'height': height, 'width': width, 'tabOrder': z},
        'visual': {'visualType': 'textbox', 'objects': {'general': [{'properties': {
            'paragraphs': [{'textRuns': [{'value': text, 'textStyle': {
                'fontFamily': 'Segoe UI', 'fontSize': f'{font_size}pt',
                'fontWeight': 'bold' if font_size >= 24 else 'normal'
            }}]}]
        }}]}, 'drillFilterOtherVisuals': True}
    }

def main():
    if not (PAGES / 'pages.json').exists():
        raise RuntimeError('PBIP report not found. Put this file in PharmaFlow/scripts/')
    backup = ROOT / ('PharmaFlow_Dashboard.Report.backup_polish_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
    shutil.copytree(REPORT, backup)
    print('Backup:', backup)
    order = read(PAGES / 'pages.json').get('pageOrder', [])
    for page_id in order:
        folder = PAGES / page_id
        page_file = folder / 'page.json'
        if not page_file.exists(): continue
        page = read(page_file)
        label = page.get('displayName', 'PharmaFlow Analytics')
        W, H = float(page.get('width') or 1280), float(page.get('height') or 720)
        # Most Power BI 16:9 pages are 1280x720; custom page sizes use actual metadata.
        margin, gap = W * .035, W * .014
        usable = W - 2 * margin
        visual_files = list((folder / 'visuals').glob('*/visual.json'))
        cards, charts, old_textboxes = [], [], []
        for path in visual_files:
            obj = read(path)
            kind = obj.get('visual', {}).get('visualType')
            if kind == 'textbox': old_textboxes.append(path)
            elif kind in ('card', 'cardVisual'): cards.append((path, obj))
            else: charts.append((path, obj))
        # Keep source-generated order rather than guessing chart semantics.
        cards.sort(key=lambda x: x[1].get('position', {}).get('z', 0))
        charts.sort(key=lambda x: x[1].get('position', {}).get('z', 0))
        # Replace previous auto-generated textboxes with clean title + subtitle.
        for path in old_textboxes: shutil.rmtree(path.parent)
        title_h = H * .075
        for txt, y, size, height in [
            ('PHARMAFLOW  /  ' + label.upper(), H * .035, 27, title_h),
            ('Pharmaceutical Supply Chain  •  Synthetic demonstration data  •  Snowflake + dbt', H * .11, 12, H * .042)
        ]:
            t = textbox(txt, margin, y, usable, height, size, 0)
            dest = folder / 'visuals' / t['name']
            dest.mkdir(parents=True, exist_ok=True)
            write(dest / 'visual.json', t)
        # Full-width KPI row, followed by large 2-column analytics charts.
        card_count = len(cards)
        card_y, card_h = H * .18, H * .145
        if card_count:
            card_w = (usable - gap * (card_count - 1)) / card_count
            for i, (path, obj) in enumerate(cards):
                obj['position'].update(x=round(margin + i * (card_w + gap), 2),
                    y=round(card_y, 2), width=round(card_w, 2), height=round(card_h, 2), z=i + 1, tabOrder=i + 1)
                write(path, obj)
        chart_y = H * .365
        chart_h_total = H * .57
        rows = max(1, (len(charts) + 1) // 2)
        row_gap = H * .022
        chart_h = (chart_h_total - (rows - 1) * row_gap) / rows
        chart_w = (usable - gap) / 2
        for i, (path, obj) in enumerate(charts):
            row, col = divmod(i, 2)
            obj['position'].update(x=round(margin + col * (chart_w + gap), 2),
                y=round(chart_y + row * (chart_h + row_gap), 2),
                width=round(chart_w, 2), height=round(chart_h, 2), z=card_count + i + 3,
                tabOrder=card_count + i + 3)
            write(path, obj)
        print(f'{label}: {card_count} KPIs + {len(charts)} charts; canvas {W:g} x {H:g}')
    print('Layout updated. Open .pbip in Power BI and inspect before saving.')

if __name__ == '__main__': main()
