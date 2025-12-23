from datetime import datetime
from typing import Dict, Any

import pytz

from phoenix_engine.core.config import ChartConfig
from phoenix_engine.engines.birth import BirthChartEngine
from phoenix_engine.core.factory import ChartFactory


class ChartOrchestrator:
    """
    Orchestrates the chart computation pipeline for CLI or other callers.
    """

    def __init__(self, config: ChartConfig):
        self.config = config

    def run_birth_chart(
        self,
        name: str,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        second: int,
        lat: float,
        lon: float,
        tz: str | None = None,
    ) -> Dict[str, Any]:
        """
        Execute the full birth chart pipeline with second-level precision.
        If a timezone is provided, the datetime is localized to handle DST correctly.
        """
        dt_naive = datetime(year, month, day, hour, minute, second)
        if tz:
            try:
                tzinfo = pytz.timezone(tz)
                dt_aware = tzinfo.localize(dt_naive)
            except Exception:
                dt_aware = dt_naive.replace(tzinfo=pytz.UTC)
        else:
            dt_aware = dt_naive.replace(tzinfo=pytz.UTC)

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

        report.setdefault("meta", {})
        report["meta"].update(
            {
                "name": name,
                "birth_date": f"{year:04d}-{month:02d}-{day:02d}",
                "birth_time": f"{hour:02d}:{minute:02d}:{second:02d}",
                "location": {"lat": lat, "lon": lon},
                "timezone": tz or "UTC",
                "ayanamsa": getattr(self.config, "ayanamsa", "LAHIRI"),
            }
        )

        return report

    def run_annual_forecast(
        self,
        name: str,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        second: int,
        lat: float,
        lon: float,
        target_year: int,
        tz: str | None = None,
    ) -> Dict[str, Any]:
        """
        Execute the annual (Varshaphal) pipeline.
        """
        # Build aware datetime
        dt_naive = datetime(year, month, day, hour, minute, second)
        if tz:
            try:
                tzinfo = pytz.timezone(tz)
                dt_aware = tzinfo.localize(dt_naive)
            except Exception:
                dt_aware = dt_naive.replace(tzinfo=pytz.UTC)
        else:
            dt_aware = dt_naive.replace(tzinfo=pytz.UTC)

        # Prepare context (ChartContext) similar to BirthChartEngine
        from phoenix_engine.domain.input import BirthData
        from phoenix_engine.core.context import ChartContext
        from phoenix_engine.infrastructure.time.manager import TimeEngine

        birth_data = BirthData(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            timezone=str(dt_aware.tzinfo),
            lat=lat,
            lon=lon,
        )
        ctx = ChartContext(birth_data, self.config)
        time_engine = TimeEngine()
        ctx.jd_ut = time_engine.get_julian_day(dt_aware)
        ctx.target_year = target_year
        # Expose basic fields for plugins expecting direct attrs
        ctx.year = year
        ctx.month = month
        ctx.day = day
        ctx.hour = hour
        ctx.minute = minute
        ctx.second = second
        ctx.latitude = lat
        ctx.longitude = lon
        ctx.name = name

        pipeline = ChartFactory.create_pipeline("ANNUAL", self.config)
        for plugin in pipeline:
            plugin.execute(ctx)

        return ctx.analysis
