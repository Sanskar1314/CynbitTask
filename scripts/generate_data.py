"""Reproducible fictional kirana store, not Cynbit/customer data."""
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.calendar_data import load_holiday_snapshot
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
AS_OF=pd.Timestamp('2026-10-16')

def generate():
    rng=np.random.default_rng(42)
    # id, name, category, price, cost, lead, MOQ, pack, remaining shelf life on receipt, base demand
    specs=[('P01','Cola 500ml','Beverages',40,28,4,12,6,120,20),
      ('P02','Bottled Water 1L','Beverages',20,12,3,12,12,180,28),
      ('P03','Mango Drink','Beverages',35,24,5,12,6,90,13),
      ('P04','Milk 500ml','Dairy',30,25,1,10,5,3,36),
      ('P05','Yogurt 100g','Dairy',25,18,2,12,6,7,6),
      ('P06','Masala Chips','Snacks',20,14,4,12,6,60,17),
      ('P07','Tea 250g','Pantry',120,90,7,6,3,180,9),
      ('P08','Coffee 100g','Pantry',150,112,7,6,3,180,5),
      ('P09','Plain Biscuits','Snacks',30,20,5,12,6,90,1.5),
      ('P10','Chocolate Box','Gifting',180,130,10,6,3,90,3),
      ('P11','Packaged Sweets','Gifting',250,180,5,6,3,15,4),
      ('P12','Rice 1kg','Essentials',65,48,12,10,5,180,16),
      ('P13','Sugar-free Cola','Beverages',45,32,5,12,6,90,0)]
    products=[]
    for pid,name,cat,price,cost,lead,moq,pack,shelf,base in specs:
        products.append(dict(product_id=pid,product_name=name,category=cat,selling_price=price,cost_price=cost,
          supplier_id='SUP-'+cat,lead_time_days=lead,minimum_order_quantity=moq,pack_size=pack,
          shelf_life_days=shelf,max_stock=1500,backorders=0,
          aliases={'P01':'cola|cold drink|soft drink','P03':'mango drink|mango drinks','P13':'sugar-free cold drink|sugar-free cold drinks|sugar free cola|sugar-free cola'}.get(pid,name.lower())))
    # Actual public calendar dates, imported through the connected Google Calendar.
    # Demand/stock remain synthetic; regenerated so event labels match simulated history.
    events, calendar_metadata = load_holiday_snapshot()
    event_dates = events.festival_date
    sales=[]
    for pid,name,cat,price,cost,lead,moq,pack,shelf,base in specs[:-1]:
        closing=0
        for date in pd.date_range('2024-01-01',AS_OF):
            summer=np.sin(2*np.pi*(date.dayofyear-30)/365.25)
            # Synthetic hot-drink scenario peaks in January, not the inverse of
            # the beverage curve (which incorrectly peaked in October).
            winter=np.cos(2*np.pi*(date.dayofyear-15)/365.25)
            season=1+.30*winter if pid in ['P07','P08'] else 1+(.45 if cat=='Beverages' else .06)*summer
            t=(date-pd.Timestamp('2024-01-01')).days
            trend=max(.2,1+(.00055 if pid=='P03' else -.00055 if pid=='P09' else .00008)*t)
            pre_event=any(0<=(d-date).days<=7 for d in event_dates)
            event_mult=1.9 if pre_event and cat=='Gifting' else 1.10 if pre_event and cat=='Snacks' else 1
            promotion=int(date.day in [5,6] and cat!='Dairy')
            mu=base*season*trend*(1.15 if date.dayofweek>=5 else 1)*event_mult*(1+.18*promotion)
            demand=int(rng.poisson(max(.1,mu)))
            # Historical supply ledger: discard carried stock for dairy explicitly as writeoff.
            opening=closing;writeoff=opening if cat=='Dairy' else 0
            opening-=writeoff
            target=int(max(5,mu*(1.4 if cat=='Dairy' else 4)))
            disruption=rng.random()<.035
            received=max(0,target-opening) if not disruption else 0
            available=opening+received
            sold=min(demand,available);closing=available-sold
            sales.append(dict(date=date.date().isoformat(),product_id=pid,quantity_sold=sold,unit_price=price,
              opening_stock=opening,received_units=received,available_stock=available,closing_stock=closing,
              prior_stock_writeoff=writeoff,stockout=int(demand>available),promotion=promotion,
              simulated_demand=demand))
    sales=pd.DataFrame(sales)
    batches=[]
    for i,p in enumerate(products[:-1]):
        pid=p['product_id'];qty=int(sales[sales.product_id==pid].iloc[-1].closing_stock)
        # Snapshot intentionally reflects the final ledger quantity. Split into FEFO batches.
        if pid=='P09': # create overstock through a recorded final-day receipt
            extra=300;sales.loc[(sales.product_id==pid)&(sales.date==str(AS_OF.date())),['received_units','available_stock','closing_stock']]+=extra;qty+=extra
        if pid=='P05':
            extra=80;sales.loc[(sales.product_id==pid)&(sales.date==str(AS_OF.date())),['received_units','available_stock','closing_stock']]+=extra;qty+=extra
        a=qty//2;b=qty-a
        for suffix,q,days in [('A',a,2 if pid=='P05' else max(1,p['shelf_life_days']//3)),('B',b,p['shelf_life_days'])]:
            batches.append(dict(batch_id=f'{pid}-{suffix}',product_id=pid,manufacturing_date=str((AS_OF-pd.Timedelta(days=7)).date()),
              expiry_date=str((AS_OF+pd.Timedelta(days=days)).date()),quantity_remaining=q,cost_price=p['cost_price'],supplier_id=p['supplier_id']))
    # Give known examples unknown/expired status without inventing dates in the application.
    batches[10]['expiry_date']=''
    batches[14]['expiry_date']=str((AS_OF-pd.Timedelta(days=1)).date())
    orders=pd.DataFrame([dict(purchase_order_id='PO01',product_id='P01',quantity_ordered=24,order_date='2026-10-14',expected_delivery_date='2026-10-19',status='confirmed'),
      dict(purchase_order_id='PO02',product_id='P12',quantity_ordered=30,order_date='2026-10-10',expected_delivery_date='2026-11-12',status='confirmed'),
      dict(purchase_order_id='PO03',product_id='P03',quantity_ordered=12,order_date='2026-10-12',expected_delivery_date='2026-10-20',status='draft')])
    texts=['I visited three times, but sugar-free cold drinks are never available.','Please keep more mango drinks during summer.',
      'Milk is out of stock every evening.','The yogurt was spoiled.','Please stock more chocolate boxes before Diwali.',
      'Tea is always available, thank you.','The biscuits taste stale.','Can you bring a new low salt snack variant?',
      'No complaints about water availability.','Coffee was unavailable yesterday.','Please keep rice in larger bags.',
      'Sugar-free cola would be useful.','The staff were friendly.','Do not stock this damaged chocolate box.']
    reviews=pd.DataFrame([dict(review_id=f'R{i+1:02}',date='2026-10-15',rating=3,review_text=t,product_id='') for i,t in enumerate(texts)])
    tables={'products':pd.DataFrame(products),'sales':sales,'batches':pd.DataFrame(batches),'purchase_orders':orders,'reviews':reviews,'festivals':events}
    out=ROOT/'data/sample';out.mkdir(parents=True,exist_ok=True)
    for name,frame in tables.items():frame.to_csv(out/f'{name}.csv',index=False)
    (out/'metadata.json').write_text(json.dumps({'synthetic':True,'seed':42,'as_of':str(AS_OF.date()),'calendar':'Public Google Calendar holiday snapshot; dates as listed, regional differences possible','calendar_imported_on':calendar_metadata['retrieved_on'],'dataset_version':'winter-calendar-v3','rows':{k:len(v) for k,v in tables.items()}},indent=2))
    return tables
if __name__=='__main__':
    print({k:len(v) for k,v in generate().items()})
