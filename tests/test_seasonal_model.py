import numpy as np
import pandas as pd
from src.data import load_demo
from src.calendar_data import load_holiday_snapshot
from src.seasonal_model import calendar_features,train_seasonal,SEASONAL_FEATURES,SEASONAL_METHOD
from src.forecasting import predict

def test_imported_dates_vary_and_preserve_tentative():
    f,meta=load_holiday_snapshot()
    assert len(f)==28
    assert f[f.festival_name=='Holi'].festival_date.dt.strftime('%m-%d').nunique()==4
    assert f[(f.festival_name=='Dussehra')&(f.festival_date.dt.year==2026)].festival_date.iloc[0]==pd.Timestamp('2026-10-20')
    assert f[(f.festival_name=='Eid al-Fitr')&(f.festival_date.dt.year==2027)].date_status.iloc[0]=='Tentative'
    assert meta['calendar_id']=='en.indian#holiday@group.v.calendar.google.com'

def test_calendar_feature_event_alignment_and_continuity():
    t=load_demo();dates=pd.to_datetime(['2026-11-01','2026-11-08','2026-11-09'])
    x=calendar_features(dates,t['festivals']);i=SEASONAL_FEATURES.index('pre8_Diwali')
    assert x[:,i].tolist()==[1,1,0]
    boundary=calendar_features(pd.to_datetime(['2026-01-31','2026-02-01']),t['festivals'])
    assert abs(boundary[0,1]-boundary[1,1])<.03

def test_joint_model_learns_product_specific_seasons_without_future_sales():
    t=load_demo();cutoff=pd.Timestamp('2025-12-31');model=train_seasonal(t,cutoff)
    dates=pd.to_datetime(['2026-01-12','2026-05-11']) # Mondays; no selected event nearby
    cola=model.predict_product('P01',dates,t['festivals']);tea=model.predict_product('P07',dates,t['festivals'])
    assert cola[1]>cola[0] and tea[1]<tea[0]
    changed={k:v.copy() for k,v in t.items()};changed['sales'].loc[changed['sales'].date>cutoff,'quantity_sold']=99999
    other=train_seasonal(changed,cutoff)
    np.testing.assert_allclose(cola,other.predict_product('P01',dates,t['festivals']))
    pred=predict(t,cutoff,SEASONAL_METHOD,model)
    assert pred[pred.product_id=='P13'].prediction.isna().all()
    assert pred[pred.product_id=='P01'].prediction.ge(0).all()

def test_festival_effect_learned_not_universal():
    t=load_demo();model=train_seasonal(t,t['sales'].date.max());dates=pd.date_range('2026-11-01',periods=8)
    all_events=t['festivals'];without=all_events[all_events.festival_name!='Diwali']
    sweets=model.predict_product('P10',dates,all_events)/model.predict_product('P10',dates,without)
    water=model.predict_product('P02',dates,all_events)/model.predict_product('P02',dates,without)
    assert sweets.mean()>1.2 and abs(water.mean()-1)<.3

def test_short_annual_history_falls_back_honestly():
    t=load_demo();end=t['sales'].date.max();t['sales']=t['sales'][t['sales'].date>end-pd.Timedelta(days=100)]
    model=train_seasonal(t,end);f=predict(t,end,SEASONAL_METHOD,model)
    assert f[f.product_id=='P01'].method.str.contains('annual history insufficient').all()

def test_evaluation_join_handles_new_product_without_history():
    from src.forecasting import score_predictions
    t=load_demo();f=predict(t,t['sales'].date.max()-pd.Timedelta(days=30))
    scored=score_predictions(t,f)
    assert len(scored)==390
    assert scored[scored.product_id=='P13'].actual.isna().all()
    assert scored[scored.product_id=='P01'].actual.notna().any()
