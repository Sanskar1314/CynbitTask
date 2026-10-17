"""One count-demand model per SKU: season, weekday, trend and dated festivals jointly."""
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.linear_model import PoissonRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from src.data import demand_series

SEASONAL_METHOD = 'Seasonal Poisson regression'
SEASONAL_FEATURES = ['trend_years', 'annual_sin1', 'annual_cos1', 'annual_sin2', 'annual_cos2'] + [f'weekday_{i}' for i in range(1,7)] + ['pre8_any_event']

def calendar_features(dates, festivals):
    dates = pd.DatetimeIndex(dates)
    # Smooth leap-safe annual phase: no step change at each month boundary.
    phase = (dates.dayofyear.to_numpy()-1) / np.where(dates.is_leap_year,366.,365.)
    trend = (dates-pd.Timestamp('2024-01-01')).days.to_numpy()/365.25
    columns = [trend, np.sin(2*np.pi*phase), np.cos(2*np.pi*phase), np.sin(4*np.pi*phase), np.cos(4*np.pi*phase)]
    columns += [(dates.dayofweek==i).astype(float) for i in range(1,7)]
    days = dates.to_numpy(dtype='datetime64[D]')
    # Pool event windows per product: only 2–3 occurrences of each named festival
    # are available. Separate coefficients were fitting noise (notably tea/Diwali).
    events = festivals.festival_date.to_numpy(dtype='datetime64[D]')
    delta = events[None,:]-days[:,None]
    columns.append(((delta>=np.timedelta64(0,'D'))&(delta<=np.timedelta64(7,'D'))).any(axis=1).astype(float))
    return np.column_stack(columns)

@dataclass
class SeasonalModel:
    models: dict
    trained_through: pd.Timestamp

    def predict_product(self, pid, dates, festivals):
        model = self.models.get(pid)
        if model is None:
            return np.full(len(dates),np.nan)
        if isinstance(model,float):
            return np.full(len(dates),model)
        return model.predict(calendar_features(dates,festivals))


def train_seasonal(tables, cutoff):
    sales = tables['sales'][tables['sales'].date<=cutoff]
    models = {}
    for pid in tables['products'].product_id:
        y = demand_series(sales,pid).dropna()
        # One annual cycle is the minimum before fitting annual coefficients.
        if len(y)<180 or (y.index.max()-y.index.min()).days<365:
            continue
        if y.sum()==0:
            models[pid]=0.;continue
        model = make_pipeline(StandardScaler(),PoissonRegressor(alpha=.03,max_iter=500,tol=1e-7))
        model.fit(calendar_features(y.index,tables['festivals']),y.to_numpy())
        models[pid]=model
    return SeasonalModel(models,pd.Timestamp(cutoff))
