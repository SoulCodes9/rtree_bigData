from tqdm import tqdm
import sys
import math
import time
from rtree_con import RTree
import pickle


def main():
    data = list()
    startWhole = time.time()
    # Datapoints
    with open("150KData.txt", 'r') as dataP:
        for d in dataP.readlines():
            d = d.split()
            data.append({'id': int(d[0]),
                        'x': int(d[1]),
                         'y': int(d[2])
                         })
    # Query
    query = list()

    with open('200rq.txt', 'r') as queries:
        for q in queries.readlines():
            q = q.split()
            query.append({"id": int(q[0]), "x1": int(q[1]), "x2": int(
                q[2]), "y1": int(q[3]), "y2": int(q[4])})

    startSS = time.time()

    result = []
    print('\n ### Sequential Based Scan')
    ##### Sequential Based Scan ####
    for q in tqdm(query):
        count = 0
        for p in data:
            if(q['x1'] <= p['x'] <= q['x2'] and q['y1'] <= p['y'] <= q['y2']):
                count += 1
        result.append(count)

    # Write Sequential Scan results to a text file\
    # with open('SeqS-Results.txt', 'w') as f:
    #     for l in result:
    #         f.write(str(l))
    #         f.write('\n')

    print(result)
    #et = time.time()
    print("The time taken for the sequential scan is",
          round((time.time() - startSS), 3), "seconds \n")

    startRT = time.time()
    rtree = RTree()

    print("Building the R-Tree: ")
    for point in tqdm(data):  # insert data points from the root one by one
        rtree.insert(rtree.root, point)

    print('The RTree took', round(
        time.time() - startRT, 2), 'seconds to build. \n')

    # Store the constructed RTree in a pickle file, used for testing the Range Query as
    # we would of had to rebuild the tree everytime.
    # pickle.dump(rtree, file=open('rtree.pickle', 'wb'))
    #rtree = pickle.load(open('rtree.pickle', 'rb'))

    res1 = []

    print('### R-Tree based scan')
    for q in tqdm(query):
        res1.append(rtree.RQ(rtree.root, q))
    # Write Sequential Scan results to a text file\
    # with open('RTree-Results.txt', 'w') as f:
    #     for l in res1:
    #         f.write(str(l))
    #         f.write('\n')

    print(res1)
    start1 = time.time()
    # count = 0
    # for i in range(len(result)):
    #     if res1[i] == result[i]:
    #         count += 1

    print("The time taken for the RTree scan is",
          round((time.time() - start1), 6), "seconds \n")

    print('The time taken for the entire file to run is',
          round(time.time() - startWhole, 0))


if __name__ == "__main__":
    main()
