"""Main program of the system, also contains gateway interface to user"""
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.python import log
from kademlia.network import Server
import socket
import mysql.connector
from bluepymaster.bluepy.btle import *
from mysql.connector.errors import ProgrammingError
import thread


HANDLED_INSTRUCTIONS = []
GROUP_INSTRUCTION = 1
"""Change below values to correct values"""
GATEWAY_ID = "bluegate1"
BOOTSTRAP_IP = "192.168.50.111"
BOOTSTRAP_PORT = 8468

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
        self.bootstrap_ip = BOOTSTRAP_IP
        self.bootstrap_port = BOOTSTRAP_PORT
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
    def listGroups(self):
        """returns a list of Group ID:s"""
        if(self.dbconnection):
            c = self.dbconnection.cursor()
            c.execute("SELECT * FROM bluegroups")
            res = []
            for row in c.fetchall():
                res.append(row[0])
            return res
        return []
    def listGroup(self,groupid):
        """returns a list of tuples (gateway ID,population ID)
                            
        Parameters:
        groupid -- the group ID"""
        c = self.dbconnection.cursor()
        c.execute("SELECT * FROM " + groupid)
        return c.fetchall()
    def insertPopulation(self,groupid,gatewayid,popid):
        c = self.dbconnection.cursor()
        #add checks for existance of tables if time
        c.execute("INSERT INTO " + groupid + " VALUES (%s,%s)",(gatewayid,popid,))
        self.dbconnection.commit()
    def removePopulation(self,groupid,gatewayid,popid):
        c = self.dbconnection.cursor()
        #add checks for existance of tables if time
        c.execute("SELECT * FROM " + groupid + " WHERE gatewayid=%s AND populationid=%s",(gatewayid,popid,))
        if c.fetchall():
            c.execute("DELETE FROM " + groupid + " WHERE gatewayid=%s AND populationid=%s",(gatewayid,popid,))
        self.dbconnection.commit()
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
    def addGroup(self,groupid):
        """adds a group to the database
                            
        Parameters:
        groupid -- the group ID"""
        if(self.dbconnection):
            c = self.dbconnection.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS bluegroups (groupid VARCHAR(40))")
            c.execute("CREATE TABLE IF NOT EXISTS " + groupid + " (gatewayid VARCHAR(40), populationid VARCHAR(40))")
            self.dbconnection.commit()
            c.execute("INSERT INTO bluegroups VALUES (%s)",(groupid,))
            self.dbconnection.commit()
    def deleteGroup(self,groupid):
        """deletes a group from database
                            
        Parameters:
        groupid -- the group ID"""
        c = self.dbconnection.cursor()
        c.execute("SELECT * FROM bluegroups WHERE groupid=%s",(groupid,))
        if c.fetchall():
            c.execute("DELETE FROM bluegroups WHERE groupid=%s",(groupid,)) #select for check
            c.execute("DROP TABLE IF EXISTS " + groupid)
            print("Deleted " + groupid + " from database")
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
        #print("updatepop kors!")
        targetpop = self.getPopulation(popid)
        (uuid,major,minor,soft_reboot) = (data[0], data[1], data[2],data[3])
        for p in targetpop.members:
            p.writeCharacteristic(32,uuid)
            p.writeCharacteristic(34,major)
            p.writeCharacteristic(36,minor)
            p.writeCharacteristic(50,soft_reboot)
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
    
def createPopInstruction(gatewayid,popid,uuid,major,minor,soft_reboot):
    return gatewayid + "," + popid + "," + uuid + "," + major + "," + minor + "," + soft_reboot + "," + str(time.time() * 1000)

def createGroupsInstruction(groupids,uuid,major,minor,soft_reboot):
    res = ""
    for groupid in groupids:
        res += groupid + ":"
    return res[:-1] + "," + uuid + "," + major + "," + minor + "," + soft_reboot + "," + str(time.time() * 1000)

def interpretPopInstruction(result,gateway):
    print(result)
#     if result == None or result.split(",")[0] != GATEWAY_ID or result.split(",")[6] in  HANDLED_INSTRUCTIONS:
#         print("denna galler")
#     else:        
#         instruction = result.split(",")
#         gateway.updatePopulation(instruction[2:5],instruction[1])
#         print("instruction handled!")

def interpretGroupsInstruction(result,server,gateway):
    if result == None or result.split(",")[5] in  HANDLED_INSTRUCTIONS:
        pass
    else:
        instruction = result.split(",")
        groups = instruction[0].split(":")
        populationstoupdate = []
        for group in groups:
            for row in gateway.listGroup(group):
                if(row[0] == GATEWAY_ID):
                    populationstoupdate += row[1]
        for population in populationstoupdate:
            gateway.updatePopulation(instruction[1:4],population)
            print(population + "updated!")
        print("instruction handled!")

