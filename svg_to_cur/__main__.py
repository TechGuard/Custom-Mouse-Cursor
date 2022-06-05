import sys, os, glob
import cairosvg
from cairosvg import surface
from cairosvg.parser import Tree
from cairosvg.helpers import node_format
from PIL import Image
import CurImagePlugin

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
        hotspot = [float(x) for x in tree.get('hotspot', '0,0').split(',')]
        width, height, _ = node_format(instance, tree)
        
        # To CUR
        img = Image.open("%s.png"%filename)
        img.save("%s.cur"%filename, hotspot=(hotspot[0]/width*256, hotspot[1]/height*256))

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print('Usage: %s <file|folder> - Converts all .svg files to .png and .cur' % sys.argv[0])
        exit(1)
    convert(sys.argv[1])