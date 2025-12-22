from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.infrastructure.astronomy.swiss import SwissEphemeris
from phoenix_engine.vedic.calculations.upagraha import UpagrahaEngine
from phoenix_engine.vedic.calculations.special_lagnas import SpecialLagnaEngine
from phoenix_engine.domain.celestial import PlanetPosition


class SubtleBodiesPlugin(IChartPlugin):
    @property
    def name(self): return "Invisible Bodies & Special Lagnas"

    def execute(self, ctx):
        # 1. Init Helpers
        swe = SwissEphemeris()
        
        # 2. Sun-based Upagrahas (Dhooma etc.)
        sun = ctx.planets['Sun'].longitude
        sun_upas = UpagrahaEngine.calculate_sun_upagrahas(sun)
        
        # Add to planets list
        for name, lon in sun_upas.items():
            self._add_body(ctx, name, lon, "Upagraha")
            
        # 3. Time-based Upagrahas (Mandi, Gulika)
        # Need Sunrise/Sunset
        sunrise_jd, sunset_jd = swe.get_rise_set(ctx.jd_ut, ctx.input.lat, ctx.input.lon)
        
        # Weekday (0=Mon...6=Sun in Python? No, swe.julday gives JD. 
        # Need day of week from JD. (JD + 1.5) % 7 -> 0=Sun, 1=Mon...)
        wd_idx = int(ctx.jd_ut + 1.5) % 7
        
        kuta_times = UpagrahaEngine.calculate_kalavela(ctx.jd_ut, sunrise_jd, sunset_jd, wd_idx)
        
        # Calculate Ascendant for these times (Mandi/Gulika positions)
        for k_name, k_jd in kuta_times.items():
            # Calculate Ascendant at that specific moment
            res = swe.calculate_houses_sidereal(k_jd, ctx.input.lat, ctx.input.lon)
            body_name = k_name.replace("_JD", "") # Gulika, Mandi
            self._add_body(ctx, body_name, res['ascendant'], "Upagraha")
            
        # 4. Special Lagnas (HL, GL)
        # Need time elapsed since sunrise in Hours
        # If born before sunrise, need logic. Simplified: abs diff
        dt_diff_days = ctx.jd_ut - sunrise_jd
        # Normalize if negative (birth before sunrise, same day logic?)
        # Usually handled by Sunrise of the day.
        hours_since_rise = dt_diff_days * 24.0
        
        # Get Sun position exactly at Sunrise (for HL/GL base)
        sun_rise_pos = swe.calculate_planets(sunrise_jd)['Sun']['longitude']
        
        hl = SpecialLagnaEngine.calculate_hora_lagna(sun_rise_pos, hours_since_rise)
        gl = SpecialLagnaEngine.calculate_ghati_lagna(sun_rise_pos, hours_since_rise)
        
        self._add_body(ctx, "Hora Lagna", hl, "Special Lagna")
        self._add_body(ctx, "Ghati Lagna", gl, "Special Lagna")
        
        # 5. Bhrigu Bindu
        bb = SpecialLagnaEngine.calculate_bhrigu_bindu(ctx.planets['Moon'].longitude, ctx.planets['Rahu'].longitude)
        self._add_body(ctx, "Bhrigu Bindu", bb, "Point")
        
        # 6. Yogi/Avayogi
        yogi_data = SpecialLagnaEngine.calculate_yogi_point(sun, ctx.planets['Moon'].longitude)
        self._add_body(ctx, "Yogi Point", yogi_data['Yoga_Point'], "Point")
        
        # Store Meta info about Yogi planet
        ctx.analysis['yogi_info'] = {
            "yogi_planet": yogi_data['Yogi'],
            "avayogi_planet": yogi_data['Avayogi']
        }

    def _add_body(self, ctx, name, lon, type_tag):
        # Helper to inject into ctx.planets
        sign_id = int(lon / 30) + 1
        asc_sign = int(ctx.ascendant / 30) + 1
        house = (sign_id - asc_sign) % 12 + 1
        if house <= 0: house += 12
        
        # Dummy speed/retro for points
        ctx.planets[name] = PlanetPosition(
            id=900, # Mock ID
            name=name,
            longitude=lon,
            speed=0,
            is_retrograde=False,
            sign=sign_id,
            sign_name="",
            degree=lon % 30,
            house=house,
            nakshatra=str(int(lon / 13.3333)+1),
            nakshatra_pada=0
        )
