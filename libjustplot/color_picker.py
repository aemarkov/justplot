class ColorPicker:
    """ Return next color like standard matplotlib property cycle """
    _COLORS = [
        '#1f77b4',
        '#ff7f0e',
        '#2ca02c',
        '#d62728',
        '#9467bd',
        '#8c564b',
        '#e377c2',
        '#7f7f7f',
        '#bcbd22',
        '#17becf']

    def __init__(self):
        self._color_index = 0

    def next_color(self) -> str:
        """ Get next color """
        clr = self._COLORS[self._color_index]
        self._color_index = (self._color_index + 1) % len(self._COLORS)
        return clr
