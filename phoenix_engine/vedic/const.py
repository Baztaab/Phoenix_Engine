# 0=Aries, 1=Taurus, ..., 11=Pisces
ODD_SIGNS = [0, 2, 4, 6, 8, 10]
EVEN_SIGNS = [1, 3, 5, 7, 9, 11]

# Footedness (Prakriti) for Chara/Narayana Duration Counting
# Odd Footed (Vishama Pada): Aries, Taurus, Gemini, Libra, Scorpio, Sagittarius
# Even Footed (Sama Pada): Cancer, Leo, Virgo, Capricorn, Aquarius, Pisces
ODD_FOOTED_SIGNS = [0, 1, 2, 6, 7, 8]
EVEN_FOOTED_SIGNS = [3, 4, 5, 9, 10, 11]

MOVABLE_SIGNS = [0, 3, 6, 9]
FIXED_SIGNS = [1, 4, 7, 10]
DUAL_SIGNS = [2, 5, 8, 11]

# Planet IDs (Standard Map)
SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN, RAHU, KETU = 0, 1, 2, 3, 4, 5, 6, 7, 8

# Exaltation/Debilitation Signs (approx for +1/-1 year logic)
EXALTATION_SIGNS = {0: 0, 1: 1, 2: 9, 3: 5, 4: 3, 5: 11, 6: 6, 7: 1, 8: 7} # Sun:Ar, Mon:Ta...
DEBILITATION_SIGNS = {0: 6, 1: 7, 2: 3, 3: 11, 4: 9, 5: 5, 6: 0, 7: 7, 8: 1}

# Narayana Progression Exceptions (from JHora narayana.md)
NARAYANA_NORMAL = [
    [1,2,3,4,5,6,7,8,9,10,11,12], # Ar
    [2,9,4,11,6,1,8,3,10,5,12,7], # Ta (Fixed logic in JHora table is specific)
    [3,11,7,6,2,10,9,5,1,12,8,4], # Ge
    [4,3,2,1,12,11,10,9,8,7,6,5], # Cn
    [5,10,3,8,1,6,11,4,9,2,7,12], # Le
    [6,10,2,3,7,11,12,4,8,9,1,5], # Vi
    [7,8,9,10,11,12,1,2,3,4,5,6], # Li
    [8,3,10,5,12,7,2,9,4,11,6,1], # Sc
    [9,5,1,12,8,4,3,11,7,6,2,10], # Sg
    [10,9,8,7,6,5,4,3,2,1,12,11], # Cp
    [11,4,9,2,7,12,5,10,3,8,1,6], # Aq
    [12,4,8,9,1,5,6,10,2,3,7,11]  # Pi
]
# Note: Provide full tables if needed, but logic generation is better.
# JHora uses explicit tables. Let's use logic in the class for compactness or tables if provided.
