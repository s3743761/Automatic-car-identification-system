import re
import webbrowser
import socketio
import sys
import Bluetooth
import time

car_id = 2

login = False
sio = socketio.Client()

class ap:
    """
    the agent pi class, used for receiveing and communicating with MP
    """
    def __init__(self):
        self._blueTooth = Bluetooth()

    def menu(self):
        global login
        """
        menu for ap, user can either log in with image or username and password
        """
        print('{:^24s}'.format("\nWelcome to the car rental system"))
        print('{:^24s}'.format("---------------MENU---------------"))
        print(  '1:login with your image\n'
                '2:login with Username and Password\n'
                '3:Bluetooth function\n'
                '4:exit')

        while True:
            if login == True:
                break
            Input = input("Choose from the menu:\n")
            if Input =="1":
                sio.connect('http://127.0.0.1:5000')
                recognise().run()
                sio.emit('name',{'imgname':recognise().name}) 
            
            elif Input =="2":
                sio.connect('http://127.0.0.1:5000')
                print('my sid is', sio.sid)
                username = input('Please enter your username: ')
                password = input('Please enter your password: ')
                sio.emit('identity', {'username' : username, 'password' : password})

            elif Input =="3":
                message = self._blueTooth.main()
                time.sleep(5)
                continue

            elif Input =="4":
                print("thank you for using our system")
                sys.exit()
            else:
                print("Enter from 1 to 3")
        #while(quit == False):
        while login == True:
            print('1:unlock the car\n'
                    '2:return the car\n'
                    '3:show all the cars\'location\n'
                    '4:exit') 
            
            option = input('Please choose an option:\n')
            if(option == '1'):
                print('The car is unlocked!!')
            elif(option == '2'):
                sio.emit('finish', {'car_id' : car_id})
            elif(option == '3'):
                pass
            elif(option == '4'):
                sio.disconnect()
                sys.exit()    

  
    def check(self):
        """
        check if the user has logged in
        """
        if bool(login) is False:
            print("You haven't logged in yet\n")
            print("Please login with password or your own image")
            
@sio.event
def connect():
    """
    when successfully connecte with master pi
    """
    print("I'm connected!")

@sio.event
def connect_error():
    """
    print when connection has error
    """
    print("The connection failed!")

@sio.event
def disconnect():
    """
    when disconnect from the master pi
    """
    print("I'm disconnected!")

@sio.event
def my_event(sid, data):
    # handle the message
    return "OK", 123

@sio.on('my response')
def on_message(data):
    print('I received a message!' + str(data))

@sio.on('validate')
def on_validate_message(data):
    global login
    """
    sub-menu for the ap
    """
    print('I received a message!' + str(data))
    result = data['result']
    if result == 'success':
        print('Congradulation! You login successfully!!')
        login = True
        
        
    else:
        print("Error, your username or password incorrect!!")

if __name__ == '__main__':
    ap().menu()
   
    
            
