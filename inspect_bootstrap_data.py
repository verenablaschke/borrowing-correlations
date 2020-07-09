from loanwords import *
import semantic_net
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter


class Implication:

    def __init__(self, x, y,
                 mean, sd, z, zn,
                 npmi_mean, npmi_sd, npmi_z, npmi_zn,
                 borrow_x, intersection,
                 x_field, y_field, direction=None):
        self.x = x
        self.y = y
        self.mean = float(mean)
        self.sd = float(sd)
        self.z = float(z)
        self.zn = float(zn)
        self.npmi_mean = float(npmi_mean)
        self.npmi_sd = float(npmi_sd)
        self.npmi_z = float(npmi_z)
        self.npmi_zn = float(npmi_zn)
        self.borrow_x = float(borrow_x)
        self.intersection = float(intersection)
        self.x_field = x_field
        self.y_field = y_field
        self.direction = direction

    def add_direction(self, direction):
        self.direction = direction

    def __str__(self):
        return '{} {} {}\tmean={:.2f} sd={:.2f} ({:.2f}, {:.2f})\t'\
               'pmi_mean={:.2f} pmi_sd={:.2f} ({:.2f}, {:.2f})\t'\
               'borrowability_x={:.2f}, intersection={:.2f}\t'\
               '{} {} {}'.format(
                   self.x, self.direction if self.add_direction else '->',
                   self.y, self.mean, self.sd, self.z, self.zn,
                   self.npmi_mean, self.npmi_sd, self.npmi_z, self.npmi_zn,
                   self.borrow_x, self.intersection,
                   self.x_field,
                   self.direction if self.add_direction else '->',
                   self.y_field)

    def impl_str(self):
        return '{} {} {}'.format(self.x, self.direction, self.y)


def concept_translations(verbose=False):
    wold2id = get_id2string('./data/wold/parameters.csv', key_idx=1, val_idx=0)
    id2clics = get_id2string('./data/nelex/mapped-and-ranked-lists.tsv',
                             key_idx=10, val_idx=0, sep='\t')
    wold2clics = {}
    for wold_entry in wold2id.items():
        try:
            wold2clics[wold_entry[0]] = id2clics[wold_entry[1]]
        except KeyError:
            if verbose:
                print('{} not in CLICS!'.format(wold_entry))
    return wold2clics


def prune(threshold, entries, semantic_net, wold2clics, axis, verbose=False):
    pruned_entries = set()
    for i, entry in enumerate(entries):
        if axis == 'IMPL' and entry.zn < threshold:
            continue
        if axis == 'PMI' and entry.npmi_zn < threshold:
            continue
        try:
            concept1 = wold2clics[entry.x]
        except KeyError:
            print("No CLICS entry for {}".format(entry.x))
            concept1 = entry.x
        try:
            concept2 = wold2clics[entry.y]
        except KeyError:
            print("No CLICS entry for {}".format(entry.y))
            concept2 = entry.y
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


def prefilter(axis, threshold_npmi=0, threshold_impl=0,
              threshold_intersection=3, implication_direction=False,
              impl_dir_multiplier=1.5,
              infile='out/bootstrap.txt',
              outfile='out/bootstrap_implication.txt',
              param_file='./data/wold/parameters.csv'):
    id2cat = get_id2string(param_file, key_idx=1, val_idx=3)
    entries = []
    with open(infile, encoding='utf8') as f:
        next(f)  # skip header
        for line in f:
            cells = line.strip().split('\t')
            if float(cells[-2]) < threshold_intersection:
                continue
            if float(cells[5]) < threshold_npmi:
                continue
            if float(cells[9]) > threshold_impl:
                entries.append(Implication(*cells[0:2], *cells[6:10],
                                           *cells[2:6], cells[14], cells[16],
                                           id2cat[cells[0]], id2cat[cells[1]]))
            if float(cells[13]) > threshold_impl:
                entries.append(Implication(cells[1], cells[0], *cells[10:14],
                                           *cells[2:6], *cells[15:17],
                                           id2cat[cells[1]], id2cat[cells[0]]))
    # entries.sort(key=lambda x: (x.zn if axis == 'IMPL' else x.npmi_zn,
    #                             x.intersection), reverse=True)
    entries.sort(key=lambda x: (x.x_field == x.y_field, x.x_field, x.y_field,
                                x.borrow_x),
                 reverse=True)
    entries_dir = {}
    if outfile or implication_direction:
        entry_dict = {(entry.x, entry.y): entry for entry in entries}
        concepts = {entry.x for entry in entries}
        concepts = concepts.union({entry.y for entry in entries})
        entries_dir = []
        added = set()
        for x in concepts:
            for y in concepts:
                if x == y or (x, y) in added:
                    continue
                try:
                    entry1 = entry_dict[(x, y)]
                except KeyError:
                    continue
                try:
                    entry2 = entry_dict[(y, x)]
                except KeyError:
                    entry1.add_direction('>')
                    entries_dir.append(entry1)
                    added.add((x, y))
                    continue
                directionality = entry1.zn / entry2.zn
                if directionality > impl_dir_multiplier:
                    entry1.add_direction('>')
                    entries_dir.append(entry1)
                    added.add((x, y))
                    added.add((y, x))
                elif 1 / impl_dir_multiplier > directionality:
                    entry2.add_direction('>')
                    entries_dir.append(entry2)
                    added.add((x, y))
                    added.add((y, x))
                else:
                    entry1.add_direction('<>')
                    entries_dir.append(entry1)
                    added.add((x, y))
                    added.add((y, x))
        entries_dir.sort(key=lambda x: (x.x_field == x.y_field,
                                        x.x_field, x.intersection),
                         reverse=True)
    if outfile:
        with open(outfile, 'w', encoding='utf8') as f:
            f.write("# {} RESULTS (THRESHOLD IMPL: {}, THRESHOLD NPMI: {})\n"
                    .format(len(entries), threshold_impl, threshold_npmi))
            f.write("X\tDIR\tY\tSEM_FIELD_X\tSEM_FIELD_Y\tINTERSECTION\n")
            for entry in entries_dir:
                f.write("{}\t{}\t{}\t{:.1f}\t{}\t{}\n"
                        .format(entry.x, entry.direction, entry.y,
                                entry.intersection, entry.x_field,
                                entry.y_field))
    return entries


