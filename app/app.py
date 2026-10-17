"""Invento local assessment dashboard. Run from repository root."""
from pathlib import Path
import sys,os,json
os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from src.data import ROOT,SCHEMAS,load_demo,read_csv,validate,safe_csv,serializable,historical_summary,save_snapshot,load_snapshot
from src.forecasting import METHODS,train,predict,evaluate
from src.seasonal_model import SEASONAL_METHOD
from src.calendar_data import load_holiday_snapshot,season_label
from src.inventory import plan
from src.reviews import analyze
from src.seasonality import seasonal_profile,festival_evidence

st.set_page_config(page_title='Revio Invento',page_icon='📦',layout='wide')
st.markdown('''<style>.stApp {background:#f5f7fa} h1,h2,h3 {color:#102c3a} [data-testid="stMetric"] {background:white;padding:18px;border:1px solid #dae3e8;border-radius:12px} [data-testid="stSidebar"] {background:#e8f0f2} .block-container{padding-top:2rem} </style>''',unsafe_allow_html=True)

@st.cache_data(show_spinner=False,max_entries=4)
def forecast_snapshot(tables,method):
    origin=tables['sales'].date.max();model=train(tables,origin,method) if method in (METHODS[2],SEASONAL_METHOD) else None
    if method==METHODS[2] and model is None:method=METHODS[0]
    return predict(tables,origin,method,model)

@st.cache_data(show_spinner=False,max_entries=2)
def evaluate_snapshot(tables):return evaluate(tables)[0]

def reset(tables,source):
    st.session_state.tables=tables;st.session_state.source=source
    st.session_state.pop('custom_evaluation',None)

if 'tables' not in st.session_state:reset(load_demo(),'Synthetic demo')
# Refresh only the bundled demo after its data/model revision; preserve uploaded snapshots.
if st.session_state.source=='Synthetic demo' and st.session_state.get('demo_version')!=3:
    reset(load_demo(),'Synthetic demo');st.session_state.demo_version=3
t=st.session_state.tables;as_of=t['sales'].date.max();demo=st.session_state.source=='Synthetic demo'
report=json.loads((ROOT/'evaluation/metrics.json').read_text()) if demo else st.session_state.get('custom_evaluation')
if report and report.get('version')!=3:report=None
method=report['selected_method'] if report else METHODS[0]
with st.sidebar:
    st.title('Invento')
    st.caption('Proposed Revio inventory module')
    section=st.radio('Workspace',['Executive Dashboard','Product Demand Forecasting','Smart Reorder Planner','Expiry Management','Slow-Moving Inventory','Review Intelligence','Data Management'])
    st.divider();review=st.slider('Review period (days)',1,21,7);safety=st.slider('Safety buffer (days)',0.,5.,1.5,.5)
    st.caption('Review period = days between stock checks. Safety buffer = extra demand-days held as a precaution. Draft orders need owner review.')

st.title(section)
st.caption(f"REVIO INVENTO  /  {st.session_state.source}  /  Snapshot {as_of:%d %b %Y}")
if demo:st.info('Synthetic demonstration data • No Cynbit customer records • No live Revio or POS connection')
if t['festivals'].calendar_source.str.contains('Google Calendar',case=False).any():st.caption('Calendar source: '+ ' · '.join(t['festivals'].calendar_source.drop_duplicates().astype(str)) + '. Regional dates may differ; inspect tentative entries in the calendar table.')
if t['festivals'].calendar_source.str.contains('synthetic',case=False).any():st.warning('Illustrative festival scenario: these are not verified religious calendar dates. Replace with a verified regional calendar before business use.')
if not demo and not report:st.info('Uploaded data uses the moving-average baseline until you run its own chronological evaluation in Data Management.')
if 'available_stock' not in t['sales'] and 'stockout' not in t['sales']:st.warning('Stock availability is missing. Forecasts model recorded sales; lost demand cannot be identified.')
with st.spinner('Preparing demand forecasts and inventory decisions…'):
    predictions=forecast_snapshot(t,method);reorders,batches=plan(t,predictions,review,safety);summary=historical_summary(t)

def product_picker(key):
    ids=t['products'].product_id.tolist();names=t['products'].set_index('product_id').product_name.to_dict()
    return st.selectbox('Product',ids,format_func=lambda p:names[p],key=key)

def table(frame):st.dataframe(frame,hide_index=True,use_container_width=True)

