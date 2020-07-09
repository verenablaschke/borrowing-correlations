import matplotlib.pyplot as plt

# Haspelmath and Tadmor (2009a), p. 7
field2size = {'The physical world': 75,
              'Kinship': 85,
              'Animals': 116,
              'The body': 159,
              'Food and drink': 81,
              'Clothing and grooming': 59,
              'The house': 47,
              'Agriculture and vegetation': 74,
              'Basic actions and technology': 78,
              'Motion': 82,
              'Possession': 46,
              'Spatial relations': 75,
              'Quantity': 38,
              'Time': 57,
              'Sense perception': 49,
              'Emotions and values': 48,
              'Cognition': 51,
              'Speech and language': 41,
              'Social and political relations': 36,
              'Warfare and hunting': 40,
              'Law': 26,
              'Religion and belief': 26,
              'Modern world': 57,
              'Miscellaneous function words': 14}

# Tadmor (2009), p. 64
# In %, rounded
field2loan = {'The physical world': 20,
              'Kinship': 15,
              'Animals': 26,
              'The body': 14,
              'Food and drink': 29,
              'Clothing and grooming': 39,
              'The house': 37,
              'Agriculture and vegetation': 30,
              'Basic actions and technology': 24,
              'Motion': 17,
              'Possession': 27,
              'Spatial relations': 14,
              'Quantity': 21,
              'Time': 23,
              'Sense perception': 11,
              'Emotions and values': 20,
              'Cognition': 24,
              'Speech and language': 22,
              'Social and political relations': 31,
              'Warfare and hunting': 28,
              'Law': 34,
              'Religion and belief': 41,
              # 'Modern world': MISSING
              # 'Miscellaneous function words': MISSING
              }

keys = list(field2loan.keys())
x = [field2size[key] for key in keys]
y = [field2loan[key] for key in keys]

fig, ax = plt.subplots()
ax.scatter(x, y)

for label, x_i, y_i in zip(keys, x, y):
    ax.annotate(label, (x_i, y_i))
plt.xlabel("Number of concepts")
plt.ylabel("Percentage of loanwords")
plt.show()
