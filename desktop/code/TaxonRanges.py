import csv
import os
import shutil

if len(sys.argv) < 2:
    print("Usage: python " + sys.argv[0] + " input_file")
    exit(0)

ranks = ["kingdom","phylum","class","order","family","genus","species"]

with open("processed.csv"), 'w', newline='', encoding="utf8") as outfile:
    writer = csv.writer(outfile, delimiter=',')

    with open(sys.argv[1], newline='') as taxonlist:
        taxonreader = csv.reader(taxonlist, delimiter=',')
        headings = next(taxonreader)

        itaxonid = 0
        ikingdom = 1
        irank = 8
        iconcatenated = 9
        ileft = 10

        headings = (["taxonConceptID"] + ranks + ["concatenated","rank","left"])
        writer.writerow(headings)
        taxa = []

        for row in taxonreader:
            rank_index = 0
            newrow = [''] * len(headings)
            for r in range(len(ranks)):
                if len(row[ikingdom + r]) > 0:
                    if r == len(ranks) - 1 or len(row[ikingdom + r + 1]) == 0:
                        newrow[itaxonid] = row[itaxonid]
                    newrow[ikingdom + r] = row[ikingdom + r]
                    newrow[irank] = ranks[r]
                    newrow[iconcatenated] = newrow[iconcatenated] + newrow[ikingdom + r]
                    if newrow[iconcatenated] not in taxa:
                        taxa.append(newrow[iconcatenated])
                        print(newrow[iconcatenated])
                        writer.writerow(newrow)

