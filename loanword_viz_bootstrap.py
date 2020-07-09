# dot -Tsvg out\loanwords-81-50.dot -o out\loanwords-81-50.svg && out\loanwords-81-50.svg
from loanwords import *
from inspect_bootstrap_data import *

### CONFIG ###
NPMI_THRESHOLD = 50  # in %
IMPL_THRESHOLD = 81  # in %
DIRECTION_RATIO_THRESHOLD = 1.5
N_LANG_THRESHOLD = 3
##############

DOT_FILE = 'out/loanwords-' + str(IMPL_THRESHOLD) + '-' + str(NPMI_THRESHOLD) + '.dot'

NPMI_THRESHOLD /= 100
IMPL_THRESHOLD /= 100

entries_filtered = prefilter(axis="IMPL", threshold_npmi=IMPL_THRESHOLD,
                    threshold_impl=NPMI_THRESHOLD,
                    threshold_intersection=N_LANG_THRESHOLD,
                    outfile=None, implication_direction=True)
for entry in entries_filtered:
    print(entry.__str__())
entries_all = prefilter(axis="IMPL", threshold_npmi=-1,
                    threshold_impl=-1,
                    threshold_intersection=N_LANG_THRESHOLD,
                    outfile=None)
concept2field = get_id2string('./data/wold/parameters.csv', key_idx=1,
                              val_idx=3)

field2idx = {'The physical world': 0,
             'Kinship': 1,
             'Animals': 2,
             'The body': 3,

             'Food and drink': 4,
             'Clothing and grooming': 5,
             'The house': 6,
             'Agriculture and vegetation': 7,
             'Basic actions and technology': 8,

             'Motion': 9,
             'Possession': 10,
             'Spatial relations': 11,
             'Quantity': 12,
             'Time': 13,

             'Sense perception': 14,
             'Emotions and values': 15,
             'Cognition': 16,
             'Speech and language': 17,

             'Social and political relations': 18,
             'Warfare and hunting': 19,
             'Law': 20,
             'Religion and belief': 21,
             'Modern world': 22,
             'Miscellaneous function words': 23}
field2colour = {'The physical world': 'indianred',
                'Kinship': 'brown1',
                'Animals': 'coral2',
                'The body': 'sienna3',

                'Food and drink': 'orange',
                'Clothing and grooming': 'lightsalmon',
                'The house': 'goldenrod',
                'Agriculture and vegetation': 'gold',
                'Basic actions and technology': 'khaki',

                'Motion': 'olive',
                'Possession': 'yellowgreen',
                'Spatial relations': 'mediumseagreen',
                'Quantity': 'springgreen',
                'Time': 'olivedrab',

                'Sense perception': 'lightseagreen',
                'Emotions and values': 'aqua',
                'Cognition': 'deepskyblue',
                'Speech and language': 'steelblue',

                'Social and political relations': 'mediumorchid',
                'Warfare and hunting': 'fuchsia',
                'Law': 'plum',
                'Religion and belief': 'lightpink',
                'Modern world': 'hotpink',
                'Miscellaneous function words': 'mediumpurple'}
