import loanwords
import semantic_net
import numpy as np
import matplotlib.pyplot as plt


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
    if verbose:
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
    mean_sim = 0
    if len(pruned_entries) > 0:
        mean_sim = similarity / len(pruned_entries)
    if verbose:
        print(similarity, len(pruned_entries))
        print(mean_sim)
    return mean_sim, len(pruned_entries)


ONLY_WITHOUT_INHERITED_COUNTERPARTS = True

entries = loanwords.get_loanwords(discard_forms_with_inherited_counterparts=ONLY_WITHOUT_INHERITED_COUNTERPARTS)
pmi, _ = loanwords.pmi(entries, n_langs=41, per_donor=True, out_file=None)
semantic_net = semantic_net.get_dist_network(max_dist=3)
wold2clics = concept_translations()
thresholds, sims, sizes = [], [], []
print('threshold\tmean similarity\tconcept pairs')
for threshold in range(55, 101, 1):
    threshold /= 100
    sim, size = prune(threshold, pmi, semantic_net, wold2clics)
    thresholds.append(threshold)
    sims.append(sim)
    sizes.append(size)
    print('{}\t{}\t{}'.format(threshold, sim, size))


fig, ax1 = plt.subplots()
color = 'tab:red'
ax1.set_xlabel('normalized PMI threshold')
ax1.set_ylabel('mean similarity', color=color)
ax1.set_title('Size and mean similarity of concept pair set '
              'by normalized PMI threshold')
ax1.plot(thresholds, sims, color=color, zorder=2)
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(zorder=0)

ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('number of concept pairs above threshold', color=color)
ax2.plot(thresholds, sizes, color=color, zorder=1)
ax2.tick_params(axis='y', labelcolor=color)

y2_max = round(ax2.get_ybound()[1] / 100) * 100
y_steps = (y2_max // 100) + 1
# ax1.set_yticks(np.linspace(round(ax1.get_ybound()[0] - 0.01, 2),
#                            round(ax1.get_ybound()[1], 2), y_steps))
ax1.set_yticks(np.linspace(0, 0.5, y_steps))
ax2.set_yticks(np.linspace(0, y2_max, y_steps))
ax1.set_ylim(bottom=0, top=0.51)
ax2.set_ylim(bottom=0, top=510)
ax1.set_xticks(list(threshold / 100 for threshold in range(55, 101, 5)))
fig.tight_layout()
fig.savefig("out/similarity_by_pmi.png")
plt.show()
