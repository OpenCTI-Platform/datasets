# coding: utf-8

import csv
from stix2 import Bundle, Identity, Location, Relationship, TLP_WHITE

csv_file = open('../raw/geo.csv', mode='r', encoding='utf-8')

geography = csv.reader(csv_file, delimiter=',', quotechar='"')
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

i = 0
bundle_objects = [filigran]
regions = {}
subregions = {}
relations = {}
for row in geography:
    if i == 0:
        i += 1
        continue
    id_region = row[0]
    id_subregion = row[1]
    id_country = row[2]
    region = row[3]
    subregion = row[4]
    country = row[6]
    country_code = row[7]
    country_code2 = row[8]
    country_lat = row[9]
    country_lng = row[10]
    regionlat = row[11]
    regionlng = row[12]
    subregionlat = row[13]
    subregionlng = row[14]
    if region:
        if region not in regions:
            stix_region = Location(
                id='location--' + id_region,
                name=region,
                region=region,
                latitude=float(regionlat) if len(regionlat) > 0 else None,
                longitude=float(regionlng) if len(regionlng) > 0 else None,
                created_by_ref=filigran,
                object_marking_refs=[TLP_WHITE],
                confidence=100,
                revoked=False,
                custom_properties={
                    'x_opencti_location_type': 'Region'
                }
            )
            regions[region] = stix_region
            bundle_objects.append(stix_region)
    if subregion:
        if subregion not in subregions:
            stix_subregion = Location(
                id='location--' + id_subregion,
                name=subregion,
                region=subregion,
                latitude=float(subregionlat) if len(subregionlat) > 0 else None,
                longitude=float(subregionlng) if len(subregionlng) > 0 else None,
                created_by_ref=filigran,
                object_marking_refs=[TLP_WHITE],
                confidence=100,
                revoked=False,
                custom_properties={
                    'x_opencti_location_type': 'Region'
                }
            )
            bundle_objects.append(stix_subregion)
            subregions[subregion] = stix_subregion
            if region:
                stix_subregion_relationship = Relationship(
                    relationship_type='located-at',
                    source_ref=stix_subregion.id,
                    target_ref=regions[region].id,
                    description='Region ' + stix_subregion.name + ' is located in ' + regions[region].name,
                    confidence=100,
                    revoked=False,
                    created_by_ref=filigran,
                    object_marking_refs=[TLP_WHITE],
                )
                bundle_objects.append(stix_subregion_relationship)
    stix_country = Location(
        id='location--' + id_country,
        name=country,
        country=country_code,
        latitude=float(country_lat) if len(country_lat) > 0 else None,
        longitude=float(country_lng) if len(country_lng) > 0 else None,
        created_by_ref=filigran,
        object_marking_refs=[TLP_WHITE],
        confidence=100,
        revoked=False,
        custom_properties={
            'x_opencti_location_type': 'Country',
            'x_opencti_aliases': [country_code, country_code2]
        }
    )
    bundle_objects.append(stix_country)
    if region and subregion:
        stix_country_relationship = Relationship(
            relationship_type='located-at',
            source_ref=stix_country.id,
            target_ref=subregions[subregion].id,
            description='Country ' + stix_country.name + ' is located in ' + subregions[subregion].name,
            object_marking_refs=[TLP_WHITE],
            confidence=100,
            revoked=False,
            created_by_ref=filigran,
        )
        bundle_objects.append(stix_country_relationship)
    elif region:
        stix_country_relationship = Relationship(
            relationship_type='located-at',
            source_ref=stix_country.id,
            target_ref=regions[region].id,
            description='Country ' + stix_country.name + ' is located in ' + regions[region].name,
            object_marking_refs=[TLP_WHITE],
            confidence=100,
            revoked=False,
            created_by_ref=filigran,
        )
        bundle_objects.append(stix_country_relationship)
    i += 1

bundle = Bundle(objects=bundle_objects, allow_custom=True)
fh = open('../data/geography.json', 'w')
fh.write(bundle.serialize(pretty=True, include_optional_defaults=True))
fh.close()
