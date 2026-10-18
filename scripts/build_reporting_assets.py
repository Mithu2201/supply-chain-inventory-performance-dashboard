"""Create verified management aggregates and honest data-driven report design previews.
These PNGs are visual concepts, not Power BI screenshots/PBIX exports.
"""
from pathlib import Path
from collections import defaultdict, Counter
import csv, json, statistics, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'data'/'processed'; DOC=ROOT/'documentation'; SCREEN=ROOT/'screenshots'; EXCEL=ROOT/'excel'

def read(name):
    with (D/(name+'.csv')).open(encoding='utf-8',newline='') as fh: return list(csv.DictReader(fh))
def summap(rows,key,val):
    d=defaultdict(float)
    for r in rows: d[r[key]]+=float(r[val])
    return dict(d)

def r2(x): return round(x,2)
orders=read('Orders'); lines=read('OrderLines'); products=read('Products'); suppliers=read('Suppliers'); purchase=read('PurchaseOrders'); pol=read('PurchaseOrderLines')
snaps=read('InventorySnapshots'); shipments=read('Shipments'); counts=read('PhysicalStockCounts'); labour=read('WarehouseLabour'); targets=read('SalesTargets'); carriers=read('Carriers')
prod_by={x['ProductID']:x for x in products}; pos={x['POID']:x for x in purchase}
validstatuses={'Delivered','Partially Delivered'}
monthly=defaultdict(lambda:defaultdict(float)); regions=defaultdict(lambda:defaultdict(float));
orderregion=defaultdict(lambda:defaultdict(float));
for o in orders:
    m=o['OrderDate'][:7]; a=monthly[m]; b=regions[o['Region']]
    for row in (a,b):
        row['SalesNZD']+=float(o['NetSalesNZD']);row['COGSNZD']+=float(o['COGSNZD']);row['GrossProfitNZD']+=float(o['GrossProfitNZD'])
        row['Orders']+=1;row['OrderedUnits']+=int(o['QuantityOrdered']);row['ShippedUnits']+=int(o['QuantityShipped']);row['BackorderUnits']+=int(o['QuantityBackordered'])
        if o['OrderStatus'] in validstatuses:
            row['DeliveredOrders']+=1;row['OnTimeOrders']+=o['DeliveryDate']<=o['RequiredDate']
            row['InFullOrders']+=o['QuantityBackordered']=='0'
            row['OTIFOrders']+=o['DeliveryDate']<=o['RequiredDate'] and o['QuantityBackordered']=='0'
latest='2026-09-30'; latest_snap=[x for x in snaps if x['SnapshotDate']==latest]
for s in snaps:
    a=monthly[s['SnapshotDate'][:7]]
    a['InventoryValueNZD']+=float(s['InventoryValueNZD']);a['StockoutPoints']+=int(s['StockoutFlag']);a['InventoryPoints']+=1
for s in shipments:
    monthly[s['ShipDate'][:7]]['FreightNZD']+=float(s['FreightCostNZD'])
monthly_rows=[]
for month in sorted(monthly):
    a=monthly[month]
    monthly_rows.append({'YearMonth':month,'NetSalesNZD':r2(a['SalesNZD']),'GrossProfitNZD':r2(a['GrossProfitNZD']),
                         'COGSNZD':r2(a['COGSNZD']),'Orders':int(a['Orders']),'DeliveredOrders':int(a['DeliveredOrders']),
                         'OTIFOrders':int(a['OTIFOrders']),'ShippedUnits':int(a['ShippedUnits']),
                         'BackorderUnits':int(a['BackorderUnits']),'InventoryValueNZD':r2(a['InventoryValueNZD']),
                         'StockoutPoints':int(a['StockoutPoints']),'InventoryPoints':int(a['InventoryPoints']),
                         'FreightNZD':r2(a['FreightNZD'])})
region_rows=[]
for reg in sorted(regions):
    a=regions[reg]
    region_rows.append({'Region':reg,'NetSalesNZD':r2(a['SalesNZD']),'Orders':int(a['Orders']),
                        'BackorderUnits':int(a['BackorderUnits']),'DeliveredOrders':int(a['DeliveredOrders']),
                        'OTIFOrders':int(a['OTIFOrders']),'OTIFPct':r2(100*a['OTIFOrders']/a['DeliveredOrders'])})

