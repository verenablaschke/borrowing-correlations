IN_FILE = '/content/gdrive/My Drive/colab_files/bootstrap.txt'
THRESHOLD = 0.45


class Implication:

    def __init__(self, x, y,
                 mean, sd, z, zn,
                 npmi_mean, npmi_sd, npmi_z, npmi_zn,
                 borrow_x, intersection):
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

    def __str__(self):
        return '{} -> {}: mean={:.2f} sd={:.2f} ({:.2f}, {:.2f}), '\
               'pmi_mean={:.2f} pmi_sd={:.2f} ({:.2f}, {:.2f}), '\
               'borrowability_x={:.2f}, intersection={:.2f}'.format(
                   self.x, self.y, self.mean, self.sd, self.z, self.zn,
                   self.npmi_mean, self.npmi_sd, self.npmi_z, self.npmi_zn,
                   self.borrow_x, self.intersection)


entries = []
with open(IN_FILE, encoding='utf8') as f:
    next(f)  # skip header
    for line in f:
        cells = line.strip().split('\t')
        if float(cells[-2]) < 3:  # intersection
            continue
        # if float(cells[4]) < THRESHOLD:
        #     continue
        if float(cells[8]) > THRESHOLD:
            entries.append(Implication(*cells[0:2], *cells[6:10], *cells[2:6], cells[14], cells[16]))
        if float(cells[12]) > THRESHOLD:
            entries.append(Implication(cells[1], cells[0], *cells[10:14], *cells[2:6], *cells[15:17]))
entries.sort(key=lambda x: (x.z, x.intersection), reverse=True)
print(len(entries), "results")
for entry in entries:
    print(entry)
