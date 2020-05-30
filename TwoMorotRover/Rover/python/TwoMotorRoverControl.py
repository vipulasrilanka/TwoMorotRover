import socket
from gpiozero import PWMLED
from gpiozero import LED
from time import sleep

#pin assignment
C_Turn_L = 23
C_Turn_R = 22
C_Turn_S = 26
C_Run_F = 4
C_Run_B = 17
C_Run_S = 27
 
UDP_IP = "192.168.1.200"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))
    
    
    
class Two_Motor_drive_Rover:
    
    def __init__(self,name,G_Turn_L,G_Turn_R,G_Turn_S,G_Run_F,G_Run_B,G_Run_S):
        self.name = name
        print ("init: ", name)
        print ("LEFT",G_Turn_L)
        print ("RIGT",G_Turn_R)
        print ("TSPD",G_Turn_S)
        print ("FWRD",G_Run_F)
        print ("BKWD",G_Run_B)
        print ("SPED",G_Run_S)
        self.Turn_L = LED(G_Turn_L)
        self.Turn_R = LED(G_Turn_R)
        self.Run_F  = LED(G_Run_F)
        self.Run_B  = LED(G_Run_B)
        self.Turn_S = PWMLED(G_Turn_S)
        self.Run_S = PWMLED(G_Run_S)
        self.BreakStatus = 'R'
        self.GearPosition = 'N'

 
# Turn function 

    def Turn(self, direction, angle):
        if direction == 'L':
            self.Turn_L.on()
            self.Turn_R.off()
            self.Turn_S.value = 1
        elif direction == 'R':
            self.Turn_L.off()
            self.Turn_R.on()
            self.Turn_S.value = 1
        else:
            self.Turn_L.off()
            self.Turn_R.off()
            self.Turn_S.value = 0
        print ("Turn",direction, angle)
            
# Gear Shift Function 
                
    def Gear(self,gear):
        if gear == 'N':
            self.Run_F.off()
            self.Run_B.off()
            self.Run_S.value = 0
        elif gear == 'R':
            self.Run_F.off()
            self.Run_B.on()
            self.Run_S.value = 0
        else:
            self.Run_F.on()
            self.Run_B.off()
            self.Run_S.value = 0
        self.GearPosition = gear
        print ("Drive",self.GearPosition)
            
# Gear Accelerate function ( values : 0 - 100)
    
    def Speed(self,speed):
        if self.GearPosition == 'N':
            self.Run_S.value = 0
            print ("Neutral. Can not go.!")
        elif self.BreakStatus == 'A':
            print ("Break ON. Can not go.!")
        else:
            self.Run_S.value = speed/100
            print ("speed", speed)

    def Break(self, activate):
        if activate == 'A':#Apply break
          self.Run_F.on()
          self.Run_B.on()
          self.Run_S.value = 1
          print ("Break on")
        elif activate == 'R':#Release Break
          print ("Break Release")
          self.Gear(self.GearPosition) #back to active Gear
        else:
          print ("error")
        self.BreakStatus = activate 

    def DumpGpioMap(self):
        print(self.Turn_L) 
        print(self.Turn_R) 
        print(self.Run_F)  
        print(self.Run_B)  
        print(self.Turn_S) 
        print(self.Run_S) 
            
#Start maim()

Rover = Two_Motor_drive_Rover ("Kevin",C_Turn_L,C_Turn_R,C_Turn_S,C_Run_F,C_Run_B,C_Run_S)

# Rover.Turn('L',30)
# sleep(1)
# Rover.Turn('C',0)
# sleep(1)
# Rover.Turn('R',30)
# sleep(1)
# Rover.Turn('C',30)
# sleep(1)
# 
# 
# Rover.Gear('D') #Drive
# Rover.Speed(80)
# sleep(1)
# Rover.Break('A') #Apply
# sleep(1)
# Rover.Break('R') #Release
# sleep(1)
# 
# Rover.Speed(20)
# sleep(1)
# Rover.Speed(0)
# sleep(1)
# 
# Rover.Gear('N')
# Rover.Speed(20)
# sleep(1)
# Rover.Speed(0)
# sleep(1)
# 
# Rover.Gear('R') #Reverse
# Rover.Speed(20)
# sleep(1)
# Rover.Speed(0)

print ("start")
while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print ("received message:", data)
    if data == b'LEFT':
        Rover.Turn('L',30) #Turn Left
    elif data == b'RIGT':
        Rover.Turn('R',30) #Turn Right
    elif data == b'CNTR':
        Rover.Turn('C',0)  #Centre
        
    elif data == b'FWRD':
        Rover.Gear('D')   #Drive (Gear Change)
    elif data == b'REVR':
        Rover.Gear('R')   #Drive back (Gear Change only)
    elif (data[0] == 83 and data [1] == 80): #if start with SP
        if (Rover.GearPosition == 'D' or Rover.GearPosition == 'R'):
            Rover.Speed((10*(data[2]-48))+ (data[3] - 48)) #Set Speed
    elif data == b'BREK':
        Rover.Break('A')  #Break Apply
    elif data == b'NBRK':
        Rover.Break('R')  #Break Release
    elif data == b'NUTR':
        Rover.Gear('N')   #Neutral Gear
        Rover.Speed(0)
    elif data == b'TERM':
        Rover.Speed(0)
        Rover.Turn('C',0)
        Rover.Gear('N')   #Terminate Loop
        break
    else:
        print ("error")
    
print ("end")


