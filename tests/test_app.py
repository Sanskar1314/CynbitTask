from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1]/'app/app.py')

def test_streamlit_demo_and_single_review():
    app = AppTest.from_file(APP, default_timeout=30).run()
    assert not app.exception
    assert app.metric[0].value == '18'
    app.sidebar.radio[0].set_value('Inspect one review').run()
    app.text_area[0].set_value('Terrible food and rude service.')
    app.button[0].click().run()
    assert not app.exception
    assert app.metric[0].value == 'Negative'
    app.text_area[0].set_value('')
    app.button[0].click().run()
    assert len(app.error) == 1
    app.sidebar.radio[0].set_value('Model evidence').run()
    assert not app.exception