supplier_stat=defaultdict(lambda:defaultdict(float))
for p in pol:
    sup=pos[p['POID']]['SupplierID']; a=supplier_stat[sup]; a['POLines']+=1;a['PurchaseValueNZD']+=float(p['PurchaseValueNZD'])
    if p['GoodsReceiptDate']:
        from datetime import date
        a['ReceivedLines']+=1
        a['LeadDays']+=(date.fromisoformat(p['GoodsReceiptDate'])-date.fromisoformat(pos[p['POID']]['PODate'])).days
        a['OnTimeLines']+=p['GoodsReceiptDate']<=p['PromisedReceiptDate']
supplier_rows=[]
for sup in sorted(supplier_stat):
    a=supplier_stat[sup]; ct=a['ReceivedLines']
    supplier_rows.append({'SupplierID':sup,'SupplierName':f'Fictional Supplier {int(sup[3:]):03d}',
                          'POLines':int(a['POLines']),'ReceivedLines':int(ct),
                          'AvgLeadTimeDays':r2(a['LeadDays']/ct) if ct else None,
                          'OnTimeReceiptPct':r2(100*a['OnTimeLines']/ct) if ct else None,
                          'PurchaseValueNZD':r2(a['PurchaseValueNZD'])})

wh=defaultdict(lambda:defaultdict(float))
for l in labour:
    a=wh[l['WarehouseID']];a['UnitsPicked']+=int(l['UnitsPicked']);a['LinesPicked']+=int(l['LinesPicked']);a['LabourHours']+=float(l['LabourHours'])
for c in counts:
    a=wh[c['WarehouseID']];a['StockCounts']+=1;a['AccurateCounts']+=c['SystemQuantity']==c['PhysicalQuantity']
warehouse_rows=[]
for k,a in sorted(wh.items()):
    warehouse_rows.append({'WarehouseID':k,'LinesPicked':int(a['LinesPicked']),'UnitsPicked':int(a['UnitsPicked']),
                            'LabourHours':r2(a['LabourHours']),'UnitsPerLabourHour':r2(a['UnitsPicked']/a['LabourHours']),
                            'InventoryAccuracyPct':r2(100*a['AccurateCounts']/a['StockCounts']),
                            'StockCounts':int(a['StockCounts']),'AccurateCounts':int(a['AccurateCounts'])})

carrier_stat=defaultdict(lambda:defaultdict(float))
for sh in shipments:
    a=carrier_stat[sh['CarrierID']];a['Shipments']+=1;a['FreightNZD']+=float(sh['FreightCostNZD'])
    if sh['ShipmentStatus']=='Delivered':a['Delivered']+=1;a['OnTime']+=sh['DeliveryDate']<=sh['RequiredDate']
carrier_rows=[]
for c in carriers:
    a=carrier_stat[c['CarrierID']]; ship=a['Shipments']; delivered=a['Delivered']
    carrier_rows.append({'CarrierID':c['CarrierID'],'CarrierName':c['CarrierName'],
                         'Shipments':int(ship),'Delivered':int(delivered),'FreightNZD':r2(a['FreightNZD']),
                         'CostPerShipmentNZD':r2(a['FreightNZD']/ship),
                         'OnTimePct':r2(100*a['OnTime']/delivered)})

pstat=defaultdict(lambda:defaultdict(float))
for l in lines:
    a=pstat[l['ProductID']];a['SalesNZD']+=float(l['NetSalesNZD']);a['BackorderUnits']+=int(l['QuantityBackordered']);a['OrderedUnits']+=int(l['QuantityOrdered']);a['BackorderLines']+=int(l['QuantityBackordered'])>0
for s in latest_snap:
    a=pstat[s['ProductID']];a['InventoryValueNZD']+=float(s['InventoryValueNZD']);a['ExcessUnits']+=int(s['ExcessQuantity']);a['StockoutWarehouses']+=int(s['StockoutFlag'])
    if int(s['DaysSinceMovement'])>90: a['SlowInventoryNZD']+=float(s['InventoryValueNZD'])
