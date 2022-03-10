import pandas as pd
from pyproj import Transformer
from tqdm import tqdm
import os


from get_taxa import get_accepted_id
from get_taxa import get_taxonomy

pd.options.mode.chained_assignment = None  # default='warn'
tqdm.pandas()
transformer = Transformer.from_crs('EPSG:900913', 'EPSG:4326')

def process_AO(input_file, output_folder):
    data = pd.read_csv(input_file, sep=';', on_bad_lines='skip', dtype={'scientificname_id': 'str'})
    data = data[data['UnsureDetermination'] == 0]
    data.dropna(subset=['scientificname_id'], inplace=True)

    # too_high = data[~data["scientificname"].str.contains(" ")]
    # if len(too_high):
    #     print(f"{len(too_high)} occurrences seem to be of higher taxa, dropping these")
    #     too_high.to_csv(os.path.join(output_folder, "AO_dropped.csv"), index=False)
    #     data = data[data["scientificname"].str.contains(" ")]


    taxon_data = data[['scientificname_id', 'scientificname']].drop_duplicates()
    taxon_data['accepted_taxon_id_at_source'] = taxon_data.progress_apply(
        lambda x: get_accepted_id(x['scientificname_id'], x['scientificname']), axis=1)

    taxon_data[taxon_data['accepted_taxon_id_at_source'].isnull()].to_csv(os.path.join(output_folder, "AO_taxa_not_found.csv"), index=False)
    taxon_data = taxon_data.dropna(subset=["accepted_taxon_id_at_source"])

    print('Retrieving taxonomies')
    taxonomy_df = taxon_data.progress_apply(
        lambda row: get_taxonomy(row.accepted_taxon_id_at_source, row.scientificname),
        axis='columns',
        result_type='expand')
    taxon_data = pd.concat([taxon_data, taxonomy_df], axis='columns')
    data = data.merge(taxon_data, left_on='scientificname_id',
                      right_on='scientificname_id')


    taxa = data[
        ['accepted_taxon_id_at_source', 'self', 'kingdom', 'division', 'class', 'order', 'family',
         'genus']].drop_duplicates()
    taxa.columns = ['taxon_id_at_source', 'taxon_full_name', 'kingdom', 'division', 'class', 'order', 'family',
                    'genus']
    taxa['status_at_source'] = 'accepted'
    taxa['order'] = taxa['order'].apply(lambda x: x.strip())
    taxa = taxa[taxa['order'] != '']
    have_taxonomy = taxa['taxon_id_at_source'].tolist()
    taxa['accepted_taxon_id_at_source'] = taxa['taxon_id_at_source']

    images = data[
        ['image_url', 'record_id', 'accepted_taxon_id_at_source', 'self', 'location_XCoord', 'location_YCoord',
         'observation_datetime', 'image_id']]

    images.columns = ['image_url', 'observation_id', 'taxon_id_at_source', 'taxon_full_name', 'location_longitude',
                      'location_latitude', 'datetime', 'image_id']

    images['accepted_taxon_id_at_source'] = images['taxon_id_at_source']
    images['status_at_source'] = "accepted"
    images['date'] = images['datetime'].apply(lambda x: x[:10])
    images['time'] = images['datetime'].apply(lambda x: x[11:16])
    images.drop('datetime', axis=1, inplace=True)

    print('Transforming coordinates')
    images['coord'] = images[['location_longitude', 'location_latitude']].progress_apply(
        lambda x: transformer.transform(x.location_longitude, x.location_latitude), axis=1)
    images['location_latitude'] = images['coord'].apply(lambda x: x[0])
    images['location_longitude'] = images['coord'].apply(lambda x: x[1])
    images.drop('coord', axis=1, inplace=True)

    print('Filtering images on those with a full taxonomy')
    images = images.loc[images['accepted_taxon_id_at_source'].progress_apply(lambda x: x in have_taxonomy)]

    images['observation_id'] = images['observation_id'].apply(lambda x: "AO:" + str(x))
    images['image_id'] = images['image_id'].apply(lambda x: "AO:" + str(x))

    taxa.to_csv(os.path.join(output_folder, 'AO_taxa.csv'), index=False)
    images.to_csv(os.path.join(output_folder, 'AO_images.csv'), index=False)




