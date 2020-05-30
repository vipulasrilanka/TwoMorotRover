import socket
import pygame as Canvas
from time import sleep
NormalSpeed = 50       

# This class represents the remote rover
# It has to be initialised with a name, the IP address and the port.  
# The Name can be verified with Remote. It's not implemented yet.
# No Security protocal has been implemented yet.

class Remote_Rover:
    
    # initialization of the class.
    # Need a name, IP and the port of the remote Rover 
    # Does not check the validity of the remote Rover. #Improve

    def __init__(self,name, ipAddress, port):
        self.byte_message = bytes("0", "utf-8")
        self.name = name
        self.Direction = "C"    # Direction, L, R or C for Centre.
        self.Run  = "F"         # Run Forward or Backword.
        self.Turn_Angle = 0     # Turn Angle
        self.Run_Speed = 0      #Run Speed (0-100)
        self.BreakStatus = 'R'  #Break Released (R) or (A)
        self.GearPosition = 'N' #Gear Neutral (N), (D), (R) or a number is valid for this 
        self.RemoteIP = ipAddress   #IP address of the Rover
        self.port = port            #UDP port
        #Create the port for writing.
        self.opened_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

    # Terminate the remote rover
    # The current implementation forces the remote thread who is waiting for commands to exit.
    # Remote connect/Disconnet is not implemented #Improve

    def __del__(self):
        print("Terminate")
        self.opened_socket.sendto(bytes("CNTR", "utf-8"), (self.RemoteIP, self.port))   #Centre the Steering
        self.opened_socket.sendto(bytes("NBRK", "utf-8"), (self.RemoteIP, self.port))   #Release Dynamic Break
        self.opened_socket.sendto(bytes("NUTR", "utf-8"), (self.RemoteIP, self.port))   #Gear to Neutral
        self.opened_socket.sendto(bytes("TERM", "utf-8"), (self.RemoteIP, self.port))   #Terminate the remote Listner
        # Close the socket #improve

 
    # Turn function 
    # The current implementation does not care about the Angle. 
    # Best is to send the Angle and ignore at the remote end. #Improve

    def Turn(self, direction, angle):
        if direction == 'L':
            self.Direction = "L"
            self.opened_socket.sendto(bytes("LEFT", "utf-8"), (self.RemoteIP, self.port))
        elif direction == 'R':
            self.Direction = "R"
            self.opened_socket.sendto(bytes("RIGT", "utf-8"), (self.RemoteIP, self.port))
        else:
            self.Direction = "C"
            self.opened_socket.sendto(bytes("CNTR", "utf-8"), (self.RemoteIP, self.port))
        print ("Turn",direction, angle)
            
    # Gear Shift Function 
    # This Sets the Gear, but does not move the Rover.
                
    def Gear(self,gear):
        if gear == 'N':
            self.opened_socket.sendto(bytes("NUTR", "utf-8"), (self.RemoteIP, self.port))
        elif gear == 'R':
            self.opened_socket.sendto(bytes("REVR", "utf-8"), (self.RemoteIP, self.port))
        else:
            # for all other inputs we set the gear to Drive. 
            # Need to check the validity of the input 
            # #Improve 
            self.opened_socket.sendto(bytes("FWRD", "utf-8"), (self.RemoteIP, self.port))
        self.GearPosition = gear
        print ("Drive",self.GearPosition)
            
    # Gear Accelerate function ( Speed values : 0 - 99)
    
    def Speed(self,speed):
        if self.GearPosition == 'N':
            self.Run_Speed = 0
            print ("Neutral. Can not go.!")
        elif self.BreakStatus == 'A':
            print ("Break ON. Can not go.!")
            self.Run_Speed = 0
        else:
            # Create the Speed packet. 
            # For the moment, we have only two bytes for the Speed e.g. SP75 (75% speed)
            # Need to check if the "speed" qualifies for above restriction. #improve
            self.Run_Speed = speed
            self.SpeedCommand = "SP"+str(speed)
            self.opened_socket.sendto(bytes(self.SpeedCommand, "utf-8"), (self.RemoteIP, self.port))
            print ("speed", speed)

    # Apply Break (A) = Activate, (R) = Release

    def Break(self, activate):
        if activate == 'A':#Apply break
          self.opened_socket.sendto(bytes("BREK", "utf-8"), (self.RemoteIP, self.port))
          print ("Break on")
        elif activate == 'R':#Release Break
          self.opened_socket.sendto(bytes("NBRK", "utf-8"), (self.RemoteIP, self.port))
          print ("Break Release")
          #self.Gear(self.GearPosition) #back to active Gear
        else:
          print ("error")
        self.BreakStatus = activate 

    # Debug function to dump the current state

    def DumpGpioMap(self):
        print("Name: ",self.name) 
        print("Turn: ",self.Direction)  
        print("Turn Angle: ",self.Turn_Angle) 
#        print("Drive: ",self.Run)  
        print("Gear: ",self.GearPosition)
        print("Break: ",self.BreakStatus) 
        print("Drive Speed: ",self.Run_Speed)

    # Start the remote rover

    def RoverStart(self):
        print("Start")
        self.opened_socket.sendto(bytes("CNTR", "utf-8"), (self.RemoteIP, self.port))
        self.opened_socket.sendto(bytes("NBRK", "utf-8"), (self.RemoteIP, self.port))
        self.opened_socket.sendto(bytes("NUTR", "utf-8"), (self.RemoteIP, self.port))

    # Stop the remote rover

    def RoverStop(self):
        print("Stop")
        self.opened_socket.sendto(bytes("CNTR", "utf-8"), (self.RemoteIP, self.port))
        self.opened_socket.sendto(bytes("NBRK", "utf-8"), (self.RemoteIP, self.port))
        self.opened_socket.sendto(bytes("NUTR", "utf-8"), (self.RemoteIP, self.port))


