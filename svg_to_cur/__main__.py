import sys, os, glob, re
import cairosvg
from cairosvg import surface
from cairosvg.parser import Tree
from cairosvg.helpers import node_format
from PIL import Image
import CurImagePlugin

RE_SPLIT = re.compile(r'[^, ]+')

def parse_hotspot(tree: Tree):
    view_width, view_height, _ = node_format(None, tree)
    hotspot = [float(x) for x in RE_SPLIT.findall(tree.get('hotspot', '0 0'))]
    return (hotspot[0] / view_width, hotspot[1] / view_height)

def convert(path):
    if path.endswith('.svg'):
        files = [path]
    else:
        files = glob.glob(os.path.join(path, '**', '*.svg'))
    
    for file in files:
        filename = file[:-len('.svg')]
        print('Converting %s' % filename)

        # To PNG
        tree = Tree(url="%s.svg"%filename)
        instance = surface.PNGSurface(tree, "%s.png"%filename, dpi=96, output_width=256, output_height=256)
        instance.finish()

        # Read hotspot
        hotspot = parse_hotspot(tree)
        
        # To CUR
        img = Image.open("%s.png"%filename)
        img.save("%s.cur"%filename, hotspot=(hotspot[0]*256, hotspot[1]*256))

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print('Usage: %s <file|folder> - Converts all .svg files to .png and .cur' % sys.argv[0])
        exit(1)
    convert(sys.argv[1])