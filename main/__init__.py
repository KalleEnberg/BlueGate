"""Main program of the system, also contains gateway interface to user"""
#imports
import socket
import mysql.connector
from bluepymaster.bluepy.btle import *
from mysql.connector.errors import ProgrammingError
class Gateway:
    """Main class for communication between user program and the system""" 
    def __init__(self):
        """Constructor that initializes the class attributes
            
        Parameters:
        dbid -- the database ID (default None)
        """
        self.ip = socket.gethostbyname(socket.gethostname())
        self.scanner = Scanner()
        self.dbconnection = self.connectToDB()
    def listPopulation(self,popid):
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
        c = self.dbconnection.cursor()
        c.execute("DROP TABLE IF EXISTS " + popid)
        self.dbconnection.commit()
        return True
    def getPopulation(self,popid):
        """returns a SensorPopulation object
                            
        Parameters:
        popid -- the population ID"""
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
            self.dbconnection.commit()
            return True
        return False
    def getDB(self):
        """returns a string identifying current database"""
        return self.dbhost + ":" +  self.dbname
    def connectToDB(self):
        """returns database connection if sucessfully established, else raises exception
        
        Modify values in this method with your database information"""
        self.dbhost = "atlas.dsv.su.se"
        self.dbname =  "db_15482139"
        conn = mysql.connector.connect(user="usr_15482139", password="482139",
                              host=self.dbhost,
                              port=3306,
                              database=self.dbname)
        return conn
    def updatePopulation(self,data,popid):
        """returns true if data was sucessfully sent to population
                            
        Parameters:
        data -- the data to send
        popid -- the population ID"""
        targetpop = self.getPopulation(popid)
        ibeacon = data.split(":")
        (uuid,major,minor) = (str.encode(ibeacon[0]),str.encode(ibeacon[1]),str.encode(ibeacon[2]))
        for p in targetpop.getMembers():
            p.writeCharacteristic(32,uuid) #withresponse om detta skapar major interference
            p.writeCharacteristic(34,major)
            p.writeCharacteristic(36,minor)
            p.writeCharacteristic(50,str.encode("1234abcd"))
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
    11. Add all devices from last scan to a population
    12. Remove a device from a population
    13. Remove multiple devices from a population
    14. Send data to a device
    15. Send data to all members of a population
    16. Quit\n""")
    responseNumber=input("Enter action number:")
    if responseNumber=="1" :
        print("Connected to " + g.getDB())
    elif responseNumber=="2" :
        print("Populations:")
        for popid in g.listPopulations():
            print(popid)
    elif responseNumber=="3" :
            popid = input("Enter population ID:")
            print("Devices in " + popid + ":")
            try:
                for device in g.listPopulation(popid):
                    print(device[0])
            except ProgrammingError:
                print("Could not find specified population, please check the ID")
    elif responseNumber=="4" :
        popid = input("Enter population ID:")
        g.addPopulation(popid)
        print("Added " + popid + " to database")
    elif responseNumber=="5" :
        popid = input("Enter population IDs, separated by spaces:")
        popstoadd = popid.split(" ")
        for pop in popstoadd:
            g.addPopulation(pop)
        print("Added populations to database")
    elif responseNumber=="6" :
        popid = input("Enter population ID:")
        g.deletePopulation(popid)
        print("Deleted " + popid + " from database")
    elif responseNumber=="7" :
        popid = input("Enter population IDs, separated by spaces:")
        popstodelete = popid.split(" ")
        for pop in popstodelete:
            g.deletePopulation(pop)
        print("Deleted populations from database")
    elif responseNumber=="8" :
        """ Starts a Bluetooth LE scan and prints out the data found in the terminal, exactly what kind of data to be printed is subject to change"""
        devices = g.scanner.scan()
        for dev in devices:
            print ("Device address:", dev.addr, "Address type:", dev.addrType, "RSSI:", dev.rssi)
            
            #print (dev, dev.addr, dev.addrType, dev.rssi)
            """Prints out some additional data like Manufacturer etc. can be a bit unnecessary"""
            #for (adtype, desc, value) in dev.getScanData():
                #print (adtype, desc, value)
                
    elif responseNumber=="9" :
        print("Scan results:")
        for dev in g.scanner.getDevices():
            print(dev.addr)
    elif responseNumber=="10" :
        devicetoadd = str(input("Enter MAC of device to add:"))
        popid = input("Enter population ID:")
        c = g.dbconnection.cursor()
        #try:
        c.execute("INSERT INTO " + popid + " VALUES (%s)",(devicetoadd,))
        g.dbconnection.commit()
        print("Inserted " + devicetoadd + " into " + popid)
        #except ProgrammingError:
            #print("Could not find specified population or MAC was not in hex, please check the ID/MAC")
    elif responseNumber=="11" :
        popid = input("Enter population ID:")
        try:
            c = g.dbconnection.cursor()
            sql = "INSERT INTO " + popid + " VALUES "
            for device in g.scanner.getDevices():
                sql += "('" + device.addr + "'),"
            c.execute(sql[:-1])
            g.dbconnection.commit()
            #MESSAGE!
        except ProgrammingError:
            print("Could not find specified population, please check the ID")
    elif responseNumber=="12" :
        popid = input("Enter population ID:")
        devicetoremove = str(input("Enter MAC of device to remove:"))
        try:
            c = g.dbconnection.cursor()
            c.execute("DELETE FROM " + popid + " WHERE mac_address=%s",(devicetoremove,))
            g.dbconnection.commit()
            print("Deleted " + devicetoremove + " from " + popid)
        except ProgrammingError:
            print("Could not find specified population or MAC, please check the ID/MAC")
    elif responseNumber=="13" :
        popid = input("Enter population ID:")
        devicelist = input("Enter MAC-adresses of devices to remove, separated by a space:").split(" ")
        try:
            c = g.dbconnection.cursor()
            sql = "DELETE FROM " + popid + " WHERE mac_address IN ("
            for device in devicelist:
                sql+="'" + device + "'" + ","
                c.execute(sql[:-1] + ")")
                g.dbconnection.commit()
            print("Deleted devices from " + popid)
        except ProgrammingError:
            print("Could not find specified population, please check the ID")
    elif responseNumber=="14" :
        #try:
        device = Peripheral(input("Enter MAC of device to send to:"),ADDR_TYPE_RANDOM)
        ibeacon = input("Enter data to send (in hex), on the form UUID:major:minor :").split(":")
        (uuid,major,minor) = (str.encode(ibeacon[0]),str.encode(ibeacon[1]),str.encode(ibeacon[2]))
        device.writeCharacteristic(32, uuid)
        device.writeCharacteristic(34, major)
        device.writeCharacteristic(36, minor)
        device.writeCharacteristic(50,str.encode("1234abcd"))
        #except :
        print("Data sent!")
    elif responseNumber=="15" :
        popid = input("Enter population ID:")
        ibeacon = input("Enter data to send (in hex), on the form UUID:major:minor :")
        try:
            g.updatePopulation(ibeacon, popid)
        except ProgrammingError:
            print("Could not find specified population, please check the ID")
        print("Population updated!")
    elif responseNumber=="16" :
        print ("Bye!")
        response = False
if g.dbconnection:
    g.dbconnection.close()