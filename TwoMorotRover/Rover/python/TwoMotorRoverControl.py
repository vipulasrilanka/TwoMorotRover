import socket
from gpiozero import PWMLED
from gpiozero import LED
from time import sleep

#GPIT pin assignment
C_Turn_L = 23
C_Turn_R = 22
C_Turn_S = 26
C_Run_F = 4
C_Run_B = 17
C_Run_S = 27
 
# We are using simple UDP packets to control the morots 
# We have the Port hard coded at the momenrt. #Improve
UDP_IP = "192.168.1.206"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT)) # bind the socket to IP and port
    
    
# Two_Motor_drive_Rover defines the two motor driver

class Two_Motor_drive_Rover:

    # It has to be initialised with the GPIO pins. Each instance can be given a name.
    # The name has to be validated by the remote controler to identify the Rover. #Improve
    def __init__(self,name,G_Turn_L,G_Turn_R,G_Turn_S,G_Run_F,G_Run_B,G_Run_S):
        self.name = name
        print ("init: ", name)
        print ("LEFT",G_Turn_L)
        print ("RIGT",G_Turn_R)
        print ("TSPD",G_Turn_S)
        print ("FWRD",G_Run_F)
        print ("BKWD",G_Run_B)
        print ("SPED",G_Run_S)
        # Creating objects for GPIO Control.
        # We are using the gpiozero library for this. 
        self.Turn_L = LED(G_Turn_L)
        self.Turn_R = LED(G_Turn_R)
        self.Run_F  = LED(G_Run_F)
        self.Run_B  = LED(G_Run_B)
        self.Turn_S = PWMLED(G_Turn_S)
        self.Run_S = PWMLED(G_Run_S)
        # Initialize local state variables
        self.BreakStatus = 'R'  # This keeps track of the Break state. (R = Releaeed, A = Active)
        self.GearPosition = 'N' # This Keeps the Gear Level (N = Neutral, R = Reverse, D = Drive and Numbers can be used)

 
# Turn function 
# The implmentation is specific to the Chasis that this code runs

    def Turn(self, direction, angle):
        # The current Chasis can not contrl the Angle so we take only the direction.
        # once this function is called, the motors will be activated,.
        if direction == 'L':
            self.Turn_L.on()
            self.Turn_R.off()
            self.Turn_S.value = 1
        elif direction == 'R':
            self.Turn_L.off()
            self.Turn_R.on()
            self.Turn_S.value = 1
        else: # The only option that is applicable for the current Chasis is "C" for centre. 
            self.Turn_L.off()
            self.Turn_R.off()
            self.Turn_S.value = 0
        print ("Turn",direction, angle)
            
# Gear Shift Function 
# The implmentation is specific to the Chasis 
# Change the Gear posision. This will not drive motors.
                
    def Gear(self,gear):
        if gear == 'N':
            #Release motor Driver
            self.Run_F.off()
            self.Run_B.off()
            self.Run_S.value = 0
        elif gear == 'R':
            #Enable Reverse (Run_B.on)
            self.Run_F.off()
            self.Run_B.on()
            self.Run_S.value = 0
        else: # this can be D, 1, 2, 3, ..etc
            #Enable Drive  (Run_F.on)
            self.Run_F.on()
            self.Run_B.off()
            self.Run_S.value = 0
        self.GearPosition = gear
        print ("Drive",self.GearPosition)
            
# Motor Accelerate function ( values : 0 - 100)
# The current chasis has 6V motor and 8.4V battery pack. 
# So keep the Speed below 80 for safety.
# This method sets the Speed of the motor.    

    def Speed(self,speed):
        if self.GearPosition == 'N':
            # If you are in Neutral, no action will be done. This Chasisi has the motor directly coupled to wheels.
            self.Run_S.value = 0
            print ("Neutral. Can not go.!")
        elif self.BreakStatus == 'A':
            # If you are in Neutral, no action will be done. This Chasisi has the motor directly coupled to wheels.
            print ("Break ON. Can not go.!")
        else:
            # The PWMLED function takes a float between 0 - 1 
            # So we device the Speed value by 100 to get the correct value. 
            # This will run the motor with given Speed.
            if speed >80:
                self.Run_S.value = 0.8 #Limit the max speed as we use 6V motor.  
            else:
                self.Run_S.value = speed/100
            print ("speed", speed)

# Activate Breaks.
# This implementation is specific to the Chasis 

    def Break(self, activate):
        if activate == 'A':
          #Apply Break (Enable Both F and B in this controller, and eneble full speed)     
          self.Run_F.on()
          self.Run_B.on()
          self.Run_S.value = 1
          print ("Break on")
        elif activate == 'R':
          #Release Break. Here we put the Chasis in to the previous Gear level that's stored in GearPosition.
          print ("Break Release")
          self.Gear(self.GearPosition) #back to active Gear
        else:
          print ("error")
        #Store the current Brek Status,
        self.BreakStatus = activate 

#Dump the GPIO map for debugging. 

    def DumpGpioMap(self):
        print(self.Turn_L) 
        print(self.Turn_R) 
        print(self.Run_F)  
        print(self.Run_B)  
        print(self.Turn_S) 
        print(self.Run_S) 
            
#Start main()

#Construct the Rover Named Kevin
Rover = Two_Motor_drive_Rover ("Kevin",C_Turn_L,C_Turn_R,C_Turn_S,C_Run_F,C_Run_B,C_Run_S)

print ("start")
Rover.Break('A')  #Break Apply
Rover.Gear('N')   #Drive back (Gear Change only)
Rover.Turn('C',0)  #Centre

# Main Loop.
while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    #data will contain the data and addr will have the sender address
    #We can filter the host here but not implememted yet,
    print ("received message:", data)

    #Turning Functions
    if data == b'LEFT':
        Rover.Turn('L',30) #Turn Left
    elif data == b'RIGT':
        Rover.Turn('R',30) #Turn Right
    elif data == b'CNTR':
        Rover.Turn('C',0)  #Centre

     #Driving Functions   
    elif data == b'FWRD':
        Rover.Gear('D')   #Drive (Gear Change only)
    elif data == b'REVR':
        Rover.Gear('R')   #Drive back (Gear Change only)
    #Now check for Speed setting
    elif (data[0] == 83 and data [1] == 80): #if the packet is of SPnn,  S = (ASCII 82) P  =(ASCII P)
        if (Rover.GearPosition == 'D' or Rover.GearPosition == 'R'):
            Rover.Speed((10*(data[2]-48))+ (data[3] - 48)) #Set Speed 0 = (ASCII 48)
        else:
            print ("Invalid Speed. Not in a Driving gear")
    elif data == b'BREK':
        Rover.Break('A')  #Break Apply
    elif data == b'NBRK':
        Rover.Break('R')  #Break Release
    elif data == b'NUTR':
        Rover.Gear('N')   #Neutral Gear
        Rover.Speed(0)
        
    # Remote control functios for main loop
    elif data == b'TERM':# This terminates the loop and exit the program
        Rover.Speed(0)
        Rover.Turn('C',0)
        Rover.Gear('N')   #Terminate Loop
        break
    else:
        print ("error")
    
print ("end")


