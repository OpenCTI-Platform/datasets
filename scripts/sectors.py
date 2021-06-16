# coding: utf-8

import json
import uuid
import datetime
from stix2 import Bundle, Identity, Relationship

with open('../raw/sectors.json') as json_file:
    sectors = json.load(json_file)

anssi = Identity(
    id='identity--7b82b010-b1c0-4dae-981f-7756374a17df',
    name="Agence Nationale de la Sécurité des Systèmes d'Information",
    description="The Agence nationale de la sécurité des systèmes d'information (ANSSI; English: National Cybersecurity Agency of France) is a French service created on 7 July 2009 with responsibility for computer security.",
    identity_class='organization',
    custom_properties={
        'x_opencti_aliases': ['ANSSI'],
        'x_opencti_organization_type': 'csirt',
    }
)

bundle_objects = [anssi]
for sector in sectors:
    stix_sector = Identity(
        id=sector['stix_id'],
        name=sector['name'],
        description=sector['description'],
        identity_class='class',
        created_by_ref=anssi,
        custom_properties={
            'x_opencti_aliases': sector['aliases'],
        }
    )
    bundle_objects.append(stix_sector)
    if 'subsectors' in sector:
        for subsector in sector['subsectors']:
            stix_subsector = Identity(
                id=subsector['stix_id'],
                name=subsector['name'],
                description=subsector['description'],
                identity_class='class',
                created_by_ref=anssi,
                custom_properties={
                    'x_opencti_aliases': subsector['aliases'],
                }
            )
            bundle_objects.append(stix_subsector)
            stix_subsector_relationship = Relationship(
                relationship_type='part-of',
                source_ref=stix_subsector.id,
                target_ref=stix_sector.id,
                description='Sector ' + stix_subsector.name + ' is a subsector of ' + stix_sector.name,
                created_by_ref=anssi,
                confidence=100,
            )
            bundle_objects.append(stix_subsector_relationship)

bundle = Bundle(objects=bundle_objects)
fh = open('../data/sectors.json', 'w')
fh.write(str(bundle))
fh.close()
