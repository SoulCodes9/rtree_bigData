from tqdm import tqdm
import sys
import math
import time

B = 4  # Maximum allowed child nodes.


def main():
    points = []
    # https://www.w3schools.com/python/ref_file_readlines.asp
    with open("150KData.txt", 'r') as dataset:
        for data in dataset.readlines():
            data = data.split()  # https://www.w3schools.com/python/ref_string_split.asp
            points.append({  # https://www.w3schools.com/python/ref_list_append.asp
                'id': int(data[0]),
                'x': int(data[1]),
                'y': int(data[2])
            })
        # https://stackoverflow.com/questions/17153779/how-can-i-print-variable-and-string-on-same-line-in-python

    # build R-Tree


# R-Tree construction begins here

class Node(object):
    def __init__(self):
        self.id = 0

        # Internal Node
        self.child_node = list()

        # Leaf Nodes, where our data goes
        self.data_points = list()
        self.parent = None
        self.mbr = {
            'x1': -1,
            'y1': -1,
            'x2': -1,
            'y2': -1,
        }

    def perimeter(self):
        perim = (self.mbr['x2'] - self.mbr['x1']) + \
            (self.mbr['y2'] - self.mbr['y1'])
        return perim

    def leaf(self):  # check if node is a leaf node
        if len(self.child_node) == 0:
            return True
        else:
            return False

    def root(self):  # check if node is a root node
        if self.parent == None:
            return True
        else:
            return False

    def overflow(self):  # Check if Leaf has reached maximum capacity
        if self.leaf() == True:  # If node is a leaf
            if len(self.data_points) > B:  # B is the maximum capacity of the data points
                return True
            else:
                return False
        else:
            if len(self.child_node) > B:
                return True
            else:
                return False


