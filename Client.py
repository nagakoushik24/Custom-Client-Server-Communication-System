import socket
import json
from datetime import datetime
from tkinter import Tk, simpledialog

from Main import *

class EmailClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port

    def get_email_info_from_gui(self):
        # Replace these lines with the actual code to get email information from your GUI.
        sender, recipient, subject, body = composer_page_gui()
        return sender, recipient, subject, body

    def send_email(self, sender, recipient, subject, body):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.server_ip, self.server_port))

                client_socket.send("send".encode('utf-8'))
                acknowledgment = client_socket.recv(1024).decode('utf-8')
                if acknowledgment != "ACK1":
                    print("Server did not acknowledge. Aborting.")
                    return

                # Send recipient's email address to the server
                client_socket.send(recipient.encode('utf-8'))

                acknowledgment = client_socket.recv(1024).decode('utf-8')
                if acknowledgment != "ACK2":
                    print("Server did not acknowledge. Aborting.")
                    return

                date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                date, time = date_time.split()

                # Prepare email data in JSON format
                email_data = {
                    'Date': date,
                    'Time': time,
                    'sender': sender,
                    'subject': subject,
                    'body': body
                }

                # Send email data to the server
                client_socket.sendall(json.dumps(email_data).encode('utf-8'))

                print(f"Email sent from {sender} to {recipient}")

        except Exception as e:
            print(f"Error sending email: {e}")

    def receive_email(self, recipient):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.server_ip, self.server_port))

                client_socket.send("receive".encode('utf-8'))
                acknowledgment = client_socket.recv(1024).decode('utf-8')
                if acknowledgment != "ACK1":
                    print("Server did not acknowledge. Aborting.")
                    return

                client_socket.send(recipient.encode('utf-8'))

                acknowledgment = client_socket.recv(1024).decode('utf-8')
                if acknowledgment != "ACK2":
                    print("Server did not acknowledge. Aborting.")
                    return

                # Receive and print the mailbox contents
                mailbox_contents = client_socket.recv(1024).decode('utf-8')
                emails = json.loads(mailbox_contents)
                return emails

        except Exception as e:
            print(f"Error receiving email: {e}")


if __name__ == "__main__":
    # Get the user's choice directly from the GUI
    base_page_gui()
    #
    # if user_choice == 'send':
    #     client = EmailClient(server_ip, server_port)
    #
    #     # Get email information from the GUI
    #     sender, recipient, subject, body = client.get_email_info_from_gui()
    #     print(sender, recipient)
    #
    #     client.send_email(sender, recipient, subject, body)
    #
    # elif user_choice == 'receive':
    #     client = EmailClient(server_ip, server_port)
    #     recipient = input("Enter your email address (recipient): ")
    #     client.receive_email(recipient)
    #
    # elif user_choice == 'exit':
    #     print("Exiting the email client.")
    # else:
    #     print("Invalid choice. Please enter 'send', 'receive', or 'exit'.")
