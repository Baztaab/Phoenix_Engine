class ChartConfig:
    """
    Chart configuration settings for Phoenix Engine.
    Holds ayanamsa, house system, and other runtime flags.
    """

    def __init__(self, ayanamsa: str = "LAHIRI", house_system: str = "Placidus", sidereal_mode: bool = True, language: str = "en"):
        self.ayanamsa = ayanamsa
        self.house_system = house_system
        self.sidereal_mode = sidereal_mode
        self.language = language

    def __repr__(self):
        return f"<ChartConfig: {self.ayanamsa}, {self.house_system}>"

