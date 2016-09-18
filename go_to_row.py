import sublime, sublime_plugin  

import os
import fnmatch
from os.path import join

class GotoRowColCommand(sublime_plugin.TextCommand):
        def run(self, edit, row, col):
                print("INFO: Input: " + str({"row": row, "col": col}))
                # rows and columns are zero based, so subtract 1
                # convert text to int
                (row, col) = (int(row) - 1, int(col) - 1)
                if row > -1 and col > -1:
                        # col may be greater than the row length
                        col = min(col, len(self.view.substr(self.view.full_line(self.view.text_point(row, 0))))-1)
                        print("INFO: Calculated: " + str({"row": row, "col": col})) # r1.01 (->)
                        self.view.sel().clear()
                        self.view.sel().add(sublime.Region(self.view.text_point(row, col)))
                        self.view.show(self.view.text_point(row, col))
                else:
                        print("ERROR: row or col are less than zero")   