if __name__ == "__main__":
    transformer = Transformer.from_crs('EPSG:900913', 'EPSG:4326')

    data = pd.read_csv('./Input/Artsobservasjoner.csv', sep=';', error_bad_lines=False,
                       dtype={'scientificname_id': 'str'})

    data[['scientificname_id', 'scientificname']].drop_duplicates()[['scientificname_id', 'scientificname']].to_csv('Output/AO_taxa_testing.csv', index=False)
    exit(0)

    data = data[data['UnsureDetermination'] == 0]
    data.dropna(subset=['scientificname_id'], inplace=True)

    taxon_data = data[['scientificname_id', 'scientificname']].drop_duplicates()
    taxon_data['accepted_taxon_id_at_source'] = taxon_data.progress_apply(
        lambda x: get_accepted_id(x['scientificname_id'], x['scientificname']), axis=1)

    print('Retrieving taxonomies')
    taxonomy_df = taxon_data.progress_apply(
        lambda row: get_taxonomy(row.accepted_taxon_id_at_source, row.scientificname),
        axis='columns',
        result_type='expand')
    taxon_data = pd.concat([taxon_data, taxonomy_df], axis='columns')
    data = data.merge(taxon_data, left_on='scientificname_id',
                      right_on='scientificname_id')


    taxa = data[
        ['accepted_taxon_id_at_source', 'self', 'kingdom', 'division', 'class', 'order', 'family',
         'genus']].drop_duplicates()
    taxa.columns = ['taxon_id_at_source', 'taxon_full_name', 'kingdom', 'division', 'class', 'order', 'family',
                    'genus']
    taxa['status_at_source'] = 'accepted'
    taxa['order'] = taxa['order'].apply(lambda x: x.strip())
    taxa = taxa[taxa['order'] != '']
    have_taxonomy = taxa['taxon_id_at_source'].tolist()
    taxa['accepted_taxon_id_at_source'] = taxa['taxon_id_at_source']

    images = data[
        ['image_url', 'record_id', 'accepted_taxon_id_at_source', 'self', 'location_XCoord', 'location_YCoord',
         'observation_datetime', 'image_id']]

    images.columns = ['image_url', 'observation_id', 'taxon_id_at_source', 'taxon_full_name', 'location_longitude',
                      'location_latitude', 'datetime', 'image_id']

    images['accepted_taxon_id_at_source'] = images['taxon_id_at_source']
    images['status_at_source'] = "accepted"
    images['date'] = images['datetime'].apply(lambda x: x[:10])
    images['time'] = images['datetime'].apply(lambda x: x[11:16])
    images.drop('datetime', axis=1, inplace=True)

    print('Transforming coordinates')
    images['coord'] = images[['location_longitude', 'location_latitude']].progress_apply(
        lambda x: transformer.transform(x.location_longitude, x.location_latitude), axis=1)
    images['location_latitude'] = images['coord'].apply(lambda x: x[0])
    images['location_longitude'] = images['coord'].apply(lambda x: x[1])
    images.drop('coord', axis=1, inplace=True)

    print('Filtering images on those with a full taxonomy')
    images = images.loc[images['accepted_taxon_id_at_source'].progress_apply(lambda x: x in have_taxonomy)]

    images['observation_id'] = images['observation_id'].apply(lambda x: "AO:" + str(x))
    images['image_id'] = images['image_id'].apply(lambda x: "AO:" + str(x))

    taxa.to_csv('Output/AO_taxa.csv', index=False)
    images.to_csv('Output/AO_images.csv', index=False)