if section=='Executive Dashboard':
    c=st.columns(4);c[0].metric('Tracked products',len(t['products']));c[1].metric('Products needing review',int(reorders.priority.isin(['P1','P2']).sum()));c[2].metric('Draft order units',int(reorders.recommended_order.sum()));c[3].metric('Recorded inventory cost',f"₹{(t['batches'].quantity_remaining*t['batches'].cost_price).sum():,.0f}")
    st.caption('Inventory cost includes expired/unknown stock; it is not saleable inventory value. Draft quantities are constrained recommendations, never placed orders.')
    c=st.columns(2)
    with c[0]:
        st.subheader('Suggested order quantities');st.plotly_chart(px.bar(reorders,x='product',y='recommended_order',color='priority',color_discrete_map={'P1':'#c46238','P2':'#087e8b','P3':'#91a6b0','P4':'#b8c6cc'},labels={'recommended_order':'Draft units','product':''}),width='stretch')
    with c[1]:
        st.subheader('Sales recorded over time');daily=t['sales'].groupby('date',as_index=False).quantity_sold.sum();st.plotly_chart(px.line(daily.tail(120),x='date',y='quantity_sold',labels={'quantity_sold':'Actual units sold','date':''}),width='stretch')
    st.subheader('Action queue');table(reorders.sort_values('priority')[['product','status','priority','recommended_order','support']])
    st.caption('P1: recorded expiry concern or pre-arrival shortage. P2: replenishment/constraint/no-history review. P3: excess stock. P4: sufficient. Priority is separate from forecast support.')
    st.subheader('Historical sales intelligence');table(summary)
    st.subheader('Upcoming calendar entries');table(t['festivals'][t['festivals'].festival_date.between(as_of+pd.Timedelta(days=1),as_of+pd.Timedelta(days=30))])
elif section=='Product Demand Forecasting':
    pid=product_picker('forecast_product');h=st.select_slider('Forecast horizon',options=[7,14,30],value=30)
    actual=t['sales'][t['sales'].product_id==pid].tail(120);future=predictions[(predictions.product_id==pid)&(predictions.horizon<=h)]
    if future.prediction.isna().all():st.info('No supported forecast. Collect sales/availability history; customer requests alone cannot determine order quantities.')
    else:
        c=st.columns(3);c[0].metric(f'Next {h} days',f'{future.prediction.sum():.1f} units');c[1].metric('Selected model',future.method.iloc[0]);c[2].metric('Data support',future.support.iloc[0])
        fig=go.Figure();fig.add_trace(go.Scatter(x=actual.date,y=actual.quantity_sold,name='Recorded sales',line=dict(color='#778995')));fig.add_trace(go.Scatter(x=future.date,y=future.prediction,name='Forecast',line=dict(color='#087e8b',dash='dash')));
        for event in t['festivals'][t['festivals'].festival_date.between(as_of+pd.Timedelta(days=1),as_of+pd.Timedelta(days=h))].itertuples():
            start=max(as_of+pd.Timedelta(days=1),event.festival_date-pd.Timedelta(days=7))
            fig.add_vrect(x0=start,x1=event.festival_date,fillcolor='#e9b267',opacity=.14,line_width=0,layer='below')
            fig.add_shape(type='line',x0=event.festival_date,x1=event.festival_date,y0=0,y1=1,yref='paper',line=dict(color='#c46238',dash='dot'))
            fig.add_annotation(x=event.festival_date,y=1,yref='paper',text=event.festival_name,showarrow=False,textangle=-45)
        fig.update_layout(title=t['products'].set_index('product_id').loc[pid,'product_name']+' · Recorded sales and forecast',yaxis_title='Units / day',legend=dict(orientation='h'));st.plotly_chart(fig,width='stretch')
        st.caption('Point forecasts, not guarantees. Support labels reflect recent observed history, not calibrated probabilities. Recorded sales can be censored by stockouts.')
    st.subheader('Seasons and events included in this forecast')
    if future.method.eq(SEASONAL_METHOD).any():
        st.write('One demand forecast feeds purchasing and expiry planning. Annual patterns, weekdays, trend and dated festivals are learned together. Festival effects are pooled across past events for each product because individual festivals have few observations; no extra seasonal forecast or manual festival multiplier is added.')
    else:
        st.write('One demand forecast feeds purchasing and expiry planning. The selected method is shown above and in the forecast table. Baselines do not learn annual or festival effects; the calendar below is context. Run snapshot evaluation to compare seasonal models when sufficient history is available.')
    st.caption('Calendar period: '+', '.join(dict.fromkeys(future.date.map(season_label)))+'. These labels are broad Indian calendar groupings, not local weather observations.')
    events=t['festivals'][t['festivals'].festival_date.between(as_of+pd.Timedelta(days=1),as_of+pd.Timedelta(days=h+7))].sort_values('festival_date')
    if events.empty:st.info('No imported festival falls in this forecast or its seven-day preparation window.')
    else:
        table(events)
        windows=[]
        for event in events.itertuples():
            start=max(as_of+pd.Timedelta(days=1),event.festival_date-pd.Timedelta(days=7))
            end=min(as_of+pd.Timedelta(days=h),event.festival_date)
            values=future[future.date.between(start,end)].prediction.dropna()
            if len(values):windows.append({'Festival':event.festival_name,'Forecast window':f'{start:%d %b} – {end:%d %b}','Mean forecast units/day':round(values.mean(),1)})
        if windows:table(pd.DataFrame(windows))
        st.caption('Shaded days are the seven-day preparation period through festival day. This table summarizes the same forecast line. A fall after a festival window ends is different from a fall during the festival. Daily points can also vary by weekday.')
    with st.expander('Historical seasonal evidence (observations, not another forecast)'):
        profile=seasonal_profile(t,pid)
        if profile.empty:st.info('No sales history to estimate seasonality.')
        else:st.plotly_chart(px.bar(profile,x='month',y='mean_daily',labels={'mean_daily':'Observed mean units/day','month':'Calendar month'}),width='stretch')
        st.caption('Historical monthly averages may mix trends, stockouts and event effects. This chart is not a second prediction.')
        table(festival_evidence(t,pid))
    with st.expander('Forecast accuracy across seasons and products'):
        if report:
            scores=pd.DataFrame(report['results']);table(scores[(scores.horizon==h)&(scores.n>0)])
            if report.get('by_season'):
                st.write('Season-by-season test results (30-day windows)');table(pd.DataFrame(report['by_season']))
                st.write('Selected product: same-data model comparison');table(pd.DataFrame(report['by_product']).query('product_id == @pid'))
                st.write('Festival preparation windows versus ordinary days');table(pd.DataFrame(report['by_event_window']))
            st.caption(report['selection']+' '+report['limitations'])
        else:st.info('No evaluation for this snapshot yet. Run evaluation in Data Management. Demo metrics are not applied to uploaded data.')
    table(future);st.download_button('Download forecast CSV',safe_csv(future),'forecast.csv','text/csv')
