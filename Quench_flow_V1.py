import serial
import time
import binascii

# FUNCTIONS

def ul_to_steps(volume):
    resolution = 3000
    syringe_size = 250
    n_steps = resolution*volume/syringe_size
    return n_steps

def ul_min_to_steps_second(uL_min):
    V = 250 # Volume is 250 mm^3 (uL)
    L = 30 # Stroke is 30 mm
    A = V/L
    resolution = 3000
    linear_resolution = L/resolution
    volumetric_resolution = linear_resolution*A
    steps_per_second = uL_min/(60*volumetric_resolution)
    return steps_per_second

def dispense_volume(uL, address):
    steps = ul_to_steps(uL)
    A_command = 'A'
    R_command = 'R'
    cmd_blk = A_command + str(int(steps)) + R_command
    data = list(cmd_blk.encode())
    print(pump.send_command(address,data))

def set_top_velocity(V, address): #[V<n>], where <n> = 5..5800 Hz (1400 is the default)
    cmd_blk = V
    data = list(cmd_blk.encode())
    print(pump.send_command(address,data))

    cmd_blk = 'R'
    data = list(cmd_blk.encode())
    print(pump.send_command(address,data))

def set_start_velocity(V, address): #[v<n>], where <n> = 5..5800 Hz (900 is the default)
    cmd_blk = V
    data = list(cmd_blk.encode())
    print(pump.send_command(address,data))

    cmd_blk = 'R'
    data = list(cmd_blk.encode())
    print(pump.send_command(address,data))

def set_cutoff_velocity(V, address): #[v<n>], where <n> = 5..5800 Hz (900 is the default)
    cmd_blk = V
    data = list(cmd_blk.encode())
    print(pump.send_command(address,data))

    cmd_blk = 'R'
    data = list(cmd_blk.encode())
    print(pump.send_command(address,data))

def initialize(address): #Initialize Plunger (Set Output Valve to Right)
    cmd_blk = 'Z2'
    data = list(cmd_blk.encode())
    print(pump.send_command(address,data))

    cmd_blk = 'R'
    data = list(cmd_blk.encode())
    print(pump.send_command(address,data))

def move_valve_into_input_position(address):
    cmd_blk = 'I'
    data = list(cmd_blk.encode())
    print(pump.send_command(address,data))

    cmd_blk = 'R'
    data = list(cmd_blk.encode())
    print(pump.send_command(address,data))

def Move_valve_into_output_position(address):
    cmd_blk = 'O'
    data = list(cmd_blk.encode())
    print(pump.send_command(address,data))

    cmd_blk = 'R'
    data = list(cmd_blk.encode())
    print(pump.send_command(address,data))

# SYRINGE PUMP CLASS

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


# MAIN PROGRAM

