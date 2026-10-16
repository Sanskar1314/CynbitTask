"""Deterministic periodic-review planning with timed receipts and FEFO expiry."""
import math
import numpy as np
import pandas as pd

def periodic_quantity(demand,current,incoming,safety=0,backorders=0):
    return max(0,float(demand)+float(safety)-float(current)-float(incoming)+float(backorders))

def constrained_order(raw,pack,moq,cap):
    if raw<=0 or cap<=0:return 0
    proposed=math.ceil(max(raw,moq)/pack)*pack
    if proposed<=cap:return proposed
    safe=math.floor(cap/pack)*pack
    return safe if safe>=moq else 0

def simulate(batches,orders,forecast,as_of,shelf_life,backorders=0):
    """Expiry date is inclusive. Unknown/expired on-hand is excluded. Unmet daily demand is lost, not carried."""
    stock=[];batch_rows=[]
    for b in batches.itertuples():
        state='Unknown expiry' if pd.isna(b.expiry_date) else 'Expired' if b.expiry_date<=as_of else 'Eligible'
        row=dict(batch_id=b.batch_id,quantity=float(b.quantity_remaining),expiry_date=b.expiry_date,status=state,sold_before_expiry=0.,unsold_at_expiry=float(b.quantity_remaining) if state=='Expired' else np.nan,cost_price=float(b.cost_price))
        batch_rows.append(row)
        if state=='Eligible':stock.append(dict(id=b.batch_id,expiry=b.expiry_date,remaining=float(b.quantity_remaining),row=row))
    daily=[];waste=0.;incoming=0.
    for i,demand in enumerate(forecast,1):
        date=as_of+pd.Timedelta(days=i)
        for order in orders.itertuples():
            if order.status=='confirmed' and order.expected_delivery_date==date:
                stock.append(dict(id='PO:'+order.purchase_order_id,expiry=date+pd.Timedelta(days=shelf_life-1),remaining=float(order.quantity_ordered),row=None));incoming+=order.quantity_ordered
        for b in stock:
            if b['expiry']<date and b['remaining']>0:
                waste+=b['remaining']
                if b['row'] is not None:b['row']['unsold_at_expiry']=b['remaining']
                b['remaining']=0.
        opening=sum(b['remaining'] for b in stock if b['expiry']>=date)
        need=float(demand)+(backorders if i==1 else 0);served=0.
        for b in sorted(stock,key=lambda b:b['expiry']):
            if b['expiry']<date:continue
            take=min(need,b['remaining']);b['remaining']-=take;need-=take;served+=take
            if b['row'] is not None:b['row']['sold_before_expiry']+=take
        # Record leftovers after the last sellable day, even at horizon boundary.
        for b in stock:
            if b['expiry']==date and b['row'] is not None:b['row']['unsold_at_expiry']=b['remaining']
        daily.append(dict(date=date,opening=opening,demand=float(demand),served=served,shortage=max(0,need),closing=sum(b['remaining'] for b in stock if b['expiry']>=date),expired_loss=waste,incoming=incoming))
    horizon_end=as_of+pd.Timedelta(days=len(forecast))
    for b in stock:
        if b['row'] is not None and b['expiry']<=horizon_end and pd.isna(b['row']['unsold_at_expiry']):b['row']['unsold_at_expiry']=b['remaining']
    return pd.DataFrame(daily),pd.DataFrame(batch_rows)

