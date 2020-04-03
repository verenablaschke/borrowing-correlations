import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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


id2lang = get_id2string('./data/languages.csv')
id2param = get_id2string('./data/parameters.csv')
id2cat = get_id2string('./data/parameters.csv', val_idx=3)


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


entries = {}
with open('./data/borrowings.csv', encoding='utf8') as f:
    next(f)
    for line in f:
        cells = line.strip().split(',')
        entries[cells[1]] = Borrowing(cells[1], id2lang[cells[-1]])

with open('./data/forms.csv', encoding='utf8') as f:
    next(f)
    for line in f:
        cells = line.strip().split(',')
        try:
            entries[cells[0]].add_values(id2lang[cells[1]], id2param[cells[2]],
                                         id2cat[cells[2]])
        except KeyError:
            continue


print(entries['62'])
print(entries['36857'])
