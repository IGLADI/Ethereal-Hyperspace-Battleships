from player import Player
from threading import Thread
import data
import time

class Tutorial:
    def __init__(self, player: Player):
        self._player = player
        self._travelled = False
        self._used_radar = False
        self._combat = False
        self._mined = False
        self._upgraded = False
        data.tutorials[player.id] = self

    def travel_to_Ruebn(self):
        locationThread = Thread(target=self.await_location, args=(self._player,))
        locationThread.start()

    def await_location(self, player: Player):
        while (player.x_pos != 0 or player.y_pos != 0):
            time.sleep(1)
        self._travelled = True

    def scan_for_pirates(self):
        scanThread = Thread(target=self.await_scan, args=())
        scanThread.start()

    def await_scan(self):
        while (self._used_radar == False):
            time.sleep(1)

    # TODO add combat!
    # def combat(self):
    #     combatThread = Thread(target=self.await_combat, args=())
    #     combatThread.start()

    # def await_combat(self):
    #     while (self._combat == False):
    #         time.sleep(1)

    def mine(self):
        mineThread = Thread(target=self.await_mine, args=())
        mineThread.start()

    def await_mine(self):
        while (self._mined == False):
            time.sleep(1)
    
    def upgrade(self):
        upgradeThread = Thread(target=self.await_upgrade, args=())
        upgradeThread.start()

    def await_upgrade(self):
        while (self._upgraded == False):
            time.sleep(1)