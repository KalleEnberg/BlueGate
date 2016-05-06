"""Main program of the system, also contains gateway interface to user"""
#imports
#from twisted.internet import reactor
#from kademlia.network import Server
import socket
import mysql.connector
from bluepymaster.bluepy.btle import *
from mysql.connector.errors import ProgrammingError

GATEWAY_ID = "bluegate1" #change this to unique value
"""Change below values to actual database values"""
DB_HOST = "atlas.dsv.su.se"
DB_PORT = 3306
DB_NAME = "db_15482139"
DB_USER = "usr_15482139"
DB_PASSWORD = "482139"

class Gateway:
    """Main class for communication between user program and the system""" 
    def __init__(self):
        """Constructor that initializes the class attributes"""
        self.id = GATEWAY_ID
        self.ip = socket.gethostbyname(socket.gethostname())
        self.scanner = Scanner()
        self.dbconnection = self.connectToDB()
    def listPopulationDevices(self,popid):
        """returns a list of tuples with values from population corresponding to given ID
                    
        Parameters:
        popid -- the population ID"""

        c = self.dbconnection.cursor()
        c.execute("SELECT * FROM " + popid)
        return c.fetchall()
    def listPopulations(self):
        """returns a list of SensorPopulation ID:s"""
        if(self.dbconnection):
            c = self.dbconnection.cursor()
            c.execute("SELECT * FROM " + GATEWAY_ID)
            res = []
            for row in c.fetchall():
                res.append(row[0])
            return res
        return []
    def deletePopulation(self,popid):
        """deletes a SensorPopulation object
                            
        Parameters:
        popid -- the population ID"""
        c = self.dbconnection.cursor()
        c.execute("SELECT * FROM " + GATEWAY_ID + " WHERE population=%s",(popid,))
        if c.fetchall():
            c.execute("DELETE FROM " + GATEWAY_ID + " WHERE population=%s",(popid,)) #select for check
            c.execute("DROP TABLE IF EXISTS " + popid)
            print("Deleted " + popid + " from database")
        self.dbconnection.commit()
    def getPopulation(self,popid):
        """returns a SensorPopulation object
                            
        Parameters:
        popid -- the population ID"""
        values = self.listPopulationDevices(popid)
        if values:
            return SensorPopulation(popid,values)
        return False
    def addPopulation(self,popid):
        """adds a SensorPopulation to the database
                            
        Parameters:
        popid -- the population ID"""
        if(self.dbconnection):
            c = self.dbconnection.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS " + GATEWAY_ID + " (population VARCHAR(40))")
            self.dbconnection.commit()
            c.execute("CREATE TABLE IF NOT EXISTS " + popid + " (mac_address VARCHAR(20))")
            c.execute("INSERT INTO " + GATEWAY_ID + " VALUES (%s)",(popid,))
            self.dbconnection.commit()
    def connectToDB(self):
        """returns database connection if sucessfully established, else raises exception
        
        Modify values in main fields with your database information"""
        self.dbhost = DB_HOST
        self.dbname =  DB_NAME
        conn = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD,
                              host=self.dbhost,
                              port=DB_PORT,
                              database=self.dbname)
        return conn
    def updatePopulation(self,data,popid):
        """returns true if data was sucessfully sent to population
                            
        Parameters:
        data -- the data to send
        popid -- the population ID"""
        targetpop = self.getPopulation(popid)
        ibeacon = data.split(":")
        (uuid,major,minor) = (ibeacon[0], ibeacon[1], ibeacon[2])
        for p in targetpop.members:
            p.writeCharacteristic(32,uuid)
            p.writeCharacteristic(34,major)
            p.writeCharacteristic(36,minor)
            p.writeCharacteristic(50,"1234abcd")
        return True
    
class SensorPopulation:
    """Class to represent a population of sensors"""
    def __init__(self,popid,values=None):
        """Constructor that creates the population with the given ID, and if supplied also with members from values"""
        self.popid = popid
        self.members = []
        if(values):
            for row in values:
                self.members.append(Peripheral(row[0],ADDR_TYPE_RANDOM))
 
