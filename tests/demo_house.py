from smarthouse.domain import SmartHouse

DEMO_HOUSE = SmartHouse()

# Building house structure
ground_floor = DEMO_HOUSE.register_floor(1)
second_floor = DEMO_HOUSE.register_floor(2)

#Registering rooms in ground floor
entrance = DEMO_HOUSE.register_room(ground_floor, 13.5, "Entrance")
guest_room1 = DEMO_HOUSE.register_room(ground_floor,8, "Guest room 1" )
bathroom1 = DEMO_HOUSE.register_room(ground_floor, 6.3, "Bathroom 1")
livingroom_kitchen = DEMO_HOUSE.register_room(ground_floor, 39.75, "Livingroom/Kitchen")
garage = DEMO_HOUSE.register_room(ground_floor, 19, "Garage")

#Registering rooms in second floor
hallway = DEMO_HOUSE.register_room(second_floor, 10, "Hallway")
guest_room2 = DEMO_HOUSE.register_room(second_floor, 8, "Guest room 2")
master_bedroom = DEMO_HOUSE.register_room(second_floor, 17, "Master bedroom")
guest_room3 = DEMO_HOUSE.register_room(second_floor, 10, "Guest room 3")
bathroom2 = DEMO_HOUSE.register_room(second_floor, 9.25, "Bathroom 2")
dressing_room = DEMO_HOUSE.register_room(second_floor, 4, "Dressing room")
office = DEMO_HOUSE.register_room(second_floor, 11.75, "Office")






# TODO: continue registering the remaining floor, rooms and devices

