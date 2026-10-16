"""Descriptive season/event comparisons, not causal uplift estimates."""
import pandas as pd
import numpy as np
from src.data import demand_series

def seasonal_profile(tables,pid):
    y=demand_series(tables['sales'],pid)
    if y.empty:return pd.DataFrame(columns=['month','mean_daily','observations'])
    return y.groupby(y.index.month).agg(mean_daily='mean',observations='count').rename_axis('month').reset_index()

def festival_evidence(tables,pid):
    y=demand_series(tables['sales'],pid);end=tables['sales'].date.max();rows=[]
    for name,events in tables['festivals'].groupby('festival_name'):
        comparisons=[]
        for e in events[events.festival_date<=end].itertuples():
            pre=y.reindex(pd.date_range(e.festival_date-pd.Timedelta(days=7),periods=7)).dropna()
            base=y.reindex(pd.date_range(e.festival_date-pd.Timedelta(days=35),periods=28)).dropna()
            if len(pre)>=5 and len(base)>=20 and base.mean()>0:comparisons.append(pre.mean()/base.mean()-1)
        future=events[events.festival_date>end]
        next_date=future.festival_date.min() if len(future) else pd.NaT
        rows.append(dict(event=name,next_date=next_date,days_remaining=(next_date-end).days if pd.notna(next_date) else np.nan,comparable_occurrences=len(comparisons),mean_change_pct=100*np.mean(comparisons) if len(comparisons)>=2 else np.nan,evidence='Descriptive association; overlapping events/trend may confound.' if len(comparisons)>=2 else 'Insufficient comparable history; no claimed uplift.'))
    return pd.DataFrame(rows)