def kademliaPopInstructionListener(args):
    print("lyssnar")
    server = args[0]
    gateway = args[1]
    server.get("UPDATE_POPULATION").addCallback(interpretPopInstruction,gateway) #ska returnera och lasa resultat i en annan funktion (med callback).
def kademliaGroupInstructionListener(args):
    server = args[0]
    gateway = args[1]
    server.get("UPDATE_GROUPS").addCallback(interpretGroupsInstruction,server,gateway)
                    
def main(server,gateway):
    g = gateway
    response = True
    responseNumber = 0
    while response:
        print ("""Welcome to BlueGate! choose an action:
      
        1. Verify database and Kademlia connection
        2. List all local populations
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
        16. Send data to all members of a local population
        17. Send data to all members of a remote population
        18. List all groups
        19. List a group
        20. Create a group of populations
        21. Add a population to a group (populations of other BlueGates is accepted)
        22. Delete a population from a group
        23. Delete a group
        24. Send data to a group
        25. Quit\n""")
        responseNumber=raw_input("Enter action number:")
        if responseNumber=="1" :
            print("Connected to database: " + g.dbhost + ":" +  g.dbname)
            print("Connected to bootstrap server: " + g.bootstrap_ip + ":" + str(g.bootstrap_port))
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
            print("Scanning for devices (10 sec)...")
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
            ibeacon = raw_input("Enter data to send (as UTF-8 strings), on the form UUID:major:minor:soft_reboot_password :").split(":")
            #try:
            g.updatePopulation(ibeacon, popid)
            #except ProgrammingError:
                #print("Could not find specified population, please check the ID")
            print("Population updated!")
        elif responseNumber == "17" :
            gatewayid = raw_input("Enter target gateway ID:")
            popid = raw_input("Enter population ID:")
            ibeacon = raw_input("Enter data to send (as UTF-8 strings), on the form UUID:major:minor:soft_reboot_password :").split(":")
            print("Instruction sent!")
            server.set("UPDATE_POPULATION",createPopInstruction(gatewayid, popid,ibeacon[0],ibeacon[1], ibeacon[2], ibeacon[3]))
        elif responseNumber=="18" :
            print("Groups:")
            for group in g.listGroups():
                print(group)
        elif responseNumber=="19" :
            groupid = raw_input("Enter group ID:")
            print("Populations in " + groupid + ":")
            for row in g.listGroup(groupid):
                print(row[0] + ":" + row[1])
        elif responseNumber=="20" :
            groupid = raw_input("Enter group ID:")
            g.addGroup(groupid)
            print(groupid + " was added to database")
        elif responseNumber=="21" :
            groupid = raw_input("Enter group ID:")
            gatewayid = raw_input("Enter gateway ID where population exists:")
            popid = raw_input("Enter population ID:")
            g.insertPopulation(groupid,gatewayid,popid)
            print(gatewayid + ":" + popid + " was inserted into " + groupid)
        elif responseNumber=="22" :
            groupid = raw_input("Enter group ID:")
            gatewayid = raw_input("Enter gateway ID where population exists:")
            popid = raw_input("Enter population ID:")
            g.removePopulation(groupid,gatewayid,popid)
            print(gatewayid + ":" + popid + " was deleted from " + groupid)
        elif responseNumber=="23" :
            groupid = raw_input("Enter group ID:")
            g.deleteGroup(groupid)
            print("Deleted " + groupid + " from database")
        elif responseNumber=="24" :
            groupids = raw_input("Enter group ID:s, separated by commas:").split(",")
            ibeacon = raw_input("Enter data to send (as UTF-8 strings), on the form UUID:major:minor:soft_reboot_password :").split(":")
            print("Instructions sent!")
            server.set("UPDATE_GROUPS",createGroupsInstruction(groupids, ibeacon[0],ibeacon[1],ibeacon[2],ibeacon[3])).addCallback(waitAndClear,GROUP_INSTRUCTION,server,g) #PROBLEM, inget skickas till servern?
        elif responseNumber=="25" :
            print ("Bye!")
            response = False
            reactor.stop() #Make flag for killing the threads before this call
    if g.dbconnection:
        g.dbconnection.close()
#log.startLogging(sys.stdout) #ta bort kommentar for loggning i nod

gateway = Gateway()
server = Server()
server.listen(BOOTSTRAP_PORT)
server.bootstrap([(BOOTSTRAP_IP, BOOTSTRAP_PORT)])

#grouploop = LoopingCall(kademliaGroupInstructionListener,(server,gateway)) 
#grouploop.start(1)
poploop = LoopingCall(kademliaPopInstructionListener,(server,gateway))
poploop.start(1)

#main(server,gateway)
reactor.run()