if __name__ == "__main__":

    pump = SyringePump()

    ########## VARIABLES #######################

    pump_1_address_ = 0x34
    pump_2_address_ = 0x35
    pump_3_address_ = 0x36

    volume_to_pull_syringe_1 = 10
    volume_to_push_syringe_1 = 5

    volume_to_pull_syringe_2 = 10
    volume_to_push_syringe_2 = 5

    volume_to_pull_syringe_3 = 20
    volume_to_push_syringe_3 = 10

    flow_rate_1 = 333
    flow_rate_2 = 333
    flow_rate_3 = 666

    init_time = 3
    delay_time = 0.3
    speed_init_time = 0.5

    top_velocity_pump_1 = 'V' + str(int(ul_min_to_steps_second(flow_rate_1)))
    start_velocity_pump_1 = 'v' + str(int(ul_min_to_steps_second(flow_rate_1)))
    cutoff_velocity_pump_1 = 'c' + str(int(ul_min_to_steps_second(flow_rate_1)))

    top_velocity_pump_2 = 'V' + str(int(ul_min_to_steps_second(flow_rate_2)))
    start_velocity_pump_2 = 'v' + str(int(ul_min_to_steps_second(flow_rate_2)))
    cutoff_velocity_pump_2 = 'c' + str(int(ul_min_to_steps_second(flow_rate_2)))

    top_velocity_pump_3 = 'V' + str(int(ul_min_to_steps_second(flow_rate_3)))
    start_velocity_pump_3 = 'v' + str(int(ul_min_to_steps_second(flow_rate_3)))
    cutoff_velocity_pump_3 = 'c' + str(int(ul_min_to_steps_second(flow_rate_3)))

    ########## INITIALIZATION #####################

    initialize(pump_1_address_)

    time.sleep(init_time)  # Allow time for response

    initialize(pump_2_address_)

    time.sleep(init_time)  # Allow time for response

    initialize(pump_3_address_)

    time.sleep(init_time)  # Allow time for response

    print('Initialization done')

    # Set velocities for each pump

    set_top_velocity(top_velocity_pump_1,pump_1_address_)
    time.sleep(speed_init_time)  # Allow time for response
    set_top_velocity(top_velocity_pump_2,pump_2_address_)
    time.sleep(speed_init_time)  # Allow time for response
    set_top_velocity(top_velocity_pump_3,pump_3_address_)
    time.sleep(speed_init_time)  # Allow time for response

    set_start_velocity(start_velocity_pump_1,pump_1_address_)
    time.sleep(speed_init_time)  # Allow time for response
    set_start_velocity(start_velocity_pump_2,pump_2_address_)
    time.sleep(speed_init_time)  # Allow time for response
    set_start_velocity(start_velocity_pump_3,pump_3_address_)
    time.sleep(init_time)  # Allow time for response

    set_cutoff_velocity(cutoff_velocity_pump_1,pump_1_address_)
    time.sleep(speed_init_time)
    set_cutoff_velocity(cutoff_velocity_pump_2,pump_2_address_)
    time.sleep(speed_init_time)
    set_cutoff_velocity(cutoff_velocity_pump_2,pump_2_address_)
    time.sleep(init_time)  # Allow time for response

    print('Velocities setup done')

    ########## ROUTINE ##########################

    # Move the valves into Input position

    move_valve_into_input_position(pump_1_address_)
    time.sleep(1.5)  # Allow time for response
    move_valve_into_input_position(pump_2_address_)
    time.sleep(1.5)  # Allow time for response
    move_valve_into_input_position(pump_3_address_)
    time.sleep(1.5)  # Allow time for response

    print('Valves into input position')

    # Pull liquid from all syringes

    dispense_volume(volume_to_pull_syringe_1, pump_1_address_)
    time.sleep(3)  # Allow time for response

    dispense_volume(volume_to_pull_syringe_2, pump_2_address_)
    time.sleep(3)  # Allow time for response

    dispense_volume(volume_to_pull_syringe_3, pump_3_address_)
    time.sleep(5)  # Allow time for response

    print('Liquid pulled inside the syringes')

    # Move the valves into Output position

    Move_valve_into_output_position(pump_1_address_)
    time.sleep(2)  # Allow time for response

    Move_valve_into_output_position(pump_2_address_)
    time.sleep(2)  # Allow time for response

    Move_valve_into_output_position(pump_3_address_)
    time.sleep(3)  # Allow time for response

    print('Valves into output position')

    # Move push liquid from the first two syringes (simultaneously)

    dispense_volume(volume_to_push_syringe_1, pump_1_address_)

    dispense_volume(volume_to_push_syringe_2, pump_2_address_)

    print('Dispensing volume from the first two syringes')

    # Wait 0.3 seconds and push the liquid from the 3rd syringe

    time.sleep(delay_time)  # Allow time for response

    dispense_volume(volume_to_push_syringe_3, pump_3_address_)

    print('Dispensing volume from the third syringe')

    time.sleep(5)  # Allow time for response
    
    pump.close()  # Close the serial connection when done


