class Measurement:
    """
    This class represents a measurement taken from a sensor.
    """

    def __init__(self, timestamp, value, unit):
        self.timestamp = timestamp
        self.value = value
        self.unit = unit


class Device:
    """
    Class for all smart devices.
    """

    def __init__(self, device_id, manufacturer, model, device_type, nickname=None):
        self.device_id = device_id
        self.manufacturer = manufacturer
        self.model = model
        self.device_type = device_type
        self.nickname = nickname


class Sensor(Device):
    """
    A sensor device that records measurements.
    """

    def __init__(self, device_id, manufacturer, model, device_type, nickname=None):
        super().__init__(device_id, manufacturer, model, device_type, nickname)
        self.measurements = []

    def add_measurement(self, measurement):
        self.measurements.append(measurement)

    def get_latest_measurement(self):
        if self.measurements:
            return self.measurements[-1]
        return None

    def get_measurement_history(self):
        return self.measurements


class Actuator(Device):
    """
    A device that can change its state.
    """

    def __init__(self, device_id, manufacturer, model, device_type, nickname=None):
        super().__init__(device_id, manufacturer, model, device_type, nickname)
        self.state = False

    def turn_on(self):
        self.state = True

    def turn_off(self):
        self.state = False

    def set_state(self, state):
        self.state = state


class Room:
    """
    Represents a room in a floor.
    """

    def __init__(self, room_size, room_name=None):
        self.room_size = room_size
        self.room_name = room_name
        self.devices = []

    def add_device(self, device):
        self.devices.append(device)


class Floor:
    """
    Represents a floor in the house.
    """

    def __init__(self, level):
        self.level = level
        self.rooms = []

    def add_room(self, room):
        self.rooms.append(room)

    def get_area(self):
        return sum(room.room_size for room in self.rooms)


class SmartHouse:
    """
    This class serves as the main entity and entry point for the SmartHouse system app.
    Do not delete this class nor its predefined methods since other parts of the
    application may depend on it (you are free to add as many new methods as you like, though).

    The SmartHouse class provides functionality to register rooms and floors (i.e. changing the 
    house's physical layout) as well as register and modify smart devices and their state.
    """
    def __init__(self):
        self.floors[]
        self.device_registry = {}
    

    def register_floor(self, level):
        """
        This method registers a new floor at the given level in the house
        and returns the respective floor object.
        """
        floor = Floor(level)
        self.floors.append(floor)
        self.floors.sort(key=lambda f: f.level)
        return floor

    def register_room(self, floor, room_size, room_name = None):
        """
        This methods registers a new room with the given room areal size 
        at the given floor. Optionally the room may be assigned a mnemonic name.
        """
        room = Room(room_size, room_name)
        floor.add_room(room)
        return room


    def get_floors(self):
        """
        This method returns the list of registered floors in the house.
        The list is ordered by the floor levels, e.g. if the house has 
        registered a basement (level=0), a ground floor (level=1) and a first floor 
        (leve=1), then the resulting list contains these three flors in the above order.
        """
        return self.floors
    


    def get_rooms(self):
        """
        This methods returns the list of all registered rooms in the house.
        The resulting list has no particular order.
        """
        rooms = []
        for floor in self.floors:
            rooms.extend(floor.rooms)
        return rooms


    def get_area(self):
        """
        This methods return the total area size of the house, i.e. the sum of the area sizes of each room in the house.
        """
        return sum(floor.get_area() for floor in self.floors)



    def register_device(self, room, device):
        """
        This methods registers a given device in a given room.
        """
        room.add_device(device)

    
    def get_device(self, device_id):
        """
        This method retrieves a device object via its id.
        """
        for floor in self.floors:
            for room in floor.rooms:
                for device in room.devices:
                    if device.device_id == device_id:
                        return device
        return None


house = SmartHouse()

floor1 = house.register_floor(1)
living_room = house.register_room(floor1, 25, "Living Room")

sensor = Sensor("T100", "Philips", "TempX", "temperature")
house.register_device(living_room, sensor)

m = Measurement("2026-03-14 10:00", 21.5, "°C")
sensor.add_measurement(m)

print(sensor.get_latest_measurement().value)