import argparse
import sys, os, glob

from cairosvg import surface
from cairosvg.parser import Tree
from util import parse_hotspot, animate
from PIL import Image
from CurImagePlugin import save_ani

def convert_static(args, filename: str, tree: Tree, hotspot):
    output_size = (256,256)

    out_filename = "%s.png"%filename
    try:
        # To PNG
        instance = surface.PNGSurface(tree, out_filename, 96, output_width=output_size[0], output_height=output_size[1])
        instance.finish()
        
        # To CUR
        img = Image.open(out_filename)
        img.save("%s.cur"%filename, hotspot=(hotspot[0] * output_size[0], hotspot[1] * output_size[1]))
    finally:
        # Cleanup temp file
        if not args.output_png:
            os.remove(out_filename)

def convert_dynamic(args, filename: str, tree: Tree, hotspot, max_time):
    output_size = (256,256)
    
    frame_count = int(tree.get('frameCount', '0'))
    assert frame_count > 0, 'You need at least 1 frame for the animation'
    seconds_per_frame = max_time / frame_count

    time = 0.0
    frames = []

    try:
        # To PNGs
        for frame in range(frame_count):
            animate(tree, time)
            time += seconds_per_frame

            # Cannot convert Surface to Image in memory, because Surface outputs ARGB and Image only accepts RGBA
            # Temporarily write to disk and remove when done
            out_filename = "%s_%d.png" % (filename, frame)
            instance = surface.PNGSurface(tree, out_filename, 96, output_width=output_size[0], output_height=output_size[1])
            instance.finish()
            
            frames.append(Image.open(out_filename))

        # To ANI
        save_ani("%s.ani"%filename, frames, seconds_per_frame, hotspot=(hotspot[0] * output_size[0], hotspot[1] * output_size[1]))
    finally:
        to_remove = [x.filename for x in frames]
        frames.clear()

        # Cleanup temp files
        if not args.output_png:
            for remove in to_remove:
                os.remove(remove)

def main(args):
    files = []
    for filepath in args.filepath:
        if os.path.isdir(filepath):
            files += glob.glob(os.path.join(filepath, '**', '*.svg'))
        elif filepath.endswith('.svg'):
            files.append(filepath)
        else:
            files.append('%s.svg'%filepath)
    
    for file in files:
        filename = file[:-len('.svg')]
        print('Converting %s' % filename)

        # Parse tree
        tree = Tree(url="%s.svg"%filename)
        hotspot = parse_hotspot(tree)

        max_time = animate(tree)
        if max_time == None:
            convert_static(args, filename, tree, hotspot)
        else:
            convert_dynamic(args, filename, tree, hotspot, max_time)
    
    print('\n%d file%s converted.' % (len(files), '' if len(files) == 1 else 's'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert .svg file(s) to Windows Cursors')
    parser.add_argument('filepath', type=str, action="extend", nargs="+", metavar='filepath|folder')
    parser.add_argument('--output-png', default=False, action='store_true', help='Also output .png files')
    main(parser.parse_args())