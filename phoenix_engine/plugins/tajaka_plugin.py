from typing import Any, Dict

from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.core.context import ChartContext
from phoenix_engine.core.factory import ChartFactory
from phoenix_engine.vedic.calculations.tajaka.tajaka_engine import TajakaEngine


class TajakaChartPlugin(IChartPlugin):
    """
    Annual Return (Varshaphal) Analyzer.
    Requires a populated Birth Context (Planets & Houses) to find the exact solar return.
    """

    def __init__(self, config):
        self.config = config

    @property
    def name(self):
        return "Tajaka (Annual) Engine"

    def execute(self, ctx: ChartContext):
        print(f"   ... Executing {self.name} ...")

        if not ctx.planets:
            raise ValueError("[Kai/Error]: Cannot calculate Tajaka. Birth planets are missing from Context.")

        natal_sun = ctx.get_planet("Sun")
        if not natal_sun:
            raise ValueError("[Kai/Error]: Sun not found in birth chart context.")

        natal_sun_lon = natal_sun.longitude

        target_year = ctx.analysis.get("target_year") or getattr(ctx, "target_year", None) or ctx.birth_data.year

        asc_struct = self._get_ascendant_struct(ctx)
        houses_struct = self._get_houses_struct(ctx)
        planets_struct = self._get_planets_struct(ctx)
        if not houses_struct:
            raise ValueError("[Kai/Error]: Houses are missing from Context.")

        natal_data = {
            "meta": {
                "jd": getattr(ctx, "jd", ctx.jd_ut),
                "birth_date": f"{ctx.birth_data.year:04d}-{ctx.birth_data.month:02d}-{ctx.birth_data.day:02d}",
                "birth_year": ctx.birth_data.year,
                "location": {"lat": ctx.birth_data.lat, "lon": ctx.birth_data.lon},
            },
            "planets": planets_struct,
            "houses": houses_struct,
            "ascendant": asc_struct,
        }

        factory_instance = ChartFactory()
        engine = TajakaEngine(chart_factory=factory_instance)

        try:
            annual_report = engine.generate_annual_report(natal_data, target_year)
            ctx.analysis["varshaphal"] = annual_report
            ctx.analysis["tajaka"] = annual_report
            ctx.analysis.setdefault("meta", {})["target_year"] = target_year
            ctx.analysis["tajaka"].setdefault("meta", {}).update(
                {
                    "solar_return_year": target_year,
                    "natal_sun_reference": round(natal_sun_lon, 4),
                }
            )
            print(f"   >>> [Kai/Audit]: Tajaka Report Generated for Year {target_year}.")
        except Exception as e:
            print(f"   ? Error inside Tajaka Engine: {e}")
            import traceback

            traceback.print_exc()

    def _get_ascendant_struct(self, ctx: ChartContext) -> Dict[str, Any]:
        asc_data = ctx.analysis.get("ascendant")
        if isinstance(asc_data, dict) and "sign_id" in asc_data:
            return asc_data

        try:
            lon = float(ctx.ascendant)
            return {"longitude": lon, "sign_id": int(lon / 30.0) + 1, "sign_name": "Derived"}
        except Exception:
            return {"longitude": 0.0, "sign_id": 1, "sign_name": "Aries"}

    def _get_houses_struct(self, ctx: ChartContext) -> Dict[int, Dict[str, Any]]:
        houses = ctx.analysis.get("houses")
        if isinstance(houses, dict) and houses:
            return houses

        houses_struct: Dict[int, Dict[str, Any]] = {}
        if isinstance(ctx.houses, (list, tuple)):
            for idx, cusp in enumerate(ctx.houses, start=1):
                sign_id = int(float(cusp) / 30) + 1
                houses_struct[idx] = {
                    "longitude": float(cusp),
                    "sign_id": sign_id,
                    "sign_name": self._sign_name(sign_id),
                }
        return houses_struct

    def _get_planets_struct(self, ctx: ChartContext) -> Dict[str, Dict[str, Any]]:
        planets_struct: Dict[str, Dict[str, Any]] = {}

        for name, p in ctx.planets.items():
            sign_name = p.sign_name or self._sign_name(p.sign)
            planets_struct[name] = {
                "name": name,
                "longitude": p.longitude,
                "degree": p.degree,
                "sign_id": p.sign,
                "sign_name": sign_name,
                "speed": p.speed,
                "is_retrograde": p.is_retrograde,
                "house": p.house,
                "coordinates": {
                    "longitude": p.longitude,
                    "degree_in_sign": p.degree,
                    "sign_id": p.sign,
                    "sign_name": sign_name,
                    "speed": p.speed,
                    "is_retro": p.is_retrograde,
                },
            }

        return planets_struct

    def _sign_name(self, sign_id: int) -> str:
        signs = [
            "Aries",
            "Taurus",
            "Gemini",
            "Cancer",
            "Leo",
            "Virgo",
            "Libra",
            "Scorpio",
            "Sagittarius",
            "Capricorn",
            "Aquarius",
            "Pisces",
        ]
        return signs[(sign_id - 1) % 12]


# Backwards compatibility for ChartFactory import
class TajakaPlugin(TajakaChartPlugin):
    pass
