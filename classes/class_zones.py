try:
    from cv2 import cv2
except:
    import cv2


class Zone:
    def draw(self, frame):
        pass

    def process_coords(self, points):
        pass

    def process_single(self, track):
        pass


class CircleZone(Zone):
    def __init__(self, rel_coords, rel_rad):
        self.center_x, self.center_y = rel_coords
        self.rad = rel_rad

    def draw(self, frame):
        h, w = frame.shape[:2]
        center_x = int(self.center_x * w)
        center_y = int(self.center_y * h)
        rad = int(self.rad * w)
        return cv2.circle(frame, (center_x, center_y), rad, (255, 0, 0), 2)

    def process_coords(self, points):
        passed = {'in': 0,
                  'out': 0}

        for start, end in points:
            sx, sy = start
            ex, ey = end

            start_inside = self.inside(sx, sy)
            end_inside = self.inside(ex, ey)

            if start_inside and not end_inside:
                passed['out'] += 1
            elif not start_inside and end_inside:
                passed['in'] += 1
        return passed

    def process_single(self, track):
        sx, sy = track[0]
        ex, ey = track[1]

        start_inside = self.inside(sx, sy)
        end_inside = self.inside(ex, ey)

        if start_inside and not end_inside:
            return 'out'
        elif not start_inside and end_inside:
            return 'in'
        else:
            return 'trash'

    def inside(self, x, y):
        return (x - self.center_x) ** 2 + (y - self.center_y) ** 2 < self.rad


class DividingLine(Zone):
    def __init__(self, point1, point2, invert=False):
        self.x1, self.y1 = point1
        self.x2, self.y2 = point2
        self.invert = invert

    def draw(self, frame):
        h, w = frame.shape[:2]
        x1 = int(self.x1 * w)
        y1 = int(self.y1 * h)

        x2 = int(self.x2 * w)
        y2 = int(self.y2 * h)

        return cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

    def process_coords(self, points):
        passed = {'in': 0,
                  'out': 0}

        for start, end in points:
            sx, sy = start
            ex, ey = end
            start_side = self.side(sx, sy)
            end_side = self.side(ex, ey)

            if start_side != end_side and start_side:
                passed['in'] += 1
            elif start_side != end_side and end_side:
                passed['out'] += 1
        return passed

    def process_single(self, track):
        sx, sy = track[0]
        ex, ey = track[1]
        start_side = self.side(sx, sy)
        end_side = self.side(ex, ey)

        if start_side != end_side and start_side:
            return 'in'
        elif start_side != end_side and end_side:
            return 'out'
        else:
            return 'trash'

    def side(self, x, y):
        if self.invert:
            return (x - self.x1) * (self.y2 - self.y1) - (y - self.y1) * (self.x2 - self.x1) > 0
        else:
            return (x - self.x1) * (self.y2 - self.y1) - (y - self.y1) * (self.x2 - self.x1) < 0
