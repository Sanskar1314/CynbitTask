"""Validated six-table snapshots and explicit local SQLite persistence."""
from __future__ import annotations
from pathlib import Path
import io
import re
import sqlite3
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SCHEMAS={
'products':['product_id','product_name','category','selling_price','cost_price','supplier_id','lead_time_days','minimum_order_quantity','pack_size','shelf_life_days','max_stock','backorders','aliases'],
'sales':['date','product_id','quantity_sold','unit_price'],
'batches':['batch_id','product_id','manufacturing_date','expiry_date','quantity_remaining','cost_price','supplier_id'],
'purchase_orders':['purchase_order_id','product_id','quantity_ordered','order_date','expected_delivery_date','status'],
'reviews':['review_id','date','rating','review_text','product_id'],
'festivals':['festival_name','festival_date','region','calendar_source']}
NUMERIC={'products':['selling_price','cost_price','lead_time_days','minimum_order_quantity','pack_size','shelf_life_days','max_stock','backorders'],
'sales':['quantity_sold','unit_price'],'batches':['quantity_remaining','cost_price'],'purchase_orders':['quantity_ordered'],'reviews':['rating'],'festivals':[]}
DATES={'sales':['date'],'batches':['manufacturing_date','expiry_date'],'purchase_orders':['order_date','expected_delivery_date'],'reviews':['date'],'festivals':['festival_date']}


def read_csv(raw:bytes)->pd.DataFrame:
    if len(raw)>10_000_000:raise ValueError('Each CSV must be at most 10 MB.')
    try:return pd.read_csv(io.BytesIO(raw),dtype=str,keep_default_na=False,encoding='utf-8-sig')
    except (ValueError,UnicodeError,pd.errors.ParserError,pd.errors.EmptyDataError) as exc:raise ValueError('Expected a valid UTF-8 CSV with headers.') from exc


def validate(tables:dict[str,pd.DataFrame])->dict[str,pd.DataFrame]:
    """Atomic validation: never merge only part of an invalid upload."""
    if set(tables)!=set(SCHEMAS):raise ValueError('Provide all six related tables.')
    result={}
    for name,columns in SCHEMAS.items():
        f=tables[name].copy()
        if not set(columns)<=set(f.columns):raise ValueError(f'{name}: required columns: {", ".join(columns)}')
        if len(f)>100000:raise ValueError(f'{name}: maximum 100,000 rows.')
        if name in ['products','sales'] and f.empty:raise ValueError(f'{name} cannot be empty.')
        for col in f.select_dtypes(include=['object','string']).columns:
            f[col]=f[col].fillna('').astype(str).str.strip()
            if f[col].str.len().gt(5000).any():raise ValueError(f'{name}.{col}: value too long.')
        numeric=NUMERIC[name]+([x for x in ['available_stock','opening_stock','received_units','closing_stock','stockout','promotion','simulated_demand','prior_stock_writeoff'] if x in f] if name=='sales' else [])
        for col in numeric:
            f[col]=pd.to_numeric(f[col],errors='coerce')
            if not np.isfinite(f[col]).all() or f[col].lt(0).any():raise ValueError(f'{name}.{col}: finite nonnegative numbers required.')
        for col in DATES.get(name,[]):
            values=f[col].fillna('').astype(str)
            optional=name=='batches'
            missing=values.eq('')|values.eq('NaT')
            active=values[~missing]
            if (not optional and missing.any()) or not active.str.fullmatch(r'\d{4}-\d{2}-\d{2}').all():raise ValueError(f'{name}.{col}: use YYYY-MM-DD; only batch dates may be unknown.')
            parsed=pd.to_datetime(active,format='%Y-%m-%d',errors='coerce')
            if parsed.isna().any():raise ValueError(f'{name}.{col}: invalid calendar date.')
            f[col]=pd.to_datetime(values.mask(missing),errors='coerce')
        keys={'products':['product_id'],'sales':['date','product_id'],'batches':['batch_id'],'purchase_orders':['purchase_order_id'],'reviews':['review_id'],'festivals':['festival_name','festival_date','region']}[name]
        if f[keys].isna().any().any() or (f[keys].astype(str)=='').any().any() or f.duplicated(keys).any():raise ValueError(f'{name}: blank or duplicate record key.')
        result[name]=f
    p=result['products'];ids=set(p.product_id)
    if len(p)>100:raise ValueError('Prototype supports at most 100 products.')
    for col in ['lead_time_days','minimum_order_quantity','pack_size','shelf_life_days','max_stock','backorders']:
        if (p[col]%1!=0).any():raise ValueError(f'products.{col}: whole units/days required.')
    if p.pack_size.le(0).any() or p.shelf_life_days.le(0).any():raise ValueError('Pack size and receipt shelf life must be positive.')
    if p.lead_time_days.gt(30).any():raise ValueError('Lead time exceeds the 30-day prototype forecast horizon.')
    for name in ['sales','batches','purchase_orders','reviews']:
        f=result[name];unknown=set(f.product_id)-ids-({''} if name=='reviews' else set())
        if unknown:raise ValueError(f'{name}: unknown product IDs {sorted(unknown)}')
    s=result['sales'];as_of=s.date.max()
    if (as_of-s.date.min()).days>2000:raise ValueError('History exceeds the 2000-day prototype limit.')
    if 'stockout' in s and not s.stockout.isin([0,1]).all():raise ValueError('stockout must be 0 or 1.')
    if 'available_stock' in s and s.quantity_sold.gt(s.available_stock).any():raise ValueError('Sales exceed recorded availability.')
    if {'opening_stock','received_units','available_stock','closing_stock'}<=set(s):
        if not np.allclose(s.opening_stock+s.received_units,s.available_stock) or not np.allclose(s.available_stock-s.quantity_sold,s.closing_stock):raise ValueError('Historical stock ledger does not balance.')
    b=result['batches']
    if (b.manufacturing_date.notna()&b.expiry_date.notna()&(b.manufacturing_date>b.expiry_date)).any():raise ValueError('Batch manufacturing date is after expiry.')
    if b.manufacturing_date.gt(as_of).any():raise ValueError('On-hand batch cannot be manufactured after the snapshot date.')
    o=result['purchase_orders']
    if not o.status.isin(['confirmed','draft','received','cancelled']).all():raise ValueError('Unknown purchase-order status.')
    if (o.expected_delivery_date<o.order_date).any() or o.order_date.gt(as_of).any():raise ValueError('Invalid purchase-order date sequence.')
    if not result['reviews'].rating.between(1,5).all():raise ValueError('Review ratings must be between 1 and 5.')
    if result['reviews'].review_text.eq('').any():raise ValueError('Review text cannot be blank.')
    return result


