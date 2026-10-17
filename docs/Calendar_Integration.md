# Google Calendar dates used by StockSense

Imported2026-10-17 through the connected Google Calendar tool, calendar **Holidays in India**, public ID `en.indian#holiday@group.v.calendar.google.com`. Queried2024-01-01 through2028-01-01 exclusive;242 public events returned with no next page. Only28 entries covering Holi, Eid al-Fitr (source title Ramzan Id), Raksha Bandhan, first day of Sharad Navratri, Dussehra, Diwali/Deepavali and Christmas were retained. No personal appointments or other calendars were read or persisted.

`data/calendar/google_india_holidays.json` preserves selected public source title, all-day start/end, visibility, source link and retrieval metadata. `src/calendar_data.py` normalizes names without changing dates.2027 Eid remains marked Tentative. Dates are as listed by Google, with regional/lunar-calendar differences possible. All-day dates keep their literal date; display timezone parameters in source URLs are not used to shift them.

The app now uses this imported snapshot. Connecting Google Calendar to the assistant does not provide browser-app OAuth credentials or an automatic background sync. Data Management lets you inspect/download/apply the imported dates. To refresh the source, ask the connected assistant to reread this public calendar and update the snapshot, or upload a newer festivals CSV as part of a validated dataset. No account tokens, private ICS links or personal records are committed.

Seasons are learned through continuous day-of-year Fourier features, not inferred from holiday titles. Broad seasonal labels in the UI are for interpretation/evaluation only, not weather measurements. Festival windows and annual patterns enter the same demand model. There is no separate seasonal prediction or additive manual uplift.

Synthetic sales were regenerated around these dates. Real/user-uploaded sales must never be rewritten to fit a calendar. Applying a replacement calendar invalidates prior evaluation and triggers refitting under the selected/default policy.
