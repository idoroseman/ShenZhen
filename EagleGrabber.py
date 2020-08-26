import os
import xml.etree.ElementTree as ET

lib_path = os.path.expanduser('~/Library/Application Support/Eagle/lbr/')

class EagleGrabber():
    def __init__(self):
        libs = []
        with open(os.path.join(lib_path,'libraries.rc')) as fin:
            lines = fin.readlines()
            for line in lines:
                try:
                    q,p = line.split(" = ")
                    if q.startswith("Lbr") and q.endswith("path"):
                        libs.append(p.strip()[1:-1])
                except:
                    pass

        self.packages = {}
        self.symbols = {}

        for xmlfile in libs:
            print(xmlfile)
            tree = ET.parse(xmlfile)
            root = tree.getroot()
            for package in root.find('./drawing/library/packages'):
                name = package.attrib['name']
                # urn = package.attrib['urn']
                if name not in self.packages:
                    self.packages[name] = []
                found = False
                for p in self.packages[name]:
                    if ET.tostring(p) == ET.tostring(package):
                        found = True
                if not found:
                  self.packages[name].append(package)

            for symbol in root.find('./drawing/library/symbols'):
                name = symbol.attrib['name']
                if name not in self.symbols:
                    self.symbols[name] = symbol

    def symbol_as_string(self, symbol):
        return ET.tostring(self.symbols[symbol]).decode("utf-8") if symbol in self.symbols else ""

    def package_as_string(self, package):
        return ET.tostring(self.packages[package][0]).decode("utf-8") if package in self.packages else ""

    def save_to_file(self, filename):
        root = ET.Element("eagle")
        root.attrib['version']="9.4.0"
        drawing = ET.SubElement(root, 'drawing')
        lib = ET.SubElement(drawing, 'library')
        packs = ET.SubElement(lib, 'packages')
        for footprint in sorted(self.packages, key=lambda item: len(self.packages[item])):
            packs.append(self.packages[footprint][0])
        symbols = ET.SubElement(lib, 'symbols')
        for s in self.symbols:
            symbols.append(self.symbols[s])
        tree = ET.ElementTree(root)
        tree.write('lib/'+filename)

