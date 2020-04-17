import math


class Borrowing:

    def __init__(self, word_id, src_lang):
        self.id = word_id
        self.src_lang = src_lang

    def add_values(self, target_lang, concept, category):
        self.target_lang = target_lang
        self.concept = concept
        self.category = category

    def __str__(self):
        return '<{}, {}, {}, {}, {}>'.format(self.id, self.src_lang,
                                             self.target_lang, self.concept,
                                             self.category)


def get_id2string(infile, to_int=False, key_idx=0, val_idx=1):
    id2lang = {}
    with open(infile, encoding='utf8') as f:
        for line in f:
            if line.startswith('ID,'):
                continue
            cells = line.split(',')
            entry_id = cells[key_idx]
            if to_int:
                entry_id = int(entry_id)
            id2lang[entry_id] = cells[val_idx]
    return id2lang


def get_loanwords(lang_file='./data/languages.csv',
                  param_file='./data/parameters.csv',
                  borrowing_file='./data/borrowings.csv',
                  form_file='./data/forms.csv'):
    id2lang = get_id2string(lang_file)
    id2param = get_id2string(param_file)
    id2cat = get_id2string(param_file, val_idx=3)

    entries = {}
    with open(borrowing_file, encoding='utf8') as f:
        next(f)
        for line in f:
            cells = line.strip().split(',')
            entries[cells[1]] = Borrowing(cells[1], id2lang[cells[-1]])

    with open(form_file, encoding='utf8') as f:
        next(f)
        for line in f:
            cells = line.strip().split(',')
            try:
                entries[cells[0]].add_values(id2lang[cells[1]],
                                             id2param[cells[2]],
                                             id2cat[cells[2]])
            except KeyError:
                continue

    print("Found {} borrowings".format(len(entries)))
    print(entries['62'])
    print(entries['36856'])
    return entries


def pmi(entries, min_langs=3, per_donor=False, out_file='out/nmpi.tsv'):
    assert min_langs > 0
    borrowed = {}
    langs = set()
    for entry in entries.values():
        langs.add(entry.target_lang)
        if per_donor:
            lang = entry.src_lang + ' > ' + entry.target_lang
        else:
            lang = entry.target_lang
        try:
            borrowed[entry.concept].add(lang)
        except KeyError:
            borrowed[entry.concept] = {lang}
    n_langs = len(langs)
    npmi = []
    concepts = list(borrowed.keys())
    for i in range(len(concepts)):
        x = concepts[i]
        for j in range(i + 1, len(concepts)):
            y = concepts[j]
            intersection = borrowed[x].intersection(borrowed[y])
            if len(intersection) < min_langs:
                continue
            p_x = len(borrowed[x]) / n_langs
            p_y = len(borrowed[y]) / n_langs
            p_xy = len(intersection) / n_langs
            pmi = math.log(p_xy / (p_x * p_y))
            h_xy = -math.log(p_xy)
            npmi.append((x, y, pmi / h_xy, borrowed[x], borrowed[y],
                        intersection))
    npmi.sort(key=lambda x: (x[2], len(x[5])), reverse=True)
    print(npmi[0])
    if out_file:
        with open(out_file, 'w', encoding='utf8') as f:
            f.write('Concept 1\tConcept 2\tNormalized PMI\tLanguages\n')
            for entry in npmi:
                f.write('{}\t{}\t{:.6f}\t{}\n'.format(entry[0], entry[1],
                                                      entry[2], entry[5]))


def implications(entries, min_langs=3, per_donor=False,
                 out_file='out/implications.tsv'):
    # "If a language borrowed X, it also borrowed Y."
    assert min_langs > 0
    borrowed = {}
    for entry in entries.values():
        if per_donor:
            lang = entry.src_lang + ' > ' + entry.target_lang
        else:
            lang = entry.target_lang
        try:
            borrowed[entry.concept].add(lang)
        except KeyError:
            borrowed[entry.concept] = {lang}
    implications = []
    for x in borrowed:
        for y in borrowed:
            if x == y:
                continue
            intersection = borrowed[x].intersection(borrowed[y])
            if len(intersection) < min_langs:
                continue
            strength = len(intersection) / len(borrowed[x])
            implications.append((x, y, strength, borrowed[x], borrowed[y],
                                 intersection))
    implications.sort(key=lambda x: (x[2], len(x[5])), reverse=True)
    print(implications[0])
    if out_file:
        with open(out_file, 'w', encoding='utf8') as f:
            f.write('Concept 1\tConcept 2\tImplication strength\tLanguages\n')
            for entry in implications:
                f.write('{}\t{}\t{:.6f}\t{}\n'.format(entry[0], entry[1],
                                                      entry[2], entry[5]))


entries = get_loanwords()
pmi(entries)
pmi(entries, per_donor=True, out_file='out/npmi_per_donor.tsv')
implications(entries)
implications(entries, per_donor=True,
             out_file='out/implications_per_donor.tsv')

# TODO: things to consider analysing

# some languages have multiple words with different borrowing statuses for
# a single concept

# consider donor langs

# breakdown by concept category

# effect: insertion vs coexistence

# age score, simplicity score

# 'immediate' vs. 'earlier' borrowing for the same ID
