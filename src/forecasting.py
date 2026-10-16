"""Direct multi-horizon global regression; strictly origin-only demand features."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from src.data import demand_series

METHODS=('Moving average 28d','Weekly seasonal naive','HistGradientBoosting')
FEATURES=['product_index','horizon','lag1','lag7','mean7','mean28','mean84','std28','trend','unknown28','dow','month_sin','month_cos','event_next7']

def event_flag(dates,festivals):
    events=festivals.festival_date.to_numpy(dtype='datetime64[D]')
    days=np.asarray(dates,dtype='datetime64[D]')
    return ((events[None,:]-days[:,None]>=np.timedelta64(0,'D'))&(events[None,:]-days[:,None]<=np.timedelta64(7,'D'))).any(axis=1).astype(float)

def features(y,origin,pindex,festivals,horizon=30):
    past=y.loc[:origin];valid=past.dropna()
    if len(valid)<14 or past.tail(28).count()<7:return None
    recent=past.tail(28);mean=recent.mean();m7=past.tail(7).mean();m84=past.tail(84).mean()
    lag1=past.iloc[-1];lag7=past.iloc[-7] if len(past)>=7 else np.nan
    dates=pd.date_range(origin+pd.Timedelta(days=1),periods=horizon)
    rows=np.column_stack([np.full(horizon,pindex),np.arange(1,horizon+1),np.full(horizon,lag1),np.full(horizon,lag7),
      np.full(horizon,m7),np.full(horizon,mean),np.full(horizon,m84),np.full(horizon,recent.std()),
      np.full(horizon,mean-m84),np.full(horizon,recent.isna().mean()),dates.dayofweek,
      np.sin(2*np.pi*dates.month/12),np.cos(2*np.pi*dates.month/12),event_flag(dates,festivals)])
    return rows

def train(tables,cutoff):
    xs=[];ys=[];s=tables['sales'];fest=tables['festivals']
    for pi,pid in enumerate(tables['products'].product_id):
        y=demand_series(s[s.date<=cutoff],pid)
        if y.empty:continue
        for origin in pd.date_range(y.index.min()+pd.Timedelta(days=83),cutoff-pd.Timedelta(days=1),freq='7D'):
            n=min(30,(cutoff-origin).days);x=features(y,origin,pi,fest,n)
            if x is None:continue
            target=y.reindex(pd.date_range(origin+pd.Timedelta(days=1),periods=n)).to_numpy()
            keep=np.isfinite(target);xs.extend(x[keep]);ys.extend(target[keep])
    if len(ys)<100:return None
    model=HistGradientBoostingRegressor(max_iter=90,max_leaf_nodes=15,learning_rate=.08,l2_regularization=2,random_state=42,early_stopping=False,categorical_features=[0])
    model.fit(np.asarray(xs),np.asarray(ys));return model

def predict(tables,origin,method=METHODS[0],model=None,horizon=30):
    rows=[];s=tables['sales'];fest=tables['festivals']
    for pi,p in enumerate(tables['products'].itertuples()):
        y=demand_series(s[s.date<=origin],p.product_id);x=features(y,origin,pi,fest,horizon)
        supported=x is not None
        if not supported:pred=np.full(horizon,np.nan)
        elif method==METHODS[2] and model is not None:pred=np.maximum(0,model.predict(x))
        elif method==METHODS[1]:
            week=y.reindex(pd.date_range(origin-pd.Timedelta(days=6),origin)).fillna(y.tail(28).mean()).to_numpy();pred=np.resize(week,horizon)
        else:pred=np.full(horizon,y.tail(28).mean())
        confidence='Unsupported' if not supported else 'Limited' if y.tail(84).count()<56 or y.tail(28).isna().mean()>.2 else 'Historical support'
        for h,value in enumerate(pred,1):rows.append(dict(product_id=p.product_id,date=origin+pd.Timedelta(days=h),horizon=h,prediction=value,method=method if supported else 'Insufficient history',support=confidence))
    return pd.DataFrame(rows)

def metrics(actual,predicted):
    a=np.asarray(actual,float);p=np.asarray(predicted,float);valid=np.isfinite(a)&np.isfinite(p);a=a[valid];p=p[valid]
    if not len(a):return dict(n=0,mae=None,rmse=None,wape_pct=None,bias=None)
    error=p-a;denom=np.abs(a).sum()
    return dict(n=int(len(a)),mae=float(np.abs(error).mean()),rmse=float(np.sqrt((error**2).mean())),wape_pct=float(np.abs(error).sum()/denom*100) if denom else None,bias=float(error.mean()))

def score_predictions(tables,pred):
    actual=[]
    for row in pred.itertuples():actual.append(demand_series(tables['sales'],row.product_id).get(row.date,np.nan))
    out=pred.copy();out['actual']=actual;return out

def evaluate(tables):
    """Three chronological validation origins; untouched last 30 days for reporting."""
    end=tables['sales'].date.max();allrows=[]
    for days in [120,90,60,30]:
        origin=end-pd.Timedelta(days=days);model=train(tables,origin)
        for method in METHODS:
            if method==METHODS[2] and model is None:continue
            frame=score_predictions(tables,predict(tables,origin,method,model));frame['origin']=origin
            frame['split']='test' if days==30 else 'validation';allrows.append(frame)
    detail=pd.concat(allrows,ignore_index=True)
    validation={m:metrics(g.actual,g.prediction) for m,g in detail[detail.split=='validation'].groupby('method')}
    selected=min(validation,key=lambda m: validation[m]['mae'] if validation[m]['mae'] is not None else float('inf'))
    results=[]
    for (split,method),g in detail.groupby(['split','method']):
        for horizon in [7,14,30]:
            f=g[g.horizon<=horizon];results.append(dict(split=split,method=method,horizon=horizon,**metrics(f.actual,f.prediction)))
    latent=detail[detail.split=='test'].merge(tables['sales'][['date','product_id','simulated_demand']],on=['date','product_id'],how='left') if 'simulated_demand' in tables['sales'] else None
    report={'selected_method':selected,'selection':'Lowest pooled MAE on three 30-day validation windows; final 30 days untouched by selection.',
      'as_of':str(end.date()),'validation_origins':[str((end-pd.Timedelta(days=d)).date()) for d in [120,90,60]],
      'test_origin':str((end-pd.Timedelta(days=30)).date()),'results':results,
      'synthetic_latent_test':{m:metrics(g.simulated_demand,g.prediction) for m,g in latent.groupby('method')} if latent is not None else {},
      'limitations':'Synthetic single-store data; observed metric excludes censored days and can be optimistic. Latent metric is simulation-only, unavailable in real shops. No calibrated intervals or real-world business impact measured.'}
    return report,detail