g = Gateway()
response = True
responseNumber = 0
while response:
    print ("""Welcome to BlueGate! choose an action:
  
    1. Verify database connection
    2. List all populations
    3. List a population
    4. Add a new population
    5. Add multiple populations
    6. Delete a population
    7. Delete multiple populations
    8. Start a BLE scan
    9. Show scan results
    10. Add a device to a population
    11. Add multiple devices to a population
    12. Add all devices from last scan to a population
    13. Remove a device from a population
    14. Remove multiple devices from a population
    15. Send data to a device
    16. Send data to all members of a population
    17. Quit\n""")
    responseNumber=raw_input("Enter action number:")
    if responseNumber=="1" :
        print("Connected to " + g.dbhost + ":" +  g.dbname)
    elif responseNumber=="2" :
        print("Populations:")
        for popid in g.listPopulations():
            print(popid)
    elif responseNumber=="3" :
            popid = raw_input("Enter population ID:")
            print("Devices in " + popid + ":")
            try:
                for device in g.listPopulationDevices(popid):
                    print(device[0])
            except ProgrammingError:
                print("Could not find specified population, please check the ID")
    elif responseNumber=="4" :
        popid = raw_input("Enter population ID:")
        g.addPopulation(popid)
        print("Added " + popid + " to database")
    elif responseNumber=="5" :
        popid = raw_input("Enter population IDs, separated by spaces:")
        popstoadd = popid.split(" ")
        for pop in popstoadd:
            g.addPopulation(pop)
        print("Added populations to database")
    elif responseNumber=="6" :
        popid = raw_input("Enter population ID:")
        g.deletePopulation(popid)
    elif responseNumber=="7" :
        popid = raw_input("Enter population IDs, separated by spaces:")
        popstodelete = popid.split(" ")
        for pop in popstodelete:
            g.deletePopulation(pop)
    elif responseNumber=="8" :
        """ Starts a Bluetooth LE scan and prints out the data found in the terminal, exactly what kind of data to be printed is subject to change""" #i dont get the last part 
        devices = g.scanner.scan()
        for dev in devices:
            print ("Device address:", dev.addr, "Address type:", dev.addrType, "RSSI:", dev.rssi, "Device name:", dev.getValueText(9))
    elif responseNumber=="9" :
        print("Scan results:")
        for dev in g.scanner.getDevices():
            print ("Device address:", dev.addr, "Address type:", dev.addrType, "RSSI:", dev.rssi, "Device name:", dev.getValueText(9))
    elif responseNumber=="10" :
        popid = raw_input("Enter population ID:")
        devicetoadd = str(raw_input("Enter MAC of device to add:"))
        c = g.dbconnection.cursor()
        #try:
        c.execute("INSERT INTO " + popid + " VALUES (%s)",(devicetoadd,))
        g.dbconnection.commit()
        print("Inserted " + devicetoadd + " into " + popid)
        #except ProgrammingError:
            #print("Could not find specified population or MAC was not in hex, please check the ID/MAC")
    elif responseNumber=="11" :
        devicestoadd = raw_input("Enter MAC addresses of devices to add, separated by colons:").split(":")
        popid = raw_input("Enter population ID:")
        c = g.dbconnection.cursor()
        #try:
        sql = "INSERT INTO "+ popid + " VALUES "
        for devicetoadd in devicestoadd:
            sql+= "('" + devicetoadd + "'),"
        c.execute(sql[:-1])
        g.dbconnection.commit()
        print("Inserted devices into " + popid)
        #except ProgrammingError:
    elif responseNumber=="12" :
        popid = raw_input("Enter population ID:")
        #try:
        c = g.dbconnection.cursor()
        sql = "INSERT INTO " + popid +" VALUES "
        for device in g.scanner.getDevices():
            sql += "('" + device.addr + "'),"
            c.execute(sql[:-1])
        g.dbconnection.commit()
        print("Added devices to population")
        #except ProgrammingError:
            #print("Could not find specified population, please check the ID")
    elif responseNumber=="13" :
        popid = raw_input("Enter population ID:")
        devicetoremove = str(raw_input("Enter MAC of device to remove:"))
        #try:
        c = g.dbconnection.cursor()
        c.execute("DELETE FROM " + popid + " WHERE mac_address=%s",(devicetoremove,))
        g.dbconnection.commit()
        print("Deleted " + devicetoremove + " from " + popid)
        #except ProgrammingError:
            #print("Could not find specified population or MAC, please check the ID/MAC")
    elif responseNumber=="14" :
        popid = raw_input("Enter population ID:")
        devicelist = raw_input("Enter MAC-adresses of devices to remove, separated by a colon:").split(":")
        #try:
        c = g.dbconnection.cursor()
        sql = "DELETE FROM " + popid +" WHERE mac_address IN ("
        for device in devicelist:
            sql+="'" + device + "'" + ","
            c.execute(sql[:-1] + ")")
            g.dbconnection.commit()
        print("Deleted devices from " + popid)
        #except ProgrammingError:
            #print("Could not find specified population, please check the ID")
    elif responseNumber=="15" :
        #try:
        device = Peripheral(raw_input("Enter MAC of device to send to:"),ADDR_TYPE_RANDOM)
        ibeacon = raw_input("Enter data to send (as UTF-8 strings), on the form UUID:major:minor :").split(":")
        (uuid,major,minor) = ibeacon[0], ibeacon[1], ibeacon[2]
        device.writeCharacteristic(32, uuid)
        device.writeCharacteristic(34, major)
        device.writeCharacteristic(36, minor)
        device.writeCharacteristic(50, "1234abcd")
        #except :
        print("Data sent!")
    elif responseNumber=="16" :
        popid = raw_input("Enter population ID:")
        ibeacon = raw_input("Enter data to send (as UTF-8 strings), on the form UUID:major:minor :")
        #try:
        g.updatePopulation(ibeacon, popid)
        #except ProgrammingError:
            #print("Could not find specified population, please check the ID")
        print("Population updated!")
    elif responseNumber=="17" :
        print ("Bye!")
        response = False
if g.dbconnection:
    g.dbconnection.close()
    