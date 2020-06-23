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
    concepts2pmi,concepts2intersection, concept2borrowability = pmi_and_implications(
        entry_sample, concepts2pmi, concepts2intersection,
        concept2borrowability, sample_idx, n_langs, per_donor=PER_DONOR,
        array_len=N_RESAMPLES)
    gc.collect()


# Given the large number of samples, we assume that the distributions of PMI
# and implication strength values we sampled is normally distributed.
# z is the 95% quantile of the standard normal distribution (one-sided!)
z = 1.64485
with open(OUT_FILE, 'w', encoding='utf8') as f:
    f.write('CONCEPT X\tCONCEPT Y\t'
            'NPMI (MEAN)\tNPMI (STD DEV)\tNPMI (MIN 95%)\tNPMI (MIN N 95%)\t'
            'IMPL STR X->Y (MEAN)\tIMPL STR X->Y (SD)\tIMPL STR X->Y (MIN 95%)\tIMPL STR X->Y (MIN  N 95%)\t'
            'IMPL STR Y->X (MEAN)\tIMPL STR Y->X (SD)\tIMPL STR Y->X (MIN 95%)\tIMPL STR Y->X (MIN N 95%)\t'
            'BORROWABILITY_X\tBORROWABILITY_Y\tINTERSECTION (MEAN)\tN_INSTANCES\n')
    for (x, y), intersection in concepts2intersection.items():
        # Average across samples
        try:
            pmi_array = concepts2pmi[(x, y)]
        except KeyError:
            pmi_array = concepts2pmi[(y, x)]
        pmi_mean = np.nanmean(pmi_array)
        if pmi_mean < 0.2:
            continue
        n_samples = np.count_nonzero(~np.isnan(intersection))
        # z_n takes the sample size into account
        # (large samples are more meaningful and we expect less variation)
        z_n = z / np.sqrt(n_samples)
        pmi_sd = np.sqrt(np.nanmean((pmi_array - pmi_mean) ** 2))
        # (minimum) threshold for a (one-sided) 95% confidence interval
        pmi_threshold = pmi_mean - z * pmi_sd
        pmi_threshold_n = pmi_mean - z_n * pmi_sd
        borrowability_x = np.nanmean(concept2borrowability[x])
        implication_xy = intersection / borrowability_x
        implication_xy_mean = np.nanmean(implication_xy)
        implication_xy_sd = np.sqrt(np.nanmean(
            (implication_xy - implication_xy_mean) ** 2))
        implication_xy_threshold = implication_xy_mean - z * implication_xy_sd
        implication_xy_threshold_n = implication_xy_mean - z_n * implication_xy_sd
        borrowability_y = np.nanmean(concept2borrowability[y])
        implication_yx = intersection / borrowability_y
        implication_yx_mean = np.nanmean(implication_yx)
        implication_yx_sd = np.sqrt(np.nanmean(
            (implication_yx - implication_yx_mean) ** 2))
        implication_yx_threshold = implication_yx_mean - z * implication_yx_sd
        implication_yx_threshold_n = implication_yx_mean - z_n * implication_yx_sd
        intersection_mean = np.nanmean(intersection)
        f.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
            x, y, pmi_mean, pmi_sd, pmi_threshold, pmi_threshold_n,
            implication_xy_mean, implication_xy_sd,
            implication_xy_threshold, implication_xy_threshold_n,
            implication_yx_mean, implication_yx_sd,
            implication_yx_threshold, implication_yx_threshold_n,
            borrowability_x, borrowability_y, intersection, n_samples))
        if pmi_mean > 0.7:
            print('{}, {}\t'
                  'PMI ({}, {}, {}, {})\t'
                  'X->Y ({}, {}, {}, {})\t'
                  'Y->X ({}, {}, {}, {})\t'
                  'X: {}\tY: {}\tIntersection: {}\tN: {}'.format(
                      x, y, pmi_mean, pmi_sd, pmi_threshold, pmi_threshold_n,
                      implication_xy_mean, implication_xy_sd,
                      implication_xy_threshold, implication_xy_threshold_n,
                      implication_yx_mean, implication_yx_sd,
                      implication_yx_threshold, implication_yx_threshold_n,
                      borrowability_x, borrowability_y, intersection, n_samples))
print('DONE.')

