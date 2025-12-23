from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.vedic.calculations.yogas.parasari_yogas import ParasariYogaEngine
from phoenix_engine.core.context import ChartContext


class ParasariYogasPlugin(IChartPlugin):
    @property
    def name(self):
        return "Parasari Raja Yogas (Phase 5.5)"

    def execute(self, ctx: ChartContext):
        if 'yogas' not in ctx.analysis:
            ctx.analysis['yogas'] = []

        asc_sign = int(ctx.ascendant / 30) + 1

        # Adapter: convert PlanetPosition objects to legacy dict format
        adapted_planets = {
            name: {
                "longitude": p.longitude,
                "speed": p.speed,
                "house": p.house,
                "is_retrograde": p.is_retrograde,
            }
            for name, p in ctx.planets.items()
        }

        parasari_list = ParasariYogaEngine.calculate_yogas(asc_sign, adapted_planets)

        ctx.analysis['parasari_yogas'] = parasari_list
