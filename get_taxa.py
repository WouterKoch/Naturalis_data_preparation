import json
import os
import urllib.request

corrections = {
    'Dendrocopus major': 'Dendrocopos major',
    'Dendrocopus minor': 'Dendrocopos minor',
    'Xanthia icteritia': 'Cirrhia icteritia',
    'Semiothisa clathrata': 'Chiasmia clathrata',
    'Catoptria permutatella': 'Catoptria permutatellus',
    'Herminia lunalis': 'Zanclognatha lunalis',
    'Caryocolum blandulella': 'Caryocolum',
    'Ancylis obtusana': 'Ancylis',
    'Anatrachyntis badia': 'Cosmopterigidae',
    'Epicallima formosella': 'Oecophoridae',
}


def get_gbif_synonyms(name):
    with urllib.request.urlopen(
            "https://api.gbif.org/v1/species?name=" + urllib.parse.quote(name)) as url:
        data = json.loads(url.read().decode('utf-8'))
        synonyms = []
        for result in data['results']:
            if 'rank' in result and result['rank'].lower() in result and result[result['rank'].lower()] != name:
                synonyms += [result[result['rank'].lower()]]
            if 'key' in result:
                with urllib.request.urlopen(
                        "https://api.gbif.org/v1/species/{}/synonyms".format(result['key'])) as url_syn:
                    syn_data = json.loads(url_syn.read().decode('utf-8'))
                    for syn in syn_data['results']:
                        if 'canonicalName' in syn:
                            synonyms += [syn['canonicalName']]

        return list(set(synonyms))


def get_accepted_id(id, name=""):
    data = get_taxon_json(id, add_tree=False)
    if 'TaxonomicStatus' not in data:
        id = getScientificNameId(name)

    if 'TaxonomicStatus' in data and data['TaxonomicStatus'] != "accepted":
        id = data['AcceptedNameUsage']['ScientificNameId']
        data = get_taxon_json(id, add_tree=False)

    if 'TaxonRank' in data and (
            data['TaxonRank'] == 'subgenus' or
            data['TaxonRank'] == 'section' or
            data['TaxonRank'] == 'infraorder' or
            data['TaxonRank'] == 'suborder'):
        id = data['HigherClassification'][-1]['ScientificNameId']

    return id


def getScientificNameId(name):
    if name in corrections:
        name = corrections[name]

    filepath = os.path.join('JSON', 'name', name)
    found = False
    if not os.path.isfile(filepath):

        if " " not in name:
            for rank in ["genus", "family", "order"]:
                with urllib.request.urlopen(f"https://artsdatabanken.no/api/Resource/?Type=taxon&Name={urllib.parse.quote(name)}&SubType=Rank/{rank}") as url:
                    data = json.loads(url.read().decode('utf-8'))
                    for result in data:
                        if name in result['Name']:
                            found = result
                            break
            if not found:
                print(f"{name} not found")
                exit(0)
        else:
            with urllib.request.urlopen(
                    "https://artsdatabanken.no/api/Resource/?Type=taxon&Name=" + urllib.parse.quote(name)) as url:
                data = json.loads(url.read().decode('utf-8'))
                for result in data:
                    if name in result['Name']:
                        found = result
                        break
                if not found:
                    if name in corrections:
                        return getScientificNameId(corrections[name])

                    if len(data) > 0:
                        found = data[0]
                        print(f"No exact match for {name}, going with the first result: {found['AcceptedNameUsage']['ScientificName']}")
                    else:
                        # print(name)
                        found = {'AcceptedNameUsage': {'ScientificNameId': None}}

        with open(filepath, 'w') as json_file:
            json.dump(found, json_file)
    else:
        with open(filepath) as f:
            found = json.load(f)

    return found['AcceptedNameUsage']['ScientificNameId']


def get_taxon_json(id, add_tree=True):
    data = {}
    if id is not None:
        filepath = os.path.join('JSON', 'id', id)

        if not os.path.isfile(filepath):
            with urllib.request.urlopen("https://artsdatabanken.no/api/Resource/ScientificName/{}".format(id)) as url:
                data = json.loads(url.read().decode('utf-8'))
                with open(filepath, 'w') as json_file:
                    json.dump(data, json_file)
        else:
            with open(filepath) as f:
                data = json.load(f)

    if 'ScientificName' not in data:
        if id is not None:
            print("No result found for taxon {}".format(id))
        data['TaxonTree'] = {}
        return data

    if add_tree and not 'TaxonTree' in data:
        data['TaxonTree'] = {}
        data['TaxonTree'][data['TaxonRank']] = data['ScientificName'] if 'ScientificName' in data else ""
        data['TaxonTree']['self'] = data['ScientificName'] if 'ScientificName' in data else ""

        if 'HigherClassification' in data:
            for parent in data['HigherClassification']:
                parentData = get_taxon_json(parent['ScientificNameId'], add_tree=False)
                data['TaxonTree'][parentData['TaxonRank']] = parentData['ScientificName']
            with open(filepath, 'w') as json_file:
                json.dump(data, json_file)
        else:
            print("No higher classification found for taxon {}".format(id))

    return data


def get_taxonomy(id, name):
    data = get_taxon_json(id)

    return {
        'kingdom': data['TaxonTree']['kingdom'] if ('kingdom' in data['TaxonTree']) else "",
        'division': data['TaxonTree']['division'] if ('division' in data['TaxonTree']) else (
            data['TaxonTree']['phylum'] if ('phylum' in data['TaxonTree']) else ""),
        'class': data['TaxonTree']['class'] if ('class' in data['TaxonTree']) else "",
        'order': data['TaxonTree']['order'] if ('order' in data['TaxonTree']) else "",
        'family': data['TaxonTree']['family'] if ('family' in data['TaxonTree']) else "",
        'genus': data['TaxonTree']['genus'] if ('genus' in data['TaxonTree']) else "",
        'self': data['TaxonTree']['self'] if ('self' in data['TaxonTree']) else name,
    }


if __name__ == "__main__":
    print('Usage: get_taxonomy(id)')
