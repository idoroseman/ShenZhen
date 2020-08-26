import re
import os
import json
import grabber
from EagleLibraryWriter import EagleLib
from EagleGrabber import EagleGrabber

eagle_libs = EagleGrabber()
eagle_libs.save_to_file('packages.lbr')
def post_process_rcl(items, prefix):
    for item in items:
        params = []
        value = re.search("\d+(\.\d)*[GMKmµuUnNp]*[ΩHF]", item['desc'].replace(" OHM", "Ω"))
        if value:
            params.append(value.group())
        power = re.search("(1\/)*\d+W", item['desc'])
        if power:
            params.append(power.group())
        volt = re.search("\d+V", item['desc'])
        if volt:
            params.append(volt.group())
        accu = re.search("±\d+\%", item['desc'])
        if accu:
            params.append(accu.group()[1:])

        item['value'] = '-'.join(params)
        if value is None:
            print("part with no value!", item['desc'])
        item['symbol'] = prefix

#-------------------------------------------------------------------------------

data_path = "data/"

def category_grab(cat):
    items = grabber.get_items(cat)
    with open(os.path.join(data_path, "%s.json" % cat) , "w") as fout:
        json.dump(items, fout, indent=4)

def category_load(cat):
    with open(os.path.join(data_path, "%s.json" % cat)) as fin:
        return json.load(fin)

def category_dump(cat, items):
    with open(os.path.join(data_path, "%s.json" % cat) , "w") as fout:
        json.dump(items, fout, indent=4)

################################################################################

if not os.path.exists(data_path):
    os.mkdir(data_path)

if not os.path.exists(os.path.join(data_path,"categories.json")):
    print("download categories list")
    categories = grabber.get_categories()
    category_dump("categories", categories)
else:
    print("download selected categories")
    categories = category_load('categories')
    for cat in categories:
        if categories[cat]['download'] and not os.path.exists(os.path.join(data_path, "%s.json" % cat)):
            items = grabber.get_items(cat)
            category_dump(cat, items)

    print("processing")
    for cat in categories:
        if os.path.exists(os.path.join(data_path, "%s.json" % cat)):
            try:
                prefix = categories[cat]['prefix']
            except:
                prefix = None
            items = category_load(cat)
            post_process_rcl(items, prefix)
            lbr = EagleLib(cat, categories[cat], eagle_libs)
            for item in items:
                lbr.add_item(item)
            lbr.save_to_file()