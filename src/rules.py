#!/usr/bin/env python
# -*- coding: utf-8; -*

"""
Module containing classes that represent Fading Suns rules.
"""
import random
from PySide import QtGui, QtCore


class Char(QtGui.QWidget):
    """
    Simple character model used for NPCs where, potentially, less traits are
    required.

    :param str name: Identifier for the character
    :param int dexterity: dexterity trait
    :param int wits: wits trait
    :param int hps: hit points at the beginning of the battle
    :param int defense: characters base defense
    :param inst defense_modifier: modifiers that might vanish during battle

    Character class that allows for a smart display of the most important traits
    and easy modifications.
    """
    def __init__(self,
                 name, dexterity, wits, hps, defense,
                 defense_modifier=0,
                 parent=None):
        super(Char, self).__init__(parent)

        self.name = name
        self.dexterity = dexterity
        self.wits = wits
        self.hps = hps
        self.base_defense = defense
        self.base_hps = hps

        self.defense_modifier = defense_modifier
        self.temporary_defense_modifier = 0

        self.base_initiative = self.dexterity + self.wits

        self.order = self.base_initiative + random.randint(1, 6)

        self.initUI()

        self.choose_stance(0)

        self.set_connections()

    def initUI(self):
        """
        Create the widget containing informations and basic modifiers.

        The layout looks like this:
            NAME                                    INI
            stance              - DEFENSE +         DEF_MOD +-
            fighting stance     - HPS +
        """
        layout = QtGui.QGridLayout()

        # first line, consisting only of labels - that's easy
        self.nameWidget = QtGui.QLabel(("<b>%s</b>" % self.name))
        self.initiativeLabel = QtGui.QLabel("%i" % self.order)
        self.initiativeLabel.setAlignment(QtCore.Qt.AlignRight)
        #layout.addWidget(self.nameWidget, 0, 0)
        #layout.addWidget(self.initiativeLabel, 0, 2)
        layout.addWidget(self.nameWidget, 0, 0)
        layout.addWidget(self.initiativeLabel, 0, 1)

        # second row, more complicated
        self.stanceLabel = QtGui.QComboBox()
        self.stanceLabel.addItems(["neutral", "aggressive",
                                   "defensive", "total defense"])
        #layout.addWidget(self.stanceLabel, 1, 0)
        layout.addWidget(self.stanceLabel, 0, 2)

        self.def_layout = QtGui.QHBoxLayout()
        self.def_minus_button = QtGui.QPushButton("-")
        self.def_label = QtGui.QLabel()
        self.def_plus_button = QtGui.QPushButton("+")

        self.def_layout.addWidget(self.def_minus_button)
        self.def_layout.addWidget(self.def_label)
        self.def_layout.addWidget(self.def_plus_button)

        #layout.addLayout(self.def_layout, 1, 1)
        layout.addLayout(self.def_layout, 0, 3)

        self.box_def_modifier = QtGui.QSpinBox()
        self.box_def_modifier.setMinimum(-30)
        layout.addWidget(self.box_def_modifier, 0, 4)

        # third row, again easier
        self.fightingStanceLabel = QtGui.QLabel("fighting stance")
        #layout.addWidget(self.fightingStanceLabel, 2, 0)

        self.hp_layout = QtGui.QHBoxLayout()
        self.hp_minus_button = QtGui.QPushButton("-")
        self.hp_label = QtGui.QLabel()
        self.hp_plus_button = QtGui.QPushButton("+")

        self.hp_layout.addWidget(self.hp_minus_button)
        self.hp_layout.addWidget(self.hp_label)
        self.hp_layout.addWidget(self.hp_plus_button)

        #layout.addLayout(self.hp_layout, 2, 1, 1, 2)
        layout.addLayout(self.hp_layout, 0, 5)

        # add a line at the bottom of the widget
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.HLine)
        #layout.addWidget(frame, 3, 0, 1, 3)
        layout.addWidget(frame, 0, 6)

        self.setLayout(layout)

        self.write_current_hitpoints()
        self.write_current_defense()

    def set_connections(self):
        self.hp_minus_button.clicked.connect(self.reduce_hitpoints)
        self.hp_plus_button.clicked.connect(self.increase_hitpoints)
        self.def_minus_button.clicked.connect(self.reduce_defense)
        self.def_plus_button.clicked.connect(self.increase_defense)
        self.stanceLabel.currentIndexChanged.connect(self.choose_stance)
        self.box_def_modifier.valueChanged.connect(self.set_defense_modifier)

    @QtCore.Slot(int)
    def choose_stance(self, new_stance):
        """
        Set the current stance.

        :param int new_stance: Index of the chosen stance.

        A character can choose between four stances identified by their index:

        0 - NEUTRAL STANCE
            By default most characters are in a neutral stance which ofers no
            bonus or penalties. Surprised characters are assumed to be in a
            neutral stance.
        1 - AGGRESSIVE STANCE
            A character taking an aggressive stance is acting with out regard
            to safety. The character sacrifices defense to increase the chances
            of success. Taking an aggressive stance lowers a character’s Defense
            by 2. When taking an aggressive stance the player can choose to gain
            a +4 bonus to goal numbers or add 2 damage efect dice to any
            successful attack. When ighting with an aggressive stance a
            character cannot pull VP to try and slip under shields. All VP must
            be converted to wounds.
        2 - DEFENSIVE STANCE
            Sometimes a character wants to live more than they want to deal
            damage. Characters taking a defensive stance are keeping their head
            down, ducking and covering, and concentrating on staying out of the
            line of ire. A character in a defensive stance gains +2 Defense, but
            takes a –4 penalty to all goal numbers until their next action.
        3 - FULL DEFENSE STANCE
            Sometimes a character may want to cover up so that they can move
            across a battleield quickly. Other times they may want to hide in a
            hole and hope no one attacks them. A character can declare full
            defense before Initiative and get +4 Defense.
            On a turn where a character declares full defense the only action
            they can take is to move (move, run, or stand/kneel/prone). If they
            choose to run they still lose 2 Defense for running.

        """
        self.current_stance = new_stance
        self.stanceLabel.setCurrentIndex(self.current_stance)

        if self.current_stance == 0:
            self.next_round_defense_modifier = 0
        elif self.current_stance == 1:
            self.next_round_defense_modifier = -2
        elif self.current_stance == 2:
            self.next_round_defense_modifier = 2
        elif self.current_stance == 3:
            self.next_round_defense_modifier = 4

    @QtCore.Slot(int)
    def set_defense_modifier(self, value):
        """
        Set a finite defense modifier.

        :param int value: The value by how much defense is altered.

        Character's defense values might be altered by several reasons - PSI,
        theurgy, GM decision.
        """
        self.defense_modifier = value

    def write_current_hitpoints(self):
        hp_text = ""

        i = 0

        while i < self.hps:
            hp_text += "o"
            i += 1

        while i < self.base_hps:
            hp_text += "_"
            i += 1

        self.hp_label.setText(hp_text)

    def write_current_defense(self):
        current_defense = (self.base_defense +
                           self.defense_modifier +
                           self.temporary_defense_modifier)

        def_text = "%i" % current_defense

        self.def_label.setText(def_text)

    def reduce_hitpoints(self, amount=1):
        self.hps -= amount
        self.write_current_hitpoints()

    def increase_hitpoints(self, amount=1):
        self.hps += amount
        self.write_current_hitpoints()

    def reduce_defense(self, amount=1):
        self.temporary_defense_modifier -= amount
        self.write_current_defense()

    def increase_defense(self, amount=1):
        self.temporary_defense_modifier += amount
        self.write_current_defense()

    def next_round(self):
        self.order = self.base_initiative + random.randint(1, 6)
        self.temporary_defense_modifier = self.next_round_defense_modifier
        self.write_current_defense()
        self.initiativeLabel.setText("%i" % self.order)


