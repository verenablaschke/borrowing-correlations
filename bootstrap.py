import numpy as np
import random
from loanwords import *


### CONFIG ###
ONLY_WO_INHERITED_COUNTERPARTS = False
N_RESAMPLES = 1000
OUT_FILE = '/content/gdrive/My Drive/colab_files/bootstrap-implications.txt'
# For batch-wise processing:
BATCH_WISE = True
START_IDX = 0
STOP_IDX = 10
PMI_FILE = '/content/gdrive/My Drive/colab_files/pmi.txt'
IMPLICATIONs_FILE = '/content/gdrive/My Drive/colab_files/implications.txt'
BORROWABILITY_FILE = '/content/gdrive/My Drive/colab_files/borrowability.txt'
##############

entries, concepts = get_loanwords(
    discard_forms_with_inherited_counterparts=ONLY_WO_INHERITED_COUNTERPARTS,
    sort_by_target_lang=True, return_concepts=True)
target_langs = list(entries.keys())
n_langs = len(target_langs)

concepts2pmi = {}
concepts2implication_strength = {}
concept2borrowability = {}

if BATCH_WISE and START_IDX > 0:
    with open(PMI_FILE, encoding='utf8') as f:
        for line in file:
            cells = line.strip().split('\t')
            concepts2pmi[(cells[0], cells[1])] = np.fromstring(cells[2][1:-1],
                                                               sep=',')
    with open(IMPLICATIONs_FILE, encoding='utf8') as f:
        for line in file:
            cells = line.strip().split('\t')
            concepts2implication_strength[(cells[0], cells[1])] = np.fromstring(cells[2][1:-1], sep=',')

    with open(BORROWABILITY_FILE, encoding='utf8') as f:
        for line in file:
            cells = line.strip().split('\t')
            concept2borrowability[cells[0]] = np.fromstring(cells[1][1:-1],
                                                            sep=',')

indices = range(N_RESAMPLES)
if BATCH_WISE:
    indices = range(START_IDX, STOP_IDX)
for sample_idx in indices:
    if sample_idx % 100 == 0:
        print(sample_idx)
    # Sample with replacement.
    lang_sample = random.choices(target_langs, k=n_langs)
    langs_added = []
    idx = 1
    entry_sample = []
    for lang in lang_sample:
        if lang in langs_added:
            entry_sample += (entry.copy_and_index_lang(idx)
                             for entry in entries[lang])
            idx += 1
        else:
            langs_added.append(lang)
            entry_sample += entries[lang]
    # Calculate the PMI and implication strength for all concepts present in
    # this sample
    nmpi_scores, _ = pmi(entry_sample, n_langs, min_langs=1,
                         entries_is_entry_set=True, out_file=None)
    for (x, y, npmi, _, _) in nmpi_scores:
        try:
            concepts2pmi[(x, y)][sample_idx] = npmi
        except KeyError:
            array = np.empty(N_RESAMPLES, dtype=np.float32)
            array.fill(np.NaN)
            array[sample_idx] = npmi
            concepts2pmi[(x, y)] = array
    impl = implications(entry_sample, n_langs, min_langs=1, per_donor=True,
                        out_file=None, entries_is_entry_set=True)
    for (x, y, strength, borrowability_x, _) in impl:
        try:
            concepts2implication_strength[(x, y)][sample_idx] = strength
        except KeyError:
            array = np.empty(N_RESAMPLES, dtype=np.float32)
            array.fill(np.NaN)
            array[sample_idx] = strength
            concepts2implication_strength[(x, y)] = array
        try:
            concept2borrowability[x][sample_idx] = borrowability_x
        except KeyError:
            array = np.empty(N_RESAMPLES, dtype=np.float32)
            array.fill(np.NaN)
            array[sample_idx] = borrowability_x
            concept2borrowability[x] = array

if BATCH_WISE:
    with open(PMI_FILE, 'w', encoding='utf8') as f:
        for (x, y, pmi) in concepts2pmi:
            f.write('{}\t{}\t{}\n'.format(x, y, pmi))
    with open(IMPLICATIONs_FILE, 'w', encoding='utf8') as f:
        for (x, y, strength) in concepts2pmi:
            f.write('{}\t{}\t{}\n'.format(x, y, strength))
    with open(BORROWABILITY_FILE, 'w', encoding='utf8') as f:
        for (x, borrowability) in concepts2pmi:
            f.write('{}\t{}\t{}\n'.format(x, y, borrowability))

# Average across samples
concepts2implication_mean = [(conceptpair[0], conceptpair[1],
                              np.nanmean(strength),
                              np.count_nonzero(~np.isnan(strength)))
                             for conceptpair, strength in concepts2implication_strength.items()]
concepts2implication_mean.sort(key=lambda x: (x[2], x[0]), reverse=True)


concepts2pmi_mean = [(conceptpair[0], conceptpair[1], np.nanmean(pmi),
                      np.count_nonzero(~np.isnan(pmi)))
                     for conceptpair, pmi in concepts2pmi.items()]
concepts2pmi_mean.sort(key=lambda x: (x[2], x[0]),
                       reverse=True)
for i in range(10):
    print(concepts2pmi_mean[i])

if (not BATCH_WISE) or (BATCH_WISE and END_IDX == N_RESAMPLES):
    with open(OUT_FILE, 'w', encoding='utf8') as f:
        f.write('CONCEPT_1\tCONCEPT_2\tIMPLICATION_STRENGTH\tNPMI\tBORROWABILITY_X\tN_INSTANCES\n')
        for idx, (x, y, strength, n_samples) in enumerate(concepts2implication_mean):
            try:
                pmi = np.nanmean(concepts2pmi[(x, y)])
            except KeyError:
                try:
                    pmi = np.nanmean(concepts2pmi[(y, x)])
                except KeyError:
                    pmi = np.NaN
            try:
                borrowability = np.nanmean(concept2borrowability[x])
            except KeyError:
                borrowability = np.NaN
            f.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(x, y, strength, pmi,
                                                      borrowability, n_samples))
            if idx < 10:
                print('{}\t{}\t{}\t{}\t{}\t{}'.format(x, y, strength, pmi,
                                                      borrowability, n_samples))
print('DONE.')
