
from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.vedic.calculations.strength import ShadbalaEngine
from phoenix_engine.vedic.calculations.bhava_bala import BhavaBalaEngine
from phoenix_engine.vedic.calculations.avastha import AvasthaEngine
from phoenix_engine.vedic.calculations.phala import PhalaEngine
from phoenix_engine.domain.analysis import ShadbalaInfo

class StrengthPlugin(IChartPlugin):
    @property
    def name(self): return "Planetary Strengths"

    def execute(self, ctx):
        # 1. Shadbala
        shadbala_models = None
        if ctx.config.output.include_shadbala:
            raw = ShadbalaEngine.calculate_shadbala(ctx.planets, ctx.ascendant)
            shadbala_models = {k: ShadbalaInfo(**v) for k, v in raw.items()}
            ctx.analysis['shadbala'] = shadbala_models

        # 2. Avasthas
        if ctx.config.output.include_avasthas:
            ctx.analysis['avasthas'] = AvasthaEngine.calculate_all(ctx.planets)

        # 3. Bhava Bala (Requires Shadbala & Aspects - assuming Aspects are done or skipped for now)
        if ctx.config.output.include_bhavabala and shadbala_models:
            # Note: Aspects logic needs to be ported to a plugin or passed here. 
            # For now, passing None/Empty for aspects to avoid crash if not ready.
            ctx.analysis['bhava_bala'] = BhavaBalaEngine.calculate_all(ctx.houses, ctx.planets, shadbala_models, [])
            
        # 4. Phala
        if ctx.config.output.include_phala and shadbala_models:
             ctx.analysis['phala'] = PhalaEngine.calculate(ctx.planets, shadbala_models)
