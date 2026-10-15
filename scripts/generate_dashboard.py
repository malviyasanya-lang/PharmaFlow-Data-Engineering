"""Generate PharmaFlow PBIR report visuals without modifying the semantic model.

Run from the PharmaFlow project root with Power BI Desktop closed:
    python scripts/generate_dashboard.py

The script creates a timestamped backup of the Report directory first.
"""
from __future__ import annotations

import copy
import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / 'PharmaFlow_Dashboard.Report'
DEFINITION = REPORT / 'definition'
PAGES = DEFINITION / 'pages'


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def col(table, column):
    return {'Column': {'Expression': {'SourceRef': {'Entity': table}}, 'Property': column}}


def agg(table, column):
    return {'Aggregation': {'Expression': col(table, column), 'Function': 0}}


def projection(table, column, summed=False):
    return {
        'field': agg(table, column) if summed else col(table, column),
        'queryRef': f'Sum({table}.{column})' if summed else f'{table}.{column}',
        'nativeQueryRef': f'Sum of {column}' if summed else column,
    }


def new_id():
    return uuid.uuid4().hex[:20]


def position(x, y, w, h, z):
    return {'x': x, 'y': y, 'z': z, 'height': h, 'width': w, 'tabOrder': z}


def title_object(title):
    return {'title': [{'properties': {
        'show': {'expr': {'Literal': {'Value': 'true'}}},
        'text': {'expr': {'Literal': {'Value': json.dumps(title)}}},
    }}]}


def create_visual(visual_type, query_state, x, y, w, h, z, title=None):
    visual_id = new_id()
    visual = {
        '$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.13.0/schema.json',
        'name': visual_id,
        'position': position(x, y, w, h, z),
        'visual': {'visualType': visual_type, 'query': {'queryState': query_state}, 'drillFilterOtherVisuals': True},
    }
    if title:
        visual['visual']['objects'] = title_object(title)
    return visual


def card(table, column, x, title, z):
    # PBIR card (legacy single-value visual) uses the Values query role.
    return create_visual('card', {'Values': {'projections': [projection(table, column, True)]}}, x, 105, 290, 150, z, title)


def chart(kind, table, category, amount, x, y, w, h, title, z):
    # PBIR bar/column chart roles are Category and Y (as captured in the user's own PBIR).
    query = {
        'Category': {'projections': [projection(table, category)]},
        'Y': {'projections': [projection(table, amount, True)]},
    }
    return create_visual(kind, query, x, y, w, h, z, title)


def main():
    if not REPORT.is_dir() or not PAGES.is_dir():
        raise SystemExit('PBIP Report folder not found. Run from your PharmaFlow repository.')

    pages_manifest = PAGES / 'pages.json'
    pages_data = read_json(pages_manifest)
    page_dirs = [p for p in PAGES.iterdir() if p.is_dir() and (p / 'page.json').exists()]
    if not page_dirs:
        raise SystemExit('No PBIR page found.')
    page = page_dirs[0]
    visual_root = page / 'visuals'
    visual_files = list(visual_root.glob('*/visual.json'))
    source_bar = None
    for f in visual_files:
        d = read_json(f)
        if d.get('visual', {}).get('visualType') == 'clusteredBarChart':
            source_bar = (f, d)
            break
    if source_bar is None:
        raise SystemExit('Sample clusteredBarChart missing. Keep your original sample chart.')

    # Validate field names against actual TMDL before changing files.
    table_dir = ROOT / 'PharmaFlow_Dashboard.SemanticModel' / 'definition' / 'tables'
    required = {
        'MART_SALES_SUMMARY': ['CATEGORY', 'TOTAL_SALES_AMOUNT', 'TOTAL_ORDERS', 'SALES_MONTH'],
        'MART_INVENTORY_HEALTH': ['INBOUND_QUANTITY', 'WAREHOUSE_ID', 'NET_STOCK_MOVEMENT'],
        'MART_SUPPLIER_PERFORMANCE': ['SUPPLIER_ID', 'TOTAL_PURCHASE_VALUE'],
    }
    for table, columns in required.items():
        tmdl = table_dir / f'{table}.tmdl'
        if not tmdl.exists():
            raise SystemExit(f'Missing table: {tmdl}')
        content = tmdl.read_text(encoding='utf-8-sig').upper()
        for column in columns:
            if column not in content:
                raise SystemExit(f'Missing column {table}.{column}; no files changed.')

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = ROOT / f'PharmaFlow_Dashboard.Report.backup_{timestamp}'
    shutil.copytree(REPORT, backup)
    print(f'Backup created: {backup}')

    # Retain existing page settings and visuals; avoid changing unknown PBIR page schema.
    # Layout targets the default 1280x720 canvas; adjust in Power BI if needed.

    # Reposition existing visuals, keep original query/filters untouched.
    for f in visual_files:
        d = read_json(f)
        t = d.get('visual', {}).get('visualType')
        if t == 'textbox':
            d['position'] = position(30, 15, 1190, 75, 0)
            write_json(f, d)
        elif f == source_bar[0]:
            d['position'] = position(650, 265, 580, 190, 5)
            d['visual'].setdefault('objects', {}).update(title_object('Sales by Product Category'))
            write_json(f, d)

    visuals = [
        card('MART_SALES_SUMMARY', 'TOTAL_SALES_AMOUNT', 30, 'Completed Sales Amount', 1),
        card('MART_SALES_SUMMARY', 'TOTAL_ORDERS', 345, 'Completed Orders', 2),
        card('MART_INVENTORY_HEALTH', 'INBOUND_QUANTITY', 660, 'Inbound Units', 3),
        chart('lineChart', 'MART_SALES_SUMMARY', 'SALES_MONTH', 'TOTAL_SALES_AMOUNT', 30, 265, 590, 190, 'Monthly Sales Trend', 4),
        chart('clusteredBarChart', 'MART_SUPPLIER_PERFORMANCE', 'SUPPLIER_ID', 'TOTAL_PURCHASE_VALUE', 30, 475, 590, 205, 'Supplier Purchase Value', 6),
        chart('clusteredColumnChart', 'MART_INVENTORY_HEALTH', 'WAREHOUSE_ID', 'NET_STOCK_MOVEMENT', 650, 475, 580, 205, 'Net Stock Movement by Warehouse', 7),
    ]
    for v in visuals:
        target = visual_root / v['name'] / 'visual.json'
        write_json(target, v)
        print(f"Created: {v['visual']['visualType']} ({v['name']})")

    print('\nDone. Open PharmaFlow_Dashboard.pbip in Power BI Desktop and validate all visuals.')
    print('If a visual is blank or unsupported, restore the backup and report the issue.')
    print('Supplier chart currently shows ALL suppliers, not Top 5; apply Top N in Power BI.')


if __name__ == '__main__':
    main()
