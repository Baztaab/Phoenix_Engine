
from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.infrastructure.astronomy.swiss import SwissEphemeris
from phoenix_engine.domain.celestial import PlanetPosition

class PlanetaryPositionsPlugin(IChartPlugin):
    @property
    def name(self): return "Swiss Ephemeris Astronomy"

    def execute(self, ctx):
        # Engine requires JD
        if not hasattr(ctx, 'jd_ut') or ctx.jd_ut == 0:
             # Fallback if not set (though BirthEngine sets it)
             pass 
             
        swe = SwissEphemeris()
        
        # 1. Calc Planets
        # Note: ctx.input is BirthData. We use existing context JD.
        raw_planets = swe.calculate_planets(ctx.jd_ut)
        
        # 2. Calc Houses
        raw_houses = swe.calculate_houses_sidereal(ctx.jd_ut, ctx.input.lat, ctx.input.lon)
        
        # 3. Enrich & Store in Context
        ctx.ascendant = raw_houses['ascendant']
        ctx.houses = raw_houses['houses']
        ctx.analysis['ayanamsha'] = raw_houses['ayanamsa']
        
        # Convert raw dict to PlanetPosition models
        enriched_planets = {}
        asc_sign = int(ctx.ascendant / 30) + 1
        
        for name, data in raw_planets.items():
            p_house = (int(data['longitude'] / 30) + 1 - asc_sign) % 12 + 1
            if p_house <= 0: p_house += 12
            
            pp = PlanetPosition(
                id=data['id'],
                name=name,
                longitude=data['longitude'],
                speed=data['speed'],
                is_retrograde=data['is_retrograde'],
                sign=int(data['longitude'] / 30) + 1,
                sign_name="", # Can be filled by utility
                degree=data['longitude'] % 30,
                house=p_house,
                nakshatra=str(data['nakshatra']),
                nakshatra_pada=0
            )
            enriched_planets[name] = pp
            
        ctx.planets = enriched_planets
