from BaseClasses import NamedTuple
from typing import List
import collections
import json

class ItemData(NamedTuple):
    type: int
    amount: int
    name: str
    group: str

    @property
    def id(self) -> int:
        return self.type | (self.amount << 8)

class LocationData(NamedTuple):
    index: int
    name: str
    item: int

class RegionData(NamedTuple):
    name: str
    locations: List[LocationData]
    edges: List[int]

class BioRandData(NamedTuple):
    items: List[ItemData]
    locations: List[LocationData]
    regions: List[RegionData]

    def get_item_name_to_id_map(self):
        return {item.name: item.id for item in self.items}

    def get_location_name_to_id_map(self):
        return {location.name: location.index for location in self.locations}

    def get_item_name_groups(self):
        group_to_names = collections.defaultdict(set)
        for item in self.items:
            group_to_names[item.group].add(item.name)
        return dict(group_to_names)

def load_biorand_data(path: str) -> BioRandData:
    items = []
    locations = []
    regions = []

    with open(path, "r") as json_file:
        data = json.load(json_file)
    print(data['seed'])
    for i in data['items']:
        items.append(ItemData(i['type'], i['amount'], i['name'], i['group']))

    location_id = 0
    for region in data['regions']:
        region_locations = []
        for i in region['locations']:
            location = LocationData(location_id, i['name'], i['item'])
            locations.append(location)
            region_locations.append(location)
            location_id = location_id + 1
        regions.append(RegionData(region['name'], region_locations, region['edges']))

    return BioRandData(items, locations, regions)
