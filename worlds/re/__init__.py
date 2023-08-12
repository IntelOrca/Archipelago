from .Data import load_biorand_data
from BaseClasses import Location, Item, ItemClassification, Region, NamedTuple
from Options import Option, DefaultOnToggle
from typing import List
from worlds.AutoWorld import World
import settings
import typing

biorand_data = load_biorand_data("/mnt/f/games/re2/mod_biorand/ap_pl0.json")

class RandomMusic(DefaultOnToggle):
    """Whether background music will be randomized"""
    display_name = "Randomize music"

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
    game = "Resident Evil"
    option_definitions = residentevil_options
    settings: typing.ClassVar[ResidentEvilSettings]  # will be automatically assigned from type hint
    topology_present = True  # show path to required location checks in spoiler

    item_name_to_id = biorand_data.get_item_name_to_id_map()
    location_name_to_id = biorand_data.get_location_name_to_id_map()
    item_name_groups = biorand_data.get_item_name_groups()

    def create_item(self, name: str) -> ResidentEvilItem:
        return ResidentEvilItem(name, ItemClassification.filler, self.item_name_to_id[name], self.player)

    def create_items(self) -> None:
        item_id_to_data = {item.id: item for item in biorand_data.items}
        item_pool: List[ResidentEvilItem] = []
        for location in biorand_data.locations:
            item = item_id_to_data[location.item]
            item_pool.append(self.create_item(item.name))
        self.multiworld.itempool += item_pool

    def create_regions(self) -> None:
        menu_region = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu_region)
    
        # Create regions
        regions = []
        for br in biorand_data.regions:
            region = Region(br.name, self.player, self.multiworld)
            region_locations = {location.name: location.index for location in br.locations}
            region.add_locations(region_locations, ResidentEvilLocation)
            regions.append(region)
            self.multiworld.regions.append(region)

        # Connect regions together
        for index, br in enumerate(biorand_data.regions):
            region = regions[index]
            for edge in br.edges:
                region.connect(regions[edge])

        menu_region.connect(regions[0])

#    def generate_basic(self) -> None:
#        item = self.create_item("Green Herb")
#        self.multiworld.get_location("200", self.player).place_locked_item(item)
#
    def get_filler_item_name(self) -> str:
        return "Green Herb"
