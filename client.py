# Import socket module
import socket
import json


def Main():
    logged = 0
    state = 0
    # state: 0 -> main
    #       1 ->
    userid = 0
    host = '127.0.0.1'

    # Define the port on which you want to connect
    port = 8080

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to server on local computer
    s.connect((host, port))

    # message you send to server
    while True:
        if logged == 0:
            print("exit, signup, login, forgot")
            user_input = input()
            user_input = user_input.split()
            if(user_input[0] == "exit"):
                req = {'Request': 'STOP'}
                message = json.dumps(req)
                s.send(message.encode('ascii'))
                break
            elif(user_input[0] == "signup"):
                username = input("Username: ")
                firstname = input("First name: ")
                lastname = input("Last name: ")
                phone = input("Phone: ")
                email = input("Email: ")
                securityq = int(input("Security question: 1- First grade teacher's name, 2- Nickname "))
                securityans = input("Answer: ")
                password = input("Password: ")
                req = {'Request': "SGNUP", 'Username': username, 'FirstName': firstname, 'LastName': lastname,
                       'Phone': phone, 'Email': email, 'SecurityQ': securityq, 'SecurityAns': securityans, 'Password': password}
                message = json.dumps(req)
                s.send(message.encode('ascii'))
            elif (user_input[0] == "login"):
                username = input("Username: ")
                password = input("Password: ")
                req = {'Request': "LGIN",
                       'Username': username, 'Password': password}
                message = json.dumps(req)
                s.send(message.encode('ascii'))
                data = s.recv(1024)
                response = json.loads(data)
                if(response['Code'] == "Success"):
                    logged = 1
                    userid = response['UserID']
            elif (user_input[0] == "forgot"):
                username = input("Username: ")
                securityq = int(input("Security question: 1- First grade teacher's name, 2- Nickname "))
                answer = input("Answer: ")
                newpass = input("New Password: ")
                req = {'Request': "FORGOT", 'Username': username, 'SecurityQ': securityq, 'SecurityAns': answer, 'NewPass': newpass}
                message = json.dumps(req)
                s.send(message.encode('ascii'))
                data = s.recv(1024)
                response = json.loads(data)
                if(response['Code'] == "Success"):
                    print("Password successfully changed")
        elif logged == 1:
            print("exit, list, like 'id', search 'username', friends, requests, request 'user id'\n\
                  search 'partial string', block 'user id', dltacc\n\
                  send 'user id' 'txt'")
            user_input = input()
            user_input = user_input.split()
            #user_input = input("-1: exit, 1: list messages, 2: search users, 3: friends menu, 4: block menu, 5: delete account, send id 'text'")
            if (user_input[0] == "exit"):
                req = {'Request': 'STOP'}
                message = json.dumps(req)
                s.send(message.encode('ascii'))
                data = s.recv(1048576)
                response = json.loads(data)
                print(response)
                break

            elif (user_input[0] == "send"):
                req = {'Request': 'SEND',
                       'id': user_input[1], 'text': " ".join(user_input[2:])}
                message = json.dumps(req)
                s.send(message.encode('ascii'))
                data = s.recv(1024)
                response = json.loads(data)
                print(response)
            elif(user_input[0] == "list"):
                req = {'Request': "LISTMSGS"}
                message = json.dumps(req)
                s.send(message.encode('ascii'))
                data = s.recv(1048576)
                response = json.loads(data)
                for msg in response:
                    print("ID: " + str(msg[0]) + ", From: " + str(msg[1]) +
                          ", To: " + str(msg[2]) + ", Date: " + str(msg[4]))
                    print(msg[3])

            elif user_input[0] == "like":
                req = {'Request': "LIKEMSGS",
                       'MessageID': user_input[1], 'UserID': userid}
                message = json.dumps(req)
                s.send(message.encode('ascii'))

            elif(user_input[0] == "search"):
                search_str = user_input[1]
                req = {'Request': "USRSEARCH", 'SearchSTR': search_str}
                message = json.dumps(req)
                s.send(message.encode('ascii'))
                data = s.recv(1048576)
                response = json.loads(data)
                for user in response:
                    print(user)

            elif(user_input[0] == "requests"):
                req = {'Request': "LISTREQUESTS"}
                message = json.dumps(req)
                s.send(message.encode('ascii'))
                data = s.recv(1048576)
                response = json.loads(data)
                for user in response:
                    print(user)

            elif(user_input[0] == "friends"):
                req = {'Request': "LISTFRIENDS"}
                message = json.dumps(req)
                s.send(message.encode('ascii'))
                data = s.recv(1048576)
                response = json.loads(data)
                for user in response:
                    print(user)

            elif(user_input[0] == "request"):
                req = {'Request': "ADDFRIEND", 'id': user_input[1]}
                message = json.dumps(req)
                s.send(message.encode('ascii'))

            elif(user_input[0] == "block"):
                req = {'Request': "BLOCK", 'id': user_input[1]}
                message = json.dumps(req)
                s.send(message.encode('ascii'))

            elif(user_input[0] == "dltacc"):
                in_str = input("Are you sure?(y/n) ")
                if in_str == "y":
                    req = {'Request': "DELETEACCOUNT", 'UserID': userid}
                    s.send(message.encode('ascii'))
                    logged = 0
    # close the connection
    s.close()


if __name__ == '__main__':
    Main()
