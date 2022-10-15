import locale
import logging
import os
import socket
import threading

server_ip   = "0.0.0.0"    #ip address of the server
server_port = 8000         #port of the server
master_port = 8888         #port for master block
admin_EAC_path = "/home/config/"  #file format: {admin_EAC_path}/{mac}.txt
logs_path = "/home/logs/"

#------------------------------------------------------------------------------

logger_x = logging.getLogger("Server")
logger   = logging.getLogger("Bad")
sockets  = []

#------------------------------------------------------------------------------

def accept_read(tcp_socket_host):
    global logger_x, logger, sockets, sock

    soc, addr_client = tcp_socket_host.accept()
    logger.info(f"client connected {soc}", extra = {'user':'server'})

    #creating separate thread for next client
    thread = threading.Thread(target=accept_read, args=(tcp_socket_host, ))          
    thread.start()

    try:                                                                       
        #first message should be the initialization
        recv_data = soc.recv(1024)
        logger.info("message -> %s", str(recv_data), extra = {'user':'Server'})
    except Exception:
        logger.info("bad client", extra = {'user':'server'})
        return

    #if not initialization message -> close socket
    if str(recv_data).find("initialized") == -1:
        logger.info("bad client", extra = {'user':'server'})
        soc.close()
        return

    lock_name = (str(recv_data).split('/'))[2]
    
    logger_x.info("initialize client name -> %s", 
                  lock_name, 
                  extra = {'user':'server'})

    #if initialization passed -> add new socket to array of clients
    sockets.append( {"mac": lock_name, "socket": soc})
    #send initialization array of admin EACs
    key_file = open(admin_EAC_path + lock_name + ".txt", "r")
    Lines = key_file.readlines()
    keys = "update"
    for line in Lines:
        keys += " " + line.split('/')[0].strip().lower()
    soc.send(keys.encode("gbk"))
    
    #process of reading messages from client "handler"
    while True:                                                                
        try:
            recv_data = soc.recv(1024)

            #if not data that means client closed
            if not recv_data:
                logger_x.info("client disconnected", extra = {'user': lock_name})
                soc.close()
                sockets.remove(next(x for x in sockets if x["socket"] == soc))
                return

            #checking for access and send reply
            if recv_data:
                logger_x.info("message -> %s", 
                            str(recv_data), 
                            extra = {'user': lock_name})
                data = str(recv_data.decode('ascii'))
                
                if data.find("request") != -1:
                    card_uid = (data.split('/'))[3]
                    logger_x.info(f"open request: {card_uid}",
                                extra= {'user': lock_name})
                    permission, time = check_booking(lock_name, card_uid)
                    soc.send(f'reply {permission} {time:09}'.encode("gbk"))
                    
                elif data.find("scanned") != -1:
                    card_uid = (data.split('/'))[3]
                    sock.send(f'{lock_name}/scanned/{card_uid}'.encode("gbk"))
                    

        #exception handling for closed socket and others
        except Exception as error:
            logger_x.info("client disconnected", extra = {'user': lock_name})
            logger_x.exception(error, extra={'user': lock_name})
            soc.close()
            sockets.remove(next(x for x in sockets if x["socket"] == soc))
            return

#function for checking access
def check_booking(lock_name, card_uid):
    #lockname = mac addres of thr lock controller
    #card uid = serial number of EAC
    return 0,0


def main():
    global sock
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    set_logger(logger_x, "server.log")
    set_logger(logger, "bad.log")
    logger_x.info("Start", extra = {'user':'server'})

    #creating server on port 8000
    tcp_socket_host = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    tcp_socket_host.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, True)
    tcp_socket_host.bind((server_ip, server_port))
    tcp_socket_host.listen(8)
    
    #creating separate thread for client
    thread = threading.Thread(target=accept_read, args=(tcp_socket_host,))
    thread.start()

    #creating server for master on port master_port in localhost
    soc_master = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    soc_master.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, True)
    soc_master.bind(('127.0.0.1', master_port))
    soc_master.listen(8)

    #master can connect to server many times, but only one master can be at a time
    while True:
        sock, addr_client=soc_master.accept()
        logger_x.info("Master connected", extra = {'user':'server'})

        while True:
            try:
                recv_data = sock.recv(1024)
                if not recv_data:
                    logger_x.info("master disconnected", extra = {'user':'server'})
                    sock.close()
                    break

                #message from master -> processing and send to client
                if recv_data:
                    logger_x.info("Data from master: %s", 
                                  str(recv_data), 
                                  extra = {'user':'server'})
                    try:
                        #message format from master : "mac/open/time" 
                        mac    =     (str(recv_data.decode("ascii")).split('/'))[0]
                        action =     (str(recv_data.decode("ascii")).split('/'))[1]
                        time   = int((str(recv_data.decode("ascii")).split('/'))[2])
                    except IndexError:
                        logger_x.info("wrong message format", extra = {'user':'server'})
                        continue
                    try:
                        soc1 = (next(x for x in sockets if x["mac"] == mac))["socket"]
                        #open for time seconds
                        if (action == "open"):
                            soc1.send(f'open 1 {time:09}'.encode("gbk"))
                        #update admin EAC list
                        if (action == "update"):
                            key_file = open(admin_EAC_path + mac + ".txt", "r")
                            Lines = key_file.readlines()
                            keys = "update"
                            for line in Lines:
                                keys += " " + line.split('/')[0].strip().lower()
                            soc1.send(keys.encode("gbk"))
                        #scan EAC functionality
                        if (action == "scan"):
                            soc1.send(f"scan {time:09}".encode("gbk"))
                    #if client not found -> report log
                    except StopIteration:
                        logger_x.info("%s", 
                                      str(recv_data), 
                                      extra = {'user':'server'})
            except OSError:
                logger_x.info("master disconnected", extra = {'user':'server'})
                sock.close()
                break

def set_logger(logger: logging.Logger, filename):
    format = "%(asctime)s >>> %(process)d %(user)-12s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=format)
    filehand = logging.FileHandler(logs_path + filename)
    filehand.setFormatter(logging.Formatter(format))
    logger.addHandler(filehand)


if __name__ == '__main__':
    main()
