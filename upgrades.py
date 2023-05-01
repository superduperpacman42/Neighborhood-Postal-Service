vehicle = (
    ("Buy Mail Bag", 5, {"Capacity": 100}, "PlayerBag"),
    ("Buy Bicycle", 20, {"Speed": 50, "Capacity": 100}, "PlayerBike"),
    ("Gear Shifter", 10, {"Speed": 50}),
    ("Buy Car", 200, {"Speed": 100, "Capacity": 100}, "PlayerCar"),
    ("Buy Truck", 2000, {"Capacity": 200}, "PlayerTruck"),
    ("Bigger Tires", 1000, {"Speed": 50}),
    ("Buy Plane", 1000000, {"Speed": 300}, "PlayerPlane", "Boxes"),
    ("Supersonic", 5000000, {"Speed": 100}),
    ("Hypersonic", 10000000, {"Speed": 100}),
)

special = (
    ("Buy Running Shoes", 5, {"Speed": 100}),
    ("Forever Stamps", 10, {"Profit": 100}),
    ("Put Up Flyers", 15, {"Demand": 100}),
    ("Express Mail", 20, {"Profit": 100}),
    ("Priority Mail", 30, {"Profit": 100}),
    ("Hand Out Coupons", 50, {"Demand": 100}),
    ("Social Media", 200, {"Demand": 300}),
    ("Package Service", 250, {"Profit": 100}, None, "Box"),
    ('"Free" Shipping', 500, {"Demand": 100, "Profit": 100}),
    ("TV Commercials", 1000, {"Demand": 200}),
    ("Compressed Boxes", 5000, {"Capacity": 200}),
    ("6-Wheel Drive", 5000, {"Speed": 100}),
    ("Fractal Packing", 10000, {"Capacity": 300}),
    ("Targeted Ads", 5000000, {"Demand": 200}),
    ("Turbo Lift", 5000000, {"Capacity": 100}),
    ("Longer Runways", 10000000, {"Capacity": 100}),
    ("Big Data", 50000000, {"Demand": 200}),
    ("Jumbo Jets", 100000000, {"Capacity": 300}),
    ("Brainwashing", 100000000, {"Demand": 200}),
    ("Bribe Politicians", 500000000, {"Profit": 300}),
)

mailman = (
    ("Hire Mailman", 50, {"Employee": 0}),
    ("Upgrade Mailmen", 150, {"Employee Speed": 50, "Employee Capacity": 100}),
)

trucker = (
    ("Hire Trucker", 5000, {"Employee": 1}),
    ("Upgrade Truckers", 15000, {"Employee Speed": 50, "Employee Capacity": 100}),
)

pilot = (
    ("Hire Pilot", 10000000, {"Employee": 2}),
    ("Upgrade Pilots", 30000000, {"Employee Speed": 50, "Employee Capacity": 100}),
)

road_upgrade = (
    ("Build Highway", 2500, {"Speed": 300}),
    ("Fully Upgraded", 0, {}),
)

city_upgrade = (
    ("Build Distribution Center", 5000, {"Demand": 300}),
    ("Fully Upgraded", 0, {}),
)

capital_upgrade = (
    ("Build Corporate HQ", 100000, {"Profit": 5000}),
    ("Fully Upgraded", 0, {}),
)

nation_upgrade = (
    ("Build Regional HQ", 10000000, {"Demand": 300}),
    ("Fully Upgraded", 0, {}),
)

home_nation_upgrade = (
    ("Build Shipping Capital", 50000000, {"Profit": 200}),
    ("Build Spaceport", 1000000000, {}),
    ("Fully Upgraded", 0, {}),
)

space_upgrade = (
    ("Launch Space Colony", 10000000000, {}),
)
play_again = (
    ("Play Again", 53, {}),
)

upgraded = ("Fully Upgraded", 0, {})

parallel_types = ["special"]


def copy_upgrade(upgrade, n=5, scale=1.5):
    upgrades = []
    for i in range(n):
        upgrades.append((upgrade[0], upgrade[1] * (scale ** i), upgrade[2]))
    return upgrades


def render_upgrade(attribute, value):
    if attribute == "Employee":
        return "+1 Employee"
    return "+" + str(value) + "% " + attribute
