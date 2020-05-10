import socket
import pygame as Canvas
from time import sleep
NormalSpeed = 50       

class Remote_Rover:
    
    def __init__(self,name, ipAddress, port):
        self.byte_message = bytes("0", "utf-8")
        self.name = name
        self.Direction = "C"
        self.Run  = "F"
        self.Turn_Angle = 0
        self.Run_Speed = 0
        self.BreakStatus = 'R' #Released
        self.GearPosition = 'N' #Neutral
        self.RemoteIP = ipAddress
        self.port = port
        self.opened_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __del__(self):
        print("Terminate")
        self.opened_socket.sendto(bytes("CNTR", "utf-8"), (self.RemoteIP, self.port))
        self.opened_socket.sendto(bytes("NBRK", "utf-8"), (self.RemoteIP, self.port))
        self.opened_socket.sendto(bytes("NUTR", "utf-8"), (self.RemoteIP, self.port))
        self.opened_socket.sendto(bytes("TERM", "utf-8"), (self.RemoteIP, self.port))

 
# Turn function 

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
                
    def Gear(self,gear):
        if gear == 'N':
            self.opened_socket.sendto(bytes("NUTR", "utf-8"), (self.RemoteIP, self.port))
            #self.GearPosition = "N"
        elif gear == 'R':
            self.opened_socket.sendto(bytes("REVR", "utf-8"), (self.RemoteIP, self.port))
            #self.GearPosition = "R"
        else:
            self.opened_socket.sendto(bytes("FWRD", "utf-8"), (self.RemoteIP, self.port))
            #self.GearPosition = gear
        self.GearPosition = gear
        print ("Drive",self.GearPosition)
            
# Gear Accelerate function ( values : 0 - 100)
    
    def Speed(self,speed):
        if self.GearPosition == 'N':
            self.Run_Speed = 0
            print ("Neutral. Can not go.!")
        elif self.BreakStatus == 'A':
            print ("Break ON. Can not go.!")
            self.Run_Speed = 0
        else:
            self.Run_Speed = speed
            self.SpeedCommand = "SP"+str(speed)
            self.opened_socket.sendto(bytes(self.SpeedCommand, "utf-8"), (self.RemoteIP, self.port))
            self.Run_Speed = speed
            print ("speed", speed)

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

    def DumpGpioMap(self):
        print("Name: ",self.name) 
        print("Turn: ",self.Direction)  
        print("Turn Angle: ",self.Turn_Angle) 
#        print("Drive: ",self.Run)  
        print("Gear: ",self.GearPosition)
        print("Break: ",self.BreakStatus) 
        print("Drive Speed: ",self.Run_Speed)

    def RoverStart(self):
        print("Start")
        self.opened_socket.sendto(bytes("CNTR", "utf-8"), (self.RemoteIP, self.port))
        self.opened_socket.sendto(bytes("NBRK", "utf-8"), (self.RemoteIP, self.port))
        self.opened_socket.sendto(bytes("NUTR", "utf-8"), (self.RemoteIP, self.port))

    def RoverStop(self):
        print("Stop")
        self.opened_socket.sendto(bytes("CNTR", "utf-8"), (self.RemoteIP, self.port))
        self.opened_socket.sendto(bytes("NBRK", "utf-8"), (self.RemoteIP, self.port))
        self.opened_socket.sendto(bytes("NUTR", "utf-8"), (self.RemoteIP, self.port))


Rover = Remote_Rover("Kevin","192.168.1.200",5005)
Rover.DumpGpioMap()
Rover.RoverStart()

Canvas.init()

window = Canvas.display.set_mode((800,600))
Canvas.display.set_caption("ROVER CONTROL")
clock = Canvas.time.Clock()

black = (0,0,0)
white=(255,255,255)
yellow = (255, 255, 0)
red = (255, 0, 0)
Green = (0, 255, 0)
blue = (0, 0, 255)

