import pandas as pd
from tqdm import tqdm
import os

from DwCAtoModelStandard import DwCAReader
from get_taxa import get_taxonomy
from get_taxa import getScientificNameId
from get_taxa import get_accepted_id

pd.options.mode.chained_assignment = None  # default='warn'

corrections = {
    'Spinulum annotinum': 'Lycopodium annotinum',
    'Nephromopsis nivalis': 'Cetraria nivalis',
    'Nephromopsis cucullata': 'Flavocetraria cucullata',
    'Fomitopsis betulina': 'Piptoporus betulinus',
    'Struthiopteris spicant': 'Blechnum spicant',
    'Puccinia urticae': 'Puccinia urticata',
    'Ranunculus auricomus': 'Ranunculus',
    'Abelmoschus esculentus': None,
}



def process_GBIF(inputfile, outputfolder):
    reader = DwCAReader(inputfile, None)
    reader.read_dwca()
    reader.convert_dwca()

    images = reader.df_images
    del reader

    tqdm.pandas()
    images['taxon_full_name'] = images['taxon_full_name'].apply(lambda x: x if x not in corrections else corrections[x])
    images.dropna(subset=['taxon_full_name'], inplace=True)
    images.sort_values(by='taxon_full_name', inplace=True)

    # too_high = images[~images["taxon_full_name"].str.contains(" ")]
    # if len(too_high):
    #     print(f"{len(too_high)} occurrences seem to be of higher taxa, dropping these")
    #     too_high.to_csv(os.path.join(outputfolder, "GBIF_dropped.csv"), index=False)
    #     images = images[images["taxon_full_name"].str.contains(" ")]

    images['accepted_taxon_id_at_source'] = images['taxon_full_name'].progress_apply(lambda x: getScientificNameId(x))

    images[images['accepted_taxon_id_at_source'].isnull()].to_csv(os.path.join(outputfolder, "GBIF_taxa_not_found.csv"), index=False)
    images.dropna(subset=['accepted_taxon_id_at_source'], inplace=True)

    images['accepted_taxon_id_at_source'] = images['accepted_taxon_id_at_source'].progress_apply(lambda x: get_accepted_id(x))

    images['date'] = images['datetime'].apply(lambda x: x[:10])
    images['time'] = images['datetime'].apply(lambda x: x[11:16])
    images.drop('datetime', axis=1, inplace=True)


    taxa = pd.DataFrame(images[['accepted_taxon_id_at_source', 'taxon_full_name']])
    taxa.drop_duplicates(inplace=True)

    taxa['taxon_id_at_source'] = taxa['accepted_taxon_id_at_source']
    taxa['status_at_source'] = 'accepted'
    taxonomy_df = taxa.progress_apply(lambda row: get_taxonomy(row.taxon_id_at_source, row.taxon_full_name), axis='columns',
                                      result_type='expand')
    taxa = pd.concat([taxa, taxonomy_df], axis='columns')

    taxa['taxon_full_name'] = taxa['self']
    images = images.merge(taxa[['accepted_taxon_id_at_source', 'self']], left_on=['accepted_taxon_id_at_source'],
                          right_on=['accepted_taxon_id_at_source'])
    images['taxon_full_name'] = images['self']
    images['taxon_id_at_source'] = images['accepted_taxon_id_at_source']

    taxa['order'] = taxa['order'].apply(lambda x: x.strip())
    taxa = taxa[taxa['order'] != '']
    have_taxonomy = taxa['accepted_taxon_id_at_source'].tolist()
    images = images.loc[images['accepted_taxon_id_at_source'].progress_apply(lambda x: x in have_taxonomy)]

    images['observation_id'] = images['record_id'].apply(lambda x: "GBIF:" + str(x))
    images['image_id'] = images['image_id'].apply(lambda x: "GBIF:" + str(x))
    images.drop(columns=['record_id'], inplace=True)
    images.drop_duplicates(inplace=True)

    taxa.drop(columns=['self'], inplace=True)
    images.drop(columns=['self'], inplace=True)


    taxa.to_csv(os.path.join(outputfolder, 'GBIF_taxa.csv'), index=False)
    images.to_csv(os.path.join(outputfolder, 'GBIF_images.csv'), index=False)

if __name__ == "__main__":
    print("USAGE: process_GBIF()")