products_rows=[]
for key,a in pstat.items():
    products_rows.append({'ProductID':key,'Category':prod_by[key]['Category'],'SupplierID':prod_by[key]['SupplierID'],
                          'SalesNZD':r2(a['SalesNZD']),'BackorderUnits':int(a['BackorderUnits']),
                          'BackorderLines':int(a['BackorderLines']),'OrderedUnits':int(a['OrderedUnits']),
                          'InventoryValueNZD':r2(a['InventoryValueNZD']),
                          'SlowInventoryNZD':r2(a['SlowInventoryNZD']),
                          'ExcessUnits':int(a['ExcessUnits']),'StockoutWarehouses':int(a['StockoutWarehouses'])})

def csvout(name,rows):
    if not rows:return
    with (EXCEL/name).open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for nm,records in [('Monthly_Summary.csv',monthly_rows),('Region_Summary.csv',region_rows),('Supplier_Summary.csv',supplier_rows),
                   ('Warehouse_Summary.csv',warehouse_rows),('Carrier_Summary.csv',carrier_rows),('Product_Summary.csv',products_rows)]: csvout(nm,records)

insight={
'monthly':monthly_rows,'regions':region_rows,'suppliers':supplier_rows,'warehouses':warehouse_rows,
'carriers':carrier_rows,'products':products_rows,
'worst_otif_region':min(region_rows,key=lambda x:x['OTIFPct']),
'worst_product_backorder':max(products_rows,key=lambda x:x['BackorderUnits']),
'worst_warehouse_productivity':min(warehouse_rows,key=lambda x:x['UnitsPerLabourHour']),
'slowest_supplier':max(supplier_rows,key=lambda x:x['AvgLeadTimeDays'] or 0),
'most_expensive_carrier':max(carrier_rows,key=lambda x:x['CostPerShipmentNZD']),
'worst_carrier_ontime':min(carrier_rows,key=lambda x:x['OnTimePct']),
'biggest_region_backorder':max(region_rows,key=lambda x:x['BackorderUnits']),
'largest_stock_value_product':max(products_rows,key=lambda x:x['InventoryValueNZD'])}
(DOC/'analysis_summary.json').write_text(json.dumps(insight,indent=2),encoding='utf-8')
print('IMPORTANT INSIGHTS')
for k,v in insight.items():
    if not isinstance(v,list):print(k,':',v)

# previews use 6 charts sourced only from the aggregates; not claimed as real Power BI screenshots.
plt.rcParams.update({'font.size':10,'axes.titlesize':14})

