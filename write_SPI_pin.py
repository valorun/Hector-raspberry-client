#/home/pi/Scripts/write_SPI_pin.py
import time, sys, signal, os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

SPI_SLAVE_ADDR  = 0x40	#opcode de la carte en SPI
SPI_IOCTRL      = 0x0A

SPI_IODIRA      = 0x00
SPI_IODIRB      = 0x01

SPI_GPIOA       = 0x12
SPI_GPIOB       = 0x13

SPI_SLAVE_WRITE = 0x00	#opcode de la carte en SPI pour l'envoie
SPI_SLAVE_READ  = 0x01	#... et pour la reception

SCLK        = 11	#Serial Clock, Horloge (genere par le maitre)
MOSI        = 10	#Master Output, Slave input (genere par le maitre)
MISO        = 9		#Master input, Slave Output(genere par l'esclave)
CS          = 8		#Slave Select, Actif a l'etat bas (genere par le maitre)

input = sys.argv[1]
input_state = sys.argv[2]
def ChangeBit(input):
	Bank = input[0]
	Port = input[1]
	Pin  = input[2]
	Bank = Bank.upper()
	if Bank == "A":
		Addr = 0x40
	elif Bank == "B":
		Addr = 0x42
	
	else:
		sys.exit()
	
	if Pin == "8":
		Out = "10000000"
	elif Pin == "7":
		Out = "01000000"
	elif Pin == "6":
		Out = "00100000"
	elif Pin == "5":
		Out = "00010000"
	elif Pin == "4":
		Out = "00001000"
	elif Pin == "3":
		Out = "00000100"
	elif Pin == "2":
		Out = "00000010"
	elif Pin == "1":
		Out = "00000001"
	else:
		sys.exit()

	if Port == "1":
        	Previous = '{:08b}'.format(readSPI(Addr, 0x0A))[8-int(Pin)] # lecture de la valeur actuelle du pin. on lit la valeur sous forme d'octet et on récupère seulement le bit associé au pin désiré
        	if Previous == input_state:
            		sys.exit()
        	Bin = bin(int('{:08}'.format(readSPI(Addr, 0x0A))) ^ int(Out, 2)) # "XOR" entre la valeur actuelle des pins et la nouvelle valeur
        	sendSPI( Addr, 0x0A, int(Bin, 2) )
        	sys.exit()
    	if Port == "2":
        	Previous = '{:08b}'.format(readSPI(Addr, 0x1A))[8-int(Pin)]
        	if Previous == input_state:
            		sys.exit()
        	Bin = bin(int('{:08}'.format(readSPI(Addr, 0x1A))) ^ int(Out, 2))
        	sendSPI( Addr, 0x1A, int(Bin, 2) )
        	sys.exit()



# Méthode permettant d'envoyer des données sur les pins du raspberry
def sendValue(value):
    for i in range(8):
        if (value & 0x80):
            GPIO.output(MOSI, GPIO.HIGH)
        else:
            GPIO.output(MOSI, GPIO.LOW)
        GPIO.output(SCLK, GPIO.HIGH)
        GPIO.output(SCLK, GPIO.LOW)
        value <<= 1
# Méthode permettant d'envoyer des sur le shield via les pins SPI
# opcode = code du banc désiré
# addr = code de la ligne sur le banc
# date = valeur a envoyer
def sendSPI(opcode, addr, data):
    GPIO.output(CS, GPIO.LOW)
    sendValue(opcode|SPI_SLAVE_WRITE)
    sendValue(addr)
    sendValue(data)
    GPIO.output(CS, GPIO.HIGH)
# Méthode permettant de lire la valeur d'une ligne d'un banc sur le shield via les pins SPI
# opcode = code du banc désiré
# addr = code de la ligne sur le banc   
# retourne la valeur binaire
def readSPI(opcode, addr):
    GPIO.output(CS, GPIO.LOW)
    sendValue(opcode|SPI_SLAVE_READ)
    sendValue(addr)
   
    value = 0
    for i in range(8):        
        value <<= 1
        if(GPIO.input(MISO)):
            value |= 0x01   
        GPIO.output(SCLK, GPIO.HIGH)
        GPIO.output(SCLK, GPIO.LOW)

    GPIO.output(CS, GPIO.HIGH)
    return value		
def main():

    GPIO.setup(SCLK, GPIO.OUT)
    GPIO.setup(MOSI, GPIO.OUT)
    GPIO.setup(MISO, GPIO.IN)
    GPIO.setup(CS, GPIO.OUT)

    GPIO.output(CS, GPIO.HIGH)
    GPIO.output(SCLK, GPIO.LOW)

    sendSPI(0x40, 0x05, 0x00)
    sendSPI(0x42, 0x05, 0x00)

    sendSPI(SPI_SLAVE_ADDR, SPI_IODIRB, 0x00) # GPPIOB comme entree
    sendSPI(SPI_SLAVE_ADDR, SPI_IODIRA, 0x00) # GPPIOA comme sortie
   # sendSPI(SPI_SLAVE_ADDR, SPI_GPIOA, 0x00) # Reset des GPIOA
   # sendSPI(SPI_SLAVE_ADDR, SPI_GPIOB, 0x00)  # Reset des GPIOB
    sendSPI(0x40, 0x0A, 0xFF)
   # sendSPI(0x42, 0x0A, 0xFF)

   # os.system("clear")
    if input[0] != "A" and input[0] != "B":
    	Menu("Incorrect Bank entered: "+input[0])
    if len(input) < 3:
	Menu("Incorrect input.")
    elif len(input) > 3:
	Menu("Too many letters / numbers.")
    else:
	ChangeBit(input)
			
if __name__ == '__main__':
main()