def plan(tables,predictions,review_days=7,safety_days=1.5):
    as_of=tables['sales'].date.max();rows=[];batch_results=[]
    for p in tables['products'].itertuples():
        b=tables['batches'].query('product_id == @p.product_id');o=tables['purchase_orders'].query('product_id == @p.product_id')
        f=predictions[predictions.product_id==p.product_id].sort_values('horizon');values=f.prediction.to_numpy();current=float(b.quantity_remaining.sum())
        eligible=b.expiry_date.notna()&b.expiry_date.gt(as_of);usable=float(b.loc[eligible,'quantity_remaining'].sum());unknown=float(b.loc[b.expiry_date.isna(),'quantity_remaining'].sum());expired=float(b.loc[b.expiry_date.le(as_of),'quantity_remaining'].sum())
        protection=int(p.lead_time_days+review_days);supported=len(values)>=30 and np.isfinite(values).all();coverage='Unsupported' if not supported else f.support.iloc[0]
        row=dict(product_id=p.product_id,product=p.product_name,current_stock=current,usable_stock=usable,unknown_expiry=unknown,expired_stock=expired,lead_time=int(p.lead_time_days),protection_days=protection,support=coverage)
        if not supported:
            row.update(incoming=0,forecast_30=np.nan,target=np.nan,safety_stock=np.nan,expiry_loss=np.nan,raw_order=np.nan,order_cap=np.nan,recommended_order=0,days_cover=np.nan,excess_stock=np.nan,status='Investigate demand',priority='P2',reason='Insufficient sales history: review requests, obtain demand evidence; no exact purchase quantity.')
            # Recorded expiry warnings still exist without a demand forecast.
            for batch in b.itertuples():batch_results.append(dict(product_id=p.product_id,product=p.product_name,batch_id=batch.batch_id,quantity=batch.quantity_remaining,expiry_date=batch.expiry_date,status='Unknown expiry' if pd.isna(batch.expiry_date) else 'Expired' if batch.expiry_date<=as_of else 'Forecast unavailable',sold_before_expiry=np.nan,unsold_at_expiry=batch.quantity_remaining if pd.notna(batch.expiry_date) and batch.expiry_date<=as_of else np.nan,cost_price=batch.cost_price))
            rows.append(row);continue
        daily,br=simulate(b,o,values,as_of,int(p.shelf_life_days),p.backorders)
        if not br.empty:
            br['product_id']=p.product_id;br['product']=p.product_name;batch_results.extend(br.to_dict('records'))
        n=min(protection,30);safety=float(values[:n].mean()*safety_days);demand=float(values[:n].sum());incoming=float(daily.iloc[n-1].incoming)
        # Loss before end of protection is unavailable for that period's demand.
        loss=float(daily.iloc[n-1].expired_loss);raw=periodic_quantity(demand,usable-loss,incoming,safety,p.backorders)
        arrival=max(1,int(p.lead_time_days));last=min(30,arrival+int(p.shelf_life_days)-1)
        # Existing/confirmed stock gets first claim on future demand. Cap new units at residual demand in receipt life.
        sellthrough=float(daily.iloc[arrival-1:last].shortage.sum());at_arrival=float(daily.iloc[arrival-1].opening)
        cap=max(0,min(sellthrough,p.max_stock-at_arrival));order=constrained_order(raw,int(p.pack_size),int(p.minimum_order_quantity),cap) if protection<=30 and unknown==0 else 0
        average=float(values.mean());cover=usable/average if average>0 else np.nan;excess=max(0,usable-values.sum())
        near_loss=float(br.loc[br.expiry_date.le(as_of+pd.Timedelta(days=7)),'unsold_at_expiry'].fillna(0).sum()) if not br.empty else 0
        early_shortage=float(daily.iloc[:arrival-1].shortage.sum())
        if expired or unknown or near_loss:status='Expiry-risk review required';priority='P1'
        elif protection>30:status='Manual horizon review';priority='P2'
        elif order>0:status='Reorder now' if early_shortage>0 or cover<=p.lead_time_days else 'Reorder soon';priority='P1' if early_shortage>0 else 'P2'
        elif excess>0:status='Avoid reordering';priority='P3'
        elif raw>0:status='Constraint review';priority='P2'
        else:status='Sufficient stock';priority='P4'
        reason=f'{n}-day demand {demand:.1f} + safety {safety:.1f}; usable {usable:.1f}, confirmed on-time incoming {incoming:.1f}, expiry loss {loss:.1f}, backorders {p.backorders}. Raw {raw:.1f}; shelf-life/storage cap {cap:.1f}; pack {p.pack_size}, MOQ {p.minimum_order_quantity}.'
        if early_shortage:reason+=f' {early_shortage:.1f} units may be unmet before new supply can arrive; expedite with supplier.'
        if unknown:reason+=' Unknown expiry blocks automatic ordering pending stock verification.'
        if protection>30:reason+=' Protection exceeds forecast horizon; quantity withheld.'
        overdue=o[(o.status=='confirmed')&(o.expected_delivery_date<=as_of)].quantity_ordered.sum()
        if overdue:reason+=f' {overdue:g} overdue incoming units excluded; confirm receipt.'
        row.update(incoming=incoming,forecast_30=float(values.sum()),target=demand+safety,safety_stock=safety,expiry_loss=loss,raw_order=raw,order_cap=cap,recommended_order=order,days_cover=cover,excess_stock=excess,status=status,priority=priority,reason=reason);rows.append(row)
    batches=pd.DataFrame(batch_results)
    if not batches.empty:
        batches['days_to_expiry']=(batches.expiry_date-as_of).dt.days
        batches['risk_value']=batches.unsold_at_expiry*batches.cost_price
        batches['action']=batches.apply(lambda r:'Quarantine; follow return/disposal policy. Never sell.' if r.status=='Expired' else 'Verify label before sale or planning.' if r.status=='Unknown expiry' else 'Prioritize eligible FEFO batches; investigate permitted returns/promotions.' if pd.notna(r.unsold_at_expiry) and r.unsold_at_expiry>0 else 'Monitor; risk beyond 30 days is unknown.' if pd.isna(r.unsold_at_expiry) else 'Expected to sell within recorded life.',axis=1)
    return pd.DataFrame(rows),batches
