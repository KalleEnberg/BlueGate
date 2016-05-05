'''
Simple tests on BlueGate (Excluding BLE tests since they are highly situational)

Created on 5 maj 2016

@author: Kalle
'''
import unittest
from main import Gateway
from mysql.connector.errors import ProgrammingError

g = Gateway()
class Test(unittest.TestCase):


    def test_listPopulationDevices(self):
        self.assertTrue(g.listPopulationDevices("ziggy"))
        with self.assertRaises(ProgrammingError):
            g.listPopulationDevices("sdad")
    
    def test_listPopulations(self):
        self.assertTrue(g.listPopulations())
        #self.assertEqual(g.listPopulations(),["ziggy"])
    
    def test_deletePopulation(self):
        g.addPopulation("ziggy2")
        g.deletePopulation("ziggy2")
        self.assertFalse("ziggy2" in g.listPopulations())
        self.assertFalse(g.deletePopulation("popid"))
        
    def test_getPopulation(self):
         with self.assertRaises(ProgrammingError):
            g.getPopulation("sdad")
    
    def test_addPopulation(self):
        self.assertFalse(g.addPopulation("ziggy3"))
        self.assertTrue("ziggy3" in g.listPopulations())
        
    def test_connectToDB(self):
        self.assertTrue(g.connectToDB())
        
if __name__ == "__main__":
    unittest.main()