def load_demo():return validate({name:read_csv((ROOT/'data/sample'/f'{name}.csv').read_bytes()) for name in SCHEMAS})


def serializable(frame):
    f=frame.copy()
    for col in f.select_dtypes(include=['datetime']).columns:f[col]=f[col].dt.strftime('%Y-%m-%d').fillna('')
    return f


def safe_csv(frame):
    f=serializable(frame).map(lambda x:"'"+x if isinstance(x,str) and x.lstrip().startswith(('=','+','-','@')) else x)
    return f.to_csv(index=False).encode()


def save_snapshot(tables,path):
    """Explicit save only, atomic replacement of a local DB; no user-chosen SQL names."""
    tables=validate({k:serializable(v) for k,v in tables.items()})
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix('.tmp')
    try:
        with sqlite3.connect(temp) as conn:
            for name,frame in tables.items():serializable(frame).to_sql(name,conn,index=False,if_exists='replace')
        temp.replace(path)
    finally:
        if temp.exists():temp.unlink()


def load_snapshot(path):
    if not Path(path).exists():raise ValueError('No saved local snapshot yet.')
    with sqlite3.connect(path) as conn:
        frames={name:pd.read_sql_query(f'SELECT * FROM {name}',conn) for name in SCHEMAS}
    return validate(frames)


def demand_series(sales,pid):
    """Missing/censored dates remain unknown, never fabricated zero demand."""
    f=sales[sales.product_id==pid].sort_values('date').set_index('date')
    if f.empty:return pd.Series(dtype=float)
    y=f.quantity_sold.astype(float)
    censored=f.get('stockout',pd.Series(0,index=f.index)).eq(1)
    if 'available_stock' in f:censored|=f.available_stock.le(f.quantity_sold)
    return y.mask(censored).reindex(pd.date_range(y.index.min(),sales.date.max()))


def historical_summary(tables):
    rows=[];s=tables['sales'];end=s.date.max()
    for p in tables['products'].itertuples():
        f=s[s.product_id==p.product_id];y=demand_series(s,p.product_id)
        recent=y.tail(28);prior=y.iloc[-56:-28];mean=recent.mean();prev=prior.mean()
        rows.append(dict(product_id=p.product_id,product=p.product_name,total_units=float(f.quantity_sold.sum()),
          revenue=float((f.quantity_sold*f.unit_price).sum()),daily_demand=float(mean) if pd.notna(mean) else np.nan,
          weekly_demand=float(mean*7) if pd.notna(mean) else np.nan,monthly_demand=float(mean*30) if pd.notna(mean) else np.nan,
          growth_pct=100*(mean/prev-1) if pd.notna(prev) and prev>0 else np.nan,
          volatility=float(recent.std()) if recent.count()>1 else np.nan,
          observed_days=int(y.notna().sum()),unknown_days=int(y.isna().sum()),
          demand_type='No history' if y.empty else 'Intermittent' if (y.dropna()==0).mean()>.3 else 'Fast moving' if mean>=15 else 'Slow moving' if mean<3 else 'Regular'))
    return pd.DataFrame(rows)
