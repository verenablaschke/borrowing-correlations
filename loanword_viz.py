# python loanword_viz.py && dot -Tsvg out\loanwords-60.dot -o out\loanwords-60.svg && out\loanwords-60.svg
# python loanword_viz.py && dot -Tsvg out\loanwords-counterpartless-70.dot -o out\loanwords-counterpartless-70.svg && out\loanwords-counterpartless-70.svg
from loanwords import *

### CONFIG ###
NPMI_THRESHOLD = 75  # in %
DIRECTION_RATIO_THRESHOLD = 1.5
ONLY_WITHOUT_INHERITED_COUNTERPARTS = True
##############

DOT_FILE = 'out/loanwords'
if ONLY_WITHOUT_INHERITED_COUNTERPARTS:
    DOT_FILE += '-counterpartless'
DOT_FILE += '-' + str(NPMI_THRESHOLD) + '.dot'

NPMI_THRESHOLD /= 100

entries = get_loanwords(discard_forms_with_inherited_counterparts=ONLY_WITHOUT_INHERITED_COUNTERPARTS)
n_langs = 41
pmi, borrowed = pmi(entries, n_langs, per_donor=True, out_file=None)

concepts = set()
for i, entry in enumerate(pmi):
    if entry[2] < NPMI_THRESHOLD:
        print("Found {} concept pairs with a normalized PMI >= {}"
              .format(i, NPMI_THRESHOLD))
        break
    concepts.add(entry[0])
    concepts.add(entry[1])

n_langs2concepts = {}
max_langs = -1
min_langs = 1000
for entry in borrowed.items():
    if entry[0] not in concepts:
        continue
    n_langs_for_concept = len(entry[1])
    if n_langs_for_concept > max_langs:
        max_langs = n_langs_for_concept
    if n_langs_for_concept < min_langs:
        min_langs = n_langs_for_concept
    try:
        n_langs2concepts[n_langs_for_concept].append(entry[0])
    except KeyError:
        n_langs2concepts[n_langs_for_concept] = [entry[0]]
print(min_langs, max_langs)
for entry in n_langs2concepts.items():
    print(entry)

concept2field = get_id2string('./data/wold/parameters.csv', key_idx=1, val_idx=3)
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

implications = implications(entries, n_langs, per_donor=True, out_file=None)
implications = {(entry[0], entry[1]): (entry[2]) for entry in implications}

with open(DOT_FILE, 'w', encoding='utf8') as f:
    f.write('digraph loanwords {\n\tnode [style = filled];\n')

    for i in reversed(range(min_langs, max_langs + 1)):
        f.write('{} [pos="0,{}!"];\n'.format(i, max_langs - i))

    for concept in concepts:
        f.write('\t"{}" [color={}];\n'.format(concept.replace(' (', '\\n('),
                                              field2colour[concept2field[concept]]))
    f.write('\n\tsubgraph dir {\n')
    undirected = []
    for entry in pmi:
        if entry[2] < NPMI_THRESHOLD:
            break
        directionality = implications[(entry[0], entry[1])] / implications[(entry[1], entry[0])]
        e0 = entry[0].replace(' (', '\\n(')
        e1 = entry[1].replace(' (', '\\n(')
        if directionality > DIRECTION_RATIO_THRESHOLD:
            f.write('\t\t"{}" -> "{}";\n'.format(e0, e1))
        elif 1 / DIRECTION_RATIO_THRESHOLD > directionality:
            f.write('\t\t"{}" -> "{}";\n'.format(e1, e0))
        else:
            undirected.append((e0, e1))
    f.write('\t}\n\n\tsubgraph undir {\n\t\tedge [dir=none];\n\t\t')

    # Number of languages per loaned concept
    f.write(' -> '.join([str(i) for i in reversed(range(min_langs, max_langs + 1))]))
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
                f.write('"{}";'.format(concept.replace(' (', '\\n(')))
        f.write('}\n')
    f.write('}\n')
