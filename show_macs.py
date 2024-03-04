import csv
from scrapli import Scrapli
from scrapli.exceptions import ScrapliException
from textfsm import TextFSM

password = input("Enter password: ")

# set variables
inventory_file = "inventory.csv"
output_file = "mac_address_table.csv"
command = "show mac address-table"
template_file = "templates/cisco_ios_show_mac-address-table.textfsm"

# initiliaze empty list of devices
inventory_list = []

# open up the inventory file and create list of devices
with open(inventory_file, mode='r') as csvfile:
    reader = csv.reader(csvfile)
    for column in reader:
        # Assuming the CSV columns are hostname, username, password in that order
        device_dict = {
            'host'              : column[0],
            'auth_username'     : column[1],
            'auth_password'     : password,
            'auth_strict_key'   : False,
            'platform'          : "cisco_iosxe"
        }
        # Add the dictionary to the list
        inventory_list.append(device_dict)


# open up the output file for writing
with open(output_file, mode="w+", newline="") as csvfile:
    writer = csv.writer(csvfile)

    # write the header row
    fieldnames = ["Device", "MAC", "TYPE", "VLAN", "PORT"] 
    writer.writerow(fieldnames)

    # loop through each device, get the mac table and parse it
    for device in inventory_list:
        try:
            with Scrapli(**device) as conn:
                response = conn.send_command(command)
            # parse the response with fsm, result will be a list of lists
            with open(template_file) as template:
                fsm = TextFSM(template)
                result = fsm.ParseText(response.result)
        except Exception as e:
            print(f"Error connecting to {device['host']}: {e}")

        # write each entry to the csv file, with the device ip or hostname as first column
        for row in result:
            row.insert(0,device['host'])      
            if 'CPU' not in row[-1]:
                row[-1] = row[-1][0]    
                writer.writerow(row)