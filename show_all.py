from scrapli import Scrapli
import csv
from textfsm import TextFSM



def execute_and_parse(device, command, template_path):
    try:
        with Scrapli(**device) as conn:
            response = conn.send_command(command)
        with open(template_path) as template_file:
            fsm = TextFSM(template_file)
            result = fsm.ParseText(response.result)
            # Convert to list of dicts for easier processing
            keys = fsm.header
            parsed_data = [dict(zip(keys, entry)) for entry in result]
        return parsed_data
    except Exception as e:
        print(f"Error connecting to {device['host']}: {e}")
        return []


if __name__ == "__main__":


    # Define the path to your CSV file
    csv_file_path = 'inventory.csv'

    # Initialize an empty list to hold the dictionaries
    inventory_list = []

    # Open the CSV file and read each row into a dictionary
    with open(csv_file_path, mode='r') as csvfile:
        reader = csv.reader(csvfile)
        for col in reader:
            # Assuming the CSV columns are hostname, username, password in that order
            device_dict = {
                'hostname': col[0],
                'username': col[1],
                'password': col[2],
            }
            # Add the dictionary to the list
            inventory_list.append(device_dict)


    # Credentials and other details
    device_base = {
        "auth_strict_key": False,
        "platform": "cisco_iosxe",
    }

    # CSV File setup
    csv_file_path = "merged_interface_data.csv"
    fieldnames_set = False

    with open(csv_file_path, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        
        # Process each device
        for node in inventory_list:
            device = device_base.copy()
            device["host"] = node["hostname"]
            device["auth_username"] = node["username"]
            device["auth_password"] = node["password"]
            
            # Execute commands and parse outputs
            status_data = execute_and_parse(device, "show interface switchport", "templates/cisco_ios_show_interfaces_switchport.textfsm")
            description_data = execute_and_parse(device, "show interface description", "templates/cisco_ios_show_interfaces_description.textfsm")

            # Merge the outputs based on the interface name and add device IP
            for entry in status_data:
                entry['DeviceIP'] = node["hostname"]  # Add device IP to each row
                entry['serial'] = node["serial"]  # Add device IP to each row

            # for entry in description_data:
            #     entry['DeviceIP'] = ip  # Ensure device IP is also added here for consistency
            
            merged_data = {}
            for entry in status_data:
                interface = entry['INTERFACE']
                merged_data[interface] = entry
                del entry["SWITCHPORT_MONITOR"]

            for entry in description_data:
                del entry["PROTOCOL"]
                interface = entry['PORT']
                if interface in merged_data:
                    merged_data[interface].update(entry)
                else:
                    merged_data[interface] = entry
            
            # rearrange so device_ip is first
            merged_data_update = {}
            for k, v in merged_data.items():
                try:
                    new_dict = {"DeviceIP": v["DeviceIP"]}
                except Exception as e:
                    new_dict = {"DeviceIP": "n/a"}
                for key, value in v.items():
                    if key != "DeviceIP":
                        new_dict[key] = value                
                        merged_data_update.update({k: new_dict})
            
            # Write header once
            if not fieldnames_set:
                #writer.writerow(['DeviceIP'] + list(list(merged_data.values())[0].keys()))
                writer.writerow(list(list(merged_data_update.values())[0].keys()))
                fieldnames_set = True
            
            # Write merged data to CSV, including device IP as the first column
            for row in merged_data_update.values():
                writer.writerow(row.values())

    print(f"Merged data written to {csv_file_path}")
