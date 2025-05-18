import socket
import threading
import csv
import json
import os
from datetime import datetime


class EmailServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_threads = []

    def create_csv_file(self, filename, email_data):
        try:
            folder_path = os.path.join(os.getcwd(), 'DataBase')
            os.makedirs(folder_path, exist_ok=True)
            full_filename = os.path.join(folder_path, filename)
            file_exists = os.path.exists(full_filename)

            with open(full_filename, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)

                if not file_exists:
                    csv_writer.writerow(['Data', 'Time', 'Sender', 'Subject', 'Body'])

                date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                date, time = date_time.split()

                sender = email_data.get('sender', '')
                subject = email_data.get('subject', '')
                body = email_data.get('body', '')

                csv_writer.writerow([date, time, sender, subject, body])
                print('Email added to the Mailserver....')

        except Exception as e:
            print(f"Error creating CSV file: {e}")

    def read_mailbox(self, client_socket, recv_email):
        try:
            mailbox_file = f"{recv_email.replace('@', '_').replace('.com', '')}.csv"
            full_filename = os.path.join(os.getcwd(), 'DataBase', mailbox_file)

            if not os.path.exists(full_filename):
                client_socket.send("NO_MAILBOX".encode('utf-8'))
                print(f"No mailbox found for {recv_email}.")
                return

            with open(full_filename, 'r') as csvfile:
                csv_reader = csv.reader(csvfile)
                next(csv_reader)  # Skip the header row
                mail_list = []
                for row in csv_reader:
                    mail_list.append({
                        'Date': row[0],
                        'Time': row[1],
                        'Sender': row[2],
                        'Subject': row[3],
                        'Body': row[4],
                    })
            client_socket.send(json.dumps(mail_list).encode('utf-8'))
            print(f"Sent mailbox contents to {recv_email}.")

        except Exception as e:
            print(f"Error reading mailbox: {e}")

    def handle_client(self, client_socket):
        try:
            command = client_socket.recv(1024).decode('utf-8')
            client_socket.send("ACK1".encode('utf-8'))
            # command = 'send'

            recv_email = client_socket.recv(1024).decode('utf-8')
            client_socket.send("ACK2".encode('utf-8'))

            if not recv_email:
                print("Error: Empty recipient email received.")
                return

            if command == 'send':
                email_data_str = client_socket.recv(1024).decode('utf-8')
                if not email_data_str:
                    print("Error: Empty email data received.")
                    return
                email_data = json.loads(email_data_str)
                try:
                    self.create_csv_file(f"{recv_email.replace('@', '_').replace('.com', '')}.csv", email_data)
                except Exception as e:
                    print(f'Email Not saved: {e}')
                print(f"Message stored in {recv_email} mailbox.")

            elif command == 'receive':
                self.read_mailbox(client_socket, recv_email)

            else:
                print(f"Error: Unknown command '{command}' received.")

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def start_server(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()

            print(f"Server listening on {self.host}:{self.port}")

            while True:
                client_socket, addr = self.server_socket.accept()
                print(f"Accepted connection from Client{len(self.client_threads)+1} : {addr}")

                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
                self.client_threads.append(client_thread)

        except Exception as e:
            print(f"Error in server: {e}")
        finally:
            self.server_socket.close()


if __name__ == "__main__":
    server = EmailServer('192.168.193.151', 5555)
    server.start_server()
