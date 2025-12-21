
from enum import Enum

class AyanamsaSystem(str, Enum):
    LAHIRI = "LAHIRI"
    RAMAN = "RAMAN"
    KP = "KP"
    TROPICAL = "TROPICAL"
    FAGAN_BRADLEY = "FAGAN_BRADLEY"

class HouseSystem(str, Enum):
    PLACIDUS = "PLACIDUS"
    WHOLE_SIGN = "WHOLE_SIGN"
    EQUAL = "EQUAL"
    PORPHYRY = "PORPHYRY"

class NodeType(str, Enum):
    TRUE_NODE = "TRUE_NODE"
    MEAN_NODE = "MEAN_NODE"

class DashaSystem(str, Enum):
    VIMSHOTTARI = "VIMSHOTTARI"
    CHARA = "CHARA_KNR"
