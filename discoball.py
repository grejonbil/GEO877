import numpy
import plotly.graph_objects as go

class Point():
    
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y
        
    def __repr__(self):
        return f'Point(x = {self.x}, y = {self.y})'


class DiscoBall():

    def __init__(self, n):

        self.n_lat = n
        self.n_lon = n * 2

        self.cells = []

        self._compute_cells()

        self.mean, self.sd, self.k = self._statisics()


    def __repr__(self):
        return f'''Disco Ball Raster:

Number of cells:                      {self.k}
Mean area of cells:                   {int(self.mean)} km2
Standard deviation of area of cells:  {int(self.sd)} km2'''


    def _cell_area(self, ll, ur):
        """Returns the area of a cell given the lower-left and upper-right coordinate on a sphere"""

        # Maths on surface integral: https://www.sharetechnote.com/html/Calculus_Integration_Surface.html

        d_theta = abs(numpy.radians(ll.x) - numpy.radians(ur.x))    # longitudinal arc length
        d_phi = abs(numpy.radians(ll.y) - numpy.radians(ur.y))    # latitudinal arc length

        phi = numpy.radians(((ll.y + ur.y) / 2) * (-1) + 90)    # average latitudinal angle of cell (north pole = 0°; south pole = 180°)

        area = numpy.sin(phi) * d_phi * d_theta * 6371**2

        return area    # [km^2]


    def _compute_cells(self):

        rows = []

        for i in numpy.linspace(0, 90, int(self.n_lat / 2), endpoint=False):
            rows.append(Point(0, i))
            rows.insert(0, Point(0, -i - (180 / self.n_lat)))

        equatorial_cell_area = self._cell_area(Point(0, 0), Point(360 / self.n_lon, 90 / self.n_lat))

        cells = []

        for row in rows:

            ll = row
            ur = Point(ll.x + 360 / self.n_lon, ll.y + 90 / self.n_lat)
            row_area = self._cell_area(ll, ur) * self.n_lon

            n_cells = row_area // equatorial_cell_area
            cell_width = 360 / n_cells

            cell_row = []

            for i in numpy.linspace(0, 360, int(n_cells), endpoint=False):
                cell_row.append([
                    Point(i, ll.y),
                    Point(i + cell_width, ll.y),
                    Point(i + cell_width, ll.y + (180 / self.n_lat)),
                    Point(i, ll.y + (180 / self.n_lat))
                    ])

            self.cells.append(cell_row)


    def _statisics(self):

        m = 0
        s = 0
        k = 0

        for row in self.cells:
            for cell in row:
                area = self._cell_area(cell[0], cell[2])
                oldm = m
                olds = s
                k += 1
                m = oldm + (area - oldm) / k
                s = olds + (area - oldm) * (area - m)

        s = numpy.sqrt(s / (k - 1))

        return m, s, k


    def display(self, height=500):

        data = []

        for row in self.cells:
            for cell in row:
                lat, lon = [], []
                for point in cell:
                    lat.append(point.y)
                    lon.append(point.x)
                data.append(
                    go.Scattergeo(lat = lat, lon = lon, mode = 'lines', line = dict(width = 1)))

        fig = go.Figure(data=data)

        fig.update_geos(projection_type="orthographic")
        fig.update_layout(height=height, margin={"r":0,"t":0,"l":0,"b":0})

        fig.show()
