import swisseph as swe

from phoenix_engine.core.context import ChartContext
from phoenix_engine.infrastructure.astronomy.swiss import SwissEphemeris
from phoenix_engine.vedic.calculations.panchanga import PanchangaEngine


class SpecialLagnaEngine:
    """
    Calculates Special Lagnas:
    1. Bhava Lagna (BL)
    2. Hora Lagna (HL)
    3. Ghati Lagna (GL)
    4. Sree Lagna (SL)

    Ref: JHora / Drik Siddhanta.
    """

    def __init__(self, config):
        self.config = config
        self.sw_engine = SwissEphemeris(getattr(config, 'ephemeris_path', None))

    def calculate_all(self, ctx: ChartContext):
        jd = ctx.jd_ut
        lat = ctx.birth_data.lat
        lon = ctx.birth_data.lon

        # 1. Get Sunrise (Vedic flags)
        res_rise = swe.rise_trans(
            tjd=jd - (5.5 / 24.0),
            body=swe.SUN,
            geopos=(lon, lat, 0.0),
            rsmi=PanchangaEngine.VEDIC_RISE_FLAGS + swe.CALC_RISE
        )
        sunrise_jd = res_rise[1][0]

        time_diff_hours = (jd - sunrise_jd) * 24.0
        if time_diff_hours < 0:
            time_diff_hours += 24.0

        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        sun_res = swe.calc_ut(sunrise_jd, swe.SUN, flags)
        sun_rise_lon = sun_res[0][0]

        time_diff_mins = time_diff_hours * 60.0

        bl_lon = (sun_rise_lon + (time_diff_mins * 0.25)) % 360
        hl_lon = (sun_rise_lon + (time_diff_mins * 0.50)) % 360
        gl_lon = (sun_rise_lon + (time_diff_mins * 1.25)) % 360

        moon = ctx.get_planet("Moon")
        asc = ctx.ascendant

        nak_span = 360.0 / 27.0
        rem = moon.longitude % nak_span if moon else 0.0
        sl_lon = (asc + (rem * 27.0)) % 360

        return {
            "Bhava Lagna": bl_lon,
            "Hora Lagna": hl_lon,
            "Ghati Lagna": gl_lon,
            "Sree Lagna": sl_lon
        }
