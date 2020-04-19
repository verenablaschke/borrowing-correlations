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
            if ('"') in line:
                cells = []
                line = line.replace('""', "'")
                for i, quote_cell in enumerate(line.split('"')):
                    if i % 2 == 0:
                        if quote_cell[-1] == ',':
                            quote_cell = quote_cell[:-1]
                        if quote_cell[0] == ',':
                            quote_cell = quote_cell[1:]
                        cells += quote_cell.split(',')
                    else:
                        cells += [quote_cell]
            else:
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


def get_concepts(param_file='./data/parameters.csv'):
    concept2field = get_id2string(param_file, key_idx=1, val_idx=3)
    field2size = {}
    for concept in concept2field:
        try:
            field2size[concept2field[concept]] += 1
        except KeyError:
            field2size[concept2field[concept]] = 1
    return concept2field, field2size


def languages_by_loanword(entries, out_file='out/loanwords_to_languages.tsv'):
    loanwords = {}
    for entry in entries.values():
        try:
            loanwords[entry.concept].add(entry.src_lang + ' > ' + entry.target_lang)
        except KeyError:
            loanwords[entry.concept] = {entry.src_lang + ' > ' + entry.target_lang}
    loanwords = list(loanwords.items())
    loanwords.sort(key=lambda x: len(x[1]), reverse=True)
    with open(out_file, 'w', encoding='utf8') as f:
        f.write('Concept\tNumber of languages\tLanguages\n')
        for entry in loanwords:
            f.write('{}\t{}\t{}\n'.format(entry[0], len(entry[1]), entry[1]))


def loan_directions(entries, out_file='out/loan_directions.tsv'):
    loanwords = {}
    for entry in entries.values():
        try:
            loanwords[entry.src_lang + ' > ' + entry.target_lang].add(entry.concept)
        except KeyError:
            loanwords[entry.src_lang + ' > ' + entry.target_lang] = {entry.concept}
    loanwords = list(loanwords.items())
    loanwords.sort(key=lambda x: len(x[1]), reverse=True)
    with open(out_file, 'w', encoding='utf8') as f:
        f.write('Rank\tLanguages\tNumber of concepts\tConcepts\n')
        for rank, entry in enumerate(loanwords):
            f.write('{}\t{}\t{}\t{}\n'.format(rank + 1, entry[0],
                                              len(entry[1]), entry[1]))


def pmi(entries, n_langs, min_langs=3, per_donor=False,
        out_file='out/nmpi.tsv'):
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
    npmi = []
    concepts = list(borrowed.keys())
    for i in range(len(concepts)):
        x = concepts[i]
        # for j in range(i + 1, len(concepts)):
        for j in range(len(concepts)):
            if i == j:
                continue
            y = concepts[j]
            intersection = borrowed[x].intersection(borrowed[y])
            if len(intersection) < min_langs:
                continue
            p_x = len(borrowed[x]) / n_langs
            p_y = len(borrowed[y]) / n_langs
            p_xy = len(intersection) / n_langs
            pmi = math.log(p_xy / (p_x * p_y))
            h_xy = -math.log(p_xy)
            npmi.append((x, y, pmi / h_xy, p_x, intersection))
    npmi.sort(key=lambda x: (x[2], x[3], len(x[4])), reverse=True)
    print(npmi[0])
    if out_file:
        with open(out_file, 'w', encoding='utf8') as f:
            f.write('Concept X\tConcept Y\tNormalized PMI\tBorrowability X\t'
                    'Languages\n')
            for entry in npmi:
                f.write('{}\t{}\t{:.6f}\t{:.6f}\t{}\n'.format(*entry))
    return npmi, n_langs


def implications(entries, n_langs, min_langs=3, per_donor=False,
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
            borrowability_x = len(borrowed[x]) / n_langs
            implications.append((x, y, strength, borrowability_x,
                                 intersection))
    implications.sort(key=lambda x: (x[2], x[3], len(x[4])), reverse=True)
    print(implications[0])
    if out_file:
        with open(out_file, 'w', encoding='utf8') as f:
            f.write('Concept X\tConcept Y\tImplication strength\t'
                    'Borrowability X\tLanguages\n')
            for entry in implications:
                f.write('{}\t{}\t{:.6f}\t{:.6f}\t{}\n'.format(*entry))


def implications_by_field(entries, n_langs, min_langs=3, per_donor=False,
                          out_file='out/implications_field.tsv'):
    # "If a language borrowed X, it also borrowed other words
    #  belonging to the same semantic field"
    assert min_langs > 0
    concept2field, field2size = get_concepts()
    borrowed = {}  # concept -> lang
    borrowed_fields = {}  # lang -> field -> concept
    for entry in entries.values():
        if per_donor:
            lang = entry.src_lang + ' > ' + entry.target_lang
        else:
            lang = entry.target_lang
        try:
            borrowed[entry.concept].add(lang)
        except KeyError:
            borrowed[entry.concept] = {lang}
        field = concept2field[entry.concept]
        try:
            borrowed_fields[lang][field].add(entry.concept)
        except KeyError:
            try:
                borrowed_fields[lang][field] = {entry.concept}
            except KeyError:
                borrowed_fields[lang] = {field: {entry.concept}}
    implications = []
    for x in borrowed:
        langs = borrowed[x]
        if len(langs) < min_langs:
            continue
        field = concept2field[x]
        strength = 0
        for lang in langs:
            try:
                strength += len(borrowed_fields[lang][field])
            except KeyError:
                continue
        strength /= len(langs)
        strength /= field2size[field]
        borrowability = len(langs) / n_langs
        implications.append((x, field, strength, borrowability, langs))
    implications.sort(key=lambda x: (x[2], x[3], len(x[4])), reverse=True)
    print(implications[0])
    if out_file:
        with open(out_file, 'w', encoding='utf8') as f:
            f.write('Concept\tField\tImplication strength\t'
                    'Borrowability of concept\tLanguages\n')
            for entry in implications:
                f.write('{}\t{}\t{:.6f}\t{:.6f}\t{}\n'.format(*entry))


entries = get_loanwords()
n_langs = 41
# pmi(entries, n_langs)
# pmi(entries, n_langs, per_donor=True, out_file='out/npmi_per_donor.tsv')
# implications(entries, n_langs)
# implications(entries, n_langs, per_donor=True,
#              out_file='out/implications_per_donor.tsv')
# implications_by_field(entries, n_langs)
# implications_by_field(entries, n_langs, per_donor=True,
#                       out_file='out/implications_field_per_donor.tsv')
# languages_by_loanword(entries)
loan_directions(entries)
