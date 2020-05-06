import loanwords
import semantic_net


def concept_translations(verbose=False):
    wold2id = loanwords.get_id2string('./data/wold/parameters.csv',
                                      key_idx=1, val_idx=0)
    id2clics = loanwords.get_id2string('./data/nelex/mapped-and-ranked-lists.tsv',
                                       key_idx=10, val_idx=0, sep='\t')
    wold2clics = {}
    for wold_entry in wold2id.items():
        try:
            wold2clics[wold_entry[0]] = id2clics[wold_entry[1]]
        except KeyError:
            if verbose:
                print('{} not in CLICS!'.format(wold_entry))
    return wold2clics


def prune(threshold, pmi, semantic_net, wold2clics, verbose=False):
    pruned_entries = set()
    for i, entry in enumerate(pmi):
        if entry[2] < threshold:
            break
        try:
            concept1 = wold2clics[entry[0]]
        except KeyError:
            print("No CLICS entry for {}".format(entry[0]))
            concept1 = entry[0]
        try:
            concept2 = wold2clics[entry[1]]
        except KeyError:
            print("No CLICS entry for {}".format(entry[1]))
            concept2 = entry[1]
        pruned_entries.add((concept1, concept2))
    print(threshold, '\t', len(pruned_entries))
    similarity = 0
    for entry in pruned_entries:
        try:
            similarity += (1 / semantic_net[(entry[0], entry[1])])
        except KeyError:
            # Very dissimilar entries
            # if verbose:
            #     print('Key error:', entry)
            continue
        except ZeroDivisionError:
            # Entries that are identical in CLICS but separate in WOLD
            # Knife (cutlery vs. utensil)
            # Dinner/supper (main meal vs. evening meal)
            if verbose:
                print('ZeroDivisionError:', entry)
            similarity += 1
    if verbose:
        print(similarity, len(pruned_entries))
        print(similarity / len(pruned_entries))
    return similarity / len(pruned_entries), len(pruned_entries)


ONLY_WITHOUT_INHERITED_COUNTERPARTS = True

entries = loanwords.get_loanwords(discard_forms_with_inherited_counterparts=ONLY_WITHOUT_INHERITED_COUNTERPARTS)
pmi, _ = loanwords.pmi(entries, n_langs=41, per_donor=True, out_file=None)
semantic_net = semantic_net.get_dist_network(max_dist=3)
print('threshold\tmean similarity\tconcept pairs')
wold2clics = concept_translations()
for threshold in [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9]:
    sim, size = prune(threshold, pmi, semantic_net, wold2clics)
    print('{}\t{}\t{}'.format(threshold, sim, size))
