# Correlating borrowing events across concepts to derive a data-driven source of evidence for loanword etymologies
(Verena Blaschke & Johannes Dellert)

Given that a target language A borrowed a word for concept C from a donor language B, which other words did A probably borrow from B?

Talk given at the *Model and evidence in quantitative comparative linguistics* workshop at the 43rd annual conference of the German Linguistic Society (DGfS) (Feb 26, 2021). \[[Abstract](https://www.linguistik.uni-freiburg.de/dgfs-jahrestagung-2021/programm/arbeitsgruppen-programm#page=268)\] \[Slides to come.\]

## Running the code

First, generate the bootstrap sample:
```
python bootstrap.py
```

To generate the list of concept pairs passing given NPMI and implication strength thresholds (and to generate graphics visualizing grid-searching good thresholds), run:
```
python inspect_bootstrap_data.py
```

Create the graph that shows pairs of loanwords that tend to be borrowed together:
```
python implication_graph.py
dot -Tsvg out\loanwords-80-60.dot -o out\loanwords-80-60.svg
```
(80% and 60% are the implication strength and NPMI thresholds, respectively.
Change the configuration section within the Python script to change the thresholds.)


Other scripts:
- `field_size_viz.py` visualizes the loanword ratio and number of entries by semantic field
- `loanwords.py` contains mostly methods called by the other scripts. Running this file produces some files containing an overview of the NPMI values and implication scores in the data.
- `semantic_net.py` is called by other scripts to calculate the semantic distance between two concepts.
- `singleton_implication_viz.py` visualizes the number of concept pairs passing the NPMI and implication strength thresholds compared to all other concepts by borrowability.
