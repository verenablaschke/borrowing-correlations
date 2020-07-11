import numpy as np
import random
import gc
from loanwords import *


### CONFIG ###
ONLY_WO_INHERITED_COUNTERPARTS = False
PER_DONOR = True
N_RESAMPLES = 1000
OUT_FILE = '/content/gdrive/My Drive/colab_files/bootstrap.txt'
##############

entries, concepts = get_loanwords(
    lang_file='/content/gdrive/My Drive/colab_files/data/wold/languages.csv',
    param_file='/content/gdrive/My Drive/colab_files/data/wold/parameters.csv',
    borrowing_file='/content/gdrive/My Drive/colab_files/data/wold/borrowings.csv',
    form_file='/content/gdrive/My Drive/colab_files/data/wold/forms.csv',
    discard_forms_with_inherited_counterparts=ONLY_WO_INHERITED_COUNTERPARTS,
    sort_by_target_lang=True, return_concepts=True)
# entries, concepts = get_loanwords(
#     discard_forms_with_inherited_counterparts=ONLY_WO_INHERITED_COUNTERPARTS,
#     sort_by_target_lang=True, return_concepts=True)
target_langs = list(entries.keys())
n_langs = len(target_langs)
print(n_langs, "languages.")

concepts2pmi = {}
concepts2intersection = {}
concept2borrowability = {}

for sample_idx in range(N_RESAMPLES):
    if sample_idx % 50 == 0:
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
    concepts2pmi, concepts2intersection, concept2borrowability = pmi_and_implications(
        entry_sample, concepts2pmi, concepts2intersection,
        concept2borrowability, sample_idx, n_langs, per_donor=PER_DONOR,
        array_len=N_RESAMPLES)
    gc.collect()


def threshold(score, z_n):
    mean = np.nanmean(score)
    sd = np.sqrt(np.nanmean((score - mean) ** 2))
    return mean - z_n * sd


# Given the large number of samples, we assume that the distributions of PMI
# and implication strength values we sampled is normally distributed.
# z is the 95% quantile of the standard normal distribution (one-sided!)
z = 1.64485
with open(OUT_FILE, 'w', encoding='utf8') as f:
    f.write('CONCEPT X\tCONCEPT Y\tNPMI\t'
            'IMPL STR X->Y\tIMPL STR Y->X\t'
            'BORROWABILITY_X\tBORROWABILITY_Y\tINTERSECTION\n')
    for (x, y), intersection in concepts2intersection.items():
        # Average across samples
        try:
            pmi_array = concepts2pmi[(x, y)]
        except KeyError:
            pmi_array = concepts2pmi[(y, x)]
        # z_n takes the sample size into account
        # (large samples are more meaningful and we expect less variation)
        # -> for calculating the (minimum) threshold for a (one-sided) 95%
        # confidence interval
        n_samples = np.count_nonzero(~np.isnan(intersection))
        z_n = z / np.sqrt(n_samples)
        borrowability_x = threshold(concept2borrowability[x], z_n)
        if borrowability_x < 3:
            continue
        pmi = threshold(pmi_array, z_n)
        implication_xy = threshold(intersection / borrowability_x, z_n)
        borrowability_y = threshold(concept2borrowability[y], z_n)
        implication_yx = threshold(intersection / borrowability_y, z_n)
        intersection = threshold(intersection, z_n)
        f.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'
                .format(x, y, pmi, implication_xy, implication_yx,
                        borrowability_x, borrowability_y, intersection))
        if pmi > 0.7 and intersection > 2.5:
            print('{}, {}\tPMI {:.4f}\tX->Y {:.4f}\tY->X {:.4f}\t'
                  'X: {:.2f}\tY: {:.2f}\tIntersection: {:.2f}\tN: {}'.format(
                      x, y, pmi, implication_xy, implication_yx,
                      borrowability_x, borrowability_y, intersection,
                      n_samples))
print('DONE.')
