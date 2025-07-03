#
# Capitalize a column in a .csv file
#
# e.g.
# python capitalize.py input.csv output.csv 3 title

import sys, csv, collections

delim = "\t"

types = {}
errors = 0
capital_row = int(sys.argv[3])
type_of_case = sys.argv[4]

with open(sys.argv[2], 'w') as f2:
    writer = csv.writer(f2, delimiter=delim, quoting=csv.QUOTE_NONE, quotechar=chr(255), escapechar='\\')
    with open(sys.argv[1], 'r') as f1:
        reader = csv.reader(f1, delimiter=delim, quoting=csv.QUOTE_NONE, quotechar=chr(255))
        for lineno, row in enumerate(reader):
            if lineno == 0:
                writer.writerow(row)
                continue
            else:
                if type_of_case == 'title':
                    row[capital_row] = row[capital_row].title()
                elif type_of_case == 'capital':
                    row[capital_row] = row[capital_row].capital()
                writer.writerow(row)
