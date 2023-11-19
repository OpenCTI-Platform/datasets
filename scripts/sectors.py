# coding: utf-8

import json
from stix2 import Bundle, Identity, Relationship, TLP_WHITE

with open('../raw/sectors.json', mode='r', encoding='utf-8') as json_file:
    sectors = json.load(json_file)

filigran = Identity(
    id='identity--8cb00c79-ab20-5ed4-b37d-337241b96a29',
    name="Filigran",
    description="Filigran is a cybertech founded in 2022, providing cyber threat intelligence, adversary simulation and crisis management solutions to cybersecurity teams across the world.",
    identity_class="organization",
    object_marking_refs=[TLP_WHITE],
    confidence=100,
    revoked=False,
    custom_properties={
        'x_opencti_organization_type': 'vendor',
    }
)

bundle_objects = [filigran]
for sector in sectors:
    stix_sector = Identity(
        id=sector['stix_id'],
        name=sector['name'],
        description=sector['description'],
        identity_class='class',
        created_by_ref=filigran,
        object_marking_refs=[TLP_WHITE],
        confidence=100,
        revoked=False,
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
                created_by_ref=filigran,
                object_marking_refs=[TLP_WHITE],
                confidence=100,
                revoked=False,
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
                created_by_ref=filigran,
                object_marking_refs=[TLP_WHITE],
                confidence=100,
                revoked=False,
            )
            bundle_objects.append(stix_subsector_relationship)

bundle = Bundle(objects=bundle_objects, allow_custom=True)
fh = open('../data/sectors.json', 'w')
fh.write(bundle.serialize(pretty=True, include_optional_defaults=True))
fh.close()
