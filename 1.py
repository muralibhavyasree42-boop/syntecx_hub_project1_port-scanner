import socket
import threading
import time
from queue import Queue

# Maximum number of threads
MAX_THREADS = 100

# Thread lock for safe printing
print_lock = threading.Lock()

# Queue to store ports
port_queue = Queue()

# -----------------------------
# Function to scan a single port
# -----------------------------
def scan_port(host):
    while not port_queue.empty():
        port = port_queue.get()

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)

            result = sock.connect_ex((host, port))

            with print_lock:
                if result == 0:
                    message = f"[OPEN] Port {port}"
                else:
                    message = f"[CLOSED] Port {port}"

                print(message)
                log_result(message)

            sock.close()

        except Exception:
            # Ignore unexpected errors safely
            pass

        port_queue.task_done()


# -----------------------------
# Logging function
# -----------------------------
def log_result(message):
    with open("scan_results.txt", "a") as file:
        file.write(message + "\n")


# -----------------------------
# Main scanning function
# -----------------------------
def start_scan(host, start_port, end_port):
    # Add ports to queue
    for port in range(start_port, end_port + 1):
        port_queue.put(port)

    # Create threads
    threads = []
    for _ in range(min(MAX_THREADS, end_port - start_port + 1)):
        thread = threading.Thread(target=scan_port, args=(host,))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    # Wait until queue is empty
    port_queue.join()


# -----------------------------
# Main Program
# -----------------------------
def main():
    print("=" * 50)
    print("        TCP PORT SCANNER")
    print("=" * 50)

    host_input = input("Enter Host (IP or Domain): ")

    try:
        host = socket.gethostbyname(host_input)
    except socket.gaierror:
        print("Invalid Host. Exiting program.")
        return

    try:
        start_port = int(input("Enter Start Port: "))
        end_port = int(input("Enter End Port: "))
    except ValueError:
        print("Invalid port number.")
        return

    if start_port < 0 or end_port > 65535 or start_port > end_port:
        print("Invalid port range.")
        return

    print(f"\nScanning {host} from port {start_port} to {end_port}")
    print("-" * 50)

    start_time = time.time()

    start_scan(host, start_port, end_port)

    end_time = time.time()

    print("-" * 50)
    print(f"Scan completed in {round(end_time - start_time, 2)} seconds")
    print("Results saved in scan_results.txt")
    print("=" * 50)


if __name__ == "__main__":
    main()