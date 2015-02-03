#!/usr/bin/env python
# -*- coding: utf-8; -*

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
        nested_base = [[] for i in range(13)]
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


class TestWindow(QtGui.QWidget):
    def __init__(self, participants, parent=None):
        super(TestWindow, self).__init__(parent)
        self.participants = participants

        self.setupUI()

        QtCore.QMetaObject.connectSlotsByName(self)

    def setupUI(self):
        layout = QtGui.QGridLayout()

        action_list = ordered_list(self.participants)
        layout.addWidget(action_list, 0, 0)

        button = QtGui.QPushButton("press me")
        button.setObjectName("button")
        layout.addWidget(button, 1, 1)

        self.setLayout(layout)

    @QtCore.Slot()
    def on_button_released(self):
        self.participants.reshuffle()
        action_list = ordered_list(self.participants)
        self.layout().addWidget(action_list, 0, 0)
        print "button released"


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)

    from rules import NPC
    #char1 = participant_model("Alice")
    #char2 = participant_model("Bob")
    #char3 = participant_model("Eve")
    #char4 = participant_model("Villain 1")
    char1 = NPC("Alice", 3, 3, 8, 1)
    char2 = NPC("Bob", 3, 3, 8, 1)
    char3 = NPC("Eve", 3, 3, 8, 1)
    char4 = NPC("Villain 1", 3, 3, 8, 1)
    #char4.reduce_hitpoints(3)

    participants = participants_list([char1, char2, char3, char4])

    ol = TestWindow(participants)
    ol.show()

    sys.exit(app.exec_())
