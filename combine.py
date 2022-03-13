import numpy as np
import pandas as pd
from tqdm import tqdm
import os
import sys
import hashlib

def generateId(image_url, prefix, exisiting_ids):
    id = f"{prefix}:{hashlib.md5(image_url.encode()).hexdigest()}"
    # while id in exisiting_ids:
    #     print(f"id {id} exists!")
    #     image_url = image_url + "1"
    #     id = f"{prefix}:{hashlib.blake2s(image_url.encode()).hexdigest()}"
    #     print(f"Changed to {id}")
    return id


def combine(taxonfiles, imagefiles, outputfolder, previousImageList):
    tqdm.pandas()
    taxa = pd.read_csv(taxonfiles[0])
    for i, file in enumerate(taxonfiles):
        if i > 0:
            taxa = pd.concat([taxa, pd.read_csv(file)], ignore_index=True)

    taxa.drop_duplicates(subset=['taxon_id_at_source'], inplace=True)
    taxa['taxon_id_at_source'] = taxa['taxon_id_at_source'].apply(lambda x: "NBIC:" + str(int(x)))
    taxa['accepted_taxon_id_at_source'] = taxa['accepted_taxon_id_at_source'].apply(lambda x: "NBIC:" + str(int(x)))

    if 'specific_epithet' not in taxa.columns.values:
        taxa['specific_epithet'] = ""

    if 'infraspecific_epithet' not in taxa.columns.values:
        taxa['infraspecific_epithet'] = ""

    taxa.to_csv(os.path.join(outputfolder, 'taxa.csv'), index=False)

    print(f"{len(taxa)} taxa")


    images = pd.read_csv(imagefiles[0])
    images["dataset"] = imagefiles[0].split("/")[-1].split("_")[0].upper()
    for i, file in enumerate(imagefiles):
        if i > 0:
            adding = pd.read_csv(file)
            adding["dataset"] = imagefiles[i].split("/")[-1].split("_")[0].upper()
            images = pd.concat([images, adding], ignore_index=True)

    if 'sex' not in images.columns.values:
        images['sex'] = ""
    if 'morph' not in images.columns.values:
        images['morph'] = ""
    if 'morph_id' not in images.columns.values:
        images['morph_id'] = ""
    if 'rijkdriehoeksstelsel_x' not in images.columns.values:
        images['rijkdriehoeksstelsel_x'] = ""
    if 'rijkdriehoeksstelsel_y' not in images.columns.values:
        images['rijkdriehoeksstelsel_y'] = ""

    images['taxon_id_at_source'] = images['taxon_id_at_source'].apply(lambda x: "NBIC:" + str(int(x)))
    images['accepted_taxon_id_at_source'] = images['accepted_taxon_id_at_source'].apply(lambda x: "NBIC:" + str(int(x)))

    images['location_latitude'] = images['location_latitude'].apply(lambda x: x if np.absolute(x) < 90 else 0)
    images['location_longitude'] = images['location_longitude'].apply(lambda x: x if np.absolute(x) < 180 else 0)

    images.drop_duplicates(subset=['image_url'], inplace=True)

    url_replacements = {
        'https://purl.org/gbifnorway/img/ipt-specimens/barstow-garden/new/2011/P5159387.jpg': 'http://folk.ntnu.no/wouterk/replacements/P5159387.jpg',
        'https://purl.org/gbifnorway/img/ipt-specimens/barstow-garden/new/2013/P6230493.jpg': 'http://folk.ntnu.no/wouterk/replacements/P6230493.jpg',
        'https://purl.org/gbifnorway/img/ipt-specimens/barstow-garden/new/2011/P5159386.jpg': 'http://folk.ntnu.no/wouterk/replacements/P5159386.jpg',
        'https://purl.org/gbifnorway/img/ipt-specimens/barstow-garden/new/2011/P5159381.jpg': 'http://folk.ntnu.no/wouterk/replacements/P5159381.jpg',
        'https://purl.org/gbifnorway/img/ipt-specimens/barstow-garden/new/2011/P5159385.jpg': 'http://folk.ntnu.no/wouterk/replacements/P5159385.jpg',
        'https://purl.org/gbifnorway/img/ipt-specimens/barstow-garden/new/2011/P5159382.jpg': 'http://folk.ntnu.no/wouterk/replacements/P5159382.jpg',
        'https://purl.org/gbifnorway/img/ipt-specimens/barstow-garden/new/2011/P5159383.jpg': 'http://folk.ntnu.no/wouterk/replacements/P5159383.jpg',
        'https://www.dagbladet.no/images/70576123.jpg?imageId=70576123&width=980&height=559&compression=80': 'http://folk.ntnu.no/wouterk/replacements/70576123.jpg',
        'https://image.klikk.no/6732049.jpg?imageId=6732049&x=0&y=0&cropw=100&croph=85.581395348837&width=1600&height=913': 'http://folk.ntnu.no/wouterk/replacements/6732049.jpg',
        'https://image.klikk.no/6732047.jpg?imageId=6732047&width=500&height=285': 'http://folk.ntnu.no/wouterk/replacements/6732047.jpg',
        'https://image.forskning.no/1559391.jpg?imageId=1559391&width=706&height=403': 'http://folk.ntnu.no/wouterk/replacements/1559391.jpg',
        'https://image.klikk.no/6732051.jpg?imageId=6732051&x=0&y=0&cropw=100&croph=85.549964054637&width=1600&height=912': 'http://folk.ntnu.no/wouterk/replacements/6732051.jpg',
        'https://image.klikk.no/6732046.jpg?imageId=6732046&x=0&y=0&cropw=100&croph=83.4375&width=468&height=267': 'http://folk.ntnu.no/wouterk/replacements/6732046.jpg',
        'https://image.klikk.no/6732048.jpg?imageId=6732048&width=1600&height=912': 'http://folk.ntnu.no/wouterk/replacements/6732048.jpg',
        'https://1jv6g9n0pik3nvjug2t92dlh-wpengine.netdna-ssl.com/wp-content/uploads/2015/07/thinkstockphotos-178588991-352x431.jpg': 'http://folk.ntnu.no/wouterk/replacements/thinkstockphotos-178588991.jpg',
        'https://1jv6g9n0pik3nvjug2t92dlh-wpengine.netdna-ssl.com/wp-content/uploads/2015/07/ulv-1100x551.jpg': 'http://folk.ntnu.no/wouterk/replacements/ulv-1100x551.jpg',
        'https://1jv6g9n0pik3nvjug2t92dlh-wpengine.netdna-ssl.com/wp-content/uploads/2015/06/ulvespor_mogens_totsas-300x201.jpg': 'http://folk.ntnu.no/wouterk/replacements/ulvespor_mogens_totsas.jpg',
        'https://1jv6g9n0pik3nvjug2t92dlh-wpengine.netdna-ssl.com/wp-content/uploads/2015/06/ulv_vinter-300x207.jpg': 'http://folk.ntnu.no/wouterk/replacements/ulv_vinter-300x207.jpg',
        'https://1jv6g9n0pik3nvjug2t92dlh-wpengine.netdna-ssl.com/wp-content/uploads/2015/06/ulv_1-300x234.jpg': 'http://folk.ntnu.no/wouterk/replacements/ulv_1.jpg',
        'https://image.forskning.no/1363982.jpg?imageId=1363982&x=0&y=11.714285714286&cropw=100&croph=86.714285714286&width=1050&height=608': 'http://folk.ntnu.no/wouterk/replacements/1363982.jpg',
        'https://image.forskning.no/1347259.jpg?imageId=1347259&x=0&y=7.1005917159763&cropw=100&croph=42.011834319527&width=1058&height=604': 'http://folk.ntnu.no/wouterk/replacements/1347259.jpg',
        'https://www.dagbladet.no/images/63196038.jpg?imageId=63196038&x=0&y=0&cropw=100.00&croph=100.00&width=980&height=552&compression=80': 'http://folk.ntnu.no/wouterk/replacements/63196038.jpg',
        'https://www.dagbladet.no/images/63196036.jpg?imageId=63196036&x=0&y=0&cropw=100.00&croph=100.00&width=1470&height=754.5': 'http://folk.ntnu.no/wouterk/replacements/63196036.jpg',
        'https://www.miljodirektoratet.no/globalassets/bilder/nyhetsbilder-2020/jerv-bard-bredesen.jpg?w=1150': 'http://folk.ntnu.no/wouterk/replacements/jerv-bard-bredesen.jpg',
        'https://www.regjeringen.no/contentassets/b895dbabc684463fb805f5f0e970e2fc/dn_006326.jpg?preset=article&v=-444535606': 'http://folk.ntnu.no/wouterk/replacements/dn_006326.jpg',
        'https://www.dagbladet.no/images/63445639.jpg?imageId=63445639&x=0&y=0&cropw=100.00&croph=100.00&width=1470&height=831': 'http://folk.ntnu.no/wouterk/replacements/63445639.jpg',
        'https://www.dagbladet.no/images/63445641.jpg?imageId=63445641&x=0&y=0&cropw=100.00&croph=100.00&width=980&height=554&compression=80': 'http://folk.ntnu.no/wouterk/replacements/63445641.jpg',
        'https://www.dagbladet.no/images/67460750.jpg?imageId=67460750&width=980&height=559&compression=80': 'http://folk.ntnu.no/wouterk/replacements/67460750.jpg',
        'https://www.dagbladet.no/images/63947838.jpg?imageId=63947838&x=2.0040080160321&y=31.108144192256&cropw=95.145631067961&croph=39.301874595992&width=938&height=582&compression=80': 'http://folk.ntnu.no/wouterk/replacements/63947838.jpg',
        'https://www.dagbladet.no/images/63971492.jpg?imageId=63971492&width=980&height=559&compression=80': 'http://folk.ntnu.no/wouterk/replacements/63971492.jpg',
        'https://www.nysgjerrigper.no/siteassets/bilder-artikler/2017-2/isbjorn-foto-shutterstock.jpg?transform=DownFit&width=700': 'http://folk.ntnu.no/wouterk/replacements/isbjorn-foto-shutterstock.jpg',
        'https://image.forskning.no/1348957.jpg?imageId=1348957&width=1058&height=604': 'http://folk.ntnu.no/wouterk/replacements/1348957.jpg',
    }

    images['image_url'] = images['image_url'].apply(lambda x: url_replacements[x] if x in url_replacements.keys() else x)


    # Ensure using the same id's as last time
    lasttime = pd.read_csv(previousImageList, usecols=["image_url", "image_id"])
    lasttime.columns = ["image_url", "old_image_id"]

    images = pd.merge(images, lasttime, on="image_url", how="left")
    existing_ids = lasttime["old_image_id"].to_list()

    images["image_id"] = images.progress_apply(lambda x: x["old_image_id"] if not pd.isna(x["old_image_id"]) else (x["image_id"] if "AO:" in x["image_id"] else generateId(x["image_url"], x["dataset"], existing_ids)) , axis=1)
    images.drop(["old_image_id","dataset"], axis=1, inplace=True)

    images.to_csv(os.path.join(outputfolder, 'images.csv'), index=False)
    # images = images[images['image_url'].apply(lambda x: x in url_replacements.keys())]
    # images['image_url'] = images['image_url'].apply(lambda x: url_replacements[x])
    # images.to_csv('Output/images_replacements.csv', index=False)
    print(f"{len(images)} images")

    taxon_counts = pd.DataFrame(taxa.value_counts(subset=['taxon_full_name']))
    taxon_counts.columns = ['Count']

    print(f"{len(images.drop_duplicates(subset=['image_id']))} image id's")


    print('Taxon names occurring more than once in taxa:')
    print(taxon_counts[taxon_counts['Count'] > 1])
    print('Taxon names in images but not in taxa:', list(set(images['taxon_full_name'].to_list()) - set(taxa['taxon_full_name'].to_list())))






if __name__ == "__main__":
    print("USAGE: combine(inputfiles, outputfolder)")
