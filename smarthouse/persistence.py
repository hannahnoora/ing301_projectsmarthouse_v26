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
            rooms_by_id[room_id] = room

        # 3. Devices: devices(id, room, kind, category, supplier, product)
        cur.execute("""
            SELECT id, room, kind, category, supplier, product
            FROM devices
            ORDER BY id
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

            h.register_device(room, device)

        cur.close()
        return h


            



    def get_latest_reading(self, sensor) -> Optional[Measurement]:
        """
        Retrieves the most recent sensor reading for the given sensor if available.
        Returns None if the given object has no sensor readings.
        """
        # TODO: After loading the smarthouse, continue here
        return NotImplemented


    def update_actuator_state(self, actuator):
        """
        Saves the state of the given actuator in the database. 
        """
        # TODO: Implement this method. You will probably need to extend the existing database structure: e.g.
        #       by creating a new table (`CREATE`), adding some data to it (`INSERT`) first, and then issue
        #       and SQL `UPDATE` statement. Remember also that you will have to call `commit()` on the `Connection`
        #       stored in the `self.conn` instance variable.
        pass


    # statistics

    
    def calc_avg_temperatures_in_room(self, room, from_date: Optional[str] = None, until_date: Optional[str] = None) -> dict:
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
        return NotImplemented

    
    def calc_hours_with_humidity_above(self, room, date: str) -> list:
        """
        This function determines during which hours of the given day
        there were more than three measurements in that hour having a humidity measurement that is above
        the average recorded humidity in that room at that particular time.
        The result is a (possibly empty) list of number representing hours [0-23].
        """
        # TODO: implement
        return NotImplemented

