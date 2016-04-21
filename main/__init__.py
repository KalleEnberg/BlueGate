"""Main program of the system, also contains gateway interface to user"""
#imports
import socket
from bluepymaster.bluepy.btle import Scanner
class Gateway:
    """Main class for communication between user program and the system""" 
    def __init__(self,dbid=None):
        """Constructor that initializes the class attributes
            
        Parameters:
        dbid -- the database ID (default None)
        """
        self.ip = socket.gethostbyname(socket.gethostname())
        #self.mac = getMacAdress() Ska vi strunta i denna? är klurig att ta fram kan diskuteras på fredag
        self.dbid = dbid
    def getIP(self): #verkar inte ha betydelse inom lokal fil (attribut direkt åtkomliga), har den betydelse för anrop från andra filer?
        """Returns the device IP"""
        return self.ip
    def getMac(self): #se diskussion i konstruktor
        """returns the device Bluetooth mac adress"""
        return None
    def startScan(self):
        """returns a Scanner object"""
        return None
    def listScan(self):
        """returns a Scanner object""" #fast ska nog inte göra det...
        return None
    def listPopulation(self,popid):
        """returns a SensorPopulation object
                    
        Parameters:
        popid -- the population ID"""
        return None
    def listPopulations(self):
        """returns a list of SensorPopulation objects"""
        return None
    def deletePopulation(self,popid):
        """deletes a SensorPopulation object
                            
        Parameters:
        popid -- the population ID"""
        return None
    def getPopulation(self,popid):
        """returns a SensorPopulation object
                            
        Parameters:
        popid -- the population ID""" #eller? ska enligt klassdiagram returnera void, vad skiljer denna mot listpopulation?
        return None
    def addPopulation(self,popid):
        """adds a SensorPopulation to the database
                            
        Parameters:
        popid -- the population ID"""
        return None
    def getDB(self):
        """returns a dbid string"""
        return None
    def setDB(self,host,port,user,password):
        """returns true if database connection was established"""
        return None
    def updatePopulation(self,data,popid):
        """returns true if data was sucessfully sent to population
                            
        Parameters:
        data -- the data to send
        popid -- the population ID"""
        return None

#g = Gateway()
#print(g.getIP())