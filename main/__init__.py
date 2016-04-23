"""Main program of the system, also contains gateway interface to user"""
#imports
import socket
import mysql.connector
from main.SensorPopulation import SensorPopulation
from bluepymaster.bluepy.btle import Scanner
class Gateway:
    """Main class for communication between user program and the system""" 
    def __init__(self,dbhost=None,dbport=None,dbname=None,dbuser=None,dbpassword=None):
        """Constructor that initializes the class attributes
            
        Parameters:
        dbid -- the database ID (default None)
        """
        self.ip = socket.gethostbyname(socket.gethostname())
        #self.mac = getMacAdress() Ska vi strunta i denna? är klurig att ta fram kan diskuteras på fredag
        (self.dbhost,self.dbport,self.dbname,self.dbuser,self.dbpassword) = (dbhost,dbport,dbname,dbuser,dbpassword)
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
        """returns database connection if sucessfully established, else raises exception"""
        conn = mysql.connector.connect(user=self.dbuser, password=self.dbpassword,
                              host=self.dbhost,
                              port=self.dbport,
                              database=self.dbname)
        return conn
    def updatePopulation(self,data,popid): #se diskussion i planering
        """returns true if data was sucessfully sent to population
                            
        Parameters:
        data -- the data to send
        popid -- the population ID"""
        targetpop = self.getPopulation(popid)
        #for p in targetpop.getMembers():
            #p.connect()
        
        return None

#g = Gateway("atlas.dsv.su.se",3306,"db_15482139","usr_15482139","482139")
#print(g.getPopulation("strawberry"))
#g.dbconnection.close()