class PC(Char):
    """
    Simple character model used for NPCs where, potentially, less traits are
    required.

    :param str name: Identifier for the character
    :param int dexterity: dexterity trait
    :param int wits: wits trait
    :param int hps: hit points at the beginning of the battle
    :param int defense: characters base defense
    :param inst defense_modifier: modifiers that might vanish during battle

    Character class that allows for a smart display of the most important traits
    and easy modifications.
    """
    def __init__(self,
                 name, dexterity, wits, hps, defense,
                 defense_modifier=0,
                 parent=None):
        super(PC, self).__init__(
            name, dexterity, wits, hps, defense,
            defense_modifier)

        self.initiative_roll = 1

    def next_round(self):
        self.initiative_roll, valid = QtGui.QInputDialog.getInteger(
            self, "Dice roll",
            "What is the result of %s's initiative roll?" % self.name,
            value=self.initiative_roll,
            minValue=1, maxValue=6, step=1)
        self.order = self.base_initiative + self.initiative_roll
        self.temporary_defense_modifier = self.next_round_defense_modifier
        self.write_current_defense()
        self.initiativeLabel.setText("%i" % self.order)


class NPC(Char):
    """
    Simple character model used for NPCs where, potentially, less traits are
    required.

    :param str name: Identifier for the character
    :param int dexterity: dexterity trait
    :param int wits: wits trait
    :param int hps: hit points at the beginning of the battle
    :param int defense: characters base defense
    :param inst defense_modifier: modifiers that might vanish during battle

    Character class that allows for a smart display of the most important traits
    and easy modifications.
    """
    def __init__(self,
                 name, dexterity, wits, hps, defense,
                 defense_modifier=0,
                 parent=None):
        super(NPC, self).__init__(
            name, dexterity, wits, hps, defense,
            defense_modifier)

    def next_round(self):
        self.order = self.base_initiative + random.randint(1, 6)
        self.temporary_defense_modifier = self.next_round_defense_modifier
        self.write_current_defense()
        self.initiativeLabel.setText("%i" % self.order)

if __name__ == "__main__":
    print "Hello World!"
