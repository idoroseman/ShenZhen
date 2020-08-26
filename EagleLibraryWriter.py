import json
import re

class EagleLib():
    package_ignore = ['0201', '0402', '0603']

    def __init__(self, name, settings, eagle_libs):
        self.name = name.replace(":","")
        self.settings = settings
        self.eagle_libs = eagle_libs
        self.prefix = settings['prefix'] if 'prefix' in settings else "U"
        self.unknowns = 0
        with open('layers.json') as fin:
            self.layers = json.load(fin)
        self.items = {}
        self.packages = {}
        self.symbols = []
        self.dictionary = [
            ("\uff08", "("),
            ("\uff09", ")"),
            ("\uff0c", ","),

            ('公制', 'Metric'),
            ('宽型端子', 'Terminal Type'),
            ('凹面端子', 'Concave Terminal'),
            ('长边端子', 'Long Terminal Lead'),
            ('型', 'type'),
            ('币形', 'Coin Shape'),
            ('反侧', 'Opposite side'),
            ('同侧', 'Same Side'),
            ('径向', 'Radial'),
            ('轴向', 'Axial'),
            ('管状', 'Tubular'),
            ('凸面', 'Convex'),
            ('凹面', 'Concave'),
            ('引线', 'Lead'),
            ('圆片式', 'Disc Type'),
            ('插件', 'Plugin'),
            ('直插', 'Inline'),
            ('芯片', 'Chip'),
            ('模块', ' Module'),
            ('祼焊盘', 'Bare Pad'),
            ('长引线', 'Long Lead'),
            ('扁平引线', 'Flat Lead'),
            ('无引线', 'Without Lead'),
            ('圆形', 'round'),
            ('方形', 'square'),
            ("细", "fine"),
            ('扁平', 'flat'),
            ('裸露焊盘', ' Exposed Pad'),
            ('隔离片', 'Spacer'),
            ('非标准型', 'Non Standard'),
            ('非标准', 'Non Standard'),
            ('盒','Box'),
            ('形', 'Shape')

        ]
    #--------------------------------------------------------------------------
    def translate(self, term):
        for chn, eng in self.dictionary:
            term = term.replace(chn, eng)
        return term

    #--------------------------------------------------------------------------
    def add_item(self, item):
        item['manufacturer'] = item['manufacturer'].replace("&","_")
        item['mpn'] = item['mpn'].replace("&","_")

        if 'symbol' in item and item['symbol'] not in self.symbols:
            self.symbols.append(item['symbol'])

        if 'package' in item:
            item['package'] = self.translate(item['package']).replace(" ","-").replace("\"","")

            # p = item['package'].split("(")
            p = re.split(',|\(', item['package'])
            if len(p)>1:
                item['_package'] = item['package']
                item['package'] = p[0]
            if item['package'].upper().startswith("THROUGH-HOLE，P="):
                item['package'] = item['package'].replace("Through Hole，P=","PTH-").replace("THROUGH-HOLE，P=",'PTH-')

            # this should be in preprocess
            if self.prefix is not None and item['package'].isnumeric() and len(item['package']) == 4:
                item['package'] = self.prefix + item['package']
            # ignore no package
            if item['package'] == "":
                return
            # ignore small packages
            if item['package'] in self.package_ignore:
                return

            # check if in packages list
            if item['package'].upper() not in self.packages:
                self.packages[item['package'].upper()] = {}

        if item['value'] == "":
            self.unknowns += 1
            item['value'] = "unkown-%03i" % self.unknowns

        if item['value'].upper() not in self.items:
            self.items[item['value'].upper()] = []

        duplicate = False
        for i in self.items[item['value'].upper()]:
            if (i['manufacturer']+'-'+i['mpn']).upper() == (item['manufacturer']+'-'+item['mpn']).upper():
                print("duplicate part")
                duplicate = True
        if not duplicate:
            self.items[item['value'].upper()].append(item)

    # --------------------------------------------------------------------------
    def save_to_file(self):
        with open("lib/"+self.name+'.lbr', 'w') as fout:
            fout.write('<?xml version="1.0" encoding="utf-8"?>\n')
            fout.write('<!DOCTYPE eagle SYSTEM "eagle.dtd">\n')
            fout.write('<eagle version="9.4.0">\n')
            fout.write('<drawing>\n')

            fout.write('<settings>\n')
            fout.write('    <setting alwaysvectorfont="no"/>\n')
            fout.write('    <setting keepoldvectorfont="yes"/>\n')
            fout.write('    <setting verticaltext="up"/>\n')
            fout.write('</settings>\n')

            fout.write('<grid distance="50" unitdist="mil" unit="mm" style="lines" multiple="1" display="yes" altdistance="5" altunitdist="mil" altunit="mm"/>\n')

            fout.write('<layers>\n')
            for i, layer in enumerate(self.layers):
                fout.write('  <layer number="{number}" name="{name}" color="{color}" fill="{fill}" visible="{visible}" active="{active}"/>\n'.format(**layer))
            fout.write('</layers>\n')

            fout.write('<library>\n')
            fout.write('<packages>\n')
            for p in self.packages:
                if p == 'C0805':
                    pass
                if p in self.eagle_libs.packages:
                    fout.write(self.eagle_libs.package_as_string(p))
                else:
                    fout.write('<package name="%s">\n' % p)
                    fout.write('</package>\n')
            fout.write('</packages>\n')

            fout.write('<packages3d>\n')
            fout.write('</packages3d>\n')
            fout.write('<symbols>\n')
            for s in self.symbols:
                fout.write(self.eagle_libs.symbol_as_string(s))
            fout.write('</symbols>\n')
            fout.write('<devicesets>\n')
            for item in self.items:
                value = self.items[item][0]['value']
                fout.write('  <deviceset name="%s" prefix="%s">\n' % (value, self.prefix))
                fout.write('  <description>\n')
                fout.write('\n'.join([obj['desc'].replace("\"", "") for obj in self.items[item]]))
                fout.write('  </description>\n')
                fout.write('  <gates>\n')
                fout.write('    <gate name="G$1" symbol="%s" x="0" y="0"/>\n' % self.items[item][0]['symbol'])
                fout.write('  </gates>\n')
                fout.write('  <devices>\n')
                for i,obj in enumerate(self.items[item]):
                    part_id = '-'.join([obj['manufacturer'],obj['mpn']])
                    fout.write('    <device name="%s" package="%s">\n' % (part_id.replace(" ","_"), obj['package']))
                    fout.write('    <connects></connects>\n')
                    fout.write('    <technologies>\n')
                    fout.write('      <technology name="">\n')
                    fout.write('        <attribute name="MPN" value="%s"/>ֿ\n' % obj['mpn'])
                    fout.write('        <attribute name="MANUFACTURER" value="%s"/>ֿ\n' % obj['manufacturer'])
                    str =      '        <attribute name="IMAGE" value="%s"/>ֿ\n' % obj['image']
                    str = str.replace("&","%38")
                    if len(str)<200:
                        fout.write(str)
                    s2 = '        <attribute name="DATASHEET" value="%s"/>ֿ\n' % obj['datasheet']
                    if len(s2)<113:
                        fout.write(s2)
                    fout.write('      </technology>\n')
                    fout.write('    </technologies>\n')
                    fout.write('    </device>\n')
                fout.write('  </devices>\n')
                fout.write('  </deviceset>\n')
            fout.write('</devicesets>\n')
            fout.write('</library>\n')
            fout.write('</drawing>\n')
            fout.write('</eagle>\n')

