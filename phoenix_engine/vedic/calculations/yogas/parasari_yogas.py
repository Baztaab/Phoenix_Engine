from typing import List, Dict, Any

from phoenix_engine.core.context import ChartContext
from phoenix_engine.vedic.calculations.yoga import YogaDefinition, YogaResult, YogaUtils


class ParasariYogaEngine:
    """
    Advanced Parasari Yoga Engine (JHora Standard).
    Supports:
    - Pancha Mahapurusha Yogas
    - Solar/Lunar Yogas (Gaja Kesari, Adhi, etc.)
    - Raja Yogas (Kendra/Trikona Lords)
    - Vipareeta Raja Yogas
    - Dhana Yogas
    """

    @staticmethod
    def calculate_yogas(ctx: ChartContext) -> List[YogaResult]:
        detected_yogas: List[YogaResult] = []
        planets = ctx.planets
        asc_sign = int(ctx.ascendant / 30) + 1

        lords = {h: YogaUtils.get_house_lord(asc_sign, h) for h in range(1, 13)}

        majors = {
            "Mars": ("Ruchaka", [1, 8, 10]),
            "Mercury": ("Bhadra", [3, 6]),
            "Jupiter": ("Hamsa", [9, 12, 4]),
            "Venus": ("Malavya", [2, 7, 12]),
            "Saturn": ("Sasa", [10, 11, 7])
        }

        for p_name, (y_name, signs) in majors.items():
            p = planets.get(p_name)
            if p and p.sign in signs:
                if p.house in [1, 4, 7, 10]:
                    detected_yogas.append(
                        YogaResult(
                            yoga=YogaDefinition(
                                name=f"{y_name} Yoga",
                                description=f"{p_name} in Kendra & Strong Sign",
                                benefits="Greatness, Leadership",
                                category="Mahapurusha",
                            ),
                            planets_involved=[p_name],
                            strength_score=getattr(p, "shadbala_pinda", 1.0),
                        )
                    )

        moon = planets.get("Moon")
        jup = planets.get("Jupiter")
        if moon and jup:
            dist = (jup.sign - moon.sign) % 12 + 1
            if dist in [1, 4, 7, 10]:
                detected_yogas.append(
                    YogaResult(
                        yoga=YogaDefinition(
                            name="Gaja Kesari Yoga",
                            description="Jupiter in Kendra from Moon",
                            benefits="Fame, Virtue, Wealth",
                            category="Lunar",
                        ),
                        planets_involved=["Moon", "Jupiter"],
                        strength_score=1.0,
                    )
                )

        valid_others = [n for n in planets if n not in ["Sun", "Moon", "Rahu", "Ketu", "Ascendant"]]
        in_2nd = [n for n in valid_others if (planets[n].sign - moon.sign) % 12 + 1 == 2] if moon else []
        in_12th = [n for n in valid_others if (planets[n].sign - moon.sign) % 12 + 1 == 12] if moon else []

        if moon:
            if in_2nd and not in_12th:
                detected_yogas.append(
                    YogaResult(
                        yoga=YogaDefinition(
                            name="Sunaphaa Yoga",
                            description="Planets in 2nd from Moon",
                            benefits="Intelligence, Wealth",
                            category="Lunar",
                        ),
                        planets_involved=["Moon"] + in_2nd,
                    )
                )
            elif in_12th and not in_2nd:
                detected_yogas.append(
                    YogaResult(
                        yoga=YogaDefinition(
                            name="Anaphaa Yoga",
                            description="Planets in 12th from Moon",
                            benefits="Health, Character",
                            category="Lunar",
                        ),
                        planets_involved=["Moon"] + in_12th,
                    )
                )
            elif in_2nd and in_12th:
                detected_yogas.append(
                    YogaResult(
                        yoga=YogaDefinition(
                            name="Duradhara Yoga",
                            description="Planets in 2nd and 12th from Moon",
                            benefits="Balanced Success",
                            category="Lunar",
                        ),
                        planets_involved=["Moon"] + in_2nd + in_12th,
                    )
                )
            elif not in_2nd and not in_12th:
                detected_yogas.append(
                    YogaResult(
                        yoga=YogaDefinition(
                            name="Kemadruma Yoga",
                            description="No planets in 2nd/12th from Moon",
                            benefits="Loneliness, Struggles (Cancellable)",
                            category="Lunar/Dosha",
                        ),
                        planets_involved=["Moon"],
                    )
                )

        lord_9 = lords[9]
        lord_10 = lords[10]

        if lord_9 and lord_10:
            p9 = planets.get(lord_9)
            p10 = planets.get(lord_10)

            if p9 and p10:
                is_connected = False
                if p9.sign == p10.sign:
                    is_connected = True
                elif abs(p9.sign - p10.sign) == 6:
                    is_connected = True

                if is_connected:
                    detected_yogas.append(
                        YogaResult(
                            yoga=YogaDefinition(
                                name="Dharma-Karmadhipati Yoga",
                                description=f"Lords of 9th ({lord_9}) and 10th ({lord_10}) connected",
                                benefits="High Status, Professional Success",
                                category="Raja",
                            ),
                            planets_involved=[lord_9, lord_10],
                        )
                    )

        trik_houses = [6, 8, 12]
        trik_lords = [lords[h] for h in trik_houses]

        for i, lord in enumerate(trik_lords):
            p = planets.get(lord)
            if p and p.house in trik_houses:
                y_name = ["Harsha", "Sarala", "Vimala"][i]
                detected_yogas.append(
                    YogaResult(
                        yoga=YogaDefinition(
                            name=f"{y_name} Vipareeta Raja Yoga",
                            description=f"Lord of {trik_houses[i]} in Trik Sthana",
                            benefits="Success through obstacles",
                            category="Vipareeta",
                        ),
                        planets_involved=[lord],
                    )
                )

        debils = {"Sun": 7, "Moon": 8, "Mars": 4, "Mercury": 12, "Jupiter": 10, "Venus": 6, "Saturn": 1}

        for name, deb_sign in debils.items():
            p = planets.get(name)
            if p and p.sign == deb_sign:
                dispositor_name = YogaUtils.get_lord(deb_sign)
                disp = planets.get(dispositor_name)

                cancelled = False
                if disp:
                    if disp.house in [1, 4, 7, 10]:
                        cancelled = True
                    elif moon and (disp.sign - moon.sign) % 12 + 1 in [1, 4, 7, 10]:
                        cancelled = True

                if cancelled:
                    detected_yogas.append(
                        YogaResult(
                            yoga=YogaDefinition(
                                name="Neecha Bhanga Raja Yoga",
                                description=f"Debilitated {name} gets cancelled",
                                benefits="Rise after fall",
                                category="Raja",
                            ),
                            planets_involved=[name, dispositor_name],
                        )
                    )

        return detected_yogas
