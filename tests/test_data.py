import pandas as pd
import pytest
from src.data import load_demo, validate, serializable, save_snapshot, load_snapshot, demand_series

def test_demo_and_ledger():
    t=load_demo();s=t['sales']
    assert len(s)>10000
    assert (s.quantity_sold<=s.available_stock).all()
    assert ((s.opening_stock+s.received_units-s.quantity_sold)==s.closing_stock).all()
    assert demand_series(s,'P13').empty
    assert demand_series(s,'P05').isna().any()

def test_snapshot(tmp_path):
    t=load_demo();p=tmp_path/'demo.sqlite';save_snapshot(t,p)
    assert load_snapshot(p)['sales'].equals(t['sales'])

@pytest.mark.parametrize('failure',['duplicate','negative','foreign','date','ledger'])
def test_rejects_invalid(failure):
    t={k:serializable(v) for k,v in load_demo().items()}
    if failure=='duplicate':t['products']=pd.concat([t['products'],t['products'].iloc[:1]])
    if failure=='negative':t['sales'].loc[0,'quantity_sold']=-1
    if failure=='foreign':t['batches'].loc[0,'product_id']='invalid'
    if failure=='date':t['batches'].loc[0,'expiry_date']='2026-02-30'
    if failure=='ledger':t['sales'].loc[0,'closing_stock']=9999
    with pytest.raises(ValueError):validate(t)
