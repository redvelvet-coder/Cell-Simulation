"""
This module provides Visualiser, a class for displaying the status of a grid of patches forming the 2D surface of a simulation.

Requirements
------------
Package matplotlib https://matplotlib.org/ which can be installed via PIP.
Python 3.7 or higher.

Notes
-----
This module provided as material for the re-exam project for DM857, DS830 (2024). 
"""

from __future__ import annotations # to use a class in type hints of its members
from typing import List, Optional
from model import Patch
import matplotlib.pyplot as plt

class Visualiser:
  """Each instance of this class maintains a window where it displays the status of a given grid of patches forming the 2D surface of a simulation."""

  def __init__(self:Visualiser, 
               patches:List[Patch], rows:int, cols:int,
               grid_lines = False, ticks = False,
               window_title : Optional[str]=None):
    """
    Parameters
    ----------
    patches: List[Patch]
      List containing the patches forming the 2D surface for the simulation.
    rows, cols: int
      Number of rows and columns of the 2D surface for the simulation (both positive).
    grid_lines, ticks : bool, default = False
      Control whether grid lines and ticks are displayed.
    window_title : Optional[str], default = None
      The title of the window.
    """
    self._size = (cols,rows)
    self._patches = [ [ None ] * cols for _ in range(rows) ]
    for patch in patches:
      self._patches[patch.row()][patch.col()] = patch
    fig, ax = plt.subplots()
    # title
    if not window_title:
      window_title = 'CellSim Visualiser'
    fig.canvas.manager.set_window_title(window_title)    
    # listen to close events
    self._is_open = True
    def on_close(_):
      self._is_open = False
    fig.canvas.mpl_connect('close_event', on_close )
    # add data raster
    self._im = ax.imshow(self.__data(), cmap='binary',vmin=0,vmax=1, animated=True)
    # add grid lines
    hlns = [ ax.axhline(-.5,color='black',linestyle='-', linewidth=1)]
    vlns = [ ax.axvline(-.5,color='black',linestyle='-', linewidth=1)]
    if grid_lines:
      hlns.extend( ax.axhline(y-.5,color='gray',linestyle='-', linewidth=1) 
                   for y in range(1,rows,1) )
      vlns.extend( ax.axvline(x-.5,color='gray',linestyle='-', linewidth=1) 
                   for x in range(1,cols,1) )
    if ticks:
      ax.tick_params(top = True, labeltop = True, right = True, labelright = True)
    else:
      ax.tick_params(bottom = False, labelbottom = False, left = False, labelleft = False)
    # blitter
    self._bm = _BlitManager(fig.canvas, [self._im] + hlns + vlns)  
    # make sure our window is on the screen and drawn
    plt.show(block=False)
    plt.pause(.1)
  
  def is_open(self:Visualiser) -> bool:
    """
    Whether the window managed by the visualiser is open or not.
    """
    return self._is_open

  def close(self:Visualiser) -> None:
    """Closes the window destroying this visualiser."""
    plt.close()

  def wait_close(self:Visualiser):
    """
    Suspends the current execution until the visualiser window is manually closed by the user.
    """
    plt.show()

  def __data(self) -> List[List[int]]:
    return [ [ patch.has_cell() for patch in row ] for row in self._patches ]

  def update(self:Visualiser) -> None:
    """Informs this visualiser that the status of its patches has been updated."""
    if self.is_open() :
      self._im.set_data(self.__data())
      self._bm.update()
      plt.pause(.1)

# this is a helper class used by Visualiser
class _BlitManager:
  def __init__(self, canvas, animated_artists=()):
      """
      Parameters
      ----------
      canvas : FigureCanvasAgg
          The canvas to work with, this only works for sub-classes of the Agg
          canvas which have the `~FigureCanvasAgg.copy_from_bbox` and
          `~FigureCanvasAgg.restore_region` methods.

      animated_artists : Iterable[Artist]
          List of the artists to manage
      """
      self.canvas = canvas
      self._bg = None
      self._artists = []

      for a in animated_artists:
          self.add_artist(a)
      # grab the background on every draw
      self.cid = canvas.mpl_connect("draw_event", self.on_draw)

  def on_draw(self, event):
      """Callback to register with 'draw_event'."""
      cv = self.canvas
      if event is not None:
          if event.canvas != cv:
              raise RuntimeError
      self._bg = cv.copy_from_bbox(cv.figure.bbox)
      self._draw_animated()

  def add_artist(self, art):
      """
      Add an artist to be managed.

      Parameters
      ----------
      art : Artist

          The artist to be added.  Will be set to 'animated' (just
          to be safe).  *art* must be in the figure associated with
          the canvas this class is managing.

      """
      if art.figure != self.canvas.figure:
          raise RuntimeError
      art.set_animated(True)
      self._artists.append(art)

  def _draw_animated(self):
      """Draw all of the animated artists."""
      fig = self.canvas.figure
      for a in self._artists:
          fig.draw_artist(a)

  def update(self):
      """Update the screen with animated artists."""
      cv = self.canvas
      fig = cv.figure
      # paranoia in case we missed the draw event,
      if self._bg is None:
          self.on_draw(None)
      else:
          # restore the background
          cv.restore_region(self._bg)
          # draw all of the animated artists
          self._draw_animated()
          # update the GUI state
          cv.blit(fig.bbox)
      # let the GUI event loop process anything it has to do
      cv.flush_events()
