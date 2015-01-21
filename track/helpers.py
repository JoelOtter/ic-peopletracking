# Returns true if a is a bound that lies within b.
def is_within(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b

    return (bx <= ax) & (ax + aw <= bx + bw) &\
           (by <= ay) & (ay + ah <= by + bh)


# Returns true if a point (a) lies inside the bound.
def is_inside(a, bound):
    ax, ay = a
    bx, by, bw, bh = bound

    return (bx <= ax) & (ax <= bx + bw) &\
           (by <= ay) & (ay <= by + bh)


# Returns bounds with all bounds removed that contain any positions
# found in ignore_positions.
def remove_bounds_containing(bounds, ignore_positions):
    return filter(lambda b: not any(map(lambda x: is_inside(x, b), ignore_positions)), bounds)