elif section=='Smart Reorder Planner':
    st.write('Review the demand, eligible stock, timed receipts and constraints behind each draft quantity.')
    table(reorders[['product','current_stock','usable_stock','incoming','forecast_30','recommended_order','lead_time','priority','status','support']])
    pid=product_picker('reorder_product');row=reorders[reorders.product_id==pid].iloc[0];st.info(row.reason)
    st.caption('Protection = lead time + review period. Target = cumulative forecast + safety buffer. Net need includes backorders and simulated expiry loss. New receipt life, storage, MOQ and pack constraints can reduce the draft. Unknown expiry blocks ordering. Longer-than-30-day protection needs manual planning.')
    table(reorders[reorders.product_id==pid]);st.download_button('Download purchasing review CSV',safe_csv(reorders),'purchasing_review.csv','text/csv')
elif section=='Expiry Management':
    st.write('Recorded batch dates determine eligibility. Forecasts estimate unsold quantities; they never invent official expiry dates.')
    if batches.empty:st.info('No batch records supplied.')
    else:
        c=st.columns(3);c[0].metric('Expired batches',int((batches.status=='Expired').sum()));c[1].metric('Unknown expiry',int((batches.status=='Unknown expiry').sum()));c[2].metric('Estimated at-risk cost (known horizon)',f'₹{batches.risk_value.sum():,.0f}')
        table(batches.sort_values('expiry_date'));st.caption('Expiry is inclusive for future days. Blank risk is unknown beyond the 30-day forecast or without supported demand, not zero. FEFO uses earlier eligible expiry first; expired stock is never sold.')
        st.download_button('Download batch review CSV',safe_csv(batches),'batch_review.csv','text/csv')
elif section=='Slow-Moving Inventory':
    merged=reorders.merge(summary[['product_id','daily_demand','growth_pct','demand_type']],on='product_id');slow=merged[(merged.excess_stock>0)|(merged.daily_demand<3)|(merged.growth_pct<-20)]
    table(slow[['product','daily_demand','growth_pct','demand_type','usable_stock','days_cover','forecast_30','excess_stock','status']])
    st.caption('Excess = max(0, eligible on-hand − 30-day forecast), a review signal, not guaranteed waste. Days cover excludes unknown/expired stock but does not model future expiry. Pause purchasing where excessive; inspect condition and return/promotion rules before acting.')
