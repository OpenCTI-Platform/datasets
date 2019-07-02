import json
import uuid

with open('../data/sectors.json') as json_file:
    sectors = json.load(json_file)

final_sectors = []
for sector in sectors:
    final_sector = dict()
    if 'stix_id' in sector:
        final_sector['stix_id'] = sector['stix_id']
    else:
        final_sector['stix_id'] = 'identity--' + str(uuid.uuid4())
    final_sector['name'] = sector['name']
    final_sector['description'] = sector['description']

    if 'subsectors' in sector:
        final_subsectors = []
        for subsector in sector['subsectors']:
            final_subsector = dict()
            if 'stix_id' in subsector:
                final_subsector['stix_id'] = subsector['stix_id']
            else:
                final_subsector['stix_id'] = 'identity--' + str(uuid.uuid4())
            final_subsector['name'] = subsector['name']
            final_subsector['description'] = subsector['description']
            final_subsectors.append(final_subsector)
        final_sector['subsectors'] = final_subsectors

    final_sectors.append(final_sector)

with open('../data/sectors.json', 'w') as file:
    json.dump(final_sectors, file, indent=4)
