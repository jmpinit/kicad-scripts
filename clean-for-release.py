#!/usr/bin/env python

import fire
import csv

def loadPos(filepath):
    # Ref Val Package PosX PosY Rot Side
    with open(filepath) as posFile:
        lines = posFile.readlines() 

        rows = []

        for line in lines:
            # Ignore comments
            if line.startswith('#'):
                continue

            rows += [line.split()]

        return rows

def loadCSV(filepath):
    with open(filepath, 'rb') as csvFile:
        csvReader = csv.reader(csvFile, delimiter=',', quotechar='"')
        return [row for row in csvReader]

# Takes a list of lists and returns a CSV string
def listsToCSV(header, rows):
    def quoteCommas(entry):
        if ',' in entry:
            return '"{0}"'.format(entry)
        else:
            return entry

    return '\n'.join(map(lambda r: ','.join(map(quoteCommas, r)), [header] + rows))

class ComponentInstance(object):
    def __init__(self, x=None, y=None, rot=None, side=None):
        self.x = x
        self.y = y
        self.rot = rot
        self.side = side

    def isValid(self):
        return not (self.x == None or self.y == None or self.rot == None or self.side == None)

    def __str__(self):
        return '({0}, {1}) @ {2} on {3}'.format(self.x, self.y, self.rot, self.side)

class Component(object):
    def __init__(self, attributes):
        # index = attributes[0]
        self.description = attributes[1]
        self.references = attributes[2].split()
        # quantity = attributes[3]
        self.vendor = attributes[4]
        self.mfg = attributes[5]
        self.vendorPartNumber = attributes[6]
        self.mfgPartNumber = attributes[7]

        self.instances = {}
        for ref in self.references:
            self.instances[ref] = ComponentInstance()

    def positionInstance(self, ref, x, y, rot, side):
        if not ref in self.instances:
            raise Exception()

        instance = self.instances[ref]
        instance.x = x
        instance.y = y
        instance.rot = rot
        instance.side = side

class Board(object):
    def __init__(self):
        self.components = []

    def add(self, count, component):
        if not isinstance(component, Component):
            raise Exception()

        self.components += [(count, component)]

    def findByRef(self, ref):
        return filter(lambda c: ref in c[1].references, self.components)

    def position(self, ref, x, y, rot, side):
        components = self.findByRef(ref)

        if components == None:
            raise Exception('Unknown component reference')

        for count, component in components:
            component.positionInstance(ref, x, y, rot, side)

    def cpl(self):
        header = ['Ref', 'PosX', 'PosY', 'Rot', 'Side']
        rows = []

        for (count, component) in self.components:
            for ref, instance in component.instances.iteritems():
                if not instance.isValid():
                    raise Exception('{0} is invalid: {1}'.format(ref, instance))

                rows += [[ref, str(instance.x), str(instance.y), str(instance.rot), instance.side]]

        return listsToCSV(header, rows)

    def bom(self):
        header = ['Description', 'References', 'Quantity Per PCB', 'Customer Supplied', 'Manufacturer', 'Manufacturer Part #', 'Vendor', 'Vendor Part #']
        rows = [[c.description, ' '.join(c.references), quantity, 'No', c.mfg, c.mfgPartNumber, c.vendor, c.vendorPartNumber] for (quantity, c) in self.components]

        # Sanity check
        assert len(header) == len(rows[0])

        return listsToCSV(header, rows)

def loadBoard(bomFilePath, cplFilePath):
    bomContents = loadCSV(bomFilePath)

    header = bomContents[0]
    expectedHeader = ['Component', 'Description', 'References', 'Quantity Per PCB', 'Vendor', 'Mfg', 'Vendor Part #', 'Mfg Part #']

    assert len(header) == len(expectedHeader), 'Unexpected # of columns in BOM'
    assert all(column in expectedHeader for column in header), 'Unexpected column in header'

    indexOfFirstEmpty = bomContents.index(next(row for row in bomContents[1:] if len(row) == 0))

    componentRows = bomContents[1:indexOfFirstEmpty]

    board = Board()

    for componentRow in componentRows:
        board.add(componentRow[3], Component(componentRow))

    cplContents = loadPos(cplFilePath)

    for row in cplContents:
        ref, val, package, x, y, rot, side = row
        board.position(ref, x, y, rot, side)

    return board

class FabricationExporter(object):
    def cpl(self, bomFilePath, cplFilePath):
        print loadBoard(bomFilePath, cplFilePath).cpl()

    def bom(self, bomFilePath, cplFilePath):
        print loadBoard(bomFilePath, cplFilePath).bom()

if __name__ == '__main__':
    fire.Fire(FabricationExporter)
