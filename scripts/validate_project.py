"""Independent CSV validation: FK integrity, arithmetic, ledger-vs-snapshot, KPIs.
Run: python scripts/validate_project.py
"""
from pathlib import Path
import csv,json
from collections import defaultdict
R=Path(__file__).resolve().parents[1];D=R/'data'/'processed'
def data(name):
    with (D/(name+'.csv')).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
products=data('Products'); customers=data('Customers'); orders=data('Orders'); lines=data('OrderLines')
warehouses=data('Warehouses'); suppliers=data('Suppliers'); po=data('PurchaseOrders'); pol=data('PurchaseOrderLines')
shots=data('InventorySnapshots'); movements=data('InventoryTransactions'); shipments=data('Shipments'); freight=data('TransportationCosts')
validation=[]
def check(name,condition):
    validation.append((name,'PASS' if condition else 'FAIL'))
    if not condition:raise AssertionError(name)
ps={r['ProductID'] for r in products};cs={r['CustomerID'] for r in customers}; ws={r['WarehouseID'] for r in warehouses};ss={r['SupplierID'] for r in suppliers}
os={r['OrderID'] for r in orders};psup={r['POID'] for r in po}; shipid={r['ShipmentID'] for r in shipments}
check('minimum realistic orderline count',100_000<=len(lines)<=200_000)
check('distinct keys',len(os)==len(orders) and len({x['OrderLineID'] for x in lines})==len(lines))
check('sales FKs',all(x['OrderID'] in os and x['ProductID'] in ps and x['WarehouseID'] in ws for x in lines))
check('master FKs',all(x['CustomerID'] in cs and x['WarehouseID'] in ws for x in orders) and all(x['SupplierID'] in ss for x in products))
check('purchasing FKs',all(x['POID'] in psup and x['ProductID'] in ps for x in pol))
check('freight FK',all(x['ShipmentID'] in shipid for x in freight))
check('orderline unit equations',all(int(x['QuantityOrdered'])==int(x['QuantityShipped'])+int(x['QuantityBackordered']) for x in lines))
check('no negative inventory snapshots',all(int(x['InventoryQuantity'])>=0 for x in shots))
check('no negative shipping',all(int(x['QuantityShipped'])>=0 for x in lines))
check('movement issue equal shipped',sum(int(x['QuantityShipped']) for x in lines)==-sum(int(x['SignedQuantity']) for x in movements if x['MovementType']=='601'))
check('shipments single order each',len(shipments)==len({x['OrderID'] for x in shipments}))
check('ship vs transportation freight',abs(sum(float(x['FreightCostNZD']) for x in shipments)-sum(float(x['FreightCostNZD']) for x in freight))<.02)
roll=defaultdict(lambda:[0,0,0,0,0])
for l in lines:
    a=roll[l['OrderID']];a[0]+=int(l['QuantityOrdered']);a[1]+=int(l['QuantityShipped']);a[2]+=int(l['QuantityBackordered']);a[3]+=float(l['NetSalesNZD']);a[4]+=float(l['COGSNZD'])
check('line totals to order header',all(roll[o['OrderID']][:3]==[int(o['QuantityOrdered']),int(o['QuantityShipped']),int(o['QuantityBackordered'])] and abs(roll[o['OrderID']][3]-float(o['NetSalesNZD']))<.02 and abs(roll[o['OrderID']][4]-float(o['COGSNZD']))<.02 for o in orders))
# Cross-period reconciliation of ALL 24 2400-point month-end closing snapshots.
bal=defaultdict(int);movements.sort(key=lambda x:x['PostingDate']); shots.sort(key=lambda x:x['SnapshotDate']);i=0;mismatches=0
for x in shots:
    dt=x['SnapshotDate']
    while i<len(movements) and movements[i]['PostingDate']<=dt:
        m=movements[i];bal[(m['WarehouseID'],m['ProductID'])]+=int(m['SignedQuantity']);i+=1
    if bal[(x['WarehouseID'],x['ProductID'])]!=int(x['InventoryQuantity']):mismatches+=1
check('all inventory snapshots reconcile to signed movement ledger',mismatches==0)
metric=json.loads((R/'documentation'/'validated_metrics.json').read_text())
check('sales baseline',abs(sum(float(o['NetSalesNZD']) for o in orders)-metric['net_sales_nzd'])<.1)
check('gross profit baseline',abs(sum(float(o['GrossProfitNZD']) for o in orders)-metric['gross_profit_nzd'])<.1)
check('snapshot counts',len(shots)==24*5*480)
print('Validation results:')
for name,status in validation:print(f'  {status} | {name}')
print(f'PASS: {len(validation)} checks; {len(lines):,} sales-order lines; {len(shots):,} ledger-reconciled stock points.')
