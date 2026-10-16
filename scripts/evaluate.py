from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.data import load_demo
from src.forecasting import evaluate
if __name__=='__main__':
    report,detail=evaluate(load_demo());out=Path(__file__).resolve().parents[1]/'evaluation';out.mkdir(exist_ok=True)
    (out/'metrics.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    detail.to_csv(out/'backtest_predictions.csv',index=False)
    print(json.dumps(report,indent=2))
