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

    def synonym(self, target_lang, concept):
        return self.target_lang == target_lang and self.concept == concept


def line_gen(lines):
    gen_line = next(lines)
    while True:
        response = yield gen_line
        if response:
            gen_line = response
            yield "dummy"
        else:
            gen_line = next(lines, None)


def split_line(generator, sep=','):
    line = next(generator, None)
    if line is None:
        return None
    line = line[:-1]
    if '"' in line:
        # Some entries that are on several lines instead of one because of a
        # line break in a comment.
        if line.count('"') % 2 == 1:
            while True:
                next_line = next(generator, None)
                if next_line is None:
                    break
                try:
                    int(next_line.split(sep)[0])
                    generator.send(next_line)
                    break
                except ValueError:
                    line += ' ' + next_line.strip()
        if line.count('"') == 1:
            return line.split(sep)
        cells = []
        line = line.replace('""', "'")
        for i, quote_cell in enumerate(line.split('"')):
            if i % 2 == 0:
                if quote_cell == '':
                    continue
                if quote_cell == sep:
                    cells += ['']
                    continue
                if quote_cell[-1] == sep:
                    quote_cell = quote_cell[:-1]
                if quote_cell[0] == sep:
                    quote_cell = quote_cell[1:]
                cells += quote_cell.split(sep)
            else:
                cells += [quote_cell]
        return cells
    else:
        return line.split(sep)


def get_id2string(infile, to_int=False, key_idx=0, val_idx=1, sep=','):
    id2lang = {}
    with open(infile, encoding='utf8') as f:
        generator = line_gen(f)
        cells = split_line(generator, sep=sep)
        while cells is not None:
            try:
                entry_id = cells[key_idx]
                if to_int:
                    entry_id = int(entry_id)
            except IndexError:
                print('Could not parse the following line (index {}): {}'
                      .format(key_idx, cells))
            try:
                id2lang[entry_id] = cells[val_idx]
            except IndexError:
                print('Could not parse the following line (index {}): {}'
                      .format(val_idx, cells))
            cells = split_line(generator, sep=sep)
    return id2lang


def get_loanwords(lang_file='./data/wold/languages.csv',
                  param_file='./data/wold/parameters.csv',
                  borrowing_file='./data/wold/borrowings.csv',
                  form_file='./data/wold/forms.csv',
                  discard_forms_with_inherited_counterparts=True):
    id2lang = get_id2string(lang_file)
    id2param = get_id2string(param_file)
    id2cat = get_id2string(param_file, val_idx=3)

    entries = {}
    with open(borrowing_file, encoding='utf8') as f:
        next(f)
        generator = line_gen(f)
        cells = split_line(generator)
        while cells is not None:
            entries[cells[1]] = Borrowing(cells[1], id2lang[cells[-1]])
            cells = split_line(generator)

    if discard_forms_with_inherited_counterparts:
        inherited_concepts = set()

    with open(form_file, encoding='utf8') as f:
        next(f)
        generator = line_gen(f)
        cells = split_line(generator)
        while cells is not None:
            try:
                entries[cells[0]].add_values(id2lang[cells[1]],
                                             id2param[cells[2]],
                                             id2cat[cells[2]])
            except KeyError:
                if discard_forms_with_inherited_counterparts and cells[9] and\
                        float(cells[9]) < 0.75:
                    inherited_concepts.add((id2lang[cells[1]],
                                            id2param[cells[2]]))
            cells = split_line(generator)

    print("Found {} borrowings".format(len(entries)))

    if discard_forms_with_inherited_counterparts:
        entries = {entry[0]: entry[1] for entry in entries.items()
                   if (entry[1].target_lang, entry[1].concept)
                   not in inherited_concepts}
        print("Found {} borrowings without inherited counterparts"
              .format(len(entries)))

    print(entries['36856'])
    print(entries.get('19687', 'N/A'))
    return entries


def get_concepts(param_file='./data/wold/parameters.csv'):
    concept2field = get_id2string(param_file, key_idx=1, val_idx=3)
    field2size = {}
    for concept in concept2field:
        try:
            field2size[concept2field[concept]] += 1
        except KeyError:
            field2size[concept2field[concept]] = 1
    return concept2field, field2size


def concept_to_langs(entries):
    concept2langs = {}
    for entry in entries.values():
        try:
            concept2langs[entry.concept].add(entry.target_lang)
        except KeyError:
            concept2langs[entry.concept] = {entry.target_lang}
    return concept2langs


def languages_by_loanword(entries, out_file='out/loanwords_to_languages.tsv'):
    loanwords = {}
    for entry in entries.values():
        try:
            loanwords[entry.concept].add(
                entry.src_lang + ' > ' + entry.target_lang)
        except KeyError:
            loanwords[entry.concept] = {
                entry.src_lang + ' > ' + entry.target_lang}
    loanwords = list(loanwords.items())
    loanwords.sort(key=lambda x: len(x[1]), reverse=True)
    with open(out_file, 'w', encoding='utf8') as f:
        f.write('Concept\tNumber of languages\tLanguages\n')
        for entry in loanwords:
            f.write('{}\t{}\t{}\n'.format(entry[0], len(entry[1]), entry[1]))
    return loanwords


def loan_directions(entries, out_file='out/loan_directions.tsv'):
    loanwords = {}
    for entry in entries.values():
        try:
            loanwords[entry.src_lang + ' > ' + entry.target_lang]\
                .add(entry.concept)
        except KeyError:
            loanwords[entry.src_lang + ' > ' + entry.target_lang] =\
                {entry.concept}
    loanwords = list(loanwords.items())
    loanwords.sort(key=lambda x: len(x[1]), reverse=True)
    with open(out_file, 'w', encoding='utf8') as f:
        f.write('Rank\tLanguages\tNumber of concepts\tConcepts\n')
        for rank, entry in enumerate(loanwords):
            f.write('{}\t{}\t{}\t{}\n'.format(rank + 1, entry[0],
                                              len(entry[1]), entry[1]))
    return loanwords


def pmi(entries, n_langs, min_langs=3, per_donor=False,
        duplicates_in_output=False, out_file='out/nmpi.tsv'):
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
    print(str(len(concepts)) + ' concepts')
    for i in range(len(concepts)):
        x = concepts[i]
        if duplicates_in_output:
            y_range = range(len(concepts))
        else:
            y_range = range(i + 1, len(concepts))
        for j in y_range:
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
    return npmi, borrowed


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
    return implications


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
    return implications


if __name__ == '__main__':
    entries = get_loanwords()
    n_langs = 41
    pmi(entries, n_langs)
    pmi(entries, n_langs, per_donor=True, out_file='out/npmi_per_donor.tsv')
    implications(entries, n_langs)
    implications(entries, n_langs, per_donor=True,
                 out_file='out/implications_per_donor.tsv')
    implications_by_field(entries, n_langs)
    implications_by_field(entries, n_langs, per_donor=True,
                          out_file='out/implications_field_per_donor.tsv')
    languages_by_loanword(entries)
    loan_directions(entries)
