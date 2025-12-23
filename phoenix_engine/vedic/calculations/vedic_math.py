from typing import List


class VedicMath:
    """
    Mathematical utilities for High-Precision Vedic Calculations.
    Derived from JHora algorithms (Inverse Lagrange Interpolation).
    """

    @staticmethod
    def inverse_lagrange(x: List[float], y: List[float], ya: float) -> float:
        """
        Given two lists x and y, find the value of x = xa when y = ya.
        Used to find the exact time when a Tithi/Nakshatra ends.
        """
        assert len(x) == len(y)
        total = 0.0
        n = len(x)

        for i in range(n):
            numer = 1.0
            denom = 1.0
            for j in range(n):
                if j != i:
                    numer *= (ya - y[j])
                    denom *= (y[i] - y[j])

            total += numer * x[i] / denom

        return total

    @staticmethod
    def unwrap_angles(angles: List[float]) -> List[float]:
        """
        Handles the 360 -> 0 crossover for interpolation.
        Example: [358, 359, 1, 2] becomes [358, 359, 361, 362]
        """
        result = [angles[0]]
        for i in range(1, len(angles)):
            angle = angles[i]
            if angle < result[i - 1] - 180:
                angle += 360
            elif angle > result[i - 1] + 180:
                angle -= 360
            result.append(angle)
        return result