class RTree(object):
    def __init__(self):
        self.root = Node()

    # Range-Query function
    def RQ(self, u, q):
        next = self.root
        count = 0
        if u.leaf():  # if node is a leaf
            for p in u.data_points:  # Check every data point within node
                if self.is_covered(p, q):  # If datapoint is within query range
                    count = count + 1  # Record it
        else:
            for c in u.child_node:  # Check all child nodes within the node
                if self.overlap(c.mbr, q):  # If the child nodes MBR overlaps with the query
                    next = c  # Record the child node
                    # Recursively traverse from that chilkd node
                    count += self.RQ(next, q)
        return count

    # Overlapping function, used for checking if current nodes MBR overlaps with the query range for efficient traversal

    def overlap(self, mbr1, mbr2):
        if (mbr1['x1'] >= mbr2['x2']) or (mbr1['x2'] <= mbr2['x1']) or (mbr1['y2'] <= mbr2['y1']) or (mbr1['y1'] >= mbr2['y2']):
            return False
        else:
            return True

    def is_covered(self, point, query):
        x1, x2, y1, y2 = query['x1'], query['x2'], query['y1'], query['y2']
        if x1 <= point['x'] <= x2 and y1 <= point['y'] <= y2:
            return True
        else:
            return False

    # Insert function, used for inserting the DataPoints into the leaf nodes
    def insert(self, u, p):
        if u.leaf():
            self.add_data_p(u, p)  # Add data_points into the leaf node
            if u.overflow():
                # Handle overflow by splitting the node into 2
                self.handle_overflow(u)
        else:
            v = self.choose_subtree(u, p)  # Select optimal subtree
            self.insert(v, p)  # Recursively check subtree
            self.update_mbr(v)  # Update MBRs size

    # Handling the overflowing
    def handle_overflow(self, node):
        u1, u2 = self.split(node)  # u1, u2 = split nodes.

        if node.root() == True:
            new_root = Node()
            # Insert the child nodes u1,u2 into the new root node and update
            # the MBR
            self.add_child(new_root, u1)
            self.add_child(new_root, u2)
            self.root = new_root
            self.update_mbr(new_root)
        else:
            w = node.parent
            # remove the current node from the child node and add the splitted children nodes
            w.child_node.remove(node)

            self.add_child(w, u1)
            self.add_child(w, u2)

            if w.overflow():
                self.handle_overflow(w)  # Recursively check the parent node

    # Returns the increase of the perimeter of an MBR after inserting the data points
    def peri_increase(self, node, p):
        original_mbr = node.mbr
        x1, x2, y1, y2 = original_mbr['x1'], original_mbr['x2'], original_mbr['y1'], original_mbr['y2']
        return (max([x1, x2, p['x']]) - min([x1, x2, p['x']]) +
                max([y1, y2, p['y']]) - min([y1, y2, p['y']])) - node.perimeter()

    # Choose optimal subtree for splitting
    def choose_subtree(self, node, p):
        if node.leaf():
            return node
        else:
            min_increase = sys.maxsize
            best_c = None
            for c in node.child_node:
                if min_increase > self.peri_increase(c, p):
                    min_increase = self.peri_increase(c, p)
                    best_c = c
            return best_c

    def split(self, u):
        # Split u into s1 and s2
        best_s1 = Node()
        best_s2 = Node()
        best_perim = sys.maxsize
        if u.leaf():
            m = len(u.data_points)
            # Sort datapoints based off their x and y values
            divides = [sorted(u.data_points, key=lambda data_point: data_point['x']),
                       sorted(u.data_points, key=lambda data_point: data_point['y'])]

            for d in divides:
                # Check the combinations to find a near-optimal one
                for i in range(math.ceil(0.4 * B), m - math.ceil(0.4 * B) + 1):
                    s1 = Node()
                    s1.data_points = d[0: i]
                    self.update_mbr(s1)
                    s2 = Node()
                    s2.data_points = d[i: len(d)]
                    self.update_mbr(s2)
                    # Calculate perimeter sum of s1 and s2's mbrs, if it is the best
                    # split, we set the best s1 and s2 to that MBR
                    if best_perim > s1.perimeter() + s2.perimeter():
                        best_perim = s1.perimeter() + s2.perimeter()
                        best_s1 = s1
                        best_s2 = s2
        else:
            m = len(u.child_node)
            # sorting based on MBRs dimnesions
            divides = [sorted(u.child_node, key=lambda child_n: child_n.mbr['x1']),
                       sorted(u.child_node,
                              key=lambda child_n: child_n.mbr['x2']),
                       sorted(u.child_node,
                              key=lambda child_n: child_n.mbr['y1']),
                       sorted(u.child_node, key=lambda child_n: child_n.mbr['y2'])]
            for d in divides:
                for i in range(math.ceil(0.4 * B), m - math.ceil(0.4 * B) + 1):
                    s1 = Node()
                    s1.child_node = d[0: i]
                    self.update_mbr(s1)
                    s2 = Node()
                    s2.child_node = d[i: len(d)]
                    self.update_mbr(s2)
                    if best_perim > s1.perimeter() + s2.perimeter():
                        best_perim = s1.perimeter() + s2.perimeter()
                        best_s1 = s1
                        best_s2 = s2

        # Return the best split found
        for ch in best_s1.child_node:
            ch.parent = best_s1
        for ch in best_s2.child_node:
            ch.parent = best_s2

        return best_s1, best_s2

    # Adding the child into a node
    def add_child(self, node, child):
        node.child_node.append(child)
        child.parent = node

        if child.mbr['x1'] < node.mbr['x1']:
            node.mbr['x1'] = child.mbr['x1']
        if child.mbr['x2'] > node.mbr['x2']:
            node.mbr['x2'] = child.mbr['x2']
        if child.mbr['y1'] < node.mbr['y1']:
            node.mbr['y1'] = child.mbr['y1']
        if child.mbr['y2'] > node.mbr['y2']:
            node.mbr['y2'] = child.mbr['y2']

    # Adding data_point into a leaf node.
    def add_data_p(self, node, data_point):
        node.data_points.append(data_point)
        if data_point['x'] < node.mbr['x1']:
            node.mbr['x1'] = data_point['x']
        if data_point['x'] > node.mbr['x2']:
            node.mbr['x2'] = data_point['x']
        if data_point['y'] < node.mbr['y1']:
            node.mbr['y1'] = data_point['y']
        if data_point['y'] > node.mbr['y2']:
            node.mbr['y2'] = data_point['y']

    # Update MBR of a node after inserting.
    def update_mbr(self, node):
        x_list = []
        y_list = []

        if node.leaf():
            x_list = [point['x'] for point in node.data_points]
            y_list = [point['y'] for point in node.data_points]
        else:
            x_list = [child.mbr['x1'] for child in node.child_node] + \
                [child.mbr['x2'] for child in node.child_node]
            y_list = [child.mbr['y1'] for child in node.child_node] + \
                [child.mbr['y2'] for child in node.child_node]
        # Calculate the new MBR based on the minimum and maximum values of the minimum v
        # x1 and y1 values within the lists and the maximum x2 and y2 values of the list.
        new_mbr = {
            'x1': min(x_list),
            'x2': max(x_list),
            'y1': min(y_list),
            'y2': max(y_list)
        }
        node.mbr = new_mbr


if __name__ == '__main__':
    main()
