import serial
import time
import binascii


def ul_to_steps(volume):
    resolution = 3000
    syringe_size = 250
    n_steps = resolution*volume/syringe_size
    return n_steps


class SyringePump:
    def __init__(self, port='COM11', baudrate=38400, timeout=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout,bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
        self.seq_number = 0  # This should be incremented for each command

    #def generate_checksum(self, message):
    #    # Assuming a simple sum checksum
    #    return sum(message) % 256
    
    def generate_checksum(self, message):
        checksum = 0
        
        # Iterate over each byte in the message
        for byte in message:
            checksum ^= byte  # XOR the current byte with the checksum
        
        return checksum
    

    def send_command(self, pump_address, data):
        if self.ser.isOpen():
            #self.seq_number += 2
            self.seq_number =0x31
            message = [0x02, pump_address, self.seq_number] + data  # STX, address, sequence number, data
            message.append(0x03)  # ETX
            message.append(self.generate_checksum(message))  # Checksum

            self.ser.write(bytes(message))
            #print("sending: ")
            #print((message))

            time.sleep(0.4)  # Allow time for response
            return self.parse_response(self.ser.read(self.ser.inWaiting()))
        else:
            print("Syringe pump is not connected.")
            return None

    def parse_response(self, response):
        #print(binascii.hexlify(response))
        
        
        if len(response) < 6:  # the shortest valid response has 6 bytes
            print(f"Response too short: {response}")
            return None
        if len(response)== 7:
            data=0
        else:
            data =response[4:len(response)-3]
        if response[1] != 0x02 or response[-3] != 0x03 or self.generate_checksum(response[:-1]) != response[-1]:
            print("Invalid response")
            return None

        return {
            'master_address': hex(response[2]),
            'status_code': hex(response[3]),
            'data': data
        }

    def close(self):
        if self.ser.isOpen():
            self.ser.close()

if __name__ == "__main__":
    
    pump = SyringePump()
    address_ = 0x36

    while(True):

        input_c = input('Enter command: ')
        R_command = 'R'
        cmd_blk = input_c + R_command
        if cmd_blk == 'end':
            break
        data = list(cmd_blk.encode())
        print(pump.send_command(address_,data))
        print('Command sent: ',cmd_blk)

        time.sleep(5)  # Allow time for response

    pump.close()  # Close the serial connection when done
    print('Program finished')

