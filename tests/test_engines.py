import numpy as np
import pandas as pd
import pytest
from src.data import load_demo,demand_series
from src.forecasting import features,train,predict,metrics,event_flag,METHODS
from src.inventory import periodic_quantity,constrained_order,simulate,plan
from src.reviews import analyze
from src.seasonality import festival_evidence

@pytest.fixture(scope='module')
def tables():return load_demo()

def test_required_reorder_example():assert periodic_quantity(20*11,80,20,30)==150

def test_pack_cap():
    assert constrained_order(150,6,12,1000)==150
    assert constrained_order(15,12,12,20)==12
    assert constrained_order(15,12,24,20)==0

def test_expiry_example_and_fefo():
    date=pd.Timestamp('2026-01-01');b=pd.DataFrame([dict(batch_id='a',expiry_date=date+pd.Timedelta(days=5),quantity_remaining=80,cost_price=2)])
    d,r=simulate(b,pd.DataFrame(),[6]*5,date,7)
    assert r.iloc[0].unsold_at_expiry==50
    assert r.iloc[0].sold_before_expiry==30
    b2=pd.concat([b.assign(batch_id='later',expiry_date=date+pd.Timedelta(days=9)),b],ignore_index=True)
    _,r=simulate(b2,pd.DataFrame(),[6]*5,date,7)
    assert r.set_index('batch_id').loc['later','sold_before_expiry']==0

def test_expired_unknown_never_sold():
    date=pd.Timestamp('2026-01-01');b=pd.DataFrame([dict(batch_id='a',expiry_date=date,quantity_remaining=80,cost_price=2),dict(batch_id='b',expiry_date=pd.NaT,quantity_remaining=20,cost_price=2)])
    d,r=simulate(b,pd.DataFrame(),[6]*5,date,7)
    assert d.served.sum()==0 and d.shortage.sum()==30

def test_timed_purchase_orders():
    date=pd.Timestamp('2026-01-01');b=pd.DataFrame();o=pd.DataFrame([dict(purchase_order_id='o',status='confirmed',expected_delivery_date=date+pd.Timedelta(days=3),quantity_ordered=20)])
    d,_=simulate(b,o,[5]*4,date,10)
    assert d.shortage.tolist()==[5,5,0,0]
    assert d.incoming.tolist()==[0,0,20,20]

def test_forecast_causality(tables):
    origin=tables['sales'].date.max()-pd.Timedelta(days=30);y=demand_series(tables['sales'],'P01')
    before=features(y,origin,0,tables['festivals']);y.loc[y.index>origin]=999999
    np.testing.assert_allclose(before,features(y,origin,0,tables['festivals']),equal_nan=True)
    assert np.isnan(metrics([0],[0])['wape_pct']) if metrics([0],[0])['wape_pct'] is not None else True

def test_forecast_and_inventory(tables):
    p=predict(tables,tables['sales'].date.max());r,b=plan(tables,p)
    assert p[p.product_id=='P13'].prediction.isna().all()
    assert r.set_index('product_id').loc['P13','recommended_order']==0
    assert r.set_index('product_id').loc['P09','excess_stock']>200
    assert (r.recommended_order<=r.order_cap.fillna(0)).all()
    assert b[b.status=='Expired'].sold_before_expiry.sum()==0
    changed={k:v.copy() for k,v in tables.items()};changed['products'].loc[0,'lead_time_days']=30
    r,_=plan(changed,p);assert r.iloc[0].recommended_order==0
    assert r.iloc[0].status in ['Manual horizon review','Expiry-risk review required']

def test_events_and_no_history(tables):
    dates=[tables['festivals'].festival_date.iloc[0]]
    assert event_flag(dates,tables['festivals'])[0]==1
    assert festival_evidence(tables,'P01').comparable_occurrences.max()>=2
    assert festival_evidence(tables,'P13').mean_change_pct.isna().all()

def test_review_unavailable_and_negation(tables):
    reviews=pd.DataFrame([dict(review_id='a',product_id='',review_text='Sugar-free cola is never available. Please stock it.'),dict(review_id='b',product_id='',review_text='Water is not out of stock.'),dict(review_id='c',product_id='',review_text='Do not stock this damaged chocolate box.')])
    r=analyze(reviews,tables['products']);a=r[r.review_id=='a']
    assert a.product_id.tolist()==['P13']
    assert 'Availability complaint' in a.iloc[0].intents
    assert not r[r.review_id=='b'].intents.str.contains('Availability complaint').any()
    assert not r[r.review_id=='c'].intents.str.contains('Product request').any()
