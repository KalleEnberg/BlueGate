"""Main program of the system, also contains gateway interface to user"""
#imports
import socket
import mysql.connector
from bluepymaster.bluepy.btle import Scanner,Peripheral
class Gateway:
    """Main class for communication between user program and the system""" 
    def __init__(self):
        """Constructor that initializes the class attributes
            
        Parameters:
        dbid -- the database ID (default None)
        """
        self.ip = socket.gethostbyname(socket.gethostname())
        #self.mac = getMacAdress() Ska vi strunta i denna? är klurig att ta fram kan diskuteras på fredag t
        self.dbconnection = self.connectToDB()
    def getIP(self): #verkar inte ha betydelse inom lokal fil (attribut direkt åtkomliga), har den betydelse för anrop från andra filer?
        """Returns the device IP"""
        return self.ip
    def getMac(self): #se diskussion i konstruktor
        """returns the device Bluetooth mac adress"""
        return None
    def startScan(self):
        """returns a Scanner object"""
        return Scanner()
    def listScan(self):
        """returns a Scanner object""" #fast ska nog inte göra det...
        return Scanner()
    def listPopulation(self,popid):
        """returns a list of tuples with values from population corresponding to given ID
                    
        Parameters:
        popid -- the population ID"""
        if(self.dbconnection):
            c = self.dbconnection.cursor()
            c.execute("SELECT * FROM " + popid)
            return c.fetchall()
        return False
    def listPopulations(self):
        """returns a list of SensorPopulation ID:s"""
        if(self.dbconnection):
            c = self.dbconnection.cursor()
            c.execute("SELECT * FROM information_schema.tables WHERE table_schema='" + self.dbname + "'") 
            res = []
            for row in c.fetchall():
                res.append(row[2])
            return res
        return []
    def deletePopulation(self,popid):
        """deletes a SensorPopulation object
                            
        Parameters:
        popid -- the population ID"""
        if(self.dbconnection):
            c = self.dbconnection.cursor()
            c.execute("DROP TABLE IF EXISTS " + popid)
            return True
        return False
    def getPopulation(self,popid):
        """returns a SensorPopulation object
                            
        Parameters:
        popid -- the population ID""" #eller?
        values = self.listPopulation(popid)
        if values:
            return SensorPopulation(popid,values)
        return False
    def addPopulation(self,popid):
        """adds a SensorPopulation to the database
                            
        Parameters:
        popid -- the population ID"""
        if(self.dbconnection):
            c = self.dbconnection.cursor()
            c.execute("CREATE TABLE " + popid + " (mac_address VARCHAR(20))")
            return True
        return False
    def getDB(self):
        """returns a string identifying current database"""
        return self.dbhost + ":" +  self.dbname
    def connectToDB(self):
        """returns database connection if sucessfully established, else raises exception
        
        Modify values in this method with your database information"""
        self.dbhost = "atlas.dsv.su.se"
        self.dbport = 3306
        conn = mysql.connector.connect(user="usr_15482139", password="482139",
                              host=self.dbhost,
                              port=self.dbport,
                              database="db_15482139")
        return conn
    def updatePopulation(self,data,popid): #se diskussion i planering
        """returns true if data was sucessfully sent to population
                            
        Parameters:
        data -- the data to send
        popid -- the population ID"""
        targetpop = self.getPopulation(popid)
        ibeacon = str.split(":")
        (uuid,major,minor) = (ibeacon[0],ibeacon[1],ibeacon[2])
        for p in targetpop.getMembers():
            p.writeCharacteristic(0x01,uuid) #withresponse om detta skapar major interference
            p.writeCharacteristic(0x02,major)
            p.writeCharacteristic(0x03,minor)
        return True
    
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
    
g = Gateway()
response = True
responseNumber = 0
while response:
    print ("""Welcome to BlueGate! choose an action:

    1. Verify database connection
    2. List all populations
    3. List a population
    4. Add a new population
    5. Delete a population
    6. Delete multiple populations
    7. Start a BLE scan
    8. Show scan results
    9. Add a device to a population
    10. Add all devices from scan to a population
    11. Send data to a member of a population
    12. Send data to all members of a population
    13. Quit\n""")
    responseNumber=input("Enter action number:")
    if responseNumber=="1" :
        print ("hubba bubba")
    elif responseNumber=="2" :
        print ("hubba bubba2")
    elif responseNumber=="3" :
        print ("hubba bubba3")
    elif responseNumber=="4" :
        print ("hubba bubba4")
    elif responseNumber=="5" :
        print ("hubba bubba5")
    elif responseNumber=="6" :
        print ("hubba bubba6")
    elif responseNumber=="7" :
        print ("hubba bubba7")
    elif responseNumber=="8" :
        print ("hubba bubba8")
    elif responseNumber=="9" :
        print ("hubba bubba9")
    elif responseNumber=="13" :
        print ("Bye")
        response = False
if g.dbconnection:
    g.dbconnection.close()