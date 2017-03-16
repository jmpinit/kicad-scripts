#!/usr/bin/env python

import fire
import re

from colorama import init, Fore

from difflib import SequenceMatcher

# thx http://stackoverflow.com/a/17388505
def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

class SchematicParser(object):
    def __init__(self):
        self.initialized = False
        self.done = False
        self.currentObjectType = None
        self.currentLabel = None

        self.labels = []
        self.libs = []

    def parseLine(self, line):
        if not self.initialized:
            assert line == 'EESchema Schematic File Version 2'
            self.initialized = True

        if self.done:
            raise Exception('Unexpected input, parsing already done')

        if self.currentObjectType == None:
            if line.startswith('LIBS:'):
                self.libs += [line.split(':')[1]]
            elif line.startswith('EELAYER'):
                # TODO figure out meaning
                pass
            elif line.startswith('Text'):
                textArgs = line.split()[1:]

                # Only support GLabel and Notes for now
                assert textArgs[0] == 'GLabel' or textArgs[0] == 'Notes'
                self.currentObjectType = textArgs[0]
                
                # TODO what are a, b, c, and d?
                x = textArgs[0]
                y = textArgs[1]
                a = textArgs[2]
                b = textArgs[3]
                type = textArgs[4]
                d = textArgs[5]

                self.currentLabel = {
                    'x': x,
                    'y': y,
                    'type': type
                }
            elif line.startswith('$'):
                self.currentObjectType = line[1:].split()[0]
        else:
            if self.currentObjectType == 'GLabel':
                self.currentLabel['text'] = line
                self.labels += [self.currentLabel]
                self.currentLabel = None
                self.currentObjectType = None
            elif self.currentObjectType == 'Notes':
                # TODO
                self.currentObjectType = None
            elif self.currentObjectType == 'Descr':
                if line == '$EndDescr':
                    self.currentObjectType = None
            elif self.currentObjectType == 'Sheet':
                # TODO
                if line == '$EndSheet':
                    self.currentObjectType = None
            elif self.currentObjectType == 'Comp':
                if line == '$EndComp':
                    self.currentObjectType = None
                else:
                    fieldType = line[0]
                    args = line.split()[1:]

                    if fieldType == 'L':
                        value, reference = args
                    elif fieldType == 'U':
                        # TODO what are a and b?
                        a, b, timestamp = args
                    elif fieldType == 'P':
                        x, y = args
                    elif fieldType == 'F':
                        if len(args) == 9:
                            # Built-in
                            index, value, a, b, c, d, e, f, g = args
                        elif len(args) == 10:
                            # Custom
                            index, value, a, b, c, d, e, f, g, name = args
                    elif re.match('(-?)|(\d+)', fieldType):
                        # TODO partly seems to be position, but what else?
                        pass
                    else:
                        raise Exception('Unknown field type "{0}"'.format(fieldType)) 
            elif self.currentObjectType == 'EndSCHEMATC':
                # Aaag, why is schematic mis-spelled and in all-caps???
                self.done = True
            else:
                raise Exception('Unknown object type "{0}"'.format(self.currentObjectType))

def lint(filename):
    # Parse schematic
    parser = SchematicParser()
    with open(filename, 'r') as schematic:
        for line in schematic.readlines():
            parser.parseLine(line.strip());

    # Pretty-print warnings
    init()

    for label1 in parser.labels:
        for label2 in parser.labels:
            labelText1 = label1['text']
            labelText2 = label2['text']

            if not labelText1 == labelText2:
                if labelText2.endswith(labelText1):
                    prefix = labelText2[:labelText2.index(labelText1)]
                    print(Fore.YELLOW + 'Warning:' + Fore.RESET + ' Maybe missing prefix "{0}" on "{1}"'.format(prefix, labelText1))

if __name__ == '__main__':
    fire.Fire(lint)
