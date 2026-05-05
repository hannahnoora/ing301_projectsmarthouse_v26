import sqlite3
from typing import Optional
from smarthouse.domain import Actuator, ActuatorWithSensor, Measurement, Room, Sensor, SmartHouse

class SmartHouseRepository:
    """
    Provides the functionality to persist and load a _SmartHouse_ object 
    in a SQLite database.
    """

    def __init__(self, file: str) -> None:
        self.file = file 
        self.conn = sqlite3.connect(file, check_same_thread=False)

    def __del__(self):
        self.conn.close()

    def cursor(self) -> sqlite3.Cursor:
        """
        Provides a _raw_ SQLite cursor to interact with the database.
        When calling this method to obtain a cursors, you have to 
        rememeber calling `commit/rollback` and `close` yourself when
        you are done with issuing SQL commands.
        """
        return self.conn.cursor()

    def reconnect(self):
        """
        Closes the current connection towards the database and opens a fresh one.
        """
        self.conn.close()
        self.conn = sqlite3.connect(self.file)

    
    def load_smarthouse_deep(self):
        """
        This method retrives the complete single instance of the _SmartHouse_ 
        object stored in this database. The retrieval yields a _deep_ copy, i.e.
        all referenced objects within the object structure (e.g. floors, rooms, devices) 
        are retrieved as well. 
        """
        result = SmartHouse()
        cursor = self.cursor()

        # Creating floors
        cursor.execute('SELECT MAX(floor) from rooms;')
        no_floors = cursor.fetchone()[0]
        floors = []
        for i in range(0, no_floors):
            floors.append(result.register_floor(i + 1))

        # Creating roooms
        room_dict = {}
        cursor.execute('SELECT id, floor, area, name from rooms;')
        room_tuples = cursor.fetchall()
        for room_tuple in room_tuples:
            room = result.register_room(floors[int(room_tuple[1]) - 1], float(room_tuple[2]), room_tuple[3])
            room.db_id = int(room_tuple[0])
            room_dict[room_tuple[0]] = room

        cursor.execute('SELECT id, room, kind, category, supplier, product from devices;')
        device_tuples = cursor.fetchall()
        for device_tuple in device_tuples:
            room = room_dict[device_tuple[1]]
            category = device_tuple[3]
            if category == 'sensor':
                result.register_device(room, Sensor(device_tuple[0], device_tuple[5], device_tuple[4], device_tuple[2]))
            elif category == 'actuator':
                if device_tuple[2] == 'Heat Pump':
                    result.register_device(room, ActuatorWithSensor(device_tuple[0], device_tuple[5], device_tuple[4], device_tuple[2]))
                else:
                    result.register_device(room, Actuator(device_tuple[0], device_tuple[5], device_tuple[4], device_tuple[2]))

        for dev in result.get_devices():
            if isinstance(dev, Actuator):
                cursor.execute(f"SELECT state FROM states where device = '{dev.id}';")
                state = cursor.fetchone()[0]
                if state is None:
                    dev.turn_off()
                elif float(state) == 1.0:
                    dev.turn_on()
                else:
                    dev.turn_on(float(state))


        cursor.close()
        return result


    def get_latest_reading(self, sensor) -> Optional[Measurement]:
        """
        Retrieves the most recent sensor reading for the given sensor object if available.
        Returns None if the given object has no sensor readings.
        """
        query = f"""
SELECT ts, value, unit from measurements m 
WHERE device = '{sensor.id}'
order by ts desc 
limit 1;
        """
        c = self.cursor()
        c.execute(query)
        result = c.fetchall()
        if len(result) == 0:
            return None
        m = Measurement(result[0][0], float(result[0][1]), result[0][2])
        c.close()
        return m


    def update_actuator_state(self, actuator):
        """
        Saves the state of the given actuator in the database. 
        """
        if isinstance(actuator, Actuator):
            s = 'NULL'
            if isinstance(actuator.state, float):
                s = str(actuator.state)
            elif actuator.state is True:
                s = '1.0'
            query = f"""
UPDATE states 
SET state = {s}
WHERE device = '{actuator.id}';
        """
            c = self.cursor()
            c.execute(query)
            self.conn.commit()
            c.close()



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
        result = {}
        if isinstance(room, Room) and room.db_id is not None:
            lower_bound_pred = ""
            upper_bound_pred = ""
            if from_date is not None:
                lower_bound_pred = f"AND ts >= '{from_date} 00:00:00'"
            if until_date is not None:
                upper_bound_pred = f"AND ts <= '{until_date} 23:59:59'"
            query = f"""
    SELECT STRFTIME('%Y-%m-%d', DATETIME(ts)), avg(value) 
    FROM devices d 
    INNER join measurements m ON m.device = d.id 
    WHERE d.room = {room.db_id} AND m.unit = '°C' {lower_bound_pred} {upper_bound_pred}
    GROUP BY STRFTIME('%Y-%m-%d', DATETIME(ts)) ;
            """
            cursor = self.cursor()
            cursor.execute(query)
            query_result = cursor.fetchall()
            for row in query_result:
                result[row[0]] = float(row[1])
        return result

    
    def calc_hours_with_humidity_above(self, room, date: str) -> list:
        """
        This function determines during which hours of the given day
        there were more than three measurements in that hour having a humidity measurement that is above
        the average recorded humidity in that room at that particular time.
        The result is a (possibly empty) list of number representing hours [0-23].
        """
        result = []
        if isinstance(room, Room) and room.db_id is not None:
            query = f"""
SELECT  STRFTIME('%H', DATETIME(m.ts)) AS hours 
FROM measurements m 
INNER JOIN devices d ON m.device = d.id 
INNER JOIN rooms r ON r.id = d.room 
WHERE 
r.id = {room.db_id}
AND m.unit = '%' 
AND DATE(m.ts) = DATE('{date}')
AND m.value > (
	SELECT AVG(value) 
	FROM measurements m 
	INNER JOIN devices d on d.id = m.device
	WHERE d.room = 4 AND DATE(ts) = DATE('{date}'))
GROUP BY hours
HAVING COUNT(m.value) > 3;
            """
            cursor = self.cursor()
            cursor.execute(query)
            for h in cursor.fetchall():
                result.append(int(h[0]))
        return result