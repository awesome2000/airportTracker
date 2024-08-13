

from aeroapi_python import AeroAPI
import curses
import time
import datetime
import configparser
from datetime import timezone
from curses.textpad import Textbox, rectangle



global api_key
global refreshRate  
global rectangleWidth 
global rectangleHeight 
global airportName 
global readFromFile
global debugFileName

def main():

    readConfigFile("config.ini")
    if readFromFile == 0 and api_key == "YOUR_KEY_HERE":
        print("ERROR: Did you set the API key in config.ini?")
        raise Exception("api key not valid")

    if readFromFile == 1:
        flightInfo = eval(readFlightData(debugFileName))
    else: 
        flightInfo = getFlightData(airportName)
    

    #get most recent 3 arrivals & departures
    mostRecentThreeArrivals = [flightInfo['arrivals'][0], flightInfo['arrivals'][1], flightInfo['arrivals'][2]]
    mostRecentThreeDepartures = [flightInfo['departures'][0], flightInfo['departures'][1], flightInfo['departures'][2]]

    stdscr = curses.initscr()
    myRectangles = setUpGui(stdscr)


    #draw Arrival Flights
    drawFlight(stdscr, myRectangles[0], mostRecentThreeArrivals[0], 0)
    drawFlight(stdscr, myRectangles[0], mostRecentThreeArrivals[1], 1)
    drawFlight(stdscr, myRectangles[0], mostRecentThreeArrivals[2], 2)

    #draw Departure Flights
    drawFlight(stdscr, myRectangles[1], mostRecentThreeDepartures[0], 0)
    drawFlight(stdscr, myRectangles[1], mostRecentThreeDepartures[1], 1)
    drawFlight(stdscr, myRectangles[1], mostRecentThreeDepartures[2], 2)

    #draw quit message to bottom of screen
    stdscr.addstr(rectangleHeight+1,  0, "Press 'q' to quit")
    
    while True:
        stdscr.refresh()
        escapeKey = stdscr.getch()
        if escapeKey < 0:  #no valid key entered
            time.sleep(refreshRate)
        elif escapeKey == ord('q'):
            break
        elif escapeKey == ord('r'):
            stdscr.refresh()
    

    #clean up curses screen
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

#Gets flight data. Useful when not reading from file
def getFlightData(airportName):
    aeroapi = AeroAPI(api_key)
    myAirports = aeroapi.airports
    recentFlights = myAirports.all_flights(airportName)
    return recentFlights

#Reads flight data from stored txt file
def readFlightData(fileName):
    dictFile = open(fileName, "r")
    myReturn = dictFile.read()
    dictFile.close()
    return myReturn

#Draws a flight info in given rectangle
def drawFlight(stdscr, myDisplayRect, myFlight, entryNum):
    try:
        myString = ""
        originAirport = myFlight['origin']['city']

        #flight may not have a destination
        if myFlight['destination'] == None:
            destAirport = "(No dest set)"
        else:
            destAirport = myFlight['destination']['city']

        ident = myFlight['ident']

        #Determine if arrival or departure
        if myFlight['origin']['code'] == airportName:
            myTime = "dept " + datetime.datetime.fromisoformat(myFlight['actual_off']).astimezone().time().isoformat()  #departure
        elif myFlight['destination']['code'] == airportName:
            myTime = "arrv " +datetime.datetime.fromisoformat(myFlight['actual_on']).astimezone().time().isoformat() #arrival
        else:
            raise Exception("Error: flight didn't depart or arrive at " + airportName)
        

        myString += ident + " | " + originAirport + "->" + destAirport + " | " + myTime
        stdscr.addstr(myDisplayRect.uly + 1 + entryNum, myDisplayRect.ulx + 1, myString)
    
    
    except:
        stdscr.addstr(myDisplayRect.uly + 1 + entryNum, myDisplayRect.ulx + 1, "ERROR DISPLAYING FLIGHT")

    finally:
        stdscr.refresh()


#A rectangle class for use with curses
class displayRect:
    def __init__(self, uly2, ulx2, lry2, lrx2):
        self.uly = uly2
        self.ulx = ulx2
        self.lry = lry2
        self.lrx = lrx2

    def draw(self, stdscr):
        rectangle(stdscr, self.uly, self.ulx, self.lry, self.lrx)

#sets up GUI, returning displayRect objects for Left and Right rectangle.
def setUpGui(stdscr):
    #init curses screen (full screen terminal)
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    begin_x = 0; begin_y = 0
    height = curses.LINES; width = curses.COLS
    win = curses.newwin(height, width, begin_y, begin_x)
    win.refresh()
    stdscr.addstr(0, 1, "Recent Flight Arrivals")
    stdscr.addstr(0, rectangleWidth + 1, "Recent Flight Departures")

    leftRect = displayRect(1,1, rectangleHeight, rectangleWidth)
    leftRect.draw(stdscr)

    rightRect = displayRect(1, rectangleWidth + 1 , rectangleHeight, rectangleWidth + rectangleWidth + 1)
    rightRect.draw(stdscr)

    return [leftRect, rightRect]

#reads config file and sets global variables
def readConfigFile(fileName):

    global api_key
    global refreshRate 
    global rectangleWidth  
    global rectangleHeight 
    global airportName 
    global readFromFile
    global debugFileName



    config = configparser.ConfigParser()
    config.read(fileName)

    api_key = config.get('settings','api_key')
    refreshRate =  int(config.get('settings','refreshRate'))  #Screen refresh rate in seconds
    rectangleWidth = int(config.get('settings','rectangleWidth'))  #Dimensions for rectangles containing flight information
    rectangleHeight = int(config.get('settings','rectangleHeight'))
    airportName = config.get('settings','airportName')
    readFromFile = int(config.get('settings','readFromFile'))
    debugFileName = config.get('settings','debugFileName')
    

if __name__ == '__main__':
    main()