elif section=='Review Intelligence':
    st.write('Imported review text can suggest availability, assortment or quality investigations. These rules do not change numerical forecasts.')
    review_file=st.file_uploader('Replace reviews CSV',type='csv',max_upload_size=10,key='reviews_upload')
    if st.button('Validate and apply reviews',disabled=review_file is None):
        try:
            new={k:serializable(v) for k,v in t.items()};new['reviews']=read_csv(review_file.getvalue());validated=validate(new);st.session_state.tables=validated;st.session_state.source='Snapshot with imported reviews';st.session_state.custom_evaluation=report;st.success('Review table replaced after validation.');st.rerun()
        except ValueError as exc:st.error(str(exc))
    signals=analyze(t['reviews'],t['products']);table(signals)
    st.caption('English keyword baseline with longest alias match and limited negation handling. Supplied product IDs are input assertions. Mixed-product reviews, sarcasm and other languages require human review.')
    st.download_button('Download review signals',safe_csv(signals),'review_signals.csv','text/csv')
else:
    st.subheader('Google Calendar festival dates')
    calendar_table,calendar_meta=load_holiday_snapshot()
    st.write(f"Imported {len(calendar_table)} public holiday entries for 2024–2027 from Holidays in India on {calendar_meta['retrieved_on']}. This app uses the imported snapshot, not a continuous Google Calendar connection.")
    st.caption('Only public festival dates were imported. Refresh through the connected Calendar assistant or replace festivals.csv with a newer export. Private appointments are not used.')
    with st.expander('Inspect imported dates and source links'):table(calendar_table)
    st.download_button('Download Google Calendar festival CSV',safe_csv(calendar_table),'google_calendar_festivals.csv','text/csv')
    if st.button('Apply imported Google Calendar dates to this snapshot'):
        new={k:serializable(v) for k,v in t.items()};new['festivals']=serializable(calendar_table)
        reset(validate(new),'Snapshot with Google Calendar dates');st.rerun()
    st.caption('Applying a calendar changes model inputs and clears previous evaluation. It never rewrites uploaded sales. If sales were simulated using different dates, regenerate that simulation separately.')
    st.subheader('Snapshot and schemas');st.write('Upload all six CSVs together. Validation succeeds for the whole snapshot or leaves the current data intact. Snapshot date is the latest sales date. Download templates below.')
    with st.form('snapshot_upload'):
        files={name:st.file_uploader(name+'.csv',type='csv',max_upload_size=10,key='upload_'+name) for name in SCHEMAS}
        apply=st.form_submit_button('Validate and replace snapshot')
    if apply:
        try:
            if not all(files.values()):raise ValueError('Select all six related CSV files before replacing the snapshot.')
            new=validate({k:read_csv(v.getvalue()) for k,v in files.items()});reset(new,'Uploaded snapshot');st.rerun()
        except ValueError as exc:st.error(str(exc))
    c=st.columns(3)
    if c[0].button('Reset to synthetic demo'):reset(load_demo(),'Synthetic demo');st.rerun()
    if c[1].button('Save snapshot locally'):
        try:save_snapshot(t,ROOT/'.local/snapshot.sqlite');st.success('Saved local SQLite snapshot.')
        except (ValueError,OSError) as exc:st.error(str(exc))
    if c[2].button('Load saved snapshot'):
        try:reset(load_snapshot(ROOT/'.local/snapshot.sqlite'),'Saved local snapshot');st.rerun()
        except Exception as exc:st.error(f'Could not load snapshot: {exc}')
    st.caption('Local persistence is explicit. Reloaded snapshots require their own model selection; no credentials or cloud database are used.')
    if st.button('Run chronological evaluation for this snapshot'):
        if (as_of-t['sales'].date.min()).days<240:st.error('At least 240 calendar days are required for this evaluation protocol.')
        else:
            with st.spinner('Training chronological folds; this may take a minute…'):
                st.session_state.custom_evaluation=evaluate_snapshot(t)
                if demo:st.session_state.source='Evaluated synthetic snapshot'
            st.rerun()
    for name in SCHEMAS:
        with st.expander(name+' schema and preview'):
            st.code(', '.join(SCHEMAS[name]),language=None);table(t[name].head(20));st.download_button('Download '+name,safe_csv(t[name]),name+'.csv','text/csv',key='download_'+name)
    st.caption('Batch dates may be blank (unknown). Other dates use YYYY-MM-DD. Keys must be unique and product references valid. Sales availability fields are recommended. See docs/Data_Card.md for full definitions and prototype limits.')

st.divider();st.caption('Assessment proof of concept · Decisions require owner review · No orders placed · No measured real-store ROI')
