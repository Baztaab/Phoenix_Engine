from fastapi import FastAPI, HTTPException
from datetime import datetime
import uvicorn

# Import Core Engines & Models
from phoenix_engine.engines.birth import BirthChartEngine as VedicChart
from phoenix_engine.engines.match import MatchingEngine
from phoenix_engine.core.models import ChartRequest, ChartOutput
from phoenix_engine.domain.match import MatchRequest, MatchResult
from phoenix_engine.infrastructure.time.manager import localize_strict, AmbiguousTimeError, NonExistentTimeError

app = FastAPI(title="Phoenix Engine V13 (Cosmic)", version="13.0.0")

# --- [Kai/Fix]: Added Health Check Endpoint ---
@app.get("/")
def read_root():
    """
    System Status Check.
    Used by 'test_smoke.py' to verify API availability.
    """
    return {
        "status": "online",
        "engine": "Phoenix Engine V13 (Cosmic)",
        "version": "13.0.0"
    }
# ----------------------------------------------


@app.post("/calculate", response_model=ChartOutput)
def calculate_chart(req: ChartRequest):
    try:
        bd = req.birth_data

        # Use orchestrator to ensure full UTC/Upagraha/Panchanga logic
        from phoenix_engine.core.orchestrator import ChartOrchestrator
        orchestrator = ChartOrchestrator(req.config)

        result = orchestrator.run_birth_chart(
            name=req.name or "User",
            year=bd.year,
            month=bd.month,
            day=bd.day,
            hour=bd.hour,
            minute=bd.minute,
            second=bd.second if hasattr(bd, 'second') else 0,
            lat=bd.lat,
            lon=bd.lon,
            tz=bd.timezone  # Orchestrator will resolve via TimezoneFinder
        )

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
