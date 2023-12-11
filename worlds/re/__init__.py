from .Data import ItemData, load_biorand_data
from BaseClasses import Location, Item, ItemClassification, LocationProgressType, Region, NamedTuple
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

    # Our optional maps
    item_id_to_data = {item.id: item for item in biorand_data.items}

    def get_item_classification(self, group: str):
        if group == "key" or group == "event":
            return ItemClassification.progression
        elif group == "weapon":
            return ItemClassification.useful
        else:
            return ItemClassification.filler

    def create_item(self, item: ItemData) -> ResidentEvilItem:
        return ResidentEvilItem(item.name, self.get_item_classification(item.group), item.id, self.player)

    def create_items(self) -> None:
        item_pool: List[ResidentEvilItem] = []
        for location in biorand_data.locations:
            item = self.item_id_to_data[location.item]
            if (item.group != "event"):
                item_pool.append(self.create_item(item))
        self.multiworld.itempool += item_pool

    def create_regions(self) -> None:
        menu_region = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu_region)

        # Location map
        location_id_to_name = biorand_data.get_location_id_to_name_map()
        self.item_id_to_name = biorand_data.get_item_id_to_name_map()

        # Create regions
        regions: List[Region] = []
        for br in biorand_data.regions:
            region = Region(br.name, self.player, self.multiworld)
            region_locations = {location_id_to_name[location]: location for location in br.locations}
            region.add_locations(region_locations, ResidentEvilLocation)
            regions.append(region)
            self.multiworld.regions.append(region)

        # Connect regions together
        for index, br in enumerate(biorand_data.regions):
            region = regions[index]
            for edge in br.edges:
                target_region = regions[edge.region]
                if edge.requires:
                    keys = self.item_id_to_item_name_set(edge.requires)
                    region.connect(target_region, f"require{keys}", self.has_requirements(edge.requires))
                else:
                    region.connect(target_region)

        menu_region.connect(regions[0])

    def generate_basic(self) -> None:
        for bl in biorand_data.locations:
            location = self.multiworld.get_location(bl.name, self.player)
            item = self.item_id_to_data[bl.item]
            if item.group == "event":
                location.place_locked_item(self.create_item(item))
            if bl.requires:
                location.access_rule = self.has_requirements(bl.requires)
            # TODO
            # if bl.priority == "fixed":
            #     location.place_locked_item(...)
            if bl.priority == "low":
                location.progress_type = LocationProgressType.EXCLUDED;

        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)

    def get_filler_item_name(self) -> str:
        return "Green Herb"

    def has_requirements(self, requires: List[int]):
        keys = self.item_id_to_item_name_set(requires)
        return lambda state: state.has_all(keys, self.player)

    def item_id_to_item_name_set(self, values: List[int]):
        return set(map(lambda id: self.item_id_to_name[id], values))
