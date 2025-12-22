import math
import swisseph as swe
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from phoenix_engine.vedic.calculations.varga import VargaEngine
from phoenix_engine.vedic.calculations.maitri import MaitriEngine
from phoenix_engine.vedic.const import SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN


class ShadbalaEngine:
    """
    موتور محاسبه Shadbala (قدرت شش‌گانه) - پورت شده از JHora (نسخه ساده‌شده).
    """
    
    EXALTATION_POINTS = {
        "Sun": 10, "Moon": 33, "Mars": 298, "Mercury": 165,
        "Jupiter": 95, "Venus": 357, "Saturn": 200
    }
    
    MIN_REQ_RUPAS = {
        "Sun": 6.5, "Moon": 6.0, "Mars": 5.0, "Mercury": 7.0,
        "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5.0
    }
    
    PLANET_NAMES_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

    # -------------------------------------------------------------------------
    # 1. STHANA BALA
    # -------------------------------------------------------------------------
    @staticmethod
    def _uchcha_bala(p_name: str, p_lon: float) -> float:
        deep_exalt = ShadbalaEngine.EXALTATION_POINTS.get(p_name, 0)
        diff = abs(p_lon - deep_exalt)
        if diff > 180:
            diff = 360 - diff
        return (180.0 - diff) / 3.0

    @staticmethod
    def _saptavargaja_bala(p_name: str, vargas: Dict[str, int], compound_rels: Dict[str, str]) -> float:
        score_map = {
            "Own": 30.0, "Adhi Mitra": 22.5, "Mitra": 15.0,
            "Sama": 7.5, "Satru": 3.75, "Adhi Satru": 1.875
        }
        required_vargas = ["D1", "D2", "D3", "D7", "D9", "D12", "D30"]
        total_score = 0.0
        rulers = {1:"Mars", 2:"Venus", 3:"Mercury", 4:"Moon", 5:"Sun", 6:"Mercury", 
                  7:"Venus", 8:"Mars", 9:"Jupiter", 10:"Saturn", 11:"Saturn", 12:"Jupiter"}

        for v_code in required_vargas:
            p_sign = vargas.get(v_code, 1)
            lord_name = rulers.get(p_sign)
            if lord_name == p_name:
                rel = "Own"
            else:
                rel = compound_rels.get(lord_name, "Sama")
            total_score += score_map.get(rel, 7.5)
        return total_score

    @staticmethod
    def _ojayugma_bala(p_name: str, vargas: Dict[str, int]) -> float:
        male_planets = ["Sun", "Mars", "Jupiter", "Mercury"]
        score = 0.0
        for chart in ["D1", "D9"]:
            sign = vargas.get(chart, 1)
            is_odd = (sign % 2 != 0)
            if p_name in male_planets:
                if is_odd:
                    score += 15
            else:
                if not is_odd:
                    score += 15
        return score

    @staticmethod
    def _kendra_bala(p_sign_d1: int, asc_sign_d1: int) -> float:
        h_num = (p_sign_d1 - asc_sign_d1 + 1)
        if h_num <= 0:
            h_num += 12
        if h_num in [1, 4, 7, 10]:
            return 60.0
        if h_num in [2, 5, 8, 11]:
            return 30.0
        return 15.0

    # -------------------------------------------------------------------------
    # 2. DIG BALA
    # -------------------------------------------------------------------------
    @staticmethod
    def _dig_bala(p_name: str, p_lon: float, asc_lon: float) -> float:
        targets = {
            "Sun": 270, "Mars": 270,
            "Moon": 90, "Venus": 90,
            "Saturn": 180,
            "Mercury": 0, "Jupiter": 0
        }
        target_offset = targets.get(p_name, 0)
        target_lon = (asc_lon + target_offset) % 360
        diff = abs(p_lon - target_lon)
        if diff > 180:
            diff = 360 - diff
        return (180.0 - diff) / 3.0

    # -------------------------------------------------------------------------
    # 3. KAALA BALA
    # -------------------------------------------------------------------------
    @staticmethod
    def _natonnata_bala(p_name: str, is_day: bool) -> float:
        if p_name == "Mercury":
            return 60.0
        if p_name in ["Moon", "Mars", "Saturn"]:
            return 60.0 if not is_day else 0.0
        return 60.0 if is_day else 0.0

    @staticmethod
    def _paksha_bala(p_name: str, moon_lon: float, sun_lon: float) -> float:
        angle = (moon_lon - sun_lon) % 360
        if angle > 180:
            angle = 360 - angle
        score = (angle / 180.0) * 60.0
        benefics = ["Jupiter", "Venus", "Moon", "Mercury"]
        return score if p_name in benefics else (60.0 - score)

    @staticmethod
    def _lord_balas(p_name: str, lords: Dict[str, str]) -> float:
        score = 0.0
        if lords.get("Year") == p_name:
            score += 15
        if lords.get("Month") == p_name:
            score += 30
        if lords.get("Day") == p_name:
            score += 45
        if lords.get("Hora") == p_name:
            score += 60
        return score

    # -------------------------------------------------------------------------
    # 4. CHESTA BALA
    # -------------------------------------------------------------------------
    @staticmethod
    def _chesta_bala(p_name: str) -> float:
        # Placeholder simplified: planets other than Sun/Moon get 30
        if p_name in ["Sun", "Moon"]:
            return 0.0
        return 30.0

    # -------------------------------------------------------------------------
    # 5. NAISARGIKA
    # -------------------------------------------------------------------------
    @staticmethod
    def _naisargika_bala(p_name: str) -> float:
        vals = {
            "Sun": 60.0, "Moon": 51.43, "Mars": 17.14, "Mercury": 25.70,
            "Jupiter": 34.28, "Venus": 42.85, "Saturn": 8.57
        }
        return vals.get(p_name, 0.0)

    # -------------------------------------------------------------------------
    # 6. DRIK BALA
    # -------------------------------------------------------------------------
    @staticmethod
    def _calculate_aspect_correction(angle: float, p_name: str) -> float:
        val = 0.0
        if 30 <= angle <= 60:
            val = 0.5 * (angle - 30)
        elif 60 < angle <= 90: 
            val = (angle - 60) + 15
            if p_name == "Saturn":
                val += 45
        elif 90 < angle <= 120:
            val = 0.5 * (120 - angle) + 30
            if p_name == "Mars":
                val += 15
        elif 120 < angle <= 150:
            val = (150 - angle)
            if p_name == "Jupiter":
                val += 30
        elif 150 < angle <= 180:
            val = 2.0 * (angle - 150)
        elif 180 < angle <= 300:
            val = 0.5 * (300 - angle)
            if p_name == "Mars" and 210 <= angle <= 240:
                val += 15
            if p_name == "Jupiter" and 240 <= angle <= 270:
                val += 30
            if p_name == "Saturn" and 270 <= angle <= 300:
                val += 45
        return val

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    @staticmethod
    def get_time_lords(jd: float) -> Dict[str, str]:
        mapping = {0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter", 4: "Venus", 5: "Saturn", 6: "Sun"}
        day_lord = mapping.get(int(swe.day_of_week(jd)) % 7, "Sun")
        # Hora lord by simple hourly cycle starting from day lord at local midnight
        hora_seq = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
        start_idx = hora_seq.index(day_lord) if day_lord in hora_seq else 0
        hours_passed = (jd % 1.0) * 24.0
        hora_idx = (start_idx + int(hours_passed)) % 7
        hora_lord = hora_seq[hora_idx]
        # Month/Year placeholders
        return {"Day": day_lord, "Hora": hora_lord, "Month": day_lord, "Year": day_lord}

    # -------------------------------------------------------------------------
    # Main
    # -------------------------------------------------------------------------
    @staticmethod
    def calculate(planets: Dict[str, Any], asc_lon: float, jd: float, lat: float, lon: float) -> Dict[str, Dict]:
        results = {}
        
        simple_pos = {k: p.longitude for k, p in planets.items()}
        simple_pos["Ascendant"] = asc_lon
        vargas_data = VargaEngine.compute_vargas(simple_pos)
        
        compound_rels = {}
        for p_name in ShadbalaEngine.PLANET_NAMES_ORDER:
            if p_name in planets:
                comp = MaitriEngine.get_compound_relation(p_name, planets[p_name].sign, planets[p_name].sign)
                compound_rels[p_name] = {p_name: "Own", **{p_name: comp}}
            else:
                compound_rels[p_name] = {}

        time_lords = ShadbalaEngine.get_time_lords(jd)
        
        asc_sign = int(asc_lon / 30) + 1
        
        for p_name in ShadbalaEngine.PLANET_NAMES_ORDER:
            if p_name not in planets:
                continue
            p = planets[p_name]
            p_lon = p.longitude
            p_sign = p.sign
            
            vargas = vargas_data.get(p_name, {})
            rels = {}
            for other in ShadbalaEngine.PLANET_NAMES_ORDER:
                rels[other] = MaitriEngine.get_compound_relation(p_name, planets.get(other, p).sign if other in planets else p_sign, p_sign)
            
            uchcha = ShadbalaEngine._uchcha_bala(p_name, p_lon)
            sapta = ShadbalaEngine._saptavargaja_bala(p_name, vargas, rels)
            ojayugma = ShadbalaEngine._ojayugma_bala(p_name, vargas)
            kendra = ShadbalaEngine._kendra_bala(p_sign, asc_sign)
            drek = 0.0
            sthana = uchcha + sapta + ojayugma + kendra + drek
            
            dig = ShadbalaEngine._dig_bala(p_name, p_lon, asc_lon)
            
            asc_h = int(asc_lon / 30)
            sun_h = int(planets["Sun"].longitude / 30) if "Sun" in planets else 0
            h_diff = (sun_h - asc_h) % 12
            is_day = (6 <= h_diff <= 11)
            
            natonnata = ShadbalaEngine._natonnata_bala(p_name, is_day)
            paksha = ShadbalaEngine._paksha_bala(p_name, planets["Moon"].longitude, planets["Sun"].longitude) if "Moon" in planets and "Sun" in planets else 0.0
            lords_strength = ShadbalaEngine._lord_balas(p_name, time_lords)
            kaala = natonnata + paksha + lords_strength
            
            chesta = ShadbalaEngine._chesta_bala(p_name)
            
            naisargika = ShadbalaEngine._naisargika_bala(p_name)
            
            drik_score = 0.0
            for aspecting in ShadbalaEngine.PLANET_NAMES_ORDER:
                if aspecting == p_name or aspecting not in planets:
                    continue
                angle = (p_lon - planets[aspecting].longitude) % 360
                val = ShadbalaEngine._calculate_aspect_correction(angle, aspecting)
                is_benefic = aspecting in ["Jupiter", "Venus", "Mercury", "Moon"]
                if is_benefic:
                    drik_score += (val / 4.0)
                else:
                    drik_score -= (val / 4.0)
            
            total_virupas = sthana + dig + kaala + chesta + naisargika + drik_score
            total_rupas = total_virupas / 60.0
            
            results[p_name] = {
                "total_rupas": round(total_rupas, 2),
                "is_strong": total_rupas >= ShadbalaEngine.MIN_REQ_RUPAS.get(p_name, 5.0),
                "breakdown": {
                    "sthana": round(sthana, 1),
                    "dig": round(dig, 1),
                    "kaala": round(kaala, 1),
                    "chesta": round(chesta, 1),
                    "naisargika": round(naisargika, 1),
                    "drik": round(drik_score, 1)
                }
            }
            
        return results
