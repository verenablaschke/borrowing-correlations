import numpy as np
import random
from loanwords import *


### CONFIG ###
ONLY_WO_INHERITED_COUNTERPARTS = False
N_RESAMPLES = 1000
OUT_FILE = '/out/bootstrap.txt'
##############

entries, concepts = get_loanwords(
    discard_forms_with_inherited_counterparts=ONLY_WO_INHERITED_COUNTERPARTS,
    sort_by_target_lang=True, return_concepts=True)
target_langs = list(entries.keys())
n_langs = len(target_langs)

concepts2pmi = {}
for sample_idx in range(N_RESAMPLES):
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
    # Calculate PMI for all concepts present in this sample
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

# Average across samples
concepts2pmi_mean = [(conceptpair[0], conceptpair[1], np.nanmean(pmi),
                      np.count_nonzero(~np.isnan(pmi)))
                     for conceptpair, pmi in concepts2pmi.items()]
concepts2pmi_mean.sort(key=lambda x: (x[2], x[0]),
                       reverse=True)
for i in range(10):
    print(concepts2pmi_mean[i])
with open(OUT_FILE, 'w', encoding='utf8') as f:
    f.write('CONCEPT_1\tCONCEPT_2\tNPMI\tN_SAMPLES\n')
    for (x, y, pmi, n_samples) in concepts2pmi_mean:
        f.write('{}\t{}\t{}\t{}\n'.format(x, y, pmi, n_samples))
print('DONE.')
