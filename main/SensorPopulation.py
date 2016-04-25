#imports t
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
            if member not in memberstodelete:
                newmembers.append(member)
        self.members = newmembers
        return True
    
#s = SensorPopulation("test")
#s.members.extend([1,2,3,4,5])
#print(s.members)
#s.deleteMembers([2,4])
#print(s.members)    