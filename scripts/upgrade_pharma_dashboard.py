"""Upgrade existing PharmaFlow PBIR report to 3 pages using supported visuals.
Close Power BI Desktop before running. Makes a timestamped report backup.
Run: python scripts/upgrade_pharma_dashboard.py
"""
from pathlib import Path
import json, re, shutil, uuid
from datetime import datetime

ROOT=Path(__file__).resolve().parent.parent
REPORT=ROOT/'PharmaFlow_Dashboard.Report'
PAGES=REPORT/'definition'/'pages'
TABLES=ROOT/'PharmaFlow_Dashboard.SemanticModel'/'definition'/'tables'
SCHEMA='https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.13.0/schema.json'

def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def ident(): return uuid.uuid4().hex[:20]
def col(t,c): return {'Column':{'Expression':{'SourceRef':{'Entity':t}},'Property':c}}
def proj(t,c,sum_=False):
    return {'field':{'Aggregation':{'Expression':col(t,c),'Function':0}} if sum_ else col(t,c),
            'queryRef':f'Sum({t}.{c})' if sum_ else f'{t}.{c}',
            'nativeQueryRef':f'Sum of {c}' if sum_ else c}
def title(txt):
    return {'title':[{'properties':{'show':{'expr':{'Literal':{'Value':'true'}}},
                                      'text':{'expr':{'Literal':{'Value':json.dumps(txt)}}}}}]}
def visual(kind,query,x,y,w,h,z,heading):
    name=ident()
    return {'$schema':SCHEMA,'name':name,'position':{'x':x,'y':y,'z':z,'height':h,'width':w,'tabOrder':z},
            'visual':{'visualType':kind,'query':{'queryState':query},'objects':title(heading),'drillFilterOtherVisuals':True}}
def card(t,c,x,y,w,heading,z): return visual('card',{'Values':{'projections':[proj(t,c,True)]}},x,y,w,125,z,heading)
def graph(kind,t,category,value,x,y,w,h,heading,z):
    return visual(kind,{'Category':{'projections':[proj(t,category)]},'Y':{'projections':[proj(t,value,True)]}},x,y,w,h,z,heading)
def textbox(label,x=30,y=10,w=1170,h=70,z=0):
    name=ident()
    return {'$schema':SCHEMA,'name':name,'position':{'x':x,'y':y,'z':z,'height':h,'width':w,'tabOrder':z},
            'visual':{'visualType':'textbox','objects':{'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':label,'textStyle':{'fontFamily':'Arial','fontSize':'27pt'}}]}]}}]},'drillFilterOtherVisuals':True}}
def add(page,v): save(page/'visuals'/v['name']/'visual.json',v)
def has(t,c):
    p=TABLES/f'{t}.tmdl'
    if not p.exists(): return False
    return bool(re.search(r'^\s*column\s+[\'\"]?'+re.escape(c)+r'[\'\"]?(?:\s|$)',p.read_text(encoding='utf-8-sig'),re.I|re.M))
def optional_chart(out,kind,t,cat,val,x,y,w,h,heading,z):
    if has(t,cat) and has(t,val): out.append(graph(kind,t,cat,val,x,y,w,h,heading,z))
    else: print('Skipped optional chart:',heading,'(missing field)')
def require(t,c):
    if not has(t,c): raise RuntimeError(f'Missing model field {t}.{c}. No files changed.')

