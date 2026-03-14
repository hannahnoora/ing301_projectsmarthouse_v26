from smarthouse.domain import SmartHouse, Sensor, Actuator

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


#Registering the different devices
smartlock_entrance = Actuator('4d5f1ac6-906a-4fd1-b4bf-3a0671e4c4f1', 'Smart Lock', 'MythicalTech', 'Guardian Lock 7000', 'LockEntrance')
co2sensor_kitchen = Sensor('8a43b2d7-e8d3-4f3d-b832-7dbf37bf629e', 'CO2 sensor', 'ElysianTech', 'Smoke Warden 1000', 'CO2kitchen')
electricitymeter_entrance = Sensor('a2f8690f-2b3a-43cd-90b8-9deea98b42a7', 'Electricity Meter', 'MysticEnergy Innovations', 'Volt Watch Elite', 'ElEntrance')
heatpump_livingroom = Actuator('5e13cabc-5c58-4bb3-82a2-3039e4480a6d', 'Heat Pump', 'ElysianTech', 'Thermo Smart 6000', 'HeatLivingroom')
motionsensor_livingroom = Sensor('cd5be4e8-0e6b-4cb5-a21f-819d06cf5fc5', 'Motion Sensor', 'NebulaGuard Innovations', 'MoveZ Detect 69', 'MotionLivingroom')
humiditysensor_bathroom1 = Sensor('3d87e5c0-8716-4b0b-9c67-087eaaed7b45', 'Humidity Sensor', 'AetherCorp', 'Aqua Alert 800', 'HumidBathroom')
smartoven_guestroom1 = Actuator('8d4e4c98-21a9-4d1e-bf18-523285ad90f6', 'Smart Oven', 'AetherCorp', 'Pheonix HEAT 333', 'OvenGR1')
door_garage = Actuator('9a54c1ec-0cb5-45a7-b20d-2a7349f1b132', 'Automatic Garage Door', 'MythicalTech', 'Guardian Lock 9000', 'DoorGarage')
smartoven_masterbedroom = Actuator('c1e8fa9c-4b8d-487a-a1a5-2b148ee9d2d1', 'Smart Oven', 'IgnisTech Solutions', 'Ember Heat 3000', 'OvenMB')
tempsensor_masterbedroom = Sensor('4d8b1d62-7921-4917-9b70-bbd31f6e2e8e', 'Temperature Sensor', 'AetherCorp', 'SmartTemp 42', 'TempMB')
airquality_guestroom3 = Sensor('7c6e35e1-2d8b-4d81-a586-5d01a03bb02c', 'Air Quality Sensor', 'CelestialSense Technologies', 'AeroGuard Pro', 'AirGR3')
smartplug_office = Actuator('1a66c3d6-22b2-446e-bf5c-eb5b9d1a8c79', 'Smart Plug', 'MysticEnergy Innovations', 'FlowState X', 'PlugOffice')
dehumidifier_bathroom2 = Actuator('9e5b8274-4e77-4e4e-80d2-b40d648ea02a', 'Dehumidifier', 'ArcaneTech Solutions', 'Hydra Dry 8000', 
'DeHumidBathroom2')
light_guestroom2 = Actuator('6b1c5f6b-37f6-4e3d-9145-1cfbe2f1fc28', 'Light Bulb', 'Elysian Tech', 'Lumina Glow 4000', 'LightGR2')

#Registering devices in correct rooms
DEMO_HOUSE.register_device(entrance, smartlock_entrance)
DEMO_HOUSE.register_device(livingroom_kitchen, co2sensor_kitchen)
DEMO_HOUSE.register_device(entrance, electricitymeter_entrance)
DEMO_HOUSE.register_device(livingroom_kitchen, heatpump_livingroom)
DEMO_HOUSE.register_device(livingroom_kitchen, motionsensor_livingroom)
DEMO_HOUSE.register_device(bathroom1, humiditysensor_bathroom1)
DEMO_HOUSE.register_device(guest_room1, smartoven_guestroom1)
DEMO_HOUSE.register_device(garage, door_garage)
DEMO_HOUSE.register_device(master_bedroom, smartoven_masterbedroom)
DEMO_HOUSE.register_device(master_bedroom, tempsensor_masterbedroom)
DEMO_HOUSE.register_device(guest_room3, airquality_guestroom3)
DEMO_HOUSE.register_device(office, smartplug_office)
DEMO_HOUSE.register_device(bathroom2, dehumidifier_bathroom2)
DEMO_HOUSE.register_device(guest_room2, light_guestroom2)

