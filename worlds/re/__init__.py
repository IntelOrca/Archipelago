import settings
import typing
# from .Options import residentevil_options  # the options we defined earlier
# from .Items import residentevil_items  # data used below to add items to the World
# from .Locations import residentevil_locations  # same as above
from worlds.AutoWorld import World
from BaseClasses import Location, Item, ItemClassification, Region, NamedTuple
from Options import Option, DefaultOnToggle

class RandomMusic(DefaultOnToggle):
    """Whether background music will be randomized"""
    display_name = "Randomize music"

class ItemData(NamedTuple):
    type: int
    amount: int
    name: str

    @property
    def id(self) -> int:
        return self.type | (self.amount << 8)

residentevil_items = [
    ItemData(20, 15, "Handgun Ammo"),
    ItemData(21, 6, "Shotgun Ammo"),
    ItemData(30, 2, "Ink Ribbon"),
    ItemData(35, 1, "First Aid Spray"),
    ItemData(38, 1, "Green Herb"),
    ItemData(39, 1, "Red Herb"),
    ItemData(40, 1, "Blue Herb"),
]

class LocationData(NamedTuple):
    index: int
    name: str

residentevil_locations = [
    LocationData(index, f"Item {index}") for index in range(256)
]

residentevil_options: typing.Dict[str, type(Option)] = {
    "random_bgm": RandomMusic
}

class ResidentEvilItem(Item):  # or from Items import ResidentEvilItem
    game = "Resident Evil"  # name of the game/world this item is from


class ResidentEvilLocation(Location):  # or from Locations import ResidentEvilLocation
    game = "Resident Evil"  # name of the game/world this location is in


class ResidentEvilSettings(settings.Group):
    random_bgm = False

class ResidentEvilWorld(World):
    """Insert description of the world/game here."""
    game = "Resident Evil"  # name of the game/world
    option_definitions = residentevil_options  # options the player can set
    settings: typing.ClassVar[ResidentEvilSettings]  # will be automatically assigned from type hint
    topology_present = True  # show path to required location checks in spoiler

    # ID of first item and location, could be hard-coded but code may be easier
    # to read with this as a property.
    base_id = 1234
    # Instead of dynamic numbering, IDs could be part of data.

    # The following two dicts are required for the generation to know which
    # items exist. They could be generated from json or something else. They can
    # include events, but don't have to since events will be placed manually.
    item_name_to_id = {item.name: item.id for item in residentevil_items}
    location_name_to_id = {location.name: location.index for location in residentevil_locations}

    # Items can be grouped using their names to allow easy checking if any item
    # from that group has been collected. Group names can also be used for !hint
    item_name_groups = {
        "weapons": {"handgun", "magnum"},
    }

    def create_item(self, name: str) -> ResidentEvilItem:
        return ResidentEvilItem(name, ItemClassification.filler, self.item_name_to_id[name], self.player)

    def create_items(self) -> None:
        item_pool: List[ResidentEvilItem] = []
        for i in range(1, 10):
            for item in residentevil_items:
                item_pool.append(self.create_item(item.name))
        self.multiworld.itempool += item_pool

    def create_regions(self) -> None:
        menu_region = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu_region)

        main_region = Region("Main Area", self.player, self.multiworld)
        main_region.add_locations(self.location_name_to_id, ResidentEvilLocation)

        self.multiworld.regions.append(main_region)

        menu_region.connect(main_region)

#    def generate_basic(self) -> None:
#        item = self.create_item("Green Herb")
#        self.multiworld.get_location("200", self.player).place_locked_item(item)
#
    def get_filler_item_name(self) -> str:
        return "Green Herb"
