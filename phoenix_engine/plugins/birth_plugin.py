from datetime import datetime
import pytz

from phoenix_engine.core.context import ChartContext
from phoenix_engine.engines.birth import BirthChartEngine


class BirthChartPlugin:
    """
    Birth chart analysis plugin.
    Runs BirthChartEngine and stores results back into the context.
    """

    def __init__(self, config):
        self.config = config
        self.name = "Birth Chart Analysis Plugin"

    def execute(self, context: ChartContext):
        print(f"   ... Executing {self.name} ...")

        # Gather inputs (support both ChartContext and custom contexts)
        year = getattr(context, "year", getattr(context.input, "year", 0))
        month = getattr(context, "month", getattr(context.input, "month", 0))
        day = getattr(context, "day", getattr(context.input, "day", 0))
        hour = getattr(context, "hour", getattr(context.input, "hour", 0))
        minute = getattr(context, "minute", getattr(context.input, "minute", 0))
        second = getattr(context, "second", 0)
        lat = getattr(context, "latitude", getattr(context.input, "lat", 0.0))
        lon = getattr(context, "longitude", getattr(context.input, "lon", 0.0))
        name = getattr(context, "name", "User")

        # Run pure calculation engine
        engine = BirthChartEngine(self.config)
        report = engine.calculate_natal_chart(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            lat=lat,
            lon=lon,
            name=name,
        )

        # Persist JD if available
        context.jd_ut = report.get("meta", {}).get("jd", getattr(context, "jd_ut", 0.0))

        # Store core fields for downstream plugins
        context.ascendant = report.get("ascendant", getattr(context, "ascendant", 0.0))
        context.houses = report.get("houses", getattr(context, "houses", []))
        context.planets = report.get("planets", getattr(context, "planets", {}))

        # Merge analysis/results
        context.analysis.update(report)
