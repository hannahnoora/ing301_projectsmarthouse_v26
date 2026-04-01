import sqlite3
from typing import Optional
from dataclasses import dataclass

# Vi må definere Measurement-klassen slik at koden din kan returnere et objekt
@dataclass
class Measurement:
    device: str
    timestamp: str
    value: float
    unit: str

def get_latest_reading(file_path: str, sensor_id: str) -> Optional[Measurement]:
    """
    Henter den nyeste målingen for en gitt sensor fra databasen.
    Returnerer None hvis sensoren ikke finnes eller ikke har målinger.
    """
    try:
        # Koble til databasen
        con = sqlite3.connect(file_path)
        cur = con.cursor()

        # SQL-spørring:
        query = """
            SELECT device, ts, value, unit 
            FROM measurements 
            WHERE device = ? 
            ORDER BY ts DESC 
            LIMIT 1
        """
        
        cur.execute(query, (sensor_id,))
        row = cur.fetchone()

        con.close()

        if row is None:
            return None

        # Returnerer et nytt Measurement-objekt med data fra raden
        return Measurement(*row)
    
    except sqlite3.Error as e:
        print(f"Databasefeil: {e}")
        return None

    # Jeg bruker en CO2-sensor med ID: '8a43b2d7-e8d3-4f3d-b832-7dbf37bf629e'
database_fil = "data\\db.sql" 
sensor_id = "8a43b2d7-e8d3-4f3d-b832-7dbf37bf629e"

resultat = get_latest_reading(database_fil, sensor_id)

if resultat:
    print(f"Siste måling for {resultat.device}: {resultat.value} {resultat.unit} kl. {resultat.timestamp}")
else:
    print("Fant ingen målinger for denne sensoren.")

print(resultat)