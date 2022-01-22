#!/usr/bin/env python
# coding: utf-8

import json
import os
from csv import DictReader
from stix2 import Bundle, Identity, Relationship, TLP_WHITE


raw_file = '../raw/companies.csv'
out_file = '../data/companies.json'

sector_file = '../data/sectors.json'
geograph_file = '../data/geography.json'

anssi = Identity(
    id='identity--7b82b010-b1c0-4dae-981f-7756374a17df',
    name="Agence Nationale de la Sécurité des Systèmes d'Information",
    description="The Agence nationale de la sécurité des systèmes d'information (ANSSI; English: National Cybersecurity Agency of France) is a French service created on 7 July 2009 with responsibility for computer security.",
    identity_class='organization',
    object_marking_refs=[TLP_WHITE],
    custom_properties={
        'x_opencti_aliases': ['ANSSI'],
        'x_opencti_organization_type': 'csirt',
    }
)



def get_name_and_ids(in_file: str, classes: list):
    result_dict = {}
    bundle_id = ""
    
    if not os.path.isfile(in_file):
        print('No existing STIX file. Starting from scratch')
        return result_dict, bundle_id

    with open(in_file, 'r') as f:
        data = json.load(f)
        data_type = data.get('type', None)
        
        if data_type != "bundle":
            print('Output file is not a bundle. Starting from scratch')
            return result_dict, bundle_id
        
        for item in data['objects']:
            if item['type'] == "relationship":
                result_dict[f"{item['source_ref']}_{item['target_ref']}"] = item
            if item['type'] in classes:
                result_dict[item['name']] = item
     
        bundle_id = data['id']

    return result_dict, bundle_id


def update_list(bundle_id: str, raw_companies_file: str, companies: dict, sectors: dict) -> Bundle:
    bundles = []

    with open(raw_companies_file) as csv_file:
        csv_dict_reader = DictReader(csv_file, delimiter=',')
        
        for row in csv_dict_reader:
            if row['createdBy'] == "ANSSI":
                creator = anssi
            else:
                creator = row['createdBy']  # has to be a STIX ID

            entity_id = None
            entity_creation_date = None
            if row['name'] in companies:
                entity_id = companies[row['name']]['id']
                entity_creation_date = companies[row['name']]['created']
               
            if row['x_opencti_aliases']:
                aliases = row['x_opencti_aliases'].split(',')
            else:
                aliases = []
            
            if row['other_stix_ids']:
                stix_ids = row['x_opencti_stix_ids'].split(',')
            else:
                stix_ids = []

            markings = row['objectMarking'].split(',')
                    
            company = Identity(
                id=entity_id,
                name=row['name'],
                created=entity_creation_date,
                description=row['description'],
                contact_information=row['contact_information'],
                roles="",   # There's no real point for having a role here. Only companies/entities here, no people
                identity_class='organization',
                created_by_ref=creator,
                object_marking_refs=[TLP_WHITE],
                custom_properties={
                    'x_opencti_aliases': aliases,
                    'x_opencti_organization_type': row['x_opencti_organization_type'],
                    'x_opencti_stix_ids': stix_ids,
                }
            )
            bundles.append(company)
            
            company_sectors = row['sectors'].split(',')
            for company_sector in company_sectors:
                if company_sector == '':
                    print(f"Error: Organization {row['name']} has no Sector assigned!!")
                    return []
                
                relevant_sector = sectors.get(company_sector, None)
                # search through aliases
                if relevant_sector is None:
                    for sector_name, sector in sectors.items():
                        aliases = sector.get('x_opencti_aliases', [])
                        if company_sector in aliases:
                            relevant_sector = sector

                if relevant_sector is None:
                    print(f"Sector '{company_sector}' for company '{row['name']}' can't be found")
                    continue

                relationship_id = None
                relationship_name = f"{company.id}_{relevant_sector['id']}"
                relationship_creation_date = None
                if relationship_name in companies:
                    relationship_id = companies[relationship_name]['id']
                    relationship_creation_date = companies[relationship_name]['created']

                sector_relationship = Relationship(
                    id=relationship_id,
                    created=relationship_creation_date,
                    relationship_type='part-of',
                    source_ref=company.id,
                    target_ref=relevant_sector['id'],
                    description=f"Company '{row['name']}' is part of sector '{company_sector}'",
                    confidence=100,
                    created_by_ref=creator,
                    object_marking_refs=[TLP_WHITE],
                )
                
                bundles.append(sector_relationship)

    if bundle_id:
        bundle = Bundle(
            objects=bundles,
            id=bundle_id,
            allow_custom=True
        )
    else:
        bundle = Bundle(
            objects=bundles,
            allow_custom=True
        )
            
    return bundle


companies_json, bundle_id = get_name_and_ids(out_file, ['identity'])
sectors_json, _ = get_name_and_ids(sector_file, ['identity'])
bundle = update_list(bundle_id, raw_file, companies_json, sectors_json)
with open(out_file, 'w') as fh:
    fh.write(bundle.serialize())




