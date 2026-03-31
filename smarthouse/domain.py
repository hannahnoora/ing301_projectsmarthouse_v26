import random
import datetime


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

    def __init__(self, device_id, device_type, supplier, model_name, nickname=None):
        self.id = device_id
        self.device_type = device_type
        self.supplier = supplier
        self.model_name = model_name
        self.nickname = nickname
        self.room = None

    def is_actuator(self):
        return isinstance(self, Actuator)

    def is_sensor(self):
        return isinstance(self, Sensor)

    def get_device_type(self):
        return self.device_type


class Sensor(Device):
    """
    A sensor device that records measurements.
    """

    def __init__(self, device_id, device_type, supplier, model_name, nickname=None):
        super().__init__(device_id, device_type, supplier, model_name, nickname)
        self.measurements = []
        self.unit = "°C"

    def add_measurement(self, measurement):
        self.measurements.append(measurement)

    def get_latest_measurement(self):
        if self.measurements:
            return self.measurements[-1]
        return None

    def get_measurement_history(self):
        return self.measurements

    def last_measurement(self):
        #Simulating random measurement with the current timestamp
        
        if self.measurements:
            return self.measurements[-1]
        
        value = random.uniform(0, 100)
        timestamp = datetime.datetime.now().isoformat()
        return Measurement(timestamp, float(value), self.unit)


class Actuator(Device):
    """
    A device that can change its state.
    """

    def __init__(self, device_id, manufacturer, model, device_type, nickname=None, target_value=None):
        super().__init__(device_id, manufacturer, model, device_type, nickname)
        self.state = False
        self.target_value = None

    def turn_on(self, value=None):
        self.state = True
        self.target_value = value

    def turn_off(self):
        self.state = False
        self.target_value = None

    def is_active(self):
        return self.state


class Room:
    """
    Represents a room in a floor.
    """

    def __init__(self, room_size, room_name=None):
        self.room_size = room_size
        self.room_name = room_name
        self.devices = []

    def add_device(self, device):

        if device.room and device in device.room.devices:
            device.room.devices.remove(device)

        self.devices.append(device)
        device.room = self


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
    Main entity and entry point for the SmartHouse system.
    """

    def __init__(self):
        self.floors = []
        self.device_registry = {}

    def register_floor(self, level):
        floor = Floor(level)
        self.floors.append(floor)
        self.floors.sort(key=lambda f: f.level)
        return floor

    def register_room(self, floor, room_size, room_name=None):
        room = Room(room_size, room_name)
        floor.add_room(room)
        return room

    def get_floors(self):
        return self.floors

    def get_rooms(self):
        rooms = []
        for floor in self.floors:
            rooms.extend(floor.rooms)
        return rooms

    def get_area(self):
        return sum(floor.get_area() for floor in self.floors)

    def register_device(self, room, device):

        room.add_device(device)
        self.device_registry[device.id] = device

        return None
    
    def get_device_by_id(self, device_id):
        """
        This method retrieves a device object via its id.
        """
        for floor in self.floors:
            for room in floor.rooms:
                for device in room.devices:
                    if device.id == device_id:
                        return device
        return None
                    
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
    
    def get_device(self):

        devices = []

        for room in self.get_rooms():
            devices.extend(room.devices)

        return devices