# Main ()

# Remote IP and the port is hard coded here. #Improve
Rover = Remote_Rover("Kevin","192.168.1.206",5005)
Rover.DumpGpioMap()
# Start the Remote Rover
Rover.RoverStart()

#PyGame canvas create and initialize
Canvas.init()
window = Canvas.display.set_mode((800,600)) # Window size
Canvas.display.set_caption("ROVER CONTROL") # Window Title
clock = Canvas.time.Clock()

#define color variables to be used on the canvas
black = (0,0,0)
white=(255,255,255)
yellow = (255, 255, 0)
red = (255, 0, 0)
Green = (0, 255, 0)
blue = (0, 0, 255)

#define text formats
myFont = Canvas.font.SysFont("Courier New", 30,1,0,None)
Header = myFont.render("ROVER CONTROL",1,yellow,blue)

# Load the Images 
# Turn signals
L_ON_image = Canvas.image.load(r'Images\\LEFT_TURN.bmp')
R_ON_image = Canvas.image.load(r'Images\\RIGT_TURN.bmp')
L_OF_image = Canvas.image.load(r'Images\\LEFT_OFF.bmp')
R_OF_image = Canvas.image.load(r'Images\\RIGT_OFF.bmp')
# Gear Position
DR_OF_image = Canvas.image.load(r'Images\\DRIVE_OFF.bmp')
NU_OF_image = Canvas.image.load(r'Images\\NUTRAL_OFF.bmp')
RE_OF_image = Canvas.image.load(r'Images\\REVERSE_OFF.bmp')
DR_ON_image = Canvas.image.load(r'Images\\DRIVE_ON.bmp')
NU_ON_image = Canvas.image.load(r'Images\\NUTRAL_ON.bmp')
RE_ON_image = Canvas.image.load(r'Images\\REVERSE_ON.bmp')
# Organize the canvas
window.blit(L_OF_image, (0, 0))
window.blit(R_OF_image, (645, 0))
window.blit(DR_OF_image, (50, 150))
window.blit(NU_ON_image, (50, 275))
window.blit(RE_OF_image, (50, 400))
#Display Name
window.blit(Header,(300,0))
Canvas.display.flip()
sleep(2) # We do not need this.

gameLoop=True # Variable used to exit from the loop.

while gameLoop:

    for event in Canvas.event.get():

        if (event.type==Canvas.QUIT):
            gameLoop=False # handles with Window close
            Rover.RoverStop() # Let's stop the Rover and exit.

        if (event.type==Canvas.KEYDOWN):
            print("key Press:", event.key)
            if (event.key==Canvas.K_LEFT):
                # Left Arrow pressed
                Rover.Turn("L",30)
                window.blit(L_ON_image, (0, 0))
                Canvas.display.flip()
            if (event.key==Canvas.K_RIGHT):
                # Right Arrow pressed
                Rover.Turn("R",30)
                window.blit(R_ON_image, (645, 0))
                Canvas.display.flip()
            if (event.key==Canvas.K_UP):
                # Up Arrow pressed
                Rover.Break("R")
                window.blit(DR_ON_image, (50, 150))
                window.blit(NU_OF_image, (50, 275))
                window.blit(RE_OF_image, (50, 400))
                Canvas.display.flip()
                sleep(0.1)
                Rover.Gear("1") # Set the Drive Gear
                sleep(0.1)
                Rover.Speed(NormalSpeed) # Set the Speed
            if (event.key==Canvas.K_DOWN):
                # Down Arrow presse
                Rover.Break("R")
                window.blit(DR_OF_image, (50, 150))
                window.blit(NU_OF_image, (50, 275))
                window.blit(RE_ON_image, (50, 400))
                Canvas.display.flip()
                sleep(0.25)
                Rover.Gear("R") # Set the Reverse Gear
                sleep(0.25)
                Rover.Speed(NormalSpeed) # Set the Speed
        if (event.type==Canvas.KEYUP):
            
            print("key release:",event.key)
            if (event.key==Canvas.K_LEFT):
                # Left Arrow released
                Rover.Turn("C",0) # Centre the steering
                window.blit(L_OF_image, (0, 0))
                Canvas.display.flip()
            if (event.key==Canvas.K_RIGHT):
                # Right Arrow released
                Rover.Turn("C",0)
                window.blit(R_OF_image, (645, 0))
                Canvas.display.flip()
            if (event.key==Canvas.K_UP):
                # Up Arrow released
                Rover.Break("A") # Apply Break.
            if (event.key==Canvas.K_DOWN):
                # Down Arrow released
                Rover.Break("A") # Apply Break
            if (event.key==Canvas.K_ESCAPE):
                # Exit call.
                gameLoop=False
                exitText = myFont.render("EXIT",1,yellow,blue)
                window.blit(DR_OF_image, (50, 150))
                window.blit(NU_ON_image, (50, 275))
                window.blit(RE_OF_image, (50, 400))
                window.blit(exitText,(50,550))
                Rover.Break("A") # Apply Break
                clock.tick(50)
                Canvas.display.flip()
                sleep(1)
                Rover.Gear("N")  # Set the Reverse Gear
                Rover.RoverStop() #Stop the remote rover. 
                continue

    clock.tick(50)

    Canvas.display.flip() #update the canvas
    
del Rover # This terminates the remote listner. There is no way to remote start #Improve.
Canvas.quit() #Distroy the canvas.

#End of the program
