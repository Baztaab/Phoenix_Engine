# Phoenix Engine (Vedic Astrology API)

**Phoenix Engine** is a high-precision, production-grade Vedic Astrology (Jyotish) calculation engine built with Python. It is designed to replicate the calculation logic of industry-standard software like Parashara Light and Jagannatha Hora, providing a robust REST API for astrological applications.

## Features

### Core Astronomy
- High Precision: Uses Swiss Ephemeris (pyswisseph) for planetary positions.
- Ayanamsa: Supports Lahiri (Chitrapaksha) and other standard ayanamsas.
- True Nodes: Calculates True Rahu/Ketu positions.

### Divisional Charts (Vargas)
- Calculates all 16 Shodashavarga charts:
  - Rashi (D1), Hora (D2), Drekkana (D3), Chaturthamsha (D4), Saptamsha (D7), Navamsha (D9), Dashamsha (D10), Dwadashamsha (D12), Shodashamsha (D16), Vimshamsha (D20), Chaturvimshamsha (D24), Saptavimshamsha (D27), Trimshamsha (D30), Khavedamsha (D40), Akshavedamsha (D45), Shastiamsha (D60).

### Planetary Strength (Shadbala)
- Shadbala: Complete 6-fold strength calculation (Sthana, Dig, Kala, Chesta, Naisargika, Drik).
- Spashta Bala: Detailed strength analysis.
- Ishta and Kashta Phala: Favorable and unfavorable points.

### Ashtakavarga System
- Bhinna Ashtakavarga: Individual scores for all 7 planets.
- Sarva Ashtakavarga: Total points per sign.
- Kakshya Strength: Detailed transits reduction.

### Jaimini System
- Seven Karakas: Atmakaraka, Amatyakaraka, etc.
- Arudha Padas: Calculation of AL (Arudha Lagna) and UL (Upapada Lagna).
- Chara Dasha: K.N. Rao system with Antardashas (Sub-periods).

### Dashas and Yogas
- Vimshottari Dasha: Full nested dasha system (Maha/Antar/Pratyantar).
- Yoga Detection: Logic for 50+ major Yogas (Raja Yoga, Dhan Yoga, Pancha Mahapurusha, etc.).

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Baztaab/Phoenix_Engine.git
   cd Phoenix_Engine
   ```

2. (Optional) Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate   # Linux/macOS
   ```

3. Install dependencies:
   ```bash
   pip install fastapi uvicorn pydantic requests pyswisseph pytz
   ```

## Usage

Start the API server:
```bash
uvicorn phoenix_engine.api.app:app --reload
```
The server will start at http://127.0.0.1:8000.

- API Endpoint: /calculate
- Method: POST

Request Body (JSON):
```json
{
    "year": 1997,
    "month": 6,
    "day": 7,
    "hour": 20,
    "minute": 28,
    "timezone": "Asia/Tehran",
    "lat": 35.6892,
    "lon": 51.3890,
    "name": "Mehran"
}
```

## License
Proprietary Software.
