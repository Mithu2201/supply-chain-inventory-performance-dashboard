"""Professional teaching workbook using artifact_tool (not openpyxl/pandas).
Full-sized processed CSV files remain separate to keep Excel snappy.
"""
from pathlib import Path
import csv
from artifact_tool import Workbook, SpreadsheetFile
R=Path(__file__).resolve().parents[1]
E=R/'excel'; D=R/'data'/'processed'

def load(fp,n=None):
    with fp.open(encoding='utf-8',newline='') as f:
        rr=csv.reader(f); head=next(rr); data=[]
        for row in rr:
            data.append([convert(x) for x in row])
            if n and len(data)>=n:break
    return head,data

def convert(x):
    if x=='':return None
    # Preserve identifier strings, and ISO dates/YearMonth as text.
    try:
        if not x.startswith('0') or x=='0':
            if x.lower() in ('true','false'):return x.lower()=='true'
            if '.' in x:return float(x)
            return int(x)
    except (ValueError,TypeError):pass
    return x

wb=Workbook.create()
navy='#172842'; teal='#087E8B'; pale='#D7EEF1'; gray='#EDF2F7'; white='#FFFFFF'
style={'fill':navy,'font':{'bold':True,'color':white},'row_height':27,'vertical_alignment':'center'}

def sheet_csv(title,filename,n=None):
    head, data=load(E/filename,n)
    ws=wb.worksheets.add(title)
    ws.get_range_by_indexes(0,0,1,len(head)).values=[head]
    if data:
        # bulk blocks to reduce API round-trips
        step=350
        for start in range(0,len(data),step):
            block=data[start:start+step]
            ws.get_range_by_indexes(start+1,0,len(block),len(head)).values=block
    last=len(data)+1
    ws.get_range_by_indexes(0,0,1,len(head)).format=style
    ws.freeze_panes.freeze_rows(1)
    ws.get_range_by_indexes(0,0,last,1).format.column_width=21
    if len(head)>1:ws.get_range_by_indexes(0,1,last,len(head)-1).format.column_width=18
    # create Excel table for filter dropdowns, formulas and PivotTable source
    ws.tables.add(f'A1:{colletter(len(head))}{last}',True,title.replace('_','')+'Table')
    return ws,head,data

def colletter(n):
    a=''
    while n:
        n,m=divmod(n-1,26);a=chr(65+m)+a
    return a

intro=wb.worksheets.add('START_HERE')
intro.get_range('A1:H2').format={'fill':navy,'font':{'color':white,'bold':True,'size':17},'row_height':30}
intro.get_range('A1').values=[['END-TO-END SUPPLY CHAIN | EXCEL PERFORMANCE LAB']]
intro.get_range('A4:B13').values=[
['Purpose','NZ logistics + inventory analyst portfolio'],
['Scenario','Fictional distribution company — all figures synthetic'],
['Period','2024-10-01 to 2026-09-30'],
['Order lines','153,503 across five regional warehouses'],
['Full dataset','See ../data/raw and ../data/processed CSV files'],
['Where to start','Excel_Analysis > monthly trends > product and supplier drill-down'],
['Power Query','Excel Data > Get Data > From Text/CSV: import RAW files'],
['PivotTable','Select any tabular sheet > Insert > PivotTable'],
['Pivot slicers','Select a PivotTable > PivotTable Analyze > Insert Slicer'],
['Important','Dashboard build and screenshots are design previews; not a .pbix file']]
intro.get_range('A4:A13').format={'fill':pale,'font':{'bold':True}}
intro.get_range('A1:A25').format.column_width=27
intro.get_range('B1:B25').format.column_width=80
intro.get_range('A16:B22').values=[
['EXCEL SKILLS CHECKLIST',''],
['Tables, filters, sort','Use any preformatted source table'],
['SUMIFS / COUNTIFS','Practice on Exercise_Lookups and Orders_Sample'],
['VLOOKUP / INDEX MATCH','Exercise_Lookups columns F and G'],
['PivotTable / PivotChart','Build from Region_Summary and Product_Summary'],
['Slicers','Create a PivotTable from Product_Summary then Insert Slicer > Category'],
['Power Query cleanup','Use data/raw; fix invalid dates, currency text, spaces and blanks']]
intro.get_range('A16:B16').format={'fill':teal,'font':{'color':white,'bold':True}}

