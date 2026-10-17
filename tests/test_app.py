from streamlit.testing.v1 import AppTest
from src.data import ROOT

def test_all_sections_and_invalid_upload():
    app=AppTest.from_file(ROOT/'app/app.py',default_timeout=120).run()
    assert not app.exception
    sections=app.sidebar.radio[0].options
    for section in sections:
        app.sidebar.radio[0].set_value(section).run()
        assert not app.exception,section
        assert app.title[0].value==section
    button=next(b for b in app.button if b.label=='Validate and replace snapshot');button.click().run()
    assert app.error and 'all six' in app.error[0].value
    assert app.session_state.source=='Synthetic demo'
