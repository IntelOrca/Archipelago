from BaseClasses import NamedTuple
from typing import List
import collections
import json

class ItemData(NamedTuple):
    id: int
    type: int
    amount: int
    name: str
    group: str

class LocationData(NamedTuple):
    id: int
    name: str
    item: int
    priority: str
    requires: List[int]

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
    
    def get_item_id_to_name_map(self):
        return {item.id: item.name for item in self.items}

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
        items.append(ItemData(i['id'], i.get('type', 0), i.get('amount', 0), i['name'], group))

    locations = []
    for l in data['locations']:
        locations.append(LocationData(l['id'], l['name'], l['item'], l.get('priority', 'normal'), l.get('requires', [])))

    regions = []
    for r in data['regions']:
        edges = []
        if 'edges' in r:
            for e in r['edges']:
                edges.append(RegionEdge(e['region'], e.get('requires', [])))
        regions.append(RegionData(r['id'], r['name'], r['locations'], edges))

    return BioRandData(items, locations, regions)
