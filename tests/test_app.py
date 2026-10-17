from streamlit.testing.v1 import AppTest
from src.data import ROOT

def test_all_sections_and_invalid_upload():
    app=AppTest.from_file(ROOT/'app/app.py',default_timeout=120).run()
    assert not app.exception
    sections=app.sidebar.radio[0].options
    assert len(sections)==7
    assert not any('Festival Intelligence' in x for x in sections)
    for section in sections:
        app.sidebar.radio[0].set_value(section).run()
        assert not app.exception,section
        assert app.title[0].value==section
        if section=='Product Demand Forecasting':
            assert any('Seasons and events included' in x.value for x in app.subheader)
            assert len(app.get('plotly_chart'))==2
        if section=='Data Management':
            assert any('Apply imported Google Calendar dates' in b.label for b in app.button)
    button=next(b for b in app.button if b.label=='Validate and replace snapshot');button.click().run()
    assert app.error and 'all six' in app.error[0].value
    assert app.session_state.source=='Synthetic demo'
