#!/usr/bin/env python
# -*- coding: utf-8; -*
#
#    Copyrright (C) 2015 Jan bundesmann
#
#    This file is part of FS Gamemaster Assistant (FSGA).
#
#    FSGA is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    FSGA is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with ChordMaker.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Collection of widgets the are combined in the complete widget.
"""

import random

from PySide import QtGui
from PySide import QtCore


class participant_model(QtGui.QWidget):
    """
    Dummy-class that displays a battle participant.
    """
    def __init__(self, name, parent=None):
        super(participant_model, self).__init__(parent)

        self.name = name

        self.order = random.randint(0, 10)

        self.hps = 4

        self.initUI()

    def __repr__(self):
        result = ("%s with %i initiative and %i hp" %
                  (self.name, self.order, self.hps))

        return result

    def initUI(self):
        layout = QtGui.QGridLayout()

        self.nameWidget = QtGui.QLabel(self.name)
        self.orderWidget = QtGui.QLabel("%i" % self.order)
        self.hpsWidget = QtGui.QLabel("".join(["o" for i in range(self.hps)]))

        layout.addWidget(self.nameWidget, 0, 0)
        layout.addWidget(self.orderWidget, 1, 0)
        layout.addWidget(self.hpsWidget, 1, 1)

        self.setLayout(layout)

    def next_round(self):
        self.order = random.randint(0, 10)
        self.orderWidget.setText("%i" % self.order)
        #self.initUI()
        #self.update()
        #self.repaint()


class participants_list():
    """
    Dummy container of objects with their own order parameter
    """

    def __init__(self, participants):
        self.sort_participants(participants)

    def sort_participants(self, participants):
        # we restrict the order range to 0-10
        nested_base = [[] for i in range(23)]
        for participant in participants:
            nested_base[participant.order].append(participant)

        self.flattened_list = []
        nested_base.reverse()
        for sublist in nested_base:
            self.flattened_list.extend(sublist)

    def __len__(self):
        return self.flattened_list.__len__()

    def __getitem__(self, key):
        return self.flattened_list.__getitem__(key)

    def __iter__(self):
        return self.flattened_list.__iter__()

    def reshuffle(self):
        participants_new = []

        for participant in self.flattened_list:
            participant.next_round()

            participants_new.append(participant)

        self.sort_participants(participants_new)


class ordered_list(QtGui.QWidget):
    """
    A QT widget capable of displaying widgets stored in a list.

    :param list_object: List of displayable QT objects

    The purpose of this class is to display widgets stored in a list according
    to some order parameter.
    It basically consists of a QVBoxLayout which one by one is filled with
    the list's items.
    """
    def __init__(self, list_object, parent=None):
        super(ordered_list, self).__init__(parent)

        self.participants = list_object

        self.verticalLayout = QtGui.QVBoxLayout()

        for idx, entry in enumerate(self.participants):
            self.verticalLayout.addWidget(entry)

        self.setLayout(self.verticalLayout)


class BattleWidget(QtGui.QScrollArea):
    def __init__(self, participants, parent=None):
        super(BattleWidget, self).__init__(parent)
        self.participants = participants

        self.setupUI()
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        print self.sizePolicy().expandingDirections()

        QtCore.QMetaObject.connectSlotsByName(self)

    def setupUI(self):
        inner_widget = QtGui.QWidget()
        layout = QtGui.QGridLayout(inner_widget)

        action_list = ordered_list(self.participants)
        layout.addWidget(action_list, 0, 0, 6, 1)

        button = QtGui.QPushButton("press me")
        button.setObjectName("button")
        layout.addWidget(button, 6, 1)

        # graveyard
        layout.addWidget(QtGui.QLabel("Graveyard"), 0, 1)
        layout.addWidget(QtGui.QLabel("Liste"), 1, 1)
        button2 = QtGui.QPushButton("revive")
        button2.setObjectName("revive")
        layout.addWidget(button2, 2, 1)

        layout.addWidget(QtGui.QLabel("Pool"), 3, 1)
        layout.addWidget(QtGui.QLabel("Liste"), 4, 1)
        button3 = QtGui.QPushButton("activate")
        button3.setObjectName("activate")
        layout.addWidget(button3, 5, 1)

        inner_widget.setMinimumWidth(1000)
        self.setWidget(inner_widget)
        self.setMinimumWidth(1000)

    @QtCore.Slot()
    def on_button_released(self):
        self.participants.reshuffle()
        action_list = ordered_list(self.participants)
        self.layout().addWidget(action_list, 0, 0)
        print "button released"


class PoolWidget(QtGui.QWidget):
    def __init__(self, participants, parent=None):
        super(PoolWidget, self).__init__(parent)
        self.participants = participants

        self.setupUI()

        QtCore.QMetaObject.connectSlotsByName(self)

    def setupUI(self):
        layout = QtGui.QGridLayout()

        button = QtGui.QPushButton("press me")
        button.setObjectName("button")
        layout.addWidget(button, 1, 1)

        self.setLayout(layout)

    @QtCore.Slot()
    def on_button_released(self):
        print "button in PoolWidget released"


class TestWindow(QtGui.QWidget):
    def __init__(self, participants, parent=None):
        super(TestWindow, self).__init__(parent)
        self.participants = participants

        self.setupUI()

        QtCore.QMetaObject.connectSlotsByName(self)

    def setupUI(self):
        layout = QtGui.QGridLayout()

        tab_widget = QtGui.QTabWidget()
        layout.addWidget(tab_widget, 0, 0)

        #pool_widget = PoolWidget(self.participants)
        #tab_widget.addTab(pool_widget, "Pool")

        battle_widget = BattleWidget(self.participants)
        tab_widget.addTab(battle_widget, "Battle")

        self.setLayout(layout)

if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)

    from rules import NPC
    from rules import PC

    chars = [
        PC("Nader", 3, 8, 9, 1),
        PC("Tristan", 6, 5, 11, 1),
        PC("Hieronymus", 7, 6, 8, 1),
        PC("Frederik", 6, 9, 10, 1),
        NPC("Ronnie", 8, 3, 11, 1),

        NPC("Bob", 6, 4, 10, 1),
        NPC("Alice", 6, 4, 10, 1),
        NPC("Eve", 6, 4, 10, 1),
        NPC("Chainy", 6, 4, 10, 1),
        NPC("Yassyar", 6, 4, 10, 1),
        NPC("Palok", 6, 4, 10, 1),
        NPC("Pumpur", 6, 4, 10, 1),
    ]

    participants = participants_list(chars)

    ol = BattleWidget(participants)
    ol.show()

    sys.exit(app.exec_())
