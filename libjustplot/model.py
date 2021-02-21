from typing import Sequence
from dataclasses import dataclass
from pathlib import Path
from pyqtgraph import PlotDataItem


@dataclass
class FilePlot:
    path: Path
    plots: Sequence[PlotDataItem]
