from datetime import datetime
from typing import Any, Dict

import pytz
from timezonefinder import TimezoneFinder

from phoenix_engine.core.config import ChartConfig
from phoenix_engine.core.context import ChartContext
from phoenix_engine.core.factory import ChartFactory
from phoenix_engine.domain.input import BirthData
from phoenix_engine.engines.birth import BirthChartEngine
from phoenix_engine.infrastructure.time.manager import TimeEngine


class ChartOrchestrator:
    """
    Orchestrates the chart computation pipeline.
    Authority: Enforces Timezone Truth via Coordinates (Lat/Lon).
    """

    def __init__(self, config: ChartConfig):
        self.config = config
        self.tf = TimezoneFinder()  # The oracle of timezones

    def _resolve_utc_datetime(
        self,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        second: int,
        lat: float,
        lon: float,
    ) -> tuple[datetime, str]:
        """
        Private method to resolve strict UTC time from coordinates.
        Ignores user-provided timezone strings completely.
        Returns (dt_utc, resolved_timezone_str).
        """
        # 1. Determine Timezone from Geometry (The only truth)
        timezone_str = self.tf.timezone_at(lng=lon, lat=lat)
        if not timezone_str:
            # Fallback only if coordinates are in the middle of the ocean/unknown
            # Ideally raise error, but for stability we default to UTC
            timezone_str = "UTC"

        # 2. Localize the naive input
        local_tz = pytz.timezone(timezone_str)
        dt_naive = datetime(year, month, day, hour, minute, second)

        try:
            dt_aware = local_tz.localize(dt_naive)
        except Exception:
            # Handle non-existent times (DST gaps) strictly
            dt_aware = local_tz.localize(dt_naive, is_dst=None)

        # 3. Convert to Absolute UTC
        dt_utc = dt_aware.astimezone(pytz.UTC)

        return dt_utc, timezone_str

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
        tz: str | None = None,  # Deprecated argument, ignored logically
    ) -> Dict[str, Any]:
        """
        Execute the full birth chart pipeline.
        Standard: Coordinates determine Timezone. Output is calculated on UTC.
        """

        # Step 1: Resolve True UTC Time
        dt_utc, resolved_tz = self._resolve_utc_datetime(
            year, month, day, hour, minute, second, lat, lon
        )

        # Step 2: Inject UTC components into the Engine
        # NOTE: We pass the converted UTC year/month/day/time to the engine.
        # The engine must treat this as UTC (tz_offset=0).
        engine = BirthChartEngine(self.config)

        report = engine.calculate_natal_chart(
            year=dt_utc.year,
            month=dt_utc.month,
            day=dt_utc.day,
            hour=dt_utc.hour,
            minute=dt_utc.minute,
            second=dt_utc.second,
            lat=lat,
            lon=lon,
            name=name,
        )

        # Step 3: Enrich Meta with Truth
        report.setdefault("meta", {})
        report["meta"].update(
            {
                "name": name,
                "original_input": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}",
                "calculated_utc": dt_utc.isoformat(),
                "geo_timezone": resolved_tz,  # The resolved truth
                "location": {"lat": lat, "lon": lon},
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
        Refactored to use the new ChartContext class.
        """
        # Step 1: Resolve True UTC Time
        dt_utc, resolved_tz = self._resolve_utc_datetime(
            year, month, day, hour, minute, second, lat, lon
        )

        # Step 2: Prepare Strict Context
        # Create BirthData using the CALCULATED UTC time
        birth_data = BirthData(
            year=dt_utc.year,
            month=dt_utc.month,
            day=dt_utc.day,
            hour=dt_utc.hour,
            minute=dt_utc.minute,
            timezone="UTC",  # We are now strictly in UTC domain
            lat=lat,
            lon=lon,
        )

        # Instantiate the new Strong Context
        ctx = ChartContext(birth_data, self.config)
        ctx.name = name  # Supplemental attr
        ctx.resolved_timezone = resolved_tz
        ctx.year = dt_utc.year
        ctx.month = dt_utc.month
        ctx.day = dt_utc.day
        ctx.hour = dt_utc.hour
        ctx.minute = dt_utc.minute
        ctx.second = dt_utc.second
        ctx.latitude = lat
        ctx.longitude = lon
        ctx.target_year = target_year

        # Step 3: Initialize Time via TimeEngine
        time_engine = TimeEngine()
        # Ensure TimeEngine accepts the UTC datetime correctly
        ctx.jd_ut = time_engine.get_julian_day(dt_utc)

        # Inject Target Context
        # Note: target_year logic remains, assuming Tajaka calculates exact return
        ctx.analysis["target_year"] = target_year

        # Step 4: Execute Pipeline
        pipeline = ChartFactory.create_pipeline("ANNUAL", self.config)
        for plugin in pipeline:
            # Plugins now interact with a Class, not a Dict
            plugin.execute(ctx)

        return ctx.analysis
