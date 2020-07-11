import matplotlib.pyplot as plt

### CONFIG ###
NPMI_THRESHOLD = 50  # in %
IMPL_THRESHOLD = 81  # in %
DIRECTION_RATIO_THRESHOLD = 1.5
N_LANG_THRESHOLD = 3
##############

NPMI_THRESHOLD /= 100
IMPL_THRESHOLD /= 100

entries_filtered = filter(threshold_npmi=NPMI_THRESHOLD,
                          threshold_impl=IMPL_THRESHOLD,
                          threshold_intersection=N_LANG_THRESHOLD,
                          impl_dir_multiplier=DIRECTION_RATIO_THRESHOLD,
                          outfile=None, implication_direction=True)
entries_all = filter(threshold_npmi=-1, threshold_impl=-1,
                     threshold_intersection=N_LANG_THRESHOLD, outfile=None)


def borrowability2amount(entries):
    n_langs2concepts = {}
    max_langs = -1
    min_langs = 1000
    for entry in entries:
        n_langs_for_concept = round(entry.borrow_x)
        if n_langs_for_concept > max_langs:
            max_langs = n_langs_for_concept
        if n_langs_for_concept < min_langs:
            min_langs = n_langs_for_concept
        try:
            n_langs2concepts[n_langs_for_concept].add(entry.x)
        except KeyError:
            n_langs2concepts[n_langs_for_concept] = {entry.x}
    print("min langs", min_langs, "\tmax langs", max_langs)
    return n_langs2concepts


borrowability2all = borrowability2amount(entries_all)
borrowability2impl = borrowability2amount(entries_filtered)
borrowability2singletons = []
for (n_borrowed, n_concepts) in borrowability2all.items():
    borrowed_impl = 0
    try:
        borrowed_impl = borrowability2impl[n_borrowed]
    except KeyError:
        pass
    borrowability2singletons.append((n_borrowed, n_concepts))

borrowability2impl = [x for x in borrowability2impl.items()]
list.sort(borrowability2singletons, key=lambda x: x[0])
list.sort(borrowability2impl, key=lambda x: x[0])

fig, ax = plt.subplots()
ax.set_xlabel('Number of languages that borrowed the same concept')
ax.set_ylabel('Number of concepts by number target languages')
line1, = ax.plot([key for (key, _) in borrowability2singletons],
                 [val for (_, val) in borrowability2singletons],
                 color='tab:red', marker='x',
                 zorder=10)
line1.set_label('Concepts outside concept pairs with NPMI >= 0.7')
line2, = ax.plot([key for (key, _) in borrowability2impl],
                 [val for (_, val) in borrowability2impl],
                 color='tab:blue', marker='o',
                 zorder=5)
line2.set_label('Concepts in concept pairs with NPMI >= 0.7')
# ax.tick_params(axis='y')
ax.set_xticks(range(3, 36, 2))
ax.set_xlim(2.5, 35.5)
ax.grid(zorder=0)
ax.legend()
fig.tight_layout()
# fig.savefig("out/singleton_vs_impl.png")
plt.show()
