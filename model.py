"""
This module defines the data model for the simulation. Specifically, it provides a class for representing patches of the simulation grid and a class for representing cells that inhabit these patches.


Requirements
------------
Python 3.7 or higher.

Notes
-----
This module provided as material for the reexam project for DM857, DS830 (2024). 
"""

from __future__ import annotations # to use a class in type hints of its members
from typing import Optional

class Patch:
  """Represents a 'patch' at the intersection of the riven row and column of the simulation grid."""
  
  def __init__(self:Patch,row:int,col:int):
    """    
    Parameters
    ----------
    row, col: int
      The index of the row and column containing this patch.
    """
    self._col = col
    self._row = row
    self._cell : Optional[Cell] = None

  def col(self:Patch)->int:
    """Returns the index of the column containing this patch."""
    return self._col

  def row(self:Patch)->int:
    """Returns the index of the row containing this patch."""
    return self._row
  
  def has_cell(self:Patch)->bool:
    """Checks if the patch holds a cell."""
    return self._cell is not None

  def put_cell(self:Patch,cell:Cell)->None:
    """Puts a cell on this patch.
    
    Preconditions: there is no cell on this patch and the cell is not on another patch
    """
    assert not self.has_cell(), "This patch has a cell."
    assert cell.patch() is self, "The cell is on another patch."
    self._cell = cell

  def remove_cell(self:Patch)->None:
    """Removes any cell currently on this patch."""
    self._cell = None

  def cell(self:Patch)->Optional[Cell]:
    """Returns the cell currently on this patch, if any."""
    return self._cell

  def __repr__(self:Patch)->str:
    """Returns a string representation of this patch."""
    return f"Patch({self.col()}, {self.row()})"

class Cell:
  """Represents a cell in the simulation."""

  def __init__(self:Cell,patch:Patch):
    """    
    Parameters
    ----------
    patch: Patch
      The patch that will contain this cell (added automatically). The patch must be free.
    """
    self._patch = patch
    self._age = 0
    self._divisions = 0
    self._last_division = 0
    self._alive = True
    # inform patch that this cell is on it
    patch.put_cell(self)
  
  def patch(self:Cell)->Patch:
    """Returns the patch of this cell. If the cell is dead, it returns the patch where the cell died."""
    return self._patch

  def age(self:Cell)->int:
    """Returns the age in ticks of this cell or the age at the time of death if the cell is dead."""
    return self._age
  
  def divisions(self:Cell)->int:
    """Returns number of division performed by this cell."""
    return self._divisions

  def last_division(self:Cell)->int:
    """Returns the time in ticks since the last division this cell (or its creation if it never divided)."""
    return self._last_division
  
  def is_alive(self:Cell)->bool:
    """Returns whether this cell is alive."""
    return self._alive

  def tick(self:Cell)->None:
    """Register with this cell that a tick in the simulation happened making the cell age.
    
    Precondition: the cell is alive."""
    assert self.is_alive(), "the cell must be alive."
    self._age = self._age + 1
    self._last_division = self._last_division + 1

  def die(self:Cell)->None:
    """This cell dies and is removed from its current patch.

    Precondition: the cell is alive."""
    assert self.is_alive(), "the cell must be alive."
    self._alive = False
    # removes the cell from this cell's patch
    self._patch.remove_cell()
  
  def divide(self:Cell,patch:Patch)->Cell:
    """Divides this cell using the given patch and returns the new cell.
    
    Precondition: the cell is alive."""
    assert self.is_alive(), "the cell must be alive."
    self._last_division = 0 # reset the counter from the last division
    self._divisions = self._divisions + 1 # updates the division count
    return Cell(patch)