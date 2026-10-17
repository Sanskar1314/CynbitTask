"""Public Google holiday snapshot; no credentials or personal calendars stored."""
import json
from pathlib import Path
import pandas as pd

CALENDAR_PATH = Path(__file__).resolve().parents[1] / 'data/calendar/google_india_holidays.json'
NAMES = {'Diwali/Deepavali': 'Diwali', 'First Day of Sharad Navratri': 'Navratri', 'Ramzan Id': 'Eid al-Fitr', 'Ramzan Id (tentative)': 'Eid al-Fitr'}
EVENT_NAMES = ('Holi', 'Eid al-Fitr', 'Raksha Bandhan', 'Navratri', 'Dussehra', 'Diwali', 'Christmas')

def load_holiday_snapshot(path=CALENDAR_PATH):
    payload = json.loads(Path(path).read_text())
    rows = []
    for event in payload['events']:
        if event['status'] != 'confirmed' or event['visibility'] != 'public':
            continue
        # Holiday all-day dates retain their literal date, not a UTC conversion.
        name = NAMES.get(event['summary'], event['summary'])
        if name not in EVENT_NAMES:
            continue
        rows.append(dict(festival_name=name, festival_date=event['start'][:10], region='India',
                         calendar_source=f"Google Calendar: {payload['calendar_name']} (imported {payload['retrieved_on']})",
                         source_title=event['summary'], source_url=event['url'],
                         date_status='Tentative' if 'tentative' in event['summary'].lower() else 'As listed by calendar'))
    frame = pd.DataFrame(rows).drop_duplicates(['festival_name','festival_date','region'])
    frame['festival_date'] = pd.to_datetime(frame['festival_date'], format='%Y-%m-%d')
    return frame.sort_values('festival_date').reset_index(drop=True), payload


def season_label(date):
    """Display/evaluation grouping only; model learns continuous annual cycles."""
    month = pd.Timestamp(date).month
    return 'Winter (Dec–Feb)' if month in (12,1,2) else 'Pre-monsoon / summer (Mar–May)' if month in (3,4,5) else 'Monsoon (Jun–Sep)' if month in (6,7,8,9) else 'Post-monsoon (Oct–Nov)'
