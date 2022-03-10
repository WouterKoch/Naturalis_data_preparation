import os.path
import zipfile
from collections import defaultdict
from random import shuffle

import pandas as pd


class DwCAReader(object):

    def __init__(self, dwca_path, data_folder):
        self.data_folder = data_folder
        self.path = dwca_path
        self.df_occurrence = None
        self.df_multimedia = None
        self.df_taxa = None
        self.df_images = None

    def read_dwca(self,
                  year_min=None,
                  year_max=None,
                  with_images=True,
                  without_images=True,
                  datasets=None,
                  columns=None,
                  acceptedTaxonKeys=None,
                  ):

        if columns is None:
            columns = ['species', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'specificEpithet',
                       'infraspecificEpithet', 'acceptedTaxonKey', 'taxonomicStatus', 'gbifID',
                       'decimalLatitude', 'decimalLongitude', 'locality', 'eventDate', 'mediaType', 'datasetKey',
                       'year', 'identifier']
        if datasets is None:
            datasets = ['b124e1e0-4755-430f-9eab-894f25a9b59c', '9807df89-7446-4aab-8ec8-fd837085c1a1',
                        '50c9509d-22c7-4a22-a47d-8c48425ef4a7']

        pd.low_memory = False

        self.df_occurrence = pd.read_csv(zipfile.ZipFile(self.path).open('occurrence.txt'), sep='\t',
                                         on_bad_lines='skip', usecols=columns).dropna(subset=['species'])

        if not without_images:
            self.df_occurrence = self.df_occurrence[self.df_occurrence['mediaType'] == 'StillImage']

        if not with_images:
            self.df_occurrence = self.df_occurrence[self.df_occurrence['mediaType'] != 'StillImage']

        if datasets is not None:
            self.df_occurrence = self.df_occurrence[self.df_occurrence['datasetKey'].isin(datasets)]

        if acceptedTaxonKeys is not None:
            self.df_occurrence = self.df_occurrence[self.df_occurrence['acceptedTaxonKey'].isin(acceptedTaxonKeys)]

        if year_min is not None:
            self.df_occurrence = self.df_occurrence[self.df_occurrence['year'] >= year_min]

        if year_max is not None:
            self.df_occurrence = self.df_occurrence[self.df_occurrence['year'] <= year_max]



    def limit_dwca_images(self, min_per_taxon=None, max_per_taxon=None, equal_per_taxon=False):
        # get species counts
        counts = self.df_images['taxon_full_name'].value_counts()

        if equal_per_taxon:
            max_per_taxon = counts[counts > min_per_taxon].min()

        # for each species, remove from the set if too few, remove a random subset if too many
        for species, number in counts.iteritems():
            if min_per_taxon is not None and number < min_per_taxon:
                self.df_images = self.df_images[self.df_images['taxon_full_name'] != species]
            elif max_per_taxon is not None and number > max_per_taxon:
                selection = self.df_images[self.df_images['taxon_full_name'] == species].sample(n=max_per_taxon)
                self.df_images = self.df_images[self.df_images['taxon_full_name'] != species].append(selection)

        self.df_taxa = self.df_taxa[self.df_taxa['taxon_full_name'].isin(self.df_images['taxon_full_name'])]


    def convert_dwca(self):
        self.df_multimedia = pd.read_csv(zipfile.ZipFile(self.path).open('multimedia.txt'), sep='\t', on_bad_lines="skip")
        self.df_taxa = self.df_occurrence.drop_duplicates(subset=['species'])

        self.df_taxa = self.df_taxa[
            ['species', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'specificEpithet',
             'infraspecificEpithet', 'acceptedTaxonKey', 'taxonomicStatus', 'acceptedTaxonKey']]
        self.df_taxa.columns = ['taxon_full_name', 'kingdom', 'division', 'class', 'order', 'family', 'genus',
                                'specific_epithet', 'infraspecific_epithet', 'taxon_id_at_source', 'status_at_source',
                                'accepted_taxon_id_at_source']
        # we're going with the GBIF taxon match
        self.df_taxa['status_at_source'].values[:] = 'accepted'
        self.df_images = self.df_multimedia[['identifier', 'gbifID']]
        self.df_images = pd.merge(left=self.df_images, right=self.df_occurrence, left_on='gbifID', right_on='gbifID')
        self.df_images = self.df_images[
            ['identifier_x', 'gbifID', 'gbifID', 'acceptedTaxonKey', 'species', 'decimalLatitude', 'decimalLongitude',
             'locality', 'eventDate']]
        self.df_images.columns = ['image_url', 'record_id', 'image_id', 'taxon_id_at_source', 'taxon_full_name',
                                  'location_latitude', 'location_longitude', 'location_reference', 'datetime']

        record_id_to_sequential = defaultdict(lambda: -1)

        def get_sequence_number(record_id):
            record_id_to_sequential[record_id] += 1
            return record_id_to_sequential[record_id]

        self.df_images['image_id'] = self.df_images['image_id'].apply(
            lambda x: str(x) + '_' + str(get_sequence_number(x)))

    def apply_occurrence_count_thresholds(self, minimum, max_ratio=0):
        if minimum < 2 and max_ratio == 0:
            return 0

        counts = {}

        for index, row in self.df_taxa.iterrows():
            counts[row['taxon_full_name']] = len(
                self.df_occurrence[self.df_occurrence['species'] == row['taxon_full_name']])

        self.df_images = self.df_images[self.df_images.apply(lambda x: counts[x['taxon_full_name']] >= minimum, axis=1)]
        self.df_taxa = self.df_taxa[self.df_taxa.apply(lambda x: counts[x['taxon_full_name']] >= minimum, axis=1)]

        if max_ratio >= 1:
            counts = {}
            for index, row in self.df_taxa.iterrows():
                counts[row['taxon_full_name']] = len(
                    self.df_occurrence[self.df_occurrence['species'] == row['taxon_full_name']])

            occurrences = []
            min_number = min(counts.values())
            max_number = int(min_number * max_ratio)

            for index, taxon in self.df_taxa.iterrows():
                taxon_occurrences = self.df_occurrence[self.df_occurrence['species'] == taxon['taxon_full_name']][
                    'gbifID'].tolist()
                if len(taxon_occurrences) > max_number:
                    shuffle(taxon_occurrences)
                    occurrences = occurrences + taxon_occurrences[0:max_number + 1]
                else:
                    occurrences = occurrences + taxon_occurrences

            self.df_images = self.df_images[self.df_images['record_id'].isin(occurrences)]

    def write_data(self, subset=''):
        self.df_images.to_csv(
            os.path.join(self.data_folder, 'all_images' + ('_' + subset if len(subset) else '') + '.csv'), index=False)
        self.df_taxa.to_csv(os.path.join(self.data_folder, 'all_taxa' + ('_' + subset if len(subset) else '') + '.csv'),
                            index=False)


if __name__ == '__main__':
    print('DwCA reader')