def run(axis, sem_net, wold2clics, threshold_impl=0, threshold_npmi=0,
        threshold_min=40, threshold_max=101):
    entries = prefilter(outfile=None, axis=axis,
                        threshold_npmi=threshold_npmi,
                        threshold_impl=threshold_impl)
    thresholds_sim, thresholds_size, sims, sizes = [], [], [], []
    print('threshold\tmean similarity\tconcept pairs')
    for threshold in range(threshold_min, threshold_max, 1):
        threshold /= 100
        sim, size = prune(threshold, entries, sem_net, wold2clics, axis)
        thresholds_size.append(threshold)
        sizes.append(size)
        if size > 0:
            thresholds_sim.append(threshold)
            sims.append(sim)
        print('{}\t{}\t{}'.format(threshold, sim, size))

    fig, ax1 = plt.subplots()
    color = 'tab:blue'
    ax1.set_ylabel('Number of concept pairs above threshold', color=color)
    ax1.plot(thresholds_size, sizes, color=color, marker='o', zorder=50)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_xlabel('{} threshold'.format(
        "Implication" if axis == "IMPL" else "NPMI"))
    ax2.set_ylabel('Mean similarity', color=color)
    ax2.plot(thresholds_sim, sims, color=color, marker='x', zorder=100)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.grid(zorder=0)

    y1_max = round(ax1.get_ybound()[1] / 100) * 100
    y2_max = round(ax2.get_ybound()[1] * 100) / 100
    # y_max = y1_max if y1_max > y2_max else y2_max
    # y_steps = int((y2_max // 100) + 1)
    # print(y_steps, y1_max, y2_max, y_max)
    # ax2.set_yticks(np.linspace(0, y_max / 100, y_steps))
    # ax1.set_yticks(np.linspace(0, y_max, y_steps))
    # ax1.set_ylim(bottom=0, top=y1_max + 10)
    ax1.set_yscale('log')
    y_tick_candidates = [1, 2, 5, 10, 20, 50,
                         100, 200, 500, 1000, 2000, 5000, 10000]
    y_ticks = []
    for y_tick in y_tick_candidates:
        y_ticks.append(y_tick)
        if y_tick > y1_max:
            break

    ax1.set_yticks(y_ticks)
    ax1.get_yaxis().set_major_formatter(ScalarFormatter())
    ax1.set_ylim(bottom=1)
    ax2.set_ylim(bottom=0, top=y2_max + 0.00001)
    ax1.set_xticks(list(threshold / 100 for threshold in range(threshold_min, threshold_max, 5)))
    fig.tight_layout()
    fig.savefig("out/similarity_by_{}_bootstrap.png".format(
        "implication" if axis == "IMPL" else "npmi"))
    plt.show()


# sem_net = semantic_net.get_dist_network(max_dist=3)
# wold2clics = concept_translations()
# run("IMPL", sem_net, wold2clics, threshold_npmi=0.5)
# entries = prefilter(threshold_impl=0.81, threshold_npmi=0.5, axis="IMPL",
#                     outfile='out/bootstrap_implication_81_50.txt')
# entries = prefilter(threshold_impl=0.81, threshold_npmi=0.5, axis="IMPL",
                    # outfile=None)
