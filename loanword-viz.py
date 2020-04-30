# python loanword-viz.py && dot -Tsvg out\loanwords.dot -o out\loanwords-60.svg && out\loanwords-60.svg
# python loanword-viz.py && dot -Tsvg out\loanwords-counterpartless.dot -o out\loanwords-counterpartless-70.svg && out\loanwords-counterpartless-70.svg
from loanwords import *

### CONFIG ###
NPMI_THRESHOLD = 0.7
DIRECTION_RATIO_THRESHOLD = 1.5
ONLY_WITHOUT_INHERITED_COUNTERPARTS = True
##############

if ONLY_WITHOUT_INHERITED_COUNTERPARTS:
    DOT_FILE = 'out/loanwords-counterpartless.dot'
else:
    DOT_FILE = 'out/loanwords.dot'

entries = get_loanwords(discard_forms_with_inherited_counterparts=ONLY_WITHOUT_INHERITED_COUNTERPARTS)
n_langs = 41
pmi = pmi(entries, n_langs, per_donor=True, out_file=None)

concepts = set()
for i, entry in enumerate(pmi):
    if entry[2] < NPMI_THRESHOLD:
        print("Found {} concept pairs with a normalized PMI >= {}"
              .format(i, NPMI_THRESHOLD))
        break
    concepts.add(entry[0])
    concepts.add(entry[1])

concept2field = get_id2string('./data/parameters.csv', key_idx=1, val_idx=3)
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
    f.write('\t}\n\n\tsubgraph undir {\n\t\tedge [dir=none];\n')
    for entry in undirected:
        f.write('\t\t"{}" -> "{}";\n'.format(*entry))
    f.write('\t}\n}\n')
