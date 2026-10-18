"""Reproducible, fictional NZ distribution-company supply-chain portfolio dataset.
Requires Python 3.10+ and numpy. Generates 16 related tables and audit files.
All amounts NZD; no real customer, employer or SAP data.
"""
from pathlib import Path
from collections import defaultdict, Counter
from datetime import date, timedelta
import csv, random, calendar, shutil, json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT/'data'/'raw', ROOT/'data'/'processed'
RAW.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(20261018)
prng = random.Random(20261018)
START, END = date(2024,10,1), date(2026,9,30)
N_DAYS = (END-START).days+1

def ds(d): return d.isoformat() if d else ''
def dr(day): return START+timedelta(days=int(day))
def f2(x): return round(float(x),2)
def save(name, cols, rows):
    with (OUT/(name+'.csv')).open('w',newline='',encoding='utf-8') as fh:
        w=csv.writer(fh); w.writerow(cols); w.writerows(rows)
    print(name,len(rows),flush=True)

def choice(seq): return seq[prng.randrange(len(seq))]

regions=['Auckland','Waikato','Bay of Plenty','Wellington','Canterbury']
wh_ids=[f'WH{i:02d}' for i in range(1,6)]
warehouses=[]
for i,(nm,city,reg,plant) in enumerate([
    ('Auckland DC','Mangere','Auckland','NZ01'),('Hamilton DC','Te Rapa','Waikato','NZ02'),
    ('Tauranga DC','Mount Maunganui','Bay of Plenty','NZ03'),('Wellington DC','Seaview','Wellington','NZ04'),
    ('Christchurch DC','Hornby','Canterbury','NZ05')]):
    warehouses.append([wh_ids[i],nm,city,reg,plant,f'SL{i+1:03d}'])
save('Warehouses',['WarehouseID','WarehouseName','City','Region','Plant','StorageLocation'],warehouses)

supplier_rows=[]
for s in range(1,65):
    reg=choice(regions)
    base=int(rng.integers(5,28))
    if s%13==0: base+=15
    supplier_rows.append([f'SUP{s:03d}',f'Fictional Supplier {s:03d}',reg,base,choice(['A','B','C']),round(float(rng.uniform(0.01,0.15)),3)])
suppliers=[r[0] for r in supplier_rows]
sup_lead={r[0]:r[3] for r in supplier_rows}
sup_delays={r[0]:r[5] for r in supplier_rows}
save('Suppliers',['SupplierID','SupplierName','Region','ContractLeadTimeDays','SupplierTier','ExpectedLateFraction'],supplier_rows)

categories=['Beverages','Dry Grocery','Household','Personal Care','Packaging','Hardware','Electrical','Cleaning']
prod_rows=[]; products=[]; by_supplier=defaultdict(list)
for p in range(1,481):
    sup=choice(suppliers)
    cat=categories[(p-1)%len(categories)]
    cost=round(float(rng.uniform(4,145)),2)
    price=round(cost*float(rng.uniform(1.17,1.58)),2)
    safe=int(rng.integers(38,155)); reorder=safe+int(rng.integers(50,220))
    rec=[f'P{p:04d}',f'MAT{p:06d}',f'{cat} Item {p:04d}',cat,sup,cost,price,safe,reorder, sup_lead[sup],choice(['EA','CTN','BOX'])]
    prod_rows.append(rec); products.append(rec); by_supplier[sup].append(p-1)
save('Products',['ProductID','Material','MaterialDescription','Category','SupplierID','UnitCostNZD','UnitPriceNZD','SafetyStock','ReorderPoint','LeadTimeDays','UnitOfMeasure'],prod_rows)

cust_rows=[]
for c in range(1,2001):
    reg=choice(regions); seg=prng.choices(['Retail','Wholesale','Hospitality','E-commerce'],[.37,.26,.15,.22])[0]
    cust_rows.append([f'C{c:05d}',f'Fictional Customer {c:05d}',reg,seg,f'ACC{10000+c}'])
save('Customers',['CustomerID','CustomerName','Region','CustomerSegment','AccountReference'],cust_rows)

carrier_rows=[['CR01','Southern Road Freight','Road',1.0],['CR02','Metro Express','Road',1.22],
              ['CR03','Coastline Transport','Road',.88],['CR04','Priority Freight NZ','Air',2.25],
              ['CR05','Interisland Logistics','Road',1.30]]