m,_,monthly=sheet_csv('Monthly_Summary','Monthly_Summary.csv')
r,_,_=sheet_csv('Region_Summary','Region_Summary.csv')
s,_,_=sheet_csv('Supplier_Summary','Supplier_Summary.csv')
w,_,_=sheet_csv('Warehouse_Summary','Warehouse_Summary.csv')
c,_,_=sheet_csv('Carrier_Summary','Carrier_Summary.csv')
p,_,_=sheet_csv('Product_Summary','Product_Summary.csv')
ph,prs=load(D/'Products.csv')
prod=wb.worksheets.add('Product_Dim')
prod.get_range_by_indexes(0,0,1,5).values=[ph[:5]]
prod.get_range_by_indexes(1,0,len(prs),5).values=[row[:5] for row in prs]
prod.get_range('A1:E1').format=style
prod.tables.add('A1:E481',True,'ProductDimensionTable')
prod.freeze_panes.freeze_rows(1)
prod.get_range('A:A').format.column_width=16
prod.get_range('B:B').format.column_width=17
prod.get_range('C:C').format.column_width=31
prod.get_range('D:E').format.column_width=18

# Realistic order sample, separate from full aggregate calculations.
osh,ordr=load(D/'Orders.csv',n=450)
cols=['OrderID','OrderDate','RequiredDate','DeliveryDate','Region','OrderStatus','QtyOrdered','QtyShipped','BackorderQty','NetSalesNZD','COGSNZD','LeadDays','OTIFFlag']
ordidx={h:i for i,h in enumerate(osh)}
orderssample=[]
for x in ordr:
    orderssample.append([x[ordidx[cc]] for cc in ['OrderID','OrderDate','RequiredDate','DeliveryDate','Region','OrderStatus','QuantityOrdered','QuantityShipped','QuantityBackordered','NetSalesNZD','COGSNZD']]+[None,None])
so=wb.worksheets.add('Orders_Sample')
so.get_range('A1:M1').values=[cols]
so.get_range('A2:K451').values=[q[:11] for q in orderssample]
so.get_range('L2').formulas=[['=IFERROR(DATEVALUE(D2)-DATEVALUE(B2),"")']]
so.get_range('L2:L451').fill_down()
so.get_range('M2').formulas=[['=IFERROR(IF(AND(DATEVALUE(D2)<=DATEVALUE(C2),I2=0),1,0),0)']]
so.get_range('M2:M451').fill_down()
so.get_range('A1:M1').format=style
so.tables.add('A1:M451',True,'OrdersSampleTable')
so.freeze_panes.freeze_rows(1)
so.get_range('A:M').format.column_width=16
so.get_range('J:K').format.column_width=19
so.get_range('L:M').format.column_width=14
so.get_range('I2:I451').conditional_formats.add_data_bar({'color':'accent5','gradient':True})

lhead,ldata=load(D/'OrderLines.csv',n=300)
look=wb.worksheets.add('Exercise_Lookups')
look.get_range('A1:I1').values=[['ProductID','OrderedQty','ShippedQty','UnitPriceNZD','NetSalesNZD',
                                 'Category_VLOOKUP','Category_INDEXMATCH','SalesRecalc','VarianceNZD']]
li={h:i for i,h in enumerate(lhead)}
look.get_range('A2:E301').values=[ [row[li[t]] for t in ['ProductID','QuantityOrdered','QuantityShipped','UnitPriceNZD','NetSalesNZD']] for row in ldata]
look.get_range('F2').formulas=[['=IFERROR(VLOOKUP(A2,Product_Dim!$A$2:$D$481,4,FALSE),"Missing")']]
look.get_range('G2').formulas=[['=IFERROR(INDEX(Product_Dim!$D$2:$D$481,MATCH(A2,Product_Dim!$A$2:$A$481,0)),"Missing")']]
look.get_range('H2').formulas=[['=C2*D2']]
look.get_range('I2').formulas=[['=E2-H2']]
for cc in 'FGHI':look.get_range(f'{cc}2:{cc}301').fill_down()
look.get_range('A1:I1').format=style
look.tables.add('A1:I301',True,'LookupExerciseTable')
look.get_range('A:I').format.column_width=20
look.freeze_panes.freeze_rows(1)
look.get_range('I2:I301').conditional_formats.add_cell_is({'operator':'notEqual','formula':0,'format':{'fill':'#FBE3E1'}})

tg,targets=load(D/'SalesTargets.csv')
t=wb.worksheets.add('Sales_Targets')
t.get_range('A1:E1').values=[tg]
t.get_range('A2:E121').values=targets
t.get_range('A1:E1').format=style
t.tables.add('A1:E121',True,'MonthlyRegionTargetTable')
t.get_range('A:E').format.column_width=23

