import sqlite3
from typing import Optional
from smarthouse.domain import SmartHouse, Room, Measurement, Sensor, Actuator

class SmartHouseRepository:
    """
    Provides the functionality to persist and load a _SmartHouse_ object 
    in a SQLite database.
    """

    def __init__(self, file: str) -> None:
        self.file = file 
        self.conn = sqlite3.connect(file, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # gjør at vi kan bruke row["kolonne"] -> ny

    def __del__(self):
        try:
            self.conn.close()
        except Exception:
            pass


    def cursor(self) -> sqlite3.Cursor:
        """
        Provides a _raw_ SQLite cursor to interact with the database.
        When calling this method to obtain a cursors, you have to 
        rememeber calling `commit/rollback` and `close` yourself when
        you are done with issuing SQL commands.
        """
        return self.conn.cursor()

    def reconnect(self):
        self.conn.close()
        self.conn = sqlite3.connect(self.file, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row


    def load_smarthouse_deep(self) -> SmartHouse:
        """
        This method retrives the complete single instance of the _SmartHouse_ 
        object stored in this database. The retrieval yields a _deep_ copy, i.e.
        all referenced objects within the object structure (e.g. floors, rooms, devices) 
        are retrieved as well. 
        """
        h = SmartHouse()
        cur = self.cursor()

        # 1. Etasjer: fra rooms.floor
        cur.execute("SELECT DISTINCT floor FROM rooms ORDER BY floor")
        floors_by_level = {}
        for row in cur.fetchall():
            level = row["floor"]
            floors_by_level[level] = h.register_floor(level)

        # 2. Rom: rooms(id, floor, area, name)
        cur.execute("SELECT id, floor, area, name FROM rooms ORDER BY id")
        rooms_by_id = {}
        for row in cur.fetchall():
            room_id = row["id"]
            floor_level = row["floor"]
            area = row["area"]
            name = row["name"]

            floor = floors_by_level[floor_level]
            room = h.register_room(floor=floor, room_size=area, room_name=name)

            # --- VIKTIG: DENNE LINJEN MÅ VÆRE MED ---
            room.id = room_id 
            # ----------------------------------------

            rooms_by_id[room_id] = room

        # 3. Devices: Her legger vi på LEFT JOIN for å få med 'state'
        cur.execute("""
            SELECT d.id, d.room, d.kind, d.category, d.supplier, d.product, s.state
            FROM devices d
            LEFT JOIN actuator_states s ON d.id = s.device_id
            ORDER BY d.id
            """)
        for row in cur.fetchall():
            device_id = row["id"]
            room_id = row["room"]
            kind = row["kind"]            # f.eks. "Smart Lock", "CO2 sensor" <ref: index=2721409 firstWord=1 lastWord=10/>
            category = row["category"]    # 'sensor' / 'actuator'
            supplier = row["supplier"]    # f.eks. "MythicalTech"
            product = row["product"]      # f.eks. "Guardian Lock 7000"

            room = rooms_by_id.get(room_id)
            if room is None:
                continue

            nickname = None  # ingen kolonne for dette i devices-tabellen

            if category.lower() == "sensor":
                device = Sensor(
                    device_id=device_id,
                    device_type=kind,
                    supplier=supplier,
                    model_name=product,
                    nickname=nickname
                )
            else:
                device = Actuator(
                    device_id=device_id,
                    manufacturer=supplier,
                    model=product,
                    device_type=kind,
                    nickname=nickname
                )
                # NYTT: Her må vi faktisk sette tilstanden vi hentet fra databasen!
                # Vi henter 'state' fra raden (takket være LEFT JOIN i SQL-en din)
                db_state = row["state"]
                if db_state is not None:
                    # Sjekk om det heter .state eller .value i domain.py
                    device.state = db_state 

            h.register_device(room, device)

        cur.close()
        return h

    def get_latest_reading(self, sensor) -> Optional[Measurement]:
        """
        Retrieves the most recent sensor reading for the given sensor if available.
        Returns None if the given object has no sensor readings.
        """
        # 1. Hent ut ID-en fra sensor-objektet (fungerer for både Sensor og Actuator)
        sensor_id = sensor.id

        # 2. Bruk den eksisterende cursor-metoden i klassen
        cur = self.cursor()

        try:
            # 3. SQL-spørring for å finne den nyeste målingen basert på tidsstempel (ts)
            # Vi henter ts, value og unit fra measurements-tabellen
            query = """
                SELECT ts, value, unit 
                FROM measurements 
                WHERE device = ? 
                ORDER BY ts DESC 
                LIMIT 1
            """
            
            cur.execute(query, (sensor_id,))
            row = cur.fetchone()

            # 4. Hvis ingen rader blir funnet (f.eks. for en aktuator uten målinger), 
            # returneres None, som er det testen "test_basic_read_values" forventer.
            if row is None:
                return None

            # 5. Opprett og returner et Measurement-objekt fra domenemodellen.
            # Siden row_factory er sqlite3.Row, kan vi bruke kolonnenavnene direkte.
            # Domenemodellens Measurement forventer vanligvis (timestamp, value, unit)
            return Measurement(row["ts"], row["value"], row["unit"])
        
        finally:
            # Lukk kun cursoren, ikke self.conn, slik at databasen forblir tilgjengelig
            cur.close()


    def update_actuator_state(self, actuator):
        """
        Saves the state of the given actuator in the database. 
        """
        cur = self.cursor()
        try:
            # 1. Hent data fra objektet
            # Sjekk om objektet har .id eller .device_id
            dev_id = getattr(actuator, 'id', getattr(actuator, 'device_id', None))
            
            # Sjekk om objektet har .state eller .value (typisk i smarthus-oppgaver)
            # Hvis du er usikker, bruk det du vet Actuator-klassen bruker
            state_value = getattr(actuator, 'state', 0.0) 


            sql = "INSERT OR REPLACE INTO actuator_states (device_id, state) VALUES (?, ?)"
            
            cur.execute(sql, (dev_id, state_value))
            self.conn.commit()
            
        except sqlite3.Error as e:
            print(f"Databasefeil: {e}")
            self.conn.rollback()
        finally:
            cur.close()


    # statistics
    def calc_avg_temperatures_in_room(self, room: Room, from_date: Optional[str] = None, until_date: Optional[str] = None) -> dict:
        
        """Calculates the average temperatures in the given room for the given time range by
        fetching all available temperature sensor data (either from a dedicated temperature sensor 
        or from an actuator, which includes a temperature sensor like a heat pump) from the devices 
        located in that room, filtering the measurement by given time range.
        The latter is provided by two strings, each containing a date in the ISO 8601 format.
        If one argument is empty, it means that the upper and/or lower bound of the time range are unbounded.
        The result should be a dictionary where the keys are strings representing dates (iso format) and 
        the values are floating point numbers containing the average temperature that day.
        """
        # TODO: This and the following statistic method are a bit more challenging. Try to design the respective 
        #       SQL statements first in a SQL editor like Dbeaver and then copy it over here.  

    
        # 1. Hent hele huset "deep" for å finne ut hvilke enheter som er i rommet
        # (Alternativt kan du spørre databasen direkte, men vi bruker domenemodellen her)
        house = self.load_smarthouse_deep()
        devices_in_room = house.get_devices(room)
        
        if not devices_in_room:
            return {}

        # Hent ID-ene til alle enhetene i dette rommet
        device_ids = [d.id for d in devices_in_room]

        # 2. Forbered SQL
        # Vi bruker strftime for å gruppere på dato (YYYY-MM-DD) i SQLite
        query = """
            SELECT strftime('%Y-%m-%d', ts) as day, AVG(value) as avg_temp
            FROM measurements
            WHERE device IN ({})
        """.format(','.join(['?'] * len(device_ids)))
        
        params = list(device_ids)

        if from_date:
            query += " AND ts >= ?"
            params.append(from_date)
        
        if until_date:
            # Vi legger til 23:59:59 for å inkludere hele den siste dagen
            query += " AND ts <= ?"
            params.append(f"{until_date} 23:59:59")

        query += " GROUP BY day ORDER BY day ASC"

        # 3. Kjør spørringen
        cur = self.cursor()
        result = {}
        try:
            cur.execute(query, params)
            for row in cur.fetchall():
                # row["day"] er dato-strengen, row["avg_temp"] er gjennomsnittet
                result[row["day"]] = float(row["avg_temp"])
        finally:
            cur.close()

        return result





    def calc_hours_with_humidity_above(self, room, date: str) -> list:
        """
        This function determines during which hours of the given day
        there were more than three measurements in that hour having a humidity measurement that is above
        the average recorded humidity in that room at that particular time.
        The result is a (possibly empty) list of number representing hours [0-23].
        """
        cur = self.cursor()
        
        # Finn rom-ID
        cur.execute("SELECT id FROM rooms WHERE name = ?", (room.room_name,))
        row = cur.fetchone()
        if not row:
            cur.close()
            return []
        room_id = row["id"]

        # SQL-logikk:
        # 1. DailyAvg: Finn gjennomsnittet for dette rommet på akkurat denne datoen.
        # 2. Hovedspørring: Finn timer på denne datoen med > 3 målinger over dags-gjennomsnittet.
        query = """
        WITH DailyAvg AS (
            SELECT AVG(m.value) as avg_val
            FROM measurements m
            JOIN devices d ON m.device = d.id
            WHERE d.room = ? 
              AND date(m.ts) = ? 
              AND m.unit = '%'
        )
        SELECT 
            CAST(strftime('%H', m.ts) AS INTEGER) as hour
        FROM measurements m
        JOIN devices d ON m.device = d.id
        CROSS JOIN DailyAvg da
        WHERE d.room = ? 
          AND date(m.ts) = ? 
          AND m.unit = '%'
          AND m.value > da.avg_val
        GROUP BY hour
        HAVING COUNT(*) > 3
        ORDER BY hour
        """

        try:
            cur.execute(query, (room_id, date, room_id, date))
            rows = cur.fetchall()
            return [r["hour"] for r in rows]
        except Exception as e:
            print(f"Feil: {e}")
            return []
        finally:
            cur.close()