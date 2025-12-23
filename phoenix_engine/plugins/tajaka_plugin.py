from datetime import datetime

from phoenix_engine.core.context import ChartContext
from phoenix_engine.core.factory import ChartFactory
from phoenix_engine.vedic.calculations.tajaka.tajaka_engine import TajakaEngine


class TajakaPlugin:
    """
    Connects the annual (Varshaphal) Tajaka engine to the pipeline.
    Handles ascendant data whether dict or numeric.
    """

    def __init__(self, config):
        self.config = config
        self.name = "Tajaka Annual Analysis Plugin"

    def execute(self, context: ChartContext):
        print(f"   ... Executing {self.name} ...")

        # 1) Target year
        target_year = getattr(context, "target_year", None)
        if not target_year:
            target_year = datetime.now().year

        # 2) Normalize ascendant
        asc_data = getattr(context, "ascendant", {})
        if not isinstance(asc_data, dict):
            try:
                lon = float(asc_data)
                asc_data = {"longitude": lon, "sign_id": int(lon / 30.0) + 1, "sign_name": "Derived"}
            except Exception:
                asc_data = {"longitude": 0.0, "sign_id": 1, "sign_name": "Aries"}

        # 3) Build natal data package for TajakaEngine
        natal_data = {
            "meta": {
                "jd": getattr(context, "jd", getattr(context, "jd_ut", 0.0)),
                "birth_date": f"{getattr(context, 'year', 0)}-{getattr(context, 'month', 0)}-{getattr(context, 'day', 0)}",
                "location": {"lat": getattr(context, "latitude", 0.0), "lon": getattr(context, "longitude", 0.0)},
                "birth_year": getattr(context, "year", 0),
            },
            "planets": context.analysis.get("planets", {}),
            "houses": context.analysis.get("houses", {}),
            "ascendant": asc_data,
        }

        # 4) Run Tajaka engine
        factory_instance = ChartFactory()
        engine = TajakaEngine(chart_factory=factory_instance)

        try:
            annual_report = engine.generate_annual_report(natal_data, target_year)
            context.analysis["varshaphal"] = annual_report
        except Exception as e:
            print(f"   ❌ Error inside Tajaka Engine: {e}")
            import traceback

            traceback.print_exc()
