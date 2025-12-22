from typing import Tuple, Dict


class VedicMath:
    """
    محاسبات ریاضی خاص زمان‌های ودیک (Ghati, Vighati, etc.)
    الهام گرفته از JHora utils.
    """

    @staticmethod
    def time_diff_to_ghati(jd_birth: float, jd_sunrise: float) -> Tuple[float, str]:
        """
        تبدیل فاصله زمانی تولد و طلوع به گاتی (Ghati).
        هر روز (24 ساعت) = 60 گاتی.
        هر گاتی = 24 دقیقه.
        """
        diff = jd_birth - jd_sunrise
        if diff < 0:
            diff += 1.0
        ghatis_float = diff * 60.0
        g = int(ghatis_float)
        rem_g = (ghatis_float - g) * 60
        v = int(rem_g)
        rem_v = (rem_g - v) * 60
        p = int(rem_v)
        text = f"{g}:{v}:{p}"
        return ghatis_float, text

    @staticmethod
    def get_sexagenary_year(year_index: int) -> str:
        """
        نام سال‌های سامواتسارا (Samvatsara) - چرخه 60 ساله مشتری
        """
        samvatsaras = [
            "Prabhava", "Vibhava", "Shukla", "Pramoda", "Prajapati", "Angira", "Shrimukha", "Bhava", "Yuva", "Dhatri",
            "Ishwara", "Bahudhanya", "Pramathi", "Vikrama", "Vrusha", "Chitrabhanu", "Subhanu", "Tarana", "Parthiva", "Vyaya",
            "Sarvajit", "Sarvadhari", "Virodhi", "Vikriti", "Khara", "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukha",
            "Hemalamba", "Vilambi", "Vikari", "Sharvari", "Plava", "Shubhakrut", "Shobhakrut", "Krodhi", "Vishvavasu", "Parabhava",
            "Plavanga", "Kilaka", "Saumya", "Sadharana", "Virodhikrut", "Paridhavi", "Pramadicha", "Ananda", "Rakshasa", "Nala",
            "Pingala", "Kalayukta", "Siddharthi", "Roudra", "Durmati", "Dundubhi", "Rudhirodgari", "Raktakshi", "Krodhana", "Akshaya"
        ]
        return samvatsaras[year_index % 60]
