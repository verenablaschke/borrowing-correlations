import matplotlib.pyplot as plt
from inspect_bootstrap_data import *

### CONFIG ###
NPMI_THRESHOLD = 60  # in %
IMPL_THRESHOLD = 80  # in %
DIRECTION_RATIO_THRESHOLD = 1.5
N_LANG_THRESHOLD = 3
##############

NPMI_THRESHOLD /= 100
IMPL_THRESHOLD /= 100

entries_all = filter(threshold_npmi=-1, threshold_impl=-1,
                     threshold_borrow_x=N_LANG_THRESHOLD, outfile=None)
print(len(entries_all), "concept pairs total")
entries_filtered = filter(threshold_npmi=NPMI_THRESHOLD,
                          threshold_impl=IMPL_THRESHOLD,
                          threshold_borrow_x=N_LANG_THRESHOLD,
                          impl_dir_multiplier=DIRECTION_RATIO_THRESHOLD,
                          outfile=None, implication_direction=True)
print(len(entries_filtered), "filtered concept pairs")

concepts_impl = set()
for e in entries_filtered:
    concepts_impl.add(e.x)
    concepts_impl.add(e.y)

borrowability2singletons = {}
borrowability2impl = {}
max_langs, max_langs_impl = -1, -1
min_langs, min_langs_impl = 1000, 1000
added = set()
for entry in entries_all:
    if entry.x in added:
        continue
    added.add(entry.x)
    n_langs_for_concept = round(entry.borrow_x)
    if entry.x in concepts_impl:
        if n_langs_for_concept > max_langs_impl:
            max_langs_impl = n_langs_for_concept
        if n_langs_for_concept < min_langs_impl:
            min_langs_impl = n_langs_for_concept
        try:
            borrowability2impl[n_langs_for_concept].add(entry.x)
        except KeyError:
            borrowability2impl[n_langs_for_concept] = {entry.x}
    else:
        if n_langs_for_concept > max_langs:
            max_langs = n_langs_for_concept
        if n_langs_for_concept < min_langs:
            min_langs = n_langs_for_concept
        try:
            borrowability2singletons[n_langs_for_concept].add(entry.x)
        except KeyError:
            borrowability2singletons[n_langs_for_concept] = {entry.x}
print("min langs", min_langs, "\tmax langs", max_langs)
print("min langs (impl)", min_langs_impl, "\tmax langs (impl)", max_langs_impl)


borrowability2impl = [x for x in borrowability2impl.items()]
borrowability2singletons = [x for x in borrowability2singletons.items()]
list.sort(borrowability2singletons, key=lambda x: x[0])
list.sort(borrowability2impl, key=lambda x: x[0])

print("SINGLETONS")
for x in borrowability2singletons:
    print(x)
print("\nIMPL")
for x in borrowability2impl:
    print(x)

fig, ax = plt.subplots()
ax.set_xlabel('Number of donor-target pairs that borrowed the same concept')
ax.set_ylabel('Number of concepts by number of donor-target pairs')
line1, = ax.plot([key for (key, _) in borrowability2singletons],
                 [len(val) for (_, val) in borrowability2singletons],
                 color='tab:red', marker='x',
                 zorder=10)
line1.set_label('Concepts only in concept pairs with NPMI < 0.6 and/or implication strength < 0.8')
line2, = ax.plot([key for (key, _) in borrowability2impl],
                 [len(val) for (_, val) in borrowability2impl],
                 color='tab:blue', marker='o',
                 zorder=5)
line2.set_label('Concepts in concept pairs with NPMI ≥ 0.6, implication strength ≥ 0.8')
ax.set_xticks(range(3, 41, 2))
ax.set_xlim(2.5, 40.5)
ax.grid(zorder=0)
ax.legend()
# fig.savefig("out/singleton_vs_impl.png")
plt.show()
