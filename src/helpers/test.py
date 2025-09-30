import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("169.254.222.127", 0))  # Replace with the laptop's (client's) LAN IP
s.connect(("nursing-04.local", 8080))
print("Connection successful!")
