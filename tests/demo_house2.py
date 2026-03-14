from smarthouse.domain import SmartHouse

DEMO_HOUSE = SmartHouse()

# Building house structure
ground_floor = DEMO_HOUSE.register_floor(1)
entrance = DEMO_HOUSE.register_room(ground_floor, 13.5, "Entrance")
# TODO: continue registering the remaining floor, rooms and devices

class SmartHouse:

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


    def get_devices(self):

        devices = []

        for room in self.get_rooms():
            devices.extend(room.devices)

        return devices


    def get_device_by_id(self, device_id):

        return self.device_registry.get(device_id, None)