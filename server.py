import socket
import zlib

localIP = "127.0.0.1"
localPort = 20001
bufferSize = 1024

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((localIP, localPort))

ack = b"\1"
download_directory = None

def check_sum(data: bytes) -> bool:
    return (zlib.crc32(data) & 0xffffffff).to_bytes(6, "big")

def switch_ack(ack: bytes) -> bytes: 
    if ack == b"\0":
      return b"\1"
    else:
      return b"\0"

def read_client_message(client_message, ack, download_directory) -> bytes:
    finished_message = client_message[0:1] == b"\2"
    if not finished_message:
        client_ack = client_message[0:1]
        client_check_sum_result = client_message[1:7]
        local_check_sum_result = check_sum(client_message[7:])
      
        if client_check_sum_result == local_check_sum_result and ack != client_ack:
            ack = switch_ack(ack)
            client_has_path = client_message[7:8] == b"\1"
            img_package_bytes = None
            if client_has_path:
                download_directory = client_message[8:136].decode().replace('\x00', '')
                img_package_bytes = client_message[136:]
            else:
                img_package_bytes = client_message[8:]
            
            with open(download_directory, "ab") as f:
                f.write(img_package_bytes)
    else:
        ack = b"\1"
        download_directory = None
    server_response = b""
    server_response += ack
    server_response += check_sum(server_response)
    return ack, download_directory, server_response


while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    client_message = bytesAddressPair[0]
    address = bytesAddressPair[1]
    ack, download_directory, server_response = read_client_message(client_message, ack, download_directory)
    

    UDPServerSocket.sendto(server_response, address)