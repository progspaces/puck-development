import math

def angle_to(p, q):
    """Angle in radians from p to q, clockwise from horizontal right."""
    if p == q:
        raise ValueError("no angle from a point to itself")
    
    px, py = p
    qx, qy = q

    dx = qx - px
    dy = qy - py

    if dx == 0:
        if dy > 0:
            angle = math.pi /2
        else:
            angle = -math.pi / 2
    else:
        angle = math.atan(dy/dx)

    if dx < 0:
        angle += math.pi

    return angle



def clockwise_pt(points, black):
    """The point that is the one clockwise from black, in the square formed by points."""
    other_corners = [pt for pt in points if pt != black]
    dists_to_corners = [math.dist(black, q) for q in other_corners]
    furthest = max(dists_to_corners)
    opposite_corner = other_corners[dists_to_corners.index(furthest)]

    adjacent_corners = [pt for pt in other_corners if pt != opposite_corner]
    angles_to_corners = [angle_to(black, q) for q in adjacent_corners]

    angle_range = max(angles_to_corners) - min(angles_to_corners)

    if angle_range < math.pi:
        # should be about pi/2
        clockwise_angle = min(angles_to_corners)
    else:
        # should be about 3/2 pi
        clockwise_angle = max(angles_to_corners)

    clockwise_pt = adjacent_corners[angles_to_corners.index(clockwise_angle)]
    return clockwise_pt


def order_no_color_rectangle(point_list, reference):
    ordered = [None, None, None]
    # print(reference)
    ordered[0] = clockwise_pt(point_list, reference)
    ordered[1] = clockwise_pt(point_list, ordered[0])
    # print(ordered)
    # print(point_list)
    ordered[2] = clockwise_pt(point_list, ordered[1])
    # ordered[2] = point_list[point_list not in ordered]
    assert ordered[0] != ordered[1]
    assert ordered[1] != ordered[2]
    assert ordered[0] != ordered[2]
    # print(f"reference is : {reference}")
    # print(f"color_coords: {colored_coords}")
    return ordered
    # try:
    #     return sorted(colored_coords, key = lambda x: ordered.index(x[0]))
    # except ValueError:
    #     return {"ref

def order_rectangle(color_point_list, reference):
    assert len(color_point_list) == 4
    point_list =[p[0] for p in color_point_list]
    assert len(point_list) == 4
    assert reference in point_list
    ordered = [None, None, None]
    # print(reference)
    ordered[0] = clockwise_pt(point_list, reference)
    ordered[1] = clockwise_pt(point_list, ordered[0])
    # print(ordered)
    # print(point_list)
    ordered[2] = clockwise_pt(point_list, ordered[1])
    # ordered[2] = point_list[point_list not in ordered]
    assert ordered[0] != ordered[1]
    assert ordered[1] != ordered[2]
    assert ordered[0] != ordered[2]
    colored_coords = [c for c in color_point_list if c[0] != reference]
    # print(f"reference is : {reference}")
    # print(f"color_coords: {colored_coords}")
    return sorted(colored_coords, key = lambda x: ordered.index(x[0]))
    # try:
    #     return sorted(colored_coords, key = lambda x: ordered.index(x[0]))
    # except ValueError:
    #     return {"reference": reference, "color_coords": str(colored_coords), "ordered": str(ordered)}


if __name__ == "__main__":
    # example set of points arranged in a square
    corner_pts = [
        (2, 0),
        (22, 2),
        (0, 20), 
        (20, 22),
    ]

    # calculate what point is clockwise of each other point
    for black in corner_pts:
        print(f"clockwise from {black} is {clockwise_pt(corner_pts, black)}")

    # full set of 9 points
    pts = [
        (2, 0),
        (12, 1),
        (22, 2),
        (1, 10),
        (11, 11),
        (21, 12),
        (0, 20),
        (10, 21),
        (20, 22),
    ]