# KPI formulas are intentionally linked to summary sheets, not copied static results.
a=wb.worksheets.add('Excel_Analysis')
a.get_range('A1:H2').format={'fill':navy,'font':{'color':white,'bold':True,'size':15},'row_height':27}
a.get_range('A1').values=[['EXECUTIVE SCORECARD | TWO-YEAR DISTRIBUTION OPERATIONS']]
a.get_range('A4:B4').values=[['CORE KPI','VALUE']]
a.get_range('A4:B4').format={'fill':teal,'font':{'color':white,'bold':True},'row_height':23}
labels=['Net sales (NZD)','Gross profit (NZD)','Gross profit margin','Latest inventory (NZD)',
        'Annualised inventory turnover','Days inventory outstanding (days)','OTIF (delivered orders)',
        'Stockout: monthly stock points','Backordered units','Freight cost (NZD)',
        'Warehouse units/labour hour','Physical inventory accuracy','Supplier actual lead time (days)',
        'Supplier on-time receipt rate','Fill rate (ordered units)','Cost per shipped order (NZD)']
a.get_range('A5:A20').values=[[x] for x in labels]
formulas=[
'=SUM(Monthly_Summary!B2:B25)',
'=SUM(Monthly_Summary!C2:C25)',
'=IFERROR(B6/B5,0)',
'=INDEX(Monthly_Summary!J2:J25,ROWS(Monthly_Summary!J2:J25))',
'=IFERROR(SUM(Monthly_Summary!D2:D25)/2/AVERAGE(Monthly_Summary!J2:J25),0)',
'=IFERROR(365/B9,0)',
'=IFERROR(SUM(Monthly_Summary!G2:G25)/SUM(Monthly_Summary!F2:F25),0)',
'=IFERROR(SUM(Monthly_Summary!K2:K25)/SUM(Monthly_Summary!L2:L25),0)',
'=SUM(Monthly_Summary!I2:I25)',
'=SUM(Monthly_Summary!M2:M25)',
'=IFERROR(SUM(Warehouse_Summary!C2:C6)/SUM(Warehouse_Summary!D2:D6),0)',
'=IFERROR(SUM(Warehouse_Summary!H2:H6)/SUM(Warehouse_Summary!G2:G6),0)',
'=IFERROR(SUMPRODUCT(Supplier_Summary!E2:E65,Supplier_Summary!D2:D65)/SUM(Supplier_Summary!D2:D65),0)',
'=IFERROR(SUMPRODUCT(Supplier_Summary!F2:F65,Supplier_Summary!D2:D65)/SUM(Supplier_Summary!D2:D65)/100,0)',
'=IFERROR(SUM(Monthly_Summary!H2:H25)/(SUM(Monthly_Summary!H2:H25)+SUM(Monthly_Summary!I2:I25)),0)',
'=IFERROR(SUM(Carrier_Summary!E2:E6)/SUM(Carrier_Summary!C2:C6),0)'
]
a.get_range('B5:B20').formulas=[[v] for v in formulas]
a.get_range('A5:A20').format={'fill':gray}
a.get_range('A:A').format.column_width=39
#a summary chart with date and sales series from monthly source is anchored to empty columns.
a.get_range('B:B').format.column_width=24
a.get_range('C:M').format.column_width=14
for row in [7,11,12,16,18,19]:a.get_range(f'B{row}').set_number_format('0.0%')
for row in [5,6,8,14,20]:a.get_range(f'B{row}').set_number_format('"$"#,##0.00')
for row in [9,10,15,17]:a.get_range(f'B{row}').set_number_format('0.00')
a.get_range('B13').set_number_format('#,##0')
a.get_range('A22:B25').values=[['Important definitions',''],
                                  ['OTIF denominator','Delivered/partially delivered, excluding in-transit/open'],
                                  ['Inventory turn','Annualised: 2-year COGS/2 divided by 24 monthly closing values'],
                                  ['Ageing method','Days since last SKU/warehouse movement; not FIFO lot age']]
a.get_range('A22:B22').format={'fill':teal,'font':{'color':white,'bold':True}}
# Charts with real aggregation. Two individual charts, no overlapping cells.
try:
    chart=a.charts.add('line',{'title':'Monthly revenue (NZD)','has_legend':False})
    ser=chart.series.add('Monthly revenue')
    ser.category_formula="'Monthly_Summary'!$A$2:$A$25"
    ser.formula="'Monthly_Summary'!$B$2:$B$25"
    chart.set_position('D4','M16')
    ch2=a.charts.add('line',{'title':'Month-end inventory value (NZD)','has_legend':False})
    ss=ch2.series.add('Inventory value')
    ss.category_formula="'Monthly_Summary'!$A$2:$A$25"
    ss.formula="'Monthly_Summary'!$J$2:$J$25"
    ch2.set_position('D18','M30')
