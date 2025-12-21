
from phoenix_engine.domain.match import MatchRequest, MatchResult
from phoenix_engine.engines.match import MatchingEngine

from fastapi import FastAPI, HTTPException
from datetime import datetime
import pytz
import uvicorn
from phoenix_engine.engines.birth import BirthChartEngine as VedicChart
from phoenix_engine.core.models import ChartRequest, ChartOutput
from phoenix_engine.infrastructure.time.manager import localize_strict, AmbiguousTimeError, NonExistentTimeError

app = FastAPI(title="Phoenix Engine V13 (Cosmic)", version="13.0.0")

@app.post("/calculate", response_model=ChartOutput)
def calculate_chart(req: ChartRequest):
    try:
        # 1. Standardize Time
        bd = req.birth_data
        try:
            dt_naive = datetime(bd.year, bd.month, bd.day, bd.hour, bd.minute)
            dt_aware = localize_strict(dt_naive, bd.timezone)
        except (ValueError, AmbiguousTimeError, NonExistentTimeError) as e:
            raise HTTPException(status_code=400, detail=f"Time Error: {str(e)}")

        # 2. Process
        chart = VedicChart(dt_aware, bd.lat, bd.lon, config=req.config)
        result = chart.process()
        
        if req.name:
            result.meta["client_name"] = req.name
            
        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/match", response_model=MatchResult)
def calculate_match(req: MatchRequest):
    try:
        engine = MatchingEngine()
        return engine.process(req)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
