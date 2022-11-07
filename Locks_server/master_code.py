import socket


class Lock_Communicator:
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 8888  		# The port used by the server

    server = None


    def __init__(self) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((self.HOST, self.PORT))        


    def __send_lock_data__(self, data, time, mac, recv_data=False):
        #send messege to lock 
        send_data = f"{mac}/{data}/{time * 1000}"
        self.server.sendall(send_data.encode('gbk'))

        if recv_data:
            data = self.server.recv(1024).decode('utf-8')
            return data


    def close(self):
        self.server.close()
        self.server = None


    def scan_EAC(self):
        # data format: {mac}/scanned/eac_number
        data = self.__send_lock_data__('scan', 15, <mac_of_lock>, recv_data=True)
        data = data.split('/')

        if data[1] == 'scanned':
            return data[2]
        else:
            raise ValueError('Incorrect data from lock during scan')
        
    def open(self, mac):
        self.__send_lock_data__('open', 10, mac)