from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.core.context import ChartContext
from phoenix_engine.infrastructure.astronomy.swiss import SwissEphemerisEngine
from phoenix_engine.domain.celestial import PlanetPosition


class BirthChartPlugin(IChartPlugin):
    """
    The Genesis Plugin.
    Calculates planetary positions and house cusps based on strict UTC time.
    Populates the ChartContext with high-fidelity celestial objects.
    """

    def __init__(self, config):
        self.config = config

    @property
    def name(self):
        return "Birth Chart Calculator"

    def execute(self, ctx: ChartContext):
        print(f"   ... Executing {self.name} ...")

        if not getattr(ctx, "jd_ut", 0):
            raise ValueError("ChartContext.jd_ut is missing. TimeEngine must set it before BirthChartPlugin.")

        astro_engine = SwissEphemerisEngine(ctx.config)

        # Calculate Houses & Ascendant first (needed for planet house assignment)
        houses_data = astro_engine.calculate_houses(
            jd_ut=ctx.jd_ut,
            lat=ctx.birth_data.lat,
            lon=ctx.birth_data.lon,
            system=getattr(ctx.config, "house_system", "P"),
        )
        ascendant = houses_data["ascendant"]
        asc_sign = int(ascendant / 30) + 1

        # Calculate Planets (Swiss Ephemeris, sidereal)
        raw_planets = astro_engine.calculate_planets(
            jd_ut=ctx.jd_ut,
            lat=ctx.birth_data.lat,
            lon=ctx.birth_data.lon,
            asc_sign=asc_sign,
        )

        planet_objects = []
        for p_data in raw_planets:
            planet_objects.append(PlanetPosition(**p_data))

        # Inject Planets & Houses into Context
        ctx.set_planets(planet_objects)
        ctx.set_houses(cusps=houses_data["cusps"], ascendant=ascendant)

        # Structured houses for downstream consumers (e.g., TajakaEngine)
        houses_struct = houses_data.get("houses_struct", {})
        asc_struct = {
            "longitude": ascendant,
            "sign_id": asc_sign,
            "sign_name": astro_engine.sign_name(asc_sign),
        }

        # Analysis payload (JSON-friendly)
        ctx.analysis["planets"] = {p.name: p.model_dump() for p in planet_objects}
        ctx.analysis["houses"] = houses_struct
        ctx.analysis["ascendant"] = asc_struct
        ctx.analysis.setdefault("meta", {})["ayanamsa"] = houses_data.get("ayanamsa")

        print(f"   >>> [Kai/Audit]: Birth Chart Calculated. {len(planet_objects)} bodies injected.")