concept_replacements = {'male(1)': 'male\\n(human)',
                        'male(2)': 'male\\n(animal)',
                        'female(1)': 'female\\n(human)',
                        'female(2)': 'female\\n(animal)',
                        'to burn(1)': 'burn\\n(tr)',
                        'to burn(2)': 'burn\\n(intr)',
                        'to smell(1)': 'smell\\n(intr)',
                        'to smell(2)': 'smell\\n(tr)',
                        'the child(1)': 'the child\\n(young person)',
                        'the child(2)': 'the child\\n(daughter/son)',
                        'light(1)': 'light\\n(not heavy)',
                        'light(2)': 'light\\n(not dark)',
                        'rough(1)': 'rough\\n(uneven)',
                        'rough(2)': 'rough\\n(e.g. sea)',
                        'the day(1)': 'the day\\n(not night)',
                        'the day(2)': 'the day\\n(24 hrs)',
                        'to call(1)': 'to call\\n(summon)',
                        'to call(2)': 'to call\\n(name)',
                        'right(1)': 'right\\n(not left)',
                        'right(2)': 'right\\n(correct)',
                        'to ask(1)': 'to ask\\n(inquire)',
                        'to ask(2)': 'to ask\\n(request)',
                        'the mortar(1)': 'the mortar\\n(bowl)',
                        'the mortar(2)': 'the mortar\\n(paste)',
                        'the spring(2)': 'the spring\\n(season)',
                        'the needle(1)': 'the needle\\n(sewing)',
                        'the needle(2)': 'the needle\\n(tree)',
                        'the end(1)': 'the end\\n(spatial)',
                        'the end(2)': 'the end\\n(temporal)',
                        'to think(1)': 'to think\\n(reflect)',
                        'to think(2)': 'to think\\n(opinion)',
                        'the knife(1)': 'the knife\\n(cutlery)',
                        'the knife(2)': 'the knife\\n(preparing food)',
                        'the fork(2)/pitchfork': 'the fork\\n(pitchfork)'
                        }

concepts = set()
for i, entry in enumerate(entries_filtered):
    concepts.add(entry.x)

n_langs2concepts = {}
max_langs = -1
min_langs = 1000
for entry in entries_all:
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
for entry in n_langs2concepts.items():
    print(entry)


def clean_up_concept(concept):
    try:
        return concept_replacements[concept]
    except KeyError:
        return concept.replace(' (', '\\n(').replace(' or ', '\\nor ') \
                      .replace(' of ', '\\nof ').replace(' on ', '\\non ') \
                      .replace('/', '/\\n').replace("'s ", "'s\\n") \
                      .replace(' under ', '\\nunder ')


with open(DOT_FILE, 'w', encoding='utf8') as f:
    f.write('digraph loanwords {\n\tnode [style = filled];\n')

    for i in reversed(range(min_langs, max_langs + 1)):
        f.write('{} [pos="0,{}!"];\n'.format(i, max_langs - i))

    for concept in concepts:
        f.write('\t"{}" [color={}];\n'.format(clean_up_concept(concept),
                            field2colour[concept2field[concept]]))

    for concept_set in n_langs2concepts.values():
        for concept in concept_set:
            if concept in concepts:
                continue
            f.write('\t"{}" [color={}];\n'
                    .format(clean_up_concept(concept),
                            field2colour[concept2field[concept]]))

    f.write('\n\tsubgraph dir {\n')
    undirected = []
    for entry in entries_filtered:
        direction = entry.direction
        e0 = clean_up_concept(entry.x)
        e1 = clean_up_concept(entry.y)
        if direction == '>':
            f.write('\t\t"{}" -> "{}";\n'.format(e0, e1))
            print(entry.x, '>', entry.y)
        elif direction == '<':
            f.write('\t\t"{}" -> "{}";\n'.format(e1, e0))
            print(entry.y, '>', entry.x)
        else:
            undirected.append((e0, e1))
            print(entry.x, '<>', entry.y)
    f.write('\t}\n\n\tsubgraph undir {\n\t\tedge [dir=none];\n\t\t')

    # Number of languages per loaned concept
    f.write(' -> '.join([str(i) for i in reversed(range(min_langs,
                                                        max_langs + 1))]))
    f.write(';\n')

    # Concept pairs without directionality
    for entry in undirected:
        f.write('\t\t"{}" -> "{}";\n'.format(*entry))
    f.write('\t}\n')

    # Sort by borrowability
    for i in reversed(range(min_langs, max_langs + 1)):
        f.write('\t{{rank = same; {}; '.format(i))
        if i in n_langs2concepts:
            for concept in n_langs2concepts[i]:
                f.write('"{}";'.format(clean_up_concept(concept)))
        f.write('}\n')
    f.write('}\n')

print("Wrote output to", DOT_FILE)
