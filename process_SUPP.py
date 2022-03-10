import json
import os
import urllib.request

import pandas as pd
from tqdm import tqdm

from get_taxa import get_taxonomy
from get_taxa import getScientificNameId
from get_taxa import get_accepted_id

pd.options.mode.chained_assignment = None  # default='warn'


def process_supp(inputfiles, outputfolder, datasetname):

    data = pd.DataFrame()
    tqdm.pandas()

    for file in inputfiles:
        data = pd.concat([data, pd.read_csv(file, on_bad_lines="skip")], ignore_index=True)

    data.drop_duplicates(subset=['image_url', 'taxon_full_name'], inplace=True)

    # too_high = data[~data["taxon_full_name"].str.contains(" ")]
    # if len(too_high):
    #     print(f"{len(too_high)} occurrences seem to be of higher taxa, dropping these")
    #     too_high.to_csv(os.path.join(outputfolder, datasetname + "_dropped.csv"), index=False)
    #     data = data[data["taxon_full_name"].str.contains(" ")]

    data['accepted_taxon_id_at_source'] = data['taxon_full_name'].progress_apply(lambda x: getScientificNameId(x))

    data[data['accepted_taxon_id_at_source'].isnull()].to_csv(os.path.join(outputfolder, datasetname + "_taxa_not_found.csv"), index=False)
    data = data.dropna(subset=["accepted_taxon_id_at_source"])
   
    data['accepted_taxon_id_at_source'] = data['accepted_taxon_id_at_source'].progress_apply(lambda x: get_accepted_id(x))

    taxa = data[['taxon_full_name', 'accepted_taxon_id_at_source']].drop_duplicates()
    taxa['taxon_id_at_source'] = taxa['accepted_taxon_id_at_source']
    taxa['status_at_source'] = 'accepted'

    images = data[['image_url', 'record_id', 'accepted_taxon_id_at_source', 'taxon_full_name', 'image_id']]
    images['location_longitude'] = ""
    images['location_latitude'] = ""
    
    images['observation_id'] = images['record_id'].apply(lambda x: "SUPP:" + str(x))

    if 'image_id' not in images.columns:
        images['image_id'] = images['observation_id']

    images.drop(columns=['record_id'], inplace=True)
    images['status_at_source'] = "accepted"
    images['date'] = "2021-01-01"

    taxonomy_df = taxa.progress_apply(lambda row: get_taxonomy(row.taxon_id_at_source, row.taxon_full_name),
                                      axis='columns',
                                      result_type='expand')
    taxa = pd.concat([taxa, taxonomy_df], axis='columns')

    taxa['taxon_full_name'] = taxa['self']
    images = images.merge(taxa[['accepted_taxon_id_at_source', 'self']], left_on=['accepted_taxon_id_at_source'],
                          right_on=['accepted_taxon_id_at_source'])
    images['taxon_full_name'] = images['self']
    images.drop(columns=['self'], inplace=True)
    taxa.drop(columns=['self'], inplace=True)

    taxa['order'] = taxa['order'].apply(lambda x: x.strip())
    taxa = taxa[taxa['order'] != '']
    have_taxonomy = taxa['accepted_taxon_id_at_source'].tolist()
    images = images.loc[images['accepted_taxon_id_at_source'].progress_apply(lambda x: x in have_taxonomy)]
    images['taxon_id_at_source'] = images['accepted_taxon_id_at_source']

    taxa.to_csv(os.path.join(outputfolder, datasetname + "_taxa.csv"), index=False)
    images.to_csv(os.path.join(outputfolder, datasetname + "_images.csv"), index=False)




if __name__ == "__main__":
   print("USAGE: process_supp(inputfiles, outputfolder, datasetname)")
