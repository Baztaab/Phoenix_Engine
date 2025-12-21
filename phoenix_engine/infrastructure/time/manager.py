
from datetime import datetime
import pytz
import swisseph as swe

# Exceptions required by App
class AmbiguousTimeError(ValueError): pass
class NonExistentTimeError(ValueError): pass

def localize_strict(dt_naive: datetime, tz_str: str) -> datetime:
    try:
        tz = pytz.timezone(tz_str)
        # is_dst=None raises errors for ambiguous times, which is what we want for precision
        return tz.localize(dt_naive, is_dst=None)
    except pytz.UnknownTimeZoneError:
        raise ValueError(f"Unknown timezone: {tz_str}")
    except pytz.AmbiguousTimeError:
        raise AmbiguousTimeError(f"Ambiguous time in {tz_str} (DST transition)")
    except pytz.NonExistentTimeError:
        raise NonExistentTimeError(f"Time does not exist in {tz_str} (DST gap)")

class TimeEngine:
    def get_julian_day(self, dt_aware: datetime) -> float:
        # Convert to UTC
        dt_utc = dt_aware.astimezone(pytz.UTC)
        # Calculate decimal hour
        ut_hour = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
        # Compute JD (Julian Day)
        return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, ut_hour, swe.GREG_CAL)