myFont = Canvas.font.SysFont("Courier New", 30,1,0,None)
Header = myFont.render("ROVER CONTROL",1,yellow,blue)

L_ON_image = Canvas.image.load(r'Images\\LEFT_TURN.bmp')
R_ON_image = Canvas.image.load(r'Images\\RIGT_TURN.bmp')
L_OF_image = Canvas.image.load(r'Images\\LEFT_OFF.bmp')
R_OF_image = Canvas.image.load(r'Images\\RIGT_OFF.bmp')

DR_OF_image = Canvas.image.load(r'Images\\DRIVE_OFF.bmp')
NU_OF_image = Canvas.image.load(r'Images\\NUTRAL_OFF.bmp')
RE_OF_image = Canvas.image.load(r'Images\\REVERSE_OFF.bmp')
DR_ON_image = Canvas.image.load(r'Images\\DRIVE_ON.bmp')
NU_ON_image = Canvas.image.load(r'Images\\NUTRAL_ON.bmp')
RE_ON_image = Canvas.image.load(r'Images\\REVERSE_ON.bmp')

window.blit(L_OF_image, (0, 0))
window.blit(R_OF_image, (645, 0))
window.blit(DR_OF_image, (50, 150))
window.blit(NU_ON_image, (50, 275))
window.blit(RE_OF_image, (50, 400))

window.blit(Header,(300,0))
Canvas.display.flip()
sleep(2)



gameLoop=True
while gameLoop:

    for event in Canvas.event.get():

        if (event.type==Canvas.QUIT):
            gameLoop=False

        if (event.type==Canvas.KEYDOWN):
            print("key:", event.key)
            if (event.key==Canvas.K_LEFT):
                Rover.Turn("L",30)
                window.blit(L_ON_image, (0, 0))
                Canvas.display.flip()
            if (event.key==Canvas.K_RIGHT):
                Rover.Turn("R",30)
                window.blit(R_ON_image, (645, 0))
                Canvas.display.flip()
            if (event.key==Canvas.K_UP):
                Rover.Break("R")
                window.blit(DR_ON_image, (50, 150))
                window.blit(NU_OF_image, (50, 275))
                window.blit(RE_OF_image, (50, 400))
                Canvas.display.flip()
                sleep(0.1)
                Rover.Gear("1")
                sleep(0.1)
                Rover.Speed(NormalSpeed)
            if (event.key==Canvas.K_DOWN):
                Rover.Break("R")
                window.blit(DR_OF_image, (50, 150))
                window.blit(NU_OF_image, (50, 275))
                window.blit(RE_ON_image, (50, 400))
                Canvas.display.flip()
                sleep(0.25)
                Rover.Gear("R")
                sleep(0.25)
                Rover.Speed(NormalSpeed)
        if (event.type==Canvas.KEYUP):
            print("key:",event.key)
            if (event.key==Canvas.K_LEFT):
                Rover.Turn("C",0)
                window.blit(L_OF_image, (0, 0))
                Canvas.display.flip()
            if (event.key==Canvas.K_RIGHT):
                Rover.Turn("C",0)
                window.blit(R_OF_image, (645, 0))
                Canvas.display.flip()
            if (event.key==Canvas.K_UP):
                Rover.Break("A")
            if (event.key==Canvas.K_DOWN):
                Rover.Break("A")
            if (event.key==Canvas.K_ESCAPE):
                gameLoop=False
                exitText = myFont.render("EXIT",1,yellow,blue)
                window.blit(DR_OF_image, (50, 150))
                window.blit(NU_ON_image, (50, 275))
                window.blit(RE_OF_image, (50, 400))
                window.blit(exitText,(50,550))
                clock.tick(50)
                Canvas.display.flip()
                Rover.RoverStop()
                sleep(1)
                continue

    clock.tick(50)

    Canvas.display.flip()
    
del Rover
Canvas.quit()