def main():
    for t,c in [('MART_SALES_SUMMARY','TOTAL_SALES_AMOUNT'),('MART_SALES_SUMMARY','TOTAL_ORDERS'),('MART_SALES_SUMMARY','CATEGORY'),('MART_SALES_SUMMARY','SALES_MONTH'),('MART_INVENTORY_HEALTH','INBOUND_QUANTITY'),('MART_INVENTORY_HEALTH','WAREHOUSE_ID'),('MART_INVENTORY_HEALTH','NET_STOCK_MOVEMENT'),('MART_SUPPLIER_PERFORMANCE','SUPPLIER_ID'),('MART_SUPPLIER_PERFORMANCE','TOTAL_PURCHASE_VALUE')]: require(t,c)
    manifest=PAGES/'pages.json'
    m=load(manifest)
    original=next((p for p in PAGES.iterdir() if p.is_dir() and (p/'page.json').exists()),None)
    if not original: raise RuntimeError('PBIR page missing')
    backup=ROOT/('PharmaFlow_Dashboard.Report.backup_advanced_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
    shutil.copytree(REPORT,backup)
    print('Backup:',backup)
    # Use the existing page metadata to preserve compatibility with the user's Desktop version.
    template=load(original/'page.json')
    definitions=[
      ('Executive Overview',[
        card('MART_SALES_SUMMARY','TOTAL_SALES_AMOUNT',30,105,280,'Completed Sales Amount',1),
        card('MART_SALES_SUMMARY','TOTAL_ORDERS',330,105,280,'Completed Orders',2),
        card('MART_INVENTORY_HEALTH','INBOUND_QUANTITY',630,105,280,'Inbound Units',3),
        card('MART_INVENTORY_HEALTH','NET_STOCK_MOVEMENT',930,105,280,'Net Inventory Movement',4),
        graph('lineChart','MART_SALES_SUMMARY','SALES_MONTH','TOTAL_SALES_AMOUNT',30,250,570,200,'Monthly Completed Sales',5),
        graph('clusteredBarChart','MART_SALES_SUMMARY','CATEGORY','TOTAL_SALES_AMOUNT',620,250,590,200,'Sales by Product Category',6),
        graph('clusteredColumnChart','MART_INVENTORY_HEALTH','WAREHOUSE_ID','NET_STOCK_MOVEMENT',30,475,570,200,'Net Movement by Warehouse',7),
        graph('clusteredBarChart','MART_SUPPLIER_PERFORMANCE','SUPPLIER_ID','TOTAL_PURCHASE_VALUE',620,475,590,200,'Supplier Purchase Value (All Suppliers)',8),
      ]),
      ('Inventory Intelligence',[
        card('MART_INVENTORY_HEALTH','INBOUND_QUANTITY',30,105,280,'Inbound Units',1),
        card('MART_INVENTORY_HEALTH','OUTBOUND_QUANTITY',330,105,280,'Outbound Units',2) if has('MART_INVENTORY_HEALTH','OUTBOUND_QUANTITY') else None,
        card('MART_INVENTORY_HEALTH','NET_STOCK_MOVEMENT',630,105,280,'Net Stock Movement',3),
        card('MART_INVENTORY_HEALTH','EXPIRING_30D_TRANSACTIONS',930,105,280,'Transactions Expiring Within 30 Days',4) if has('MART_INVENTORY_HEALTH','EXPIRING_30D_TRANSACTIONS') else None,
        graph('clusteredColumnChart','MART_INVENTORY_HEALTH','WAREHOUSE_ID','INBOUND_QUANTITY',30,265,570,190,'Inbound Units by Warehouse',5),
        graph('clusteredBarChart','MART_INVENTORY_HEALTH','PRODUCT_ID','NET_STOCK_MOVEMENT',620,265,590,190,'Net Movement by Product',6) if has('MART_INVENTORY_HEALTH','PRODUCT_ID') else None,
        graph('clusteredColumnChart','MART_INVENTORY_HEALTH','WAREHOUSE_ID','OUTBOUND_QUANTITY',30,480,570,190,'Outbound Units by Warehouse',7) if has('MART_INVENTORY_HEALTH','OUTBOUND_QUANTITY') else None,
        graph('clusteredBarChart','MART_INVENTORY_HEALTH','WAREHOUSE_ID','EXPIRING_30D_TRANSACTIONS',620,480,590,190,'Expiring-30D Transaction Count by Warehouse',8) if has('MART_INVENTORY_HEALTH','EXPIRING_30D_TRANSACTIONS') else None,
      ]),
      ('Supplier and Sales',[
        card('MART_SALES_SUMMARY','TOTAL_SALES_AMOUNT',30,105,370,'Completed Sales Amount',1),
        card('MART_SALES_SUMMARY','TOTAL_ORDERS',425,105,370,'Completed Orders',2),
        card('MART_SUPPLIER_PERFORMANCE','TOTAL_PURCHASE_VALUE',820,105,370,'Total Supplier Purchase Value',3),
        graph('clusteredBarChart','MART_SUPPLIER_PERFORMANCE','SUPPLIER_ID','TOTAL_PURCHASE_VALUE',30,260,570,195,'Supplier Purchase Ranking (All Suppliers)',4),
        graph('clusteredBarChart','MART_SALES_SUMMARY','CATEGORY','TOTAL_SALES_AMOUNT',620,260,590,195,'Completed Sales by Category',5),
        graph('lineChart','MART_SALES_SUMMARY','SALES_MONTH','TOTAL_SALES_AMOUNT',30,480,570,195,'Completed Sales by Month',6),
        graph('clusteredColumnChart','MART_SALES_SUMMARY','WAREHOUSE_CITY','TOTAL_SALES_AMOUNT',620,480,590,195,'Completed Sales by Warehouse City',7) if has('MART_SALES_SUMMARY','WAREHOUSE_CITY') else None,
      ])]
    # Remove only pages created by a prior run of THIS script, if identified by displayName.
    # Preserve user's original page and other manually created pages.
    existing={load(p/'page.json').get('displayName'):p for p in PAGES.iterdir() if p.is_dir() and (p/'page.json').exists()}
    created=[]
    for page_index,(display,items) in enumerate(definitions):
        if page_index == 0:
            page=original
            page_name=page.name
            page_metadata=load(page/'page.json')
            page_metadata['displayName']=display
            save(page/'page.json',page_metadata)
            shutil.rmtree(page/'visuals',ignore_errors=True)
        elif display in existing and existing[display] != original:
            page=existing[display]
            shutil.rmtree(page/'visuals',ignore_errors=True)
            page_name=page.name
        elif display in existing and existing[display] == original:
            page=original
            shutil.rmtree(page/'visuals',ignore_errors=True)
            page_name=page.name
        else:
            page_name=ident()
            page=PAGES/page_name
            page.mkdir(parents=True,exist_ok=True)
            p=__import__('copy').deepcopy(template)
            p['name']=page_name
            p['displayName']=display
            save(page/'page.json',p)
        add(page,textbox('PharmaFlow  |  '+display))
        for v in items:
            if v: add(page,v)
        created.append(page_name)
        print(display,':',1+sum(v is not None for v in items),'visuals')
    # Update navigation order, preserving any other existing pages.
    order=m.get('pageOrder',[])
    m['pageOrder']=created+[n for n in order if n not in created]
    save(manifest,m)
    print('Done. Reopen PharmaFlow_Dashboard.pbip and validate each page before saving.')
    print('Note: supplier ranking includes all suppliers; Top 5 filter can be added in Power BI.')

if __name__=='__main__': main()
