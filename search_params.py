import loanwords
import semantic_net


def prune(threshold, pmi, semantic_net):
    pruned_entries = set()
    for i, entry in enumerate(pmi):
        if entry[2] < threshold:
            break
        pruned_entries.add((entry[0], entry[1]))
    print(threshold, '\t', len(pruned_entries))
    dist = 0
    denom = 0
    for entry in pruned_entries:
        print(entry)
        try:
            dist += semantic_net[(entry[0], entry[1])]
            denom += 1
        except KeyError:
            print('KEY ERROR', entry)


ONLY_WITHOUT_INHERITED_COUNTERPARTS = True

# entries = loanwords.get_loanwords(discard_forms_with_inherited_counterparts=ONLY_WITHOUT_INHERITED_COUNTERPARTS)
# pmi, borrowed = loanwords.pmi(entries, n_langs=41, per_donor=True, out_file=None)
semantic_net = semantic_net.get_dist_network()
# prune(0.6, pmi, semantic_net)
for entry in semantic_net:
    print(entry)
