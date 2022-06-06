import re, math
from cairosvg.parser import Tree
from cairosvg.helpers import node_format

RE_SPLIT = re.compile(r'[^, ]+')

def parse_hotspot(tree: Tree):
    view_width, view_height, _ = node_format(None, tree)
    hotspot = [float(x) for x in RE_SPLIT.findall(tree.get('hotspot', '0 0'))]
    return (hotspot[0] / view_width, hotspot[1] / view_height)

def parse_time(time: str):
    """:returns: `time` in seconds"""
    return float(time.strip('s'))

def set_max_time(time, max_time):
    if max_time is None or (time != None and time > max_time):
        return time
    return max_time

def interpolate(a, b, t):
    return a * (1.0 - t) + b * t

def animate(tree: Tree, time=0.0, max_time=None):
    """
    Update variables in `tree` to progress the animation.
    :returns: Maximum time of animation.
    """
    if 'animate' in tree.tag:
        assert tree.parent
        assert tree.tag == 'animateTransform', "Animation only supports 'animateTransform'"
        assert tree.get('attributeName')
        assert tree.get('type', 'translate') == 'translate'
        assert tree.get('calcMode', 'linear') == 'linear'
        assert tree.get('from') and tree.get('to')

        attr_from = [float(x) for x in RE_SPLIT.findall(tree.get('from'))]
        attr_to = [float(x) for x in RE_SPLIT.findall(tree.get('to'))]
        assert len(attr_from) == len(attr_to)

        duration = parse_time(tree.get('dur', 'indefinite'))
        assert type(duration) == float
        max_time = set_max_time(max_time, duration)
        
        # Update the animation attribute
        t = math.fmod(time, duration) / duration
        attrs = [str(interpolate(attr_from[i], attr_to[i], t)) for i in range(len(attr_from))]
        tree.parent[tree.get('attributeName')] = 'translate(%s)' % (' '.join(attrs))

    for child in tree.children:
        max_time = set_max_time(max_time, animate(child, time, max_time))
    return max_time