def preview(name,title,subtitle,chartlist):
    fig,axs=plt.subplots(2,2,figsize=(15.5,8.3),layout='constrained'); axs=axs.flatten()
    for ax,(caption,kind,data) in zip(axs,chartlist):
        xx,yy=data
        if kind=='line':ax.plot(range(len(yy)),yy,linewidth=2);ax.set_xticks(range(0,len(xx),max(1,len(xx)//6)),[xx[z] for z in range(0,len(xx),max(1,len(xx)//6))],rotation=25)
        elif kind=='bar':ax.bar(xx,yy);ax.tick_params(axis='x',rotation=35)
        elif kind=='barh':ax.barh(xx,yy)
        else:ax.plot(xx,yy)
        ax.set_title(caption,pad=12);ax.grid(alpha=.13,axis='y');ax.spines[['top','right']].set_visible(False)
        ax.ticklabel_format(axis='y',style='plain',useOffset=False) if kind in ('line','bar') else None
    fig.suptitle(title+'  •  '+subtitle,fontsize=18,fontweight='bold')
    fig.text(.5,.002,'DATA-DRIVEN REPORT CONCEPT — NOT A POWER BI SCREENSHOT  |  Synthetic NZ distribution data  |  2024-10 to 2026-09',ha='center',fontsize=9)
    fig.savefig(SCREEN/name,dpi=135,bbox_inches='tight');plt.close(fig)

months=[m['YearMonth'] for m in monthly_rows]; sale=[m['NetSalesNZD']/1e6 for m in monthly_rows]
inv=[m['InventoryValueNZD']/1e6 for m in monthly_rows]
otif=[100*m['OTIFOrders']/m['DeliveredOrders'] for m in monthly_rows]
reg=sorted(region_rows,key=lambda x:x['NetSalesNZD'],reverse=True)
reglabels=[r['Region'] for r in reg];regsales=[r['NetSalesNZD']/1e6 for r in reg]
wareh=[x['WarehouseID'] for x in warehouse_rows]; prod=[x['UnitsPerLabourHour'] for x in warehouse_rows]
carname=[c['CarrierID'] for c in carrier_rows];carcost=[c['CostPerShipmentNZD'] for c in carrier_rows];carotp=[c['OnTimePct'] for c in carrier_rows]
top_bad=sorted(products_rows,key=lambda x:x['BackorderUnits'],reverse=True)[:8]; top_old=sorted(products_rows,key=lambda x:x['SlowInventoryNZD'],reverse=True)[:8]
sup_bad=sorted(supplier_rows,key=lambda x:x['AvgLeadTimeDays'],reverse=True)[:8]
sup_ot=sorted(supplier_rows,key=lambda x:x['OnTimeReceiptPct'])[:8]
preview('executive_dashboard_preview.png','Executive Overview','Revenue  •  OTIF  •  Inventory',[
    ('Monthly sales (NZD millions)','line',(months,sale)),('Month-end inventory (NZD millions)','line',(months,inv)),
    ('OTIF by month (%)','line',(months,otif)),('Revenue by destination region (NZD millions)','bar',(reglabels,regsales))])
preview('inventory_dashboard_preview.png','Inventory Performance','Backorders  •  Slow-moving stock  •  Stockouts',[
    ('Product backorder units (top 8)','bar',([r['ProductID'] for r in top_bad],[r['BackorderUnits'] for r in top_bad])),
    ('Slow-moving inventory proxy (NZD millions)','bar',([r['ProductID'] for r in top_old],[r['SlowInventoryNZD']/1e6 for r in top_old])),
    ('Inventory value by month (NZD millions)','line',(months,inv)),
    ('Monthly stockout snapshot share (%)','line',(months,[100*m['StockoutPoints']/m['InventoryPoints'] for m in monthly_rows]))])
preview('supplier_dashboard_preview.png','Supplier Performance','Delivery reliability  •  Lead time',[
    ('Longest supplier lead time (days)','bar',([r['SupplierID'] for r in sup_bad],[r['AvgLeadTimeDays'] for r in sup_bad])),
    ('Lowest on-time supplier receipts (%)','bar',([r['SupplierID'] for r in sup_ot],[r['OnTimeReceiptPct'] for r in sup_ot])),
    ('Purchase spend, eight highest (NZD millions)','bar',([r['SupplierID'] for r in sorted(supplier_rows,key=lambda z:z['PurchaseValueNZD'],reverse=True)[:8]],
        [r['PurchaseValueNZD']/1e6 for r in sorted(supplier_rows,key=lambda z:z['PurchaseValueNZD'],reverse=True)[:8]])),
    ('Warehouse units picked per labour hour','bar',(wareh,prod))])
preview('warehouse_dashboard_preview.png','Warehouse Performance','Picking throughput  •  Labour  •  Stock count accuracy',[
    ('Units picked per labour hour','bar',(wareh,prod)),
    ('Units picked (thousands)','bar',(wareh,[r['UnitsPicked']/1000 for r in warehouse_rows])),
    ('Stock count accuracy (%)','bar',(wareh,[r['InventoryAccuracyPct'] for r in warehouse_rows])),
    ('Labour hours (thousands)','bar',(wareh,[r['LabourHours']/1000 for r in warehouse_rows]))])
preview('transportation_dashboard_preview.png','Transportation Performance','Cost  •  Carrier service  •  Regional throughput',[
    ('Freight cost per shipment (NZD)','bar',(carname,carcost)),
    ('Carrier on-time deliveries (%)','bar',(carname,carotp)),
    ('Freight spend by dispatch month (NZD thousands)','line',(months,[m['FreightNZD']/1000 for m in monthly_rows])),
    ('Sales by region (NZD millions)','bar',(reglabels,regsales))])
preview('customer_orders_dashboard_preview.png','Customer & Order Performance','Revenue  •  Backorders  •  OTIF',[
    ('Revenue by region (NZD millions)','bar',(reglabels,regsales)),
    ('Backorder quantity by region','bar',(reglabels,[r['BackorderUnits'] for r in reg])),
    ('OTIF by region (%)','bar',(reglabels,[r['OTIFPct'] for r in reg])),
    ('Monthly OTIF (%)','line',(months,otif))])
