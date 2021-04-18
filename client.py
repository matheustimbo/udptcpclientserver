import socket
import zlib

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

ack = b"\0"

def check_sum(data: bytes):
    return (zlib.crc32(data) & 0xffffffff).to_bytes(6, "big")

def switch_ack(ack: bytes) -> bytes: 
    if ack == b"\0":
      return b"\1"
    else:
      return b"\0"

serverAddressPort = ("127.0.0.1", 20001)

bufferSize = 1024
img_data_size = 1017
is_first_send = True
local_img_path = "./doge.jpg"
server_path_bytes_len = 128
UDPClientSocket.settimeout(3)

server_path = "./downloads/downloaded_img3.jpg"
initial_server_path_bytes = str.encode(server_path)
server_path_bytes = b""
for _ in range(server_path_bytes_len - len(initial_server_path_bytes)):
    server_path_bytes += b'\0'
server_path_bytes += initial_server_path_bytes


with open(local_img_path, "rb") as f:
    total_data = b"\1"
    total_data += server_path_bytes
    img_package_bytes = f.read(1017 - server_path_bytes_len - 1)
    total_data += img_package_bytes

    while img_package_bytes:
        sent = False
        if is_first_send == False:
              total_data = b"\0"
              total_data += img_package_bytes
        upload_data_bytes = ack + check_sum(total_data) + total_data
        while not sent:
            try:
                UDPClientSocket.sendto(upload_data_bytes, serverAddressPort)
                is_first_send = False
                bytesAddressPair = UDPClientSocket.recvfrom(bufferSize)
                msgFromServer = bytesAddressPair[0]
                address = bytesAddressPair[1]

                ack_from_server = msgFromServer[0:1]
                check_sum_from_server = msgFromServer[1:]
                
                if ack_from_server == ack and check_sum(ack_from_server) == check_sum_from_server:
                    sent = True
                    ack = switch_ack(ack)
                    img_package_bytes = f.read(img_data_size - 1)
                    
            except socket.timeout:
                pass
    finished_upload_data_bytes = b"\2"
    UDPClientSocket.sendto(finished_upload_data_bytes, serverAddressPort)

      
        

