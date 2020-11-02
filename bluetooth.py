import bluetooth
import os
import time


class Bluetooth:
    """
    Bluetooth is the method of the open Bluetooth method and connect with engineer
    """

    def main(self):
        """
        main method is output the message to the engineer and call the search method
        """
        num =1
        print("Bluetooth pairing for engineer!!!")
        return self.search(num)

    # Search for device based on device's name
    def search(self,num):
        """
        search method let the AP to search the nearby devices and get the mac address return to system.py
        :param num: get number from main method
        :return: get the mac address return to system
        """
        while True:
            if num ==1:
                device_address = None
                time.sleep(3)  # Sleep three seconds
                nearby_devices = bluetooth.discover_devices()

                for mac_address in nearby_devices:
                    device_address = mac_address
                    break
                if device_address is not None:
                    data = [{'mac_address': device_address, 'type': 4}]
                    break

                else:
                    print("Please open your bluetooth!")

        return data
