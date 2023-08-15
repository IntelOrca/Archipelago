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
    id: int
    name: str
    item: int
    priority: str

class RegionEdge(NamedTuple):
    region: int
    requires: List[int]

class RegionData(NamedTuple):
    id: int
    name: str
    locations: List[int]
    edges: List[RegionEdge]

class BioRandData(NamedTuple):
    items: List[ItemData]
    locations: List[LocationData]
    regions: List[RegionData]

    def get_item_name_to_id_map(self):
        return {item.name: item.id for item in self.items}

    def get_location_name_to_id_map(self):
        return {location.name: location.id for location in self.locations}

    def get_location_id_to_name_map(self):
        return {location.id: location.name for location in self.locations}

    def get_item_name_groups(self):
        group_to_names = collections.defaultdict(set)
        for item in self.items:
            group_to_names[item.group].add(item.name)
        return dict(group_to_names)

def load_biorand_data(path: str) -> BioRandData:

    with open(path, "r") as json_file:
        data = json.load(json_file)
    print(data['seed'])

    items = []
    for i in data['items']:
        group = i.get('group', 'misc')
        items.append(ItemData(i['type'], i['amount'], i['name'], group))

    locations = []
    for l in data['locations']:
        locations.append(LocationData(l['id'], l['name'], l['item'], l['priority']))

    regions = []
    for r in data['regions']:
        edges = []
        if ('edges' in data):
            for e in data['edges']:
                edges.append(RegionEdge(r['region'], r['requires']))
        regions.append(RegionData(r['id'], r['name'], r['locations'], edges))

    return BioRandData(items, locations, regions)
