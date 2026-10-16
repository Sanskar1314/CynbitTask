"""Auditable English rules: qualitative evidence, never numeric forecast uplift."""
import re
import pandas as pd

def analyze(reviews,products):
    aliases=[]
    for p in products.itertuples():
        for alias in [p.product_name]+str(p.aliases).split('|'):
            if alias.strip():aliases.append((alias.strip().lower(),p.product_id,p.product_name))
    aliases.sort(key=lambda x:len(x[0]),reverse=True);rows=[]
    for r in reviews.itertuples():
        text=r.review_text.lower();matches=[];occupied=[]
        for alias,pid,name in aliases:
            for match in re.finditer(r'(?<!\w)'+re.escape(alias)+r'(?!\w)',text):
                if any(match.start()<end and match.end()>start for start,end in occupied):continue
                occupied.append(match.span());matches.append((pid,name,match.group()))
        if r.product_id and not any(x[0]==r.product_id for x in matches):
            p=products[products.product_id==r.product_id].iloc[0];matches.append((r.product_id,p.product_name,'supplied product ID'))
        intents=[]
        negated=bool(re.search(r'not\s+(?:out of stock|unavailable)|never\s+out of stock|always available|no (?:stock|availability) (?:issue|problem)',text))
        if re.search(r'out of stock|never available|unavailable|not available|could not find|cannot find|can.t find|sold out',text) and not negated:intents.append('Availability complaint')
        if re.search(r'please|wish|would (?:be|like)|can you|could you|keep more|want|request|need',text) and not re.search(r'(?:do not|don.t)\s+(?:stock|keep|sell)',text):intents.append('Product request')
        if re.search(r'sugar.free|low.salt|larger|variant|vegan|gluten.free',text):intents.append('Variant preference')
        if re.search(r'spoil|stale|damag|expired|sour|bad quality',text):intents.append('Quality complaint')
        season=', '.join(w for w in ['summer','winter','monsoon','diwali','holi','christmas'] if w in text)
        if not intents:intents=['Mention only' if matches else 'No product signal']
        for pid,name,evidence in list(dict.fromkeys(matches)) or [('', 'Unmapped product','No catalog alias matched')]:
            rows.append(dict(review_id=r.review_id,product_id=pid,product=name,intents='; '.join(intents),season_or_event=season,evidence=evidence,review_text=r.review_text,
              action='Investigate availability/assortment with sales records; no automatic quantity uplift.' if any(x in intents for x in ['Product request','Availability complaint','Variant preference']) else 'Inspect affected batch and verify condition.' if 'Quality complaint' in intents else 'No purchasing action from this text alone.',confidence='Rule match; human review required'))
    return pd.DataFrame(rows,columns=['review_id','product_id','product','intents','season_or_event','evidence','review_text','action','confidence'])