except Exception as e:
    print('CHART_NOTICE',str(e))

# Formula guide on a dedicated worksheet.
g=wb.worksheets.add('Excel_Methods')
examples=[
['Technique','Example formula / action','Why it matters'],
['SUMIFS',"=SUMIFS(Orders_Sample!$J$2:$J$451,Orders_Sample!$E$2:$E$451,\"Auckland\")",'Sum sample orders in Auckland'],
['COUNTIFS',"=COUNTIFS(Orders_Sample!$E$2:$E$451,\"Auckland\",Orders_Sample!$I$2:$I$451,\">0\")",'Count sample orders with backorders'],
['IF / IFERROR','=IFERROR(IF(I2>0,"Review","OK"),"Check")','Treat blanks or errors gracefully'],
['VLOOKUP',"=VLOOKUP(A2,Product_Dim!$A$2:$D$481,4,FALSE)",'Product category mapping'],
['INDEX/MATCH',"=INDEX(Product_Dim!$D$2:$D$481,MATCH(A2,Product_Dim!$A$2:$A$481,0))",'Equivalent category lookup'],
['PivotTable','Insert > PivotTable > Product_Summary','Add Category to rows and SalesNZD to values'],
['PivotChart','PivotTable Analyze > PivotChart','Create dynamic category bar chart'],
['Slicer','PivotTable Analyze > Insert Slicer > Category','Slicer only appears after selecting a PivotTable'],
['Power Query','Data > Get Data > From Text/CSV > data/raw/Orders.csv','Trim status, replace errors, type dates'],
['Conditional format','Home > Conditional Formatting > Highlight Cell Rules','Flag stockouts or margin issues'],
['Data validation','Data > Data Validation > List > values','Control selected warehouse IDs'],
['Target lookup',"=SUMIFS(Sales_Targets!$C$2:$C$121,Sales_Targets!$A$2:$A$121,A2,Sales_Targets!$B$2:$B$121,B2)",'Month and region target'],
]
for rec in examples[1:]:
    if isinstance(rec[1],str) and rec[1].startswith('='): rec[1]="'"+rec[1]  # show example text, do not evaluate as live formula
g.get_range_by_indexes(0,0,len(examples),3).values=examples
g.get_range('A1:C1').format=style
g.get_range('A:A').format.column_width=24
g.get_range('B:B').format.column_width=91
g.get_range('C:C').format.column_width=52
g.get_range('A2:C13').format.row_height=25

# Drill-down filter worksheet (no inert select): input only illustrates data validation exercise.
f=wb.worksheets.add('Practice_Filters')
f.get_range('A1:D1').values=[['WAREHOUSE COMPARISON','WarehouseID','UnitsPerHour','Stock Accuracy']]
f.get_range('A1:D1').format=style
f.get_range('A3:A7').values=[[x] for x in ['WH01','WH02','WH03','WH04','WH05']]
f.get_range('B3').values=[['WH03']]
f.get_range('B3').data_validation={'rule':{'type':'list','values':['WH01','WH02','WH03','WH04','WH05']}}
f.get_range('C3').formulas=[['=IFERROR(INDEX(Warehouse_Summary!$E$2:$E$6,MATCH(B3,Warehouse_Summary!$A$2:$A$6,0)),0)']]
f.get_range('D3').formulas=[['=IFERROR(INDEX(Warehouse_Summary!$F$2:$F$6,MATCH(B3,Warehouse_Summary!$A$2:$A$6,0)),0)']]
f.get_range('A:D').format.column_width=26
f.get_range('B3:D3').format={'fill':pale}
f.get_range('D3').set_number_format('0.0"%"')

out=E/'Supply_Chain_Analysis.xlsx'
try:
    print('INSPECT',wb.inspect({'kind':'table','range':'Excel_Analysis!A4:B12','include':'values,formulas','table_max_rows':10,'table_max_cols':2}).ndjson[:3000])
except Exception as e:print('INSPECT_NOTICE',str(e))
SpreadsheetFile.export_xlsx(wb).save(str(out))
print('EXCEL_SAVED',out,out.stat().st_size)
