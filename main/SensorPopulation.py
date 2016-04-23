#imports
from bluepymaster.bluepy.btle import Peripheral
class SensorPopulation:
    """Class to represent a population of sensors"""
    def __init__(self,popid,values=None):
        """Constructor that creates the population with the given ID, and if supplied also with members from values"""
        self.popid = popid
        self.members = []
        if(values):
            for row in values:
                self.members.append(Peripheral(row[1]))
    def deleteMembers(self,memberstodelete):
        """Deletes specified members by creating a new list without them"""
        newmembers = []
        for member in self.members:
            lambda member: newmembers.append(member) if member not in memberstodelete else None
        self.members = newmembers
        return True