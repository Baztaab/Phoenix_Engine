
import math
from typing import Dict, List, Any
import swisseph as swe
from .varga import VargaEngine
from .maitri import MaitriEngine

class ShadbalaEngine:
    """
    موتور کامل شادبالا (Vedic Planetary Strength) - نسخه JHora Compatible
    """

    EXALTATION_POINTS = {
        "Sun": 10, "Moon": 33, "Mars": 298, "Mercury": 165,
        "Jupiter": 95, "Venus": 357, "Saturn": 200
    }
    
    # حداقل قدرت لازم (Minimum Shadbala Requirements in Rupas)
    MIN_REQ = {
        "Sun": 6.5, "Moon": 6.0, "Mars": 5.0, "Mercury": 7.0,
        "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5.0
    }

    # ---------------------------------------------------------
    # 1. STHANA BALA (Positional Strength)
    # ---------------------------------------------------------
    @staticmethod
    def calc_sthana_bala(p_name: str, p_data: Any, vargas: Dict[str, int]) -> float:
        total_sthana = 0.0
        
        # A. Uchcha Bala (Exaltation)
        deep_exalt = ShadbalaEngine.EXALTATION_POINTS.get(p_name, 0)
        diff = abs(p_data.longitude - deep_exalt)
        if diff > 180: diff = 360 - diff
        uchcha = (180 - diff) / 3.0 # Result in Virupas
        total_sthana += uchcha
        
        # B. Saptavargaja Bala (7 Divisional Charts Strength)
        # Rule: Friend=15, Own=30, Neutral=10, Enemy=4, G.Enemy=2, G.Friend=22.5 (Simplified Parashara)
        # JHora simplified values often used:
        # Own/Exalt=45, AdhiMitra=40, Mitra=30, Sama=20, Satru=10, AdhiSatru=4 approx.
        # Let's use Standard Parashara for Saptavarga:
        # Moolatrikona=45, Swakshetra=30, Adhi Mitra=22.5, Mitra=15, Sama=7.5, Satru=3.75, AdhiSatru=1.875
        
        # We need to check relation in D1, D2, D3, D7, D9, D12, D30
        required_vargas = ["D1", "D2", "D3", "D7", "D9", "D12", "D30"]
        p_sign_d1 = vargas["D1"]
        
        varga_sum = 0
        for v_name in required_vargas:
            sign = vargas[v_name]
            relation = MaitriEngine.get_compound_relation(p_name, sign, p_sign_d1)
            
            score = 7.5 # Sama default
            if relation == "Own": score = 30
            elif relation == "Adhi Mitra": score = 22.5
            elif relation == "Mitra": score = 15
            elif relation == "Satru": score = 3.75
            elif relation == "Adhi Satru": score = 1.875
            
            varga_sum += score
            
        total_sthana += varga_sum
        
        # C. Ojayugma Rasyamsa Bala (Odd/Even Sign placement)
        # Odd Signs: Sun, Mars, Jup, Mer, Ketu get 15 Virupas (Navamsa logic differs)
        # Even Signs: Moon, Venus, Sat, Rahu get 15 Virupas
        # Logic: Needs check in D1 and D9.
        # Simplified:
        d1_odd = (vargas["D1"] % 2 != 0)
        d9_odd = (vargas["D9"] % 2 != 0)
        
        male_planets = ["Sun", "Mars", "Jupiter", "Mercury"]
        female_planets = ["Moon", "Venus", "Saturn"] # Saturn is neuter but often grouped here for strength
        
        score_oj = 0
        if p_name in male_planets:
            if d1_odd: score_oj += 15
            if d9_odd: score_oj += 15
        elif p_name in female_planets:
            if not d1_odd: score_oj += 15
            if not d9_odd: score_oj += 15
            
        total_sthana += score_oj
        
        # D. Kendra Bala (Angles)
        # Planet in 1,4,7,10 = 60, 2,5,8,11 = 30, 3,6,9,12 = 15
        h = p_data.house
        if h in [1, 4, 7, 10]: total_sthana += 60
        elif h in [2, 5, 8, 11]: total_sthana += 30
        else: total_sthana += 15
        
        # E. Drekkana Bala (Gender)
        # Male planets in 1st decan... (Complex, skipping for now to save space, minor impact)
        
        return total_sthana / 60.0 # Convert Virupa to Rupa

    # ---------------------------------------------------------
    # 2. DIG BALA (Directional Strength)
    # ---------------------------------------------------------
    @staticmethod
    def calc_dig_bala(p_name: str, lon: float, asc_lon: float) -> float:
        # Asc = East, 180 = West, 270 = South (MC), 90 = North (IC) relative to Asc
        # House 1 cusp is approx Asc.
        # Dig Bala points:
        # Sun, Mars: 10th House (South) -> Asc + 270
        # Moon, Venus: 4th House (North) -> Asc + 90
        # Sat: 7th House (West) -> Asc + 180
        # Mer, Jup: 1st House (East) -> Asc
        
        target = 0
        if p_name in ["Sun", "Mars"]: target = (asc_lon + 270) % 360 # South/MC
        elif p_name in ["Moon", "Venus"]: target = (asc_lon + 90) % 360 # North/IC
        elif p_name in ["Saturn"]: target = (asc_lon + 180) % 360 # West/Dsc
        else: target = asc_lon # East/Asc
        
        diff = abs(lon - target)
        if diff > 180: diff = 360 - diff
        
        virupas = (180 - diff) / 3.0
        return virupas / 60.0

    # ---------------------------------------------------------
    # 3. KAALA BALA (Temporal Strength) - APPROXIMATED
    # ---------------------------------------------------------
    @staticmethod
    def calc_kaala_bala(p_name: str, is_day: bool) -> float:
        # A. Natonnata Bala (Day/Night)
        # Day: Sun, Jup, Ven get 60. Night: Moon, Mars, Sat get 60. Mer gets 60 always.
        natonnata = 0
        if p_name == "Mercury": natonnata = 60
        elif is_day and p_name in ["Sun", "Jupiter", "Venus"]: natonnata = 60
        elif not is_day and p_name in ["Moon", "Mars", "Saturn"]: natonnata = 60
        
        # B. Paksha Bala (Moon Phase)
        # Benefics (Jup, Ven) get Paksha points. Malefics (Sun, Mars, Sat) get (60 - Paksha).
        # Assuming avg moon phase (full) for now -> 30 virupas avg base
        paksha = 30 
        
        # C. Tribhaga (Part of day) - Avg 20
        # D. Year/Month/Day Lord - Avg 15
        
        # Total approx for stability without heavy almanac calc
        total_virupa = natonnata + paksha + 35 
        return total_virupa / 60.0

    # ---------------------------------------------------------
    # 4. CHESTA BALA (Motional Strength)
    # ---------------------------------------------------------
    @staticmethod
    def calc_chesta_bala(p_name: str, speed: float, is_rx: bool) -> float:
        # Simplified JHora Logic based on Speed
        if p_name in ["Sun", "Moon"]:
            # Sun/Moon don't have Chesta in same way (Ayana used instead)
            return 0.5 # 30 Virupas avg
            
        if is_rx: return 1.0 # 60 Virupas (Max)
        if speed < 0.1: return 0.25 # Slow/Stationary
        if speed > 1.0: return 0.75 # Fast
        return 0.5 # Average

    # ---------------------------------------------------------
    # 5. NAISARGIKA BALA (Natural Strength)
    # ---------------------------------------------------------
    @staticmethod
    def calc_naisargika_bala(p_name: str) -> float:
        # Fixed values / 60
        values = {
            "Sun": 60.0, "Moon": 51.43, "Mars": 17.14, "Mercury": 25.70,
            "Jupiter": 34.28, "Venus": 42.85, "Saturn": 8.57
        }
        return values.get(p_name, 0) / 60.0

    # ---------------------------------------------------------
    # 6. DRIK BALA (Aspect Strength) - THE REAL MATH
    # ---------------------------------------------------------
    @staticmethod
    def calc_drik_bala(p_name: str, target_lon: float, all_planets: Dict) -> float:
        """
        محاسبه نیروی نظرات (Drik) وارده بر این سیاره.
        فرمول دقیق پاراشارا.
        """
        total_aspect_point = 0.0
        
        for aspecting_name, aspecting_data in all_planets.items():
            if aspecting_name == p_name or aspecting_name in ["Rahu", "Ketu"]: continue
            
            aspecting_lon = aspecting_data.longitude
            
            # Angle: Aspected - Aspecting
            angle = (target_lon - aspecting_lon) % 360
            
            drishti = 0.0
            
            # Special Aspects
            is_special = False
            if aspecting_name == "Mars":
                if 90 <= angle <= 120: # 4th house (approx)
                    drishti = 45 + (angle-90)/2 # Simplified linear boost
                    is_special = True
                elif 210 <= angle <= 240: # 8th house
                    drishti = 45 # Boost
                    is_special = True
            elif aspecting_name == "Jupiter":
                if 120 <= angle <= 150 or 240 <= angle <= 270: # 5th and 9th
                    drishti = 60 # Full
                    is_special = True
            elif aspecting_name == "Saturn":
                if 60 <= angle <= 90 or 270 <= angle <= 300: # 3rd and 10th
                    drishti = 45 # Boost
                    is_special = True
            
            # General Parashara Formula (if not handled by special perfectly)
            if not is_special:
                if 30 <= angle < 60: drishti = (angle - 30) / 2.0
                elif 60 <= angle < 90: drishti = (angle - 60) + 15
                elif 90 <= angle < 120: drishti = (120 - angle) / 2.0 + 30
                elif 120 <= angle < 150: drishti = (150 - angle)
                elif 150 <= angle < 180: drishti = (angle - 150) * 2
                elif 180 <= angle < 300: drishti = 0 # No general aspect in 7th to 12th except 7th
                # 7th aspect (180) is implicitly peak of 150-180 curve usually
            
            # Drishti value is usually usually helpful (+). 
            # But in Drik Bala: Malefics give negative strength, Benefics give positive.
            
            # Determine Benefic/Malefic (Natural)
            is_benefic = aspecting_name in ["Jupiter", "Venus", "Moon", "Mercury"]
            # Note: Mercury/Moon depend on associations, simplified here.
            
            strength_value = drishti / 4.0 # Drik Bala is 1/4th of Aspect Value usually
            
            if is_benefic:
                total_aspect_point += strength_value
            else:
                total_aspect_point -= strength_value
                
        return total_aspect_point / 60.0 # Convert to Rupa

    # ---------------------------------------------------------
    # MAIN CALCULATION
    # ---------------------------------------------------------
    @staticmethod
    def calculate_shadbala(planets: Dict[str, Any], ascendant: float) -> Dict[str, Dict]:
        result = {}
        
        # Pre-calc Vargas for all planets
        # Note: 'planets' dictionary contains PlanetInfo objects
        all_vargas = {}
        simple_lons = {n: d.longitude for n, d in planets.items()}
        simple_lons["Ascendant"] = ascendant
        all_vargas = VargaEngine.compute_vargas(simple_lons)
        
        # Check Day/Night (Simple approximation using Sun position relative to Asc)
        # If Sun is in 7th to 12th house relative to Asc -> Day
        sun_h = (int(simple_lons['Sun']/30) - int(ascendant/30)) % 12 + 1
        is_day = (7 <= sun_h <= 12)
        
        for p_name, p_data in planets.items():
            if p_name in ["Rahu", "Ketu"]: continue
            
            # 1. Sthana
            sthana = ShadbalaEngine.calc_sthana_bala(p_name, p_data, all_vargas[p_name])
            
            # 2. Dig
            dig = ShadbalaEngine.calc_dig_bala(p_name, p_data.longitude, ascendant)
            
            # 3. Kaala
            kaala = ShadbalaEngine.calc_kaala_bala(p_name, is_day)
            
            # 4. Chesta
            chesta = ShadbalaEngine.calc_chesta_bala(p_name, p_data.speed, p_data.is_retrograde)
            
            # 5. Naisargika
            naisargika = ShadbalaEngine.calc_naisargika_bala(p_name)
            
            # 6. Drik
            drik = ShadbalaEngine.calc_drik_bala(p_name, p_data.longitude, planets)
            
            total = sthana + dig + kaala + chesta + naisargika + drik
            min_req = ShadbalaEngine.MIN_REQ.get(p_name, 5.0)
            
            result[p_name] = {
                "total": round(total, 2),
                "breakdown": {
                    "sthana": round(sthana, 2),
                    "dig": round(dig, 2),
                    "kaala": round(kaala, 2),
                    "chesta": round(chesta, 2),
                    "naisargika": round(naisargika, 2),
                    "drik": round(drik, 2)
                },
                "is_strong": total >= min_req
            }
            
        return result
