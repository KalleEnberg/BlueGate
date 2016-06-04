#BlueGate - A gateway solution for Bluetooth Low Energy Wireless Sensor Networks
##*Notice! This project is not a release version and is in need of further development before usage!*
##*We ask whoever interested to fork this repository for further development, as it is unsure if the initial authors will continue the development (completed study course)*
####BlueGate is a Python gateway interface meant to run in a Kademlia network with access to a MySQL database for storing data. BlueGate provides a CLI for the user to organize and group BLE sensors, read and log values of these sensors, and to update information in them (using GATT protocol). BlueGate provides an example of combining Kademlia and bluepy in order to create a gateway solution hopefully suitable for larger WSN:s.
####BlueGate is built upon and currently has the following dependencies:
####* A working Internet connection
####* A running Kademlia network (at a minimum a running server)
####* A running MySQL database with appropriate privilieges (add and drop tables)
####* A working BLE interface (for example a BLE dongle)
####* A Linux distribution (developed and tested on Linux debian (raspbian))
####* An installed version of the following packages: Kademlia (Bmuller), python-twisted,mysql-connector-python, bluez (with related packages), bluepy, and libglib2.0-dev.
####For more installation info, we refer to the individual package installation info sites. All packages except bluepy is available via Linux apt-get installation, and a sligthly modified version of bluepy is available with BlueGate.
###Installation and usage
####To install BlueGate, clone this repository, make sure to install all above mentioned packages including running the installation for bluepy (included in the repository, for installation see bluepy documentation).
####To start BlueGate, make sure you have a Kademlia server running (tested on Bmullers Kademlia stand-alone test server). Open \__init\__.py in the main package and modify the global variables at the top with appropriate information (Gateway ID, Kademlia and MySQL information). Note that Gateway ID should be unique for each gateway connected to the Kademlia network/MySQL database. Finally, start the program by starting \__init\__.py in the main package (no arguments).
###Suggestions for further development/current issues
####* Lacking documentation (comments in source code at the moment, instruction protocol described by functions create...Instruction())
####* More thorough unit testing, and testing of the system for larger networks
####* Support for Python3, and possibly multiple platforms
####* Further development of the instruction protocol
####* Increased usability (GUI)
####* Possibilities to act based on data read from sensors
####* Possibility to update values (UUID,Major,Minor etc.) in the sensors separately, rather then all at once
####* Application Programming Interface (API) for the gateway class
####* Possibility to read data from files, or streams rather then user input
####* Improve the logging of values in the sensors
####* Web interface
####For questions regarding BlueGate, send an email to inital authors marcus.stevelind@gmail.com or kalle.enberg@gmail.com.