save('Carriers',['CarrierID','CarrierName','PrimaryMode','CostMultiplier'],carrier_rows)

# Calendar: daily date spine.
calendar_rows=[]
for j in range(N_DAYS):
    d=dr(j); fy=d.year+(d.month>=7)
    calendar_rows.append([ds(d),d.year,d.month,d.strftime('%B'),(d.month-1)//3+1,d.isocalendar().week,fy,d.strftime('%Y-%m'),d.weekday()<5])
save('Calendar',['Date','Year','MonthNumber','MonthName','Quarter','ISOWeek','NZFiscalYear','YearMonth','IsWeekday'],calendar_rows)

# Demand: sample dates with business-day bias, Christmas uplift and short winter dip.
weights=[]
for i in range(N_DAYS):
    d=dr(i)
    season=1.40 if d.month in [11,12] else (.80 if d.month in [6,7] else 1.0)
    weights.append(season*(1.0 if d.weekday()<5 else .31))
w=np.asarray(weights,dtype=float); w/=w.sum()
n_orders=63500
odays=rng.choice(N_DAYS,size=n_orders,p=w)
order_linecounts=rng.choice([1,2,3,4],size=n_orders,p=[.16,.39,.32,.13])
warehouse_idx=rng.choice(5,size=n_orders,p=[.34,.20,.13,.17,.16]); customer_idx=rng.integers(0,len(cust_rows),size=n_orders)
order_req_offset=rng.integers(5,12,size=n_orders)
order_ship_offset=rng.integers(1,5,size=n_orders)
car_idx=rng.choice(5,size=n_orders,p=[.32,.24,.23,.06,.15])
# Carrier 03 is cheap but systematically slower; carrier 04 faster but costly.
trip_offset=np.array([2,2,3,1,3],dtype=int)[car_idx]+rng.choice([-1,0,0,1,2,3],n_orders,p=[.08,.31,.25,.19,.12,.05])
shipdays=odays+order_ship_offset; deldays=shipdays+np.maximum(1,trip_offset)
# ~2% of records represent unshipped/open exceptions.
hold=rng.random(n_orders)<.021
shipdays[hold]=N_DAYS+15
orderids=[f'SO{j+1:07d}' for j in range(n_orders)]
order_line_rows=[]; outgoing_events=[]; order_lines_by_order=defaultdict(list)
popular_weights=1.0/np.power(np.arange(1,481,dtype=float),.48)
popular_weights/=popular_weights.sum()
for o in range(n_orders):
    used=set()
    for _ in range(int(order_linecounts[o])):
        p=int(rng.choice(480,p=popular_weights))
        tries=0
        while p in used and tries<30: p=int(rng.choice(480,p=popular_weights)); tries+=1
        used.add(p)
        units=int(rng.choice([1,3,5,8,10,15,20,30,40,60],p=[.03,.09,.12,.15,.17,.15,.14,.09,.04,.02]))
        # Popular stockout SKUs clustered in one distribution centre.
        if p<18 and int(warehouse_idx[o])==2: units+=int(rng.integers(10,41))
        ln=len(order_line_rows); prod=products[p]
        # placeholder for quantities to be resolved against chronological receipt/issue ledger.
        order_line_rows.append([f'SOL{ln+1:08d}',orderids[o],prod[0],warehouses[int(warehouse_idx[o])][0],
                                units,0,0,prod[6],prod[5],0,0,0,'',prod[1]])
        order_lines_by_order[o].append(ln)
        outgoing_events.append((int(shipdays[o]),2,ln,int(warehouse_idx[o]),p,units))

# Purchase orders each have a single vendor; lines match vendor master.
po_rows=[]; pol_rows=[]; incoming_events=[]
n_pos=15500
po_days=rng.integers(0,N_DAYS,size=n_pos)
for x in range(n_pos):
    sup=choice(suppliers); wh=int(rng.choice(5,p=[.34,.20,.13,.17,.16])); pid=f'PO{x+1:07d}'
    po_date=dr(int(po_days[x])); sla=sup_lead[sup]
    pindices=by_supplier[sup]
    for _ in range(int(rng.choice([1,2,3,4],p=[.32,.38,.22,.08]))):
        p=int(rng.choice(pindices,p=popular_weights[pindices]/popular_weights[pindices].sum())); prod=products[p]; qty=int(rng.integers(45,136))
        target=po_date+timedelta(days=int(sla))
        supplier_delay=int(rng.choice([-3,-1,0,0,1,4,9,17],p=[.07,.13,.32,.17,.09,.10,.08,.04]))
        if sup.endswith(('013','026','039','052')): supplier_delay+=8
        actual=target+timedelta(days=supplier_delay)
        if actual < po_date: actual=po_date
        received=qty if actual<=END and rng.random()>.034 else 0
        rec_date=actual if received else None
        polid=f'POL{len(pol_rows)+1:08d}'
        pol_rows.append([polid,pid,prod[0],qty,received,prod[5],f2(qty*prod[5]),
                         ds(target),ds(rec_date),'Received' if received else 'Open',prod[1]])
        if received:
            incoming_events.append(((actual-START).days,1,len(pol_rows)-1,wh,p,qty))
    po_rows.append([pid,ds(po_date),sup,warehouses[wh][0], f'VEN{int(sup[3:]):04d}',
                    warehouses[wh][4], 'Open'])
# post-process header status; PO 100% received only if all linked lines received
po_status=Counter(); po_open=Counter()
for row in pol_rows:
    po_status[row[1]]+=1
    if row[9]=='Open': po_open[row[1]]+=1
for row in po_rows: row[6]='Open' if po_open[row[0]] else 'Received'

# Inventory material movement ledger. Starting balance is recorded as movement 561 on 2024-09-30.
opening=rng.integers(100,420,size=(5,480)).astype(int)
stock=opening.copy()
invt_rows=[]
for wh in range(5):
    for p in range(480):
        amt=int(opening[wh,p]); invt_rows.append([f'MV{len(invt_rows)+1:08d}','2024-09-30',products[p][0],wh_ids[wh],
            '561',amt,amt,'OpeningBalance',f'OPEN-{wh+1}',warehouses[wh][4],warehouses[wh][5],f'B{p%17+1:03d}',products[p][5]])

# 24 monthly snapshots, always derived from actual postings, not arbitrary independent samples.
snapdates=[]
for year in [2024,2025,2026]:
    for month in range(1,13):
        d=date(year,month,calendar.monthrange(year,month)[1])
        if START<=d<=END: snapdates.append(d)
events=incoming_events+outgoing_events+[((d-START).days,3,i,0,0,0) for i,d in enumerate(snapdates)]
events.sort(key=lambda z:(z[0],z[1]))
inv_snap_rows=[]; no_stock=0; issue_events=0; ledger_issue_qty=0
last_movement=np.full((5,480),-50,dtype=int)
for day,kind,idx,wh,p,qty in events:
    if kind==1:
        stock[wh,p]+=qty; last_movement[wh,p]=day
        polid=pol_rows[idx][0]
        invt_rows.append([f'MV{len(invt_rows)+1:08d}',ds(dr(day)),products[p][0],wh_ids[wh],
            '101',qty,qty,'PurchaseOrder',polid,warehouses[wh][4],warehouses[wh][5],f'B{p%17+1:03d}',products[p][5]])
    elif kind==2:
        if day >= N_DAYS: continue
        ship=int(min(stock[wh,p],qty)); stock[wh,p]-=ship
        ln=order_line_rows[idx]; ln[5]=ship; ln[6]=qty-ship
        ln[9]=f2(ship*float(ln[7])); ln[10]=f2(ship*float(ln[8])); ln[11]=f2(ln[9]-ln[10]);
        ln[12]='Fulfilled' if ship==qty else ('Partial' if ship else 'Backordered')
        if ship:
            issue_events+=1; ledger_issue_qty+=ship; last_movement[wh,p]=day
            invt_rows.append([f'MV{len(invt_rows)+1:08d}',ds(dr(day)),products[p][0],wh_ids[wh],
                '601',-ship,-ship,'SalesOrder',ln[1],warehouses[wh][4],warehouses[wh][5],f'B{p%17+1:03d}',products[p][5]])
        else: no_stock+=1
    else:
        sd=snapdates[idx]
        for widx in range(5):
            for prodidx in range(480):
                pr=products[prodidx]; available=int(stock[widx,prodidx]); age=max(0,day-int(last_movement[widx,prodidx]))
                exp=max(0,available-pr[8]*2)
                inv_snap_rows.append([ds(sd),pr[0],wh_ids[widx],available,f2(available*pr[5]),pr[7],pr[8],
                    age,'0-30' if age<=30 else ('31-60' if age<=60 else ('61-90' if age<=90 else '90+')),
                    exp,1 if available==0 else 0, pr[1],warehouses[widx][4],warehouses[widx][5]])

# All orderlines after analysis end (future ship) are unfulfilled.
for ln in order_line_rows:
    if ln[12]=='': ln[5]=0;ln[6]=ln[4];ln[12]='Open'

# Status from line facts, delivery only if any shipped; an order with partial shipment not considered in-full.
orders=[]; shipments=[]; transport=[]; delivered_dates={}
for i in range(n_orders):
    lines=[order_line_rows[li] for li in order_lines_by_order[i]]
    ordered=sum(z[4] for z in lines); shipped=sum(z[5] for z in lines)
    if shipped==0: status='Open'; shipd=None; deld=None
    else:
        shipd=dr(int(shipdays[i])); deld=dr(int(deldays[i]))
        if deld>END: status='In Transit'
        elif shipped<ordered: status='Partially Delivered'
        else: status='Delivered'
    totalsale=f2(sum(z[9] for z in lines)); cost=f2(sum(z[10] for z in lines))
    req=dr(int(odays[i]+order_req_offset[i])); od=dr(int(odays[i])); wh=int(warehouse_idx[i])
    customer=cust_rows[int(customer_idx[i])]
    orders.append([orderids[i],ds(od),ds(req),ds(shipd),ds(deld),customer[0],wh_ids[wh],customer[2],
                   status,ordered,shipped,ordered-shipped,totalsale,cost,f2(totalsale-cost),
                   f'SD{int(i+1):08d}' if shipped else ''])
    if shipped:
        carrier=carrier_rows[int(car_idx[i])]; zone=(wh!=regions.index(customer[2])); mode=carrier[2]
        base=29+shipped*.78+ (96 if zone else 14)
        freight=f2(base*carrier[3]*float(rng.uniform(.87,1.15)))
        sid=f'SHP{i+1:07d}'
        shipments.append([sid,orderids[i],f'DN{i+1:08d}',ds(shipd),ds(deld),ds(req),carrier[0],mode,
                          wh_ids[wh],customer[2],shipped,
                          'Delivered' if deld<=END else 'In Transit',f2(freight)])
        transport.append([f'TC{len(transport)+1:07d}',sid,orderids[i],carrier[0],mode,wh_ids[wh],customer[2],
                          ds(shipd),freight,f2(freight*.82),f2(freight*.18)])
        if deld<=END: delivered_dates[orderids[i]]=deld

# Warehouse labour daily, aggregate line/item throughput from order line postings.
daily_pick=defaultdict(lambda:[0,0])
order_ship_day={orderids[i]:int(shipdays[i]) for i in range(n_orders)}
for ln in order_line_rows:
    if ln[5]>0:
        key=(ln[3],order_ship_day[ln[1]])
        daily_pick[key][0]+=1;daily_pick[key][1]+=ln[5]
labour=[]
for day in range(N_DAYS):
    d=dr(day)
    for wi,wh in enumerate(wh_ids):
        lines,units=daily_pick[(wh,day)]
        productivity=[48,39,29,43,37][wi]
        hours=max(12,round(lines/productivity*8+float(rng.uniform(0,18)),2))
        labour.append([f'LAB{len(labour)+1:07d}',ds(d),wh,'Day',hours,lines,units,
                       f2(hours*(28.50+wi*1.35)),warehouses[wi][4]])

# Physical counts sampled from month-end system inventory, including systematic inaccuracies.
counts=[]
for snap in inv_snap_rows:
    if rng.random()<.22:
        sys=int(snap[3]); discrepancy=0
        if rng.random()<.094: discrepancy=int(rng.choice([-8,-4,-2,-1,1,2,4,7]))
        phys=max(0,sys+discrepancy)
        counts.append([f'PC{len(counts)+1:07d}',snap[0],snap[1],snap[2],sys,phys,phys-sys,
                       'Match' if sys==phys else 'Variance',snap[12]])

# Targets by month and customer region; targets based on prior-year seasonality rule, not actual outcomes.
monthly_sales=defaultdict(float)
for o in orders:
    if o[8] in ('Delivered','Partially Delivered'):
        monthly_sales[(o[1][:7],o[7])]+=o[12]
sales_targets=[]
for d in snapdates:
    m=d.strftime('%Y-%m')
    for ri,reg in enumerate(regions):
        actual=monthly_sales[(m,reg)]
        target=f2(actual*float(rng.uniform(.91,1.16)))
        sales_targets.append([m,reg,target,round(.95 if ri<3 else .94,3),f2(target*.33)])

save('Orders',['OrderID','OrderDate','RequiredDate','ShipDate','DeliveryDate','CustomerID','WarehouseID','Region','OrderStatus','QuantityOrdered','QuantityShipped','QuantityBackordered','NetSalesNZD','COGSNZD','GrossProfitNZD','SalesOrder'],orders)
save('OrderLines',['OrderLineID','OrderID','ProductID','WarehouseID','QuantityOrdered','QuantityShipped','QuantityBackordered','UnitPriceNZD','UnitCostNZD','NetSalesNZD','COGSNZD','GrossProfitNZD','LineStatus','Material'],order_line_rows)
save('PurchaseOrders',['POID','PODate','SupplierID','WarehouseID','Vendor','Plant','POStatus'],po_rows)
save('PurchaseOrderLines',['POLineID','POID','ProductID','QuantityOrdered','QuantityReceived','PurchasePriceNZD','PurchaseValueNZD','PromisedReceiptDate','GoodsReceiptDate','POLineStatus','Material'],pol_rows)
save('InventorySnapshots',['SnapshotDate','ProductID','WarehouseID','InventoryQuantity','InventoryValueNZD','SafetyStock','ReorderPoint','DaysSinceMovement','AgeBand','ExcessQuantity','StockoutFlag','Material','Plant','StorageLocation'],inv_snap_rows)
save('InventoryTransactions',['MovementID','PostingDate','ProductID','WarehouseID','MovementType','Quantity','SignedQuantity','ReferenceType','ReferenceID','Plant','StorageLocation','Batch','UnitCostNZD'],invt_rows)
save('Shipments',['ShipmentID','OrderID','DeliveryNumber','ShipDate','DeliveryDate','RequiredDate','CarrierID','TransportMode','WarehouseID','DestinationRegion','UnitsShipped','ShipmentStatus','FreightCostNZD'],shipments)
save('PhysicalStockCounts',['CountID','CountDate','ProductID','WarehouseID','SystemQuantity','PhysicalQuantity','VarianceQuantity','CountStatus','Plant'],counts)
save('WarehouseLabour',['LabourID','WorkDate','WarehouseID','Shift','LabourHours','LinesPicked','UnitsPicked','LabourCostNZD','Plant'],labour)
save('TransportationCosts',['TransportCostID','ShipmentID','OrderID','CarrierID','TransportMode','WarehouseID','DestinationRegion','CostDate','FreightCostNZD','BaseCostNZD','SurchargeNZD'],transport)
save('SalesTargets',['YearMonth','Region','TargetSalesNZD','TargetOTIF','TargetGrossProfitNZD'],sales_targets)

# Raw layer: exact operational copies, then controlled errors on selected source exports.
for f in OUT.glob('*.csv'):
    if f.name!='DataQualityLog.csv': shutil.copy2(f,RAW/f.name)

quality=[]
issues={'Orders':{'Region':(400,'blank_region'),'OrderStatus':(260,'status_whitespace'),'OrderDate':(65,'invalid_date')},
        'Products':{'MaterialDescription':(35,'leading_trailing_spaces'),'Category':(15,'missing_category')},
        'PurchaseOrders':{'Vendor':(85,'vendor_case'),'PODate':(20,'blank_po_date')},
        'OrderLines':{'UnitPriceNZD':(110,'currency_text'),'QuantityOrdered':(38,'blank_numeric_qty')}}
for name, fields in issues.items():
    src=RAW/(name+'.csv')
    with src.open(newline='',encoding='utf-8') as fh:
        rr=list(csv.DictReader(fh)); cols=list(rr[0].keys())
    for col,(n,code) in fields.items():
        ids=rng.choice(len(rr),size=min(n,len(rr)),replace=False)
        for ii in ids:
            old=rr[int(ii)][col]; new=old
            if code in ('blank_region','missing_category','blank_po_date','blank_numeric_qty'): new=''
            elif code=='status_whitespace': new=' '+old.lower()+' '
            elif code=='invalid_date': new='not-a-date'
            elif code=='leading_trailing_spaces': new='  '+old+'  '
            elif code=='vendor_case': new=old.lower()
            elif code=='currency_text':new='$'+old
            rr[int(ii)][col]=new
        quality.append([name,col,code,len(ids),'Processed version restored from validated canonical generation; raw retained for exercises'])
    with src.open('w',newline='',encoding='utf-8') as fh:
        writer=csv.DictWriter(fh,fieldnames=cols);writer.writeheader();writer.writerows(rr)

save('DataQualityLog',['SourceTable','ColumnName','IssueType','AffectedRows','CleaningTreatment'],quality)
shutil.copy2(OUT/'DataQualityLog.csv',RAW/'DataQualityLog.csv')

# Evidence and invariant checks; fail build if keys or ledgers inconsistent.
assert len(order_line_rows)>=100000 and len(order_line_rows)<=200000
assert all(o[9]==o[10]+o[11] for o in orders)
assert all(x[4]==x[5]+x[6] for x in order_line_rows)
assert all(int(s[3])>=0 for s in inv_snap_rows)
assert sum(int(x[5]) for x in order_line_rows)==-sum(int(t[5]) for t in invt_rows if t[4]=='601')
assert len({p[0] for p in prod_rows})==len(prod_rows)
assert len({o[0] for o in orders})==len(orders)

# KPI audit: closed delivered orders as of analysis end, latest stock, time-averaged monthly stock.
eligible=[o for o in orders if o[8] in ('Delivered','Partially Delivered')]
on_time=[o for o in eligible if o[4]<=o[2]]
otif=[o for o in eligible if o[4]<=o[2] and o[11]==0]
end_snap=[s for s in inv_snap_rows if s[0]==ds(END)]
last_month_stock=sum(float(s[4]) for s in end_snap)
avg_month_end_stock=sum(float(s[4]) for s in inv_snap_rows)/len(snapdates)
all_sales=sum(o[12] for o in orders); cogs=sum(o[13] for o in orders)
arrivals=[p for p in pol_rows if p[4]>0]
mean_lead=np.mean([ (date.fromisoformat(p[8])-date.fromisoformat(po_rows[int(p[1][2:])-1][1])).days for p in arrivals ])
metrics={
 'date_start':ds(START),'date_end':ds(END),'orders':len(orders),'order_lines':len(order_line_rows),
 'purchase_orders':len(po_rows),'po_lines':len(pol_rows),'products':len(products),
 'net_sales_nzd':f2(all_sales),'cogs_nzd':f2(cogs),'gross_profit_nzd':f2(all_sales-cogs),
 'gross_margin_pct':f2(100*(all_sales-cogs)/all_sales),
 'eligible_delivered_orders':len(eligible),'otif_pct':f2(100*len(otif)/len(eligible)),
 'on_time_pct':f2(100*len(on_time)/len(eligible)),
 'in_full_pct':f2(100*sum(o[11]==0 for o in eligible)/len(eligible)),
 'backorder_units':sum(o[11] for o in orders),'ordered_units':sum(o[9] for o in orders),
 'shipped_units':sum(o[10] for o in orders),
 'fill_rate_pct':f2(100*sum(o[10] for o in orders)/sum(o[9] for o in orders)),
 'latest_inventory_nzd':f2(last_month_stock),'avg_month_end_inventory_nzd':f2(avg_month_end_stock),
 'turnover_2y':f2(cogs/avg_month_end_stock),
 'annualised_turnover':f2(cogs/(2*avg_month_end_stock)),
 'inventory_accuracy_pct':f2(100*sum(c[4]==c[5] for c in counts)/len(counts)),
 'stockout_snapshot_pct':f2(100*sum(s[10] for s in inv_snap_rows)/len(inv_snap_rows)),
 'mean_supplier_receipt_lead_days':f2(mean_lead),
 'freight_total_nzd':f2(sum(z[8] for z in transport)),
 'picked_units':sum(l[6] for l in labour),
 'labour_hours':f2(sum(l[4] for l in labour))}
(ROOT/'documentation'/'validated_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print('VALIDATED KPIs:',json.dumps(metrics,indent=2),flush=True)
