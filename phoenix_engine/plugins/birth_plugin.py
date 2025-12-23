import swisseph as swe  # For weekday calculations

from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.core.context import ChartContext
from phoenix_engine.infrastructure.astronomy.swiss import SwissEphemerisEngine, SwissEphemeris
from phoenix_engine.domain.celestial import PlanetPosition
from phoenix_engine.vedic.calculations.upagraha import UpagrahaEngine


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

        # Inject Upagrahas (Gulika, Mandi, Sun-derived points)
        self._inject_upagrahas(ctx, asc_sign)

        # Refresh analysis planets with injected upagrahas
        ctx.analysis["planets"] = {name: p.model_dump() for name, p in ctx.planets.items()}

        print(f"   >>> [Kai/Audit]: Birth Chart Calculated. {len(ctx.planets)} bodies injected (including upagrahas).")

    def _inject_upagrahas(self, ctx: ChartContext, asc_sign: int):
        """
        Calculates Gulika, Mandi, and Sun-based Upagrahas and injects them into ctx.planets.
        """
        sw = SwissEphemeris(getattr(ctx.config, "ephemeris_path", None))

        # Sun-based Upagrahas
        sun = ctx.get_planet("Sun")
        if sun:
            sun_upas = UpagrahaEngine.calculate_sun_upagrahas(sun.longitude)
            for name, lon in sun_upas.items():
                sign_id = int(lon / 30) + 1
                house_num = (sign_id - asc_sign) % 12 + 1
                upa = PlanetPosition(
                    id=900 + len(name),
                    name=name,
                    longitude=lon,
                    speed=0.0,
                    is_retrograde=False,
                    sign=sign_id,
                    sign_name="",
                    degree=lon % 30,
                    house=house_num,
                    nakshatra="",
                    nakshatra_pada=0,
                )
                ctx.planets[name] = upa

        # Time-based Upagrahas (Gulika, Mandi)
        rise_jd, set_jd = sw.get_rise_set(ctx.jd_ut, ctx.birth_data.lat, ctx.birth_data.lon)
        dow = swe.day_of_week(ctx.jd_ut)  # 0=Sunday
        times = UpagrahaEngine.calculate_kalavela_times(ctx.jd_ut, rise_jd, set_jd, dow)

        gulika_lon = sw.get_ascendant(times["Gulika_JD"], ctx.birth_data.lat, ctx.birth_data.lon)
        mandi_lon = sw.get_ascendant(times["Mandi_JD"], ctx.birth_data.lat, ctx.birth_data.lon)

        for name, lon, pid in [("Gulika", gulika_lon, 990), ("Mandi", mandi_lon, 991)]:
            sign_id = int(lon / 30) + 1
            house_num = (sign_id - asc_sign) % 12 + 1
            ctx.planets[name] = PlanetPosition(
                id=pid,
                name=name,
                longitude=lon,
                speed=0.0,
                is_retrograde=False,
                sign=sign_id,
                sign_name="",
                degree=lon % 30,
                house=house_num,
                nakshatra="",
                nakshatra_pada=0,
            )

        print(
            f"   >>> [Kai/Upagraha]: Gulika {gulika_lon:.2f} (JD {times['Gulika_JD']:.4f}), "
            f"Mandi {mandi_lon:.2f} (JD {times['Mandi_JD']:.4f})"
        )
