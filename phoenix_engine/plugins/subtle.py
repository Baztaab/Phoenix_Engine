from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.infrastructure.astronomy.swiss import SwissEphemeris
from phoenix_engine.vedic.calculations.upagraha import UpagrahaEngine
from phoenix_engine.vedic.calculations.special_lagnas import SpecialLagnaEngine
from phoenix_engine.domain.celestial import PlanetPosition


class SubtleBodiesPlugin(IChartPlugin):
    @property
    def name(self): return "Invisible Bodies & Special Lagnas"

    def execute(self, ctx):
        swe = SwissEphemeris()
        
        # 1. Sun-based Upagrahas
        # FIX: Check if Sun exists
        if 'Sun' in ctx.planets:
            sun_lon = ctx.planets['Sun'].longitude
            sun_upas = UpagrahaEngine.calculate_sun_upagrahas(sun_lon)
            for name, lon in sun_upas.items():
                self._add_body(ctx, name, lon, "Upagraha")
        
        # 2. Time-based Upagrahas (Mandi/Gulika)
        # FIX: Handle rise/set failure gracefully
        sunrise_jd, sunset_jd = swe.get_rise_set(ctx.jd_ut, ctx.input.lat, ctx.input.lon)
        
        # Calculate Panchanga (Phase 2 Upgrade)
        try:
            from phoenix_engine.vedic.calculations.panchanga import PanchangaEngine
            if 'Sun' in ctx.planets and 'Moon' in ctx.planets:
                sun_lon = ctx.planets['Sun'].longitude
                moon_lon = ctx.planets['Moon'].longitude
                panchanga_data = PanchangaEngine.calculate_panchanga(
                    ctx.jd_ut, sun_lon, moon_lon, sunrise_jd
                )
                ctx.analysis['panchanga'] = panchanga_data
        except Exception:
            pass
        
        # If calculation failed (0.0), we can't compute accurate Mandi/Gulika
        # But UpagrahaEngine now handles 0.0 safely.
        wd_idx = int(ctx.jd_ut + 1.5) % 7
        kuta_times = UpagrahaEngine.calculate_kalavela(ctx.jd_ut, sunrise_jd, sunset_jd, wd_idx)
        
        for k_name, k_jd in kuta_times.items():
            if k_jd == 0.0: continue # Skip if invalid
            res = swe.calculate_houses_sidereal(k_jd, ctx.input.lat, ctx.input.lon)
            body_name = k_name.replace("_JD", "")
            self._add_body(ctx, body_name, res['ascendant'], "Upagraha")
            
        # 3. Special Lagnas
        # Need accurate sunrise for HL/GL
        if sunrise_jd > 0:
            dt_diff_days = ctx.jd_ut - sunrise_jd
            hours_since_rise = dt_diff_days * 24.0
            
            # Sun position at Sunrise
            # We calc it specifically for sunrise moment
            try:
                sun_rise_data = swe.calculate_planets(sunrise_jd)
                sun_rise_pos = sun_rise_data['Sun']['longitude'] if 'Sun' in sun_rise_data else 0.0
                
                hl = SpecialLagnaEngine.calculate_hora_lagna(sun_rise_pos, hours_since_rise)
                gl = SpecialLagnaEngine.calculate_ghati_lagna(sun_rise_pos, hours_since_rise)
                
                self._add_body(ctx, "Hora Lagna", hl, "Special Lagna")
                self._add_body(ctx, "Ghati Lagna", gl, "Special Lagna")
            except Exception:
                pass # Skip special lagnas on error

        # 4. Points
        if 'Moon' in ctx.planets and 'Rahu' in ctx.planets:
            bb = SpecialLagnaEngine.calculate_bhrigu_bindu(ctx.planets['Moon'].longitude, ctx.planets['Rahu'].longitude)
            self._add_body(ctx, "Bhrigu Bindu", bb, "Point")
            
        if 'Sun' in ctx.planets and 'Moon' in ctx.planets:
            yogi_data = SpecialLagnaEngine.calculate_yogi_point(ctx.planets['Sun'].longitude, ctx.planets['Moon'].longitude)
            self._add_body(ctx, "Yogi Point", yogi_data['Yoga_Point'], "Point")
            ctx.analysis['yogi_info'] = {"yogi": yogi_data['Yogi'], "avayogi": yogi_data['Avayogi']}

    def _add_body(self, ctx, name, lon, type_tag):
        sign_id = int(lon / 30) + 1
        asc_sign = int(ctx.ascendant / 30) + 1
        house = (sign_id - asc_sign) % 12 + 1
        if house <= 0: house += 12
        
        ctx.planets[name] = PlanetPosition(
            id=900, name=name, longitude=lon, speed=0, is_retrograde=False,
            sign=sign_id, sign_name="", degree=lon % 30, house=house,
            nakshatra=str(int(lon / 13.3333)+1), nakshatra_pada=0
        )
