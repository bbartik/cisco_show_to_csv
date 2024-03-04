from scrapli import Scrapli
from scrapli.driver.core import IOSXEDriver
import csv
from textfsm import TextFSM

# Connection details for your Cisco IOS device
device = {
    "host": "172.20.128.89",
    "auth_username": "cisco",
    "auth_password": "cisco",
    "auth_strict_key": False,
    "platform": "cisco_iosxe",  # Adjust as needed
}

# Connect to the device
conn = Scrapli(**device)
conn.open()

# Execute the "show interface status" command
response = conn.send_command("show interface description")

# Parse the output with TextFSM
with open("templates/cisco_ios_show_interfaces_description.textfsm", "r") as template_file:
    fsm = TextFSM(template_file)
    result = fsm.ParseText(response.result)
    breakpoint()

# Define your CSV file path
csv_file_path = "interface_status.csv"

# Write the parsed data to a CSV file
with open(csv_file_path, mode="w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(fsm.header)  # Write the header row
    for row in result:
        writer.writerow(row)

# Close the connection
conn.close()

print(f"Data written to {csv_file_path}")
