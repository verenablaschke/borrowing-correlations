import numpy as np
import random
import gc
from loanwords import *


### CONFIG ###
ONLY_WO_INHERITED_COUNTERPARTS = False
N_RESAMPLES = 1000
OUT_FILE = '/content/gdrive/My Drive/colab_files/bootstrap-implications.txt'
# For batch-wise processing:
BATCH_WISE = True
START_IDX = 0
STOP_IDX = 300
PMI_FILE = '/content/gdrive/My Drive/colab_files/pmi.txt'
INTERSECTION_FILE = '/content/gdrive/My Drive/colab_files/intersections.txt'
BORROWABILITY_FILE = '/content/gdrive/My Drive/colab_files/borrowability.txt'
PRINT_ALL_INDICES = True
##############

# entries, concepts = get_loanwords(
#     lang_file='/content/gdrive/My Drive/colab_files/data/wold/languages.csv',
#     param_file='/content/gdrive/My Drive/colab_files/data/wold/parameters.csv',
#     borrowing_file='/content/gdrive/My Drive/colab_files/data/wold/borrowings.csv',
#     form_file='/content/gdrive/My Drive/colab_files/data/wold/forms.csv',
#     discard_forms_with_inherited_counterparts=ONLY_WO_INHERITED_COUNTERPARTS,
#     sort_by_target_lang=True, return_concepts=True)
entries, concepts = get_loanwords(
    discard_forms_with_inherited_counterparts=ONLY_WO_INHERITED_COUNTERPARTS,
    sort_by_target_lang=True, return_concepts=True)
target_langs = list(entries.keys())
n_langs = len(target_langs)
print(n_langs, "languages.")

concepts2pmi = {}
concepts2intersection = {}
concept2borrowability = {}

array_len = STOP_IDX if BATCH_WISE else N_RESAMPLES
for sample_idx in range(STOP_IDX if BATCH_WISE else N_RESAMPLES):
    if PRINT_ALL_INDICES or sample_idx % 100 == 0:
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
    # Calculate the PMI values and individual and joint borrowing numbres for
    # all concepts present in this sample.
    concepts2pmi,concepts2intersection, concept2borrowability = pmi_and_implications(
        entry_sample, concepts2pmi, concepts2intersection,
        concept2borrowability, sample_idx, n_langs, per_donor=True,
        array_len=array_len)
    gc.collect()

if BATCH_WISE and START_IDX > 0:
    print("Reading previous PMI entries")
    with open(PMI_FILE, encoding='utf8') as f:
        for line in file:
            cells = line.strip().split('\t')
            array = np.empty(STOP_IDX, dtype=np.float32)
            array[:START_IDX] = np.fromstring(cells[2][1:-1], sep=',')
            try:
                array[START_IDX:] = concepts2pmi[(cells[0], cells[1])]
            except KeyError:
                array[START_IDX:] = np.NaN
            concepts2pmi[(cells[0], cells[1])] = array
    print("Reading previous intersection entries")
    with open(INTERSECTION_FILE, encoding='utf8') as f:
        for line in file:
            cells = line.strip().split('\t')
            array = np.empty(STOP_IDX, dtype=np.int8)
            array[:START_IDX] = np.fromstring(cells[2][1:-1], sep=',',
                                              dtype=np.int8)
            try:
                array[START_IDX:] = concepts2intersection[(cells[0], cells[1])]
            except KeyError:
                array[START_IDX:] = np.NaN
            concepts2intersection[(cells[0], cells[1])] = array
    print("Reading previous borrowability entries")
    with open(BORROWABILITY_FILE, encoding='utf8') as f:
        for line in file:
            cells = line.strip().split('\t')
            array = np.empty(STOP_IDX, dtype=np.float32)
            array[:START_IDX] = np.fromstring(cells[1][1:-1], sep=',',
                                              dtype=np.int8)
            try:
                array[START_IDX:] = concept2borrowability[cells[0]]
            except KeyError:
                array[START_IDX:] = np.NaN
            concept2borrowability[cells[0]] = array

if BATCH_WISE:
    print("Writing PMI file")
    with open(PMI_FILE, 'w', encoding='utf8') as f:
        for ((x, y), pmi) in concepts2pmi.items():
            if START_IDX > 0 and a.size < STOP_IDX:
                # The concept pair wasn't in the previous file.
                array = np.empty(STOP_IDX, dtype=np.float32)
                array[:START_IDX] = np.NaN
                array[START_IDX:] = pmi
                pmi = array
            f.write('{}\t{}\t{}\n'.format(x, y, pmi))
    print("Writing intersection file")
    with open(INTERSECTION_FILE, 'w', encoding='utf8') as f:
        for ((x, y), strength) in concepts2pmi.items():
            if START_IDX > 0 and a.size < STOP_IDX:
                # The concept pair wasn't in the previous file.
                array = np.empty(STOP_IDX, dtype=np.float32)
                array[:START_IDX] = np.NaN
                array[START_IDX:] = strength
                strength = array
            f.write('{}\t{}\t{}\n'.format(x, y, strength))
    print("Writing borrowability file")
    with open(BORROWABILITY_FILE, 'w', encoding='utf8') as f:
        for (x, borrowability) in concepts2pmi.items():
            if START_IDX > 0 and a.size < STOP_IDX:
                # The concept wasn't in the previous file.
                array = np.empty(STOP_IDX, dtype=np.float32)
                array[:START_IDX] = np.NaN
                array[START_IDX:] = borrowability
                borrowability = array
            f.write('{}\t{}\t{}\n'.format(x, y, borrowability))

if (not BATCH_WISE) or (BATCH_WISE and STOP_IDX == N_RESAMPLES):
    with open(OUT_FILE, 'w', encoding='utf8') as f:
        f.write('CONCEPT_1\tCONCEPT_2\tIMPLICATION_STRENGTH\tNPMI\tBORROWABILITY_X\tN_INSTANCES\n')
        for idx, ((x, y), strength) in enumerate(concepts2implication_strength.items()):
            # Average across samples
            strength = np.nanmean(strength)
            n_samples = np.count_nonzero(~np.isnan(strength))
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
                                                      borrowability,
                                                      n_samples))
            if idx < 10:
                print('{}\t{}\t{}\t{}\t{}\t{}'.format(x, y, strength, pmi,
                                                      borrowability,
                                                      n_samples))
print('DONE.')
