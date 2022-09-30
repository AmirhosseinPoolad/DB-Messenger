#TODO: forget password DONE
#TODO: Block remove from friend request
#TODO: Unblock
#TODO: Single log in
#TODO: Log
#TODO: show likes in list
#TODO: delete account remove from friend list and shown in message list
import socket
from urllib import response
import mysql.connector
import json
from hashlib import sha256
from datetime import date, datetime
from _thread import *
import threading

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

signup_query = "INSERT INTO `messaging`.`user`\
                        (`iduser`,\
                        `username`,\
                        `firstname`,\
                        `lastname`,\
                        `phone`,\
                        `email`,\
                        `idsecurity`,\
                        `securityanswer`,\
                        `password`,\
                        `isdeleted`)\
                        VALUES\
                        ({iduser},\
                        '{username}',\
                        '{firstname}',\
                        '{lastname}',\
                        '{phone}',\
                        '{email}',\
                        {idsecurity},\
                        '{securityanswer}',\
                        '{password}',\
                        0);"

login_query = "SELECT password, iduser FROM user WHERE username = '{username}';"

getmsg_query = "SELECT * FROM message WHERE fromid = {} OR toid = {} ORDER BY date DESC;"

likemsg_query = "INSERT INTO `messaging`.`likes`(`userid`,`msgid`)VALUES({userid},{msgid});"

delacc_query = "UPDATE `messaging`.`user` SET `isdeleted` = 1 WHERE `iduser` = {};"

sendmsg_query = "INSERT INTO `messaging`.`message`\
                (`messageid`,\
                `fromid`,\
                `toid`,\
                `text`,\
                `date`)\
                VALUES\
                ({messageid},\
                {fromid},\
                {toid},\
                '{text}',\
                NOW());"

usersearch_query = "SELECT iduser, username, firstname, lastname, phone, email FROM user WHERE username LIKE '%{}%'"

getreqs_query = "SELECT followingid\
                FROM friend AS f\
                WHERE f.followedid = {userid} AND NOT EXISTS\
                (SELECT * FROM friend AS g WHERE f.followingid = g.followedid and g.followingid = {userid})"

getfriends_query = "SELECT followingid\
                FROM friend AS f\
                WHERE f.followedid = {userid} AND EXISTS\
                (SELECT * FROM friend AS g WHERE f.followingid = g.followedid and g.followingid = {userid})"

block_query = "INSERT INTO `messaging`.`blocks`\
               (`blockeeid`,\
               `blockedid`)\
                VALUES\
                ({blockeeid},\
                {blockedid});"

block_query = "INSERT INTO `messaging`.`blocks`\
               (`blockeeid`,\
               `blockedid`)\
                VALUES\
                ({blockeeid},\
                {blockedid});"

unblock_query = ""

removefriend_query = ""

addfriend_query = "INSERT INTO `messaging`.`friend`\
                    (`followedid`,\
                    `followingid`)\
                    VALUES\
                    ({followedid},\
                    {followingid});\
                    "

usercount_query = "SELECT COUNT(iduser) FROM user"
msgcount_query = "SELECT COUNT(messageid) FROM message"
getuser_query = "SELECT * FROM user WHERE username = '{}'"
changepass_query = "UPDATE `messaging`.`user`\
                    SET\
                    `password` = {password},\
                    WHERE `username` = '{username}';"


def logged_in(c, cursor, db, userid):
    while True:
        data = c.recv(1024)
        if not data:
            print('Bye')
            break
        client_dict = json.loads(data)
        req = client_dict['Request']
        if req == "STOP":
            return
        elif req == "LISTMSGS":
            # TODO: seen
            # TODO: deleted account
            query = getmsg_query.format(userid, userid)
            cursor.execute(query)
            result = cursor.fetchall()
            c.send(json.dumps(result,default=json_serial).encode('ascii'))
        elif req == "LIKEMSGS":
            query = likemsg_query.format(
                userid=userid, msgid=client_dict['MessageID'])
            cursor.execute(query)
            db.commit()
        elif req == "DELETEACCOUNT":
            query = delacc_query.format(userid)
            cursor.execute(query)
            db.commit()
        elif req == "SEND":
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
            query = getfriends_query.format(userid=userid)
            cursor.execute(query)
            result = cursor.fetchall()
            if ((int(client_dict['id']),) in result):
                query = msgcount_query
                cursor.execute(query)
                result = cursor.fetchall()
                count = result[0][0]
                query = sendmsg_query.format(messageid=count+1, fromid=userid, toid=client_dict['id'],
                                             text=client_dict['text'])
                cursor.execute(query)
                db.commit()
                response = {'Code': "Success"}
                c.send(json.dumps(response).encode('ascii'))
            else:
                response = {'Code': "Error", 'Reason': "Not a friend"}
                c.send(json.dumps(response).encode('ascii'))
        elif req == "USRSEARCH":
            query = usersearch_query.format(client_dict['SearchSTR'])
            cursor.execute(query)
            result = cursor.fetchall()
            c.send(json.dumps(result).encode('ascii'))
        elif req == "LISTREQUESTS":
            query = getreqs_query.format(userid=userid)
            cursor.execute(query)
            result = cursor.fetchall()
            c.send(json.dumps(result).encode('ascii'))
        elif req == "LISTFRIENDS":
            query = getfriends_query.format(userid=userid)
            cursor.execute(query)
            result = cursor.fetchall()
            c.send(json.dumps(result).encode('ascii'))
        elif req == "BLOCK":
            query = block_query.format(
                blockeeid=userid, blockedid=client_dict['id'])
            cursor.execute(query)
        elif req == "ADDFRIEND":
            query = addfriend_query.format(
                followedid=client_dict['id'], followingid=userid)
            cursor.execute(query)
            db.commit()
            response = {'Code': "Success"}
            c.send(json.dumps(response).encode('ascii'))
            pass


def run(c, cursor, db):
    logged = 0
    userid = 0
    while True:
        data = c.recv(1024)
        if not data:
            print('Bye')
            break
        client_dict = json.loads(data)
        req = client_dict['Request']
        if logged == 0:
            if(req == "SGNUP"):
                # TODO: phone sanitization
                query = usercount_query
                cursor.execute(query)
                result = cursor.fetchall()
                count = result[0][0]
                query = signup_query.format(iduser=count+1, username=client_dict['Username'],
                                            firstname=client_dict['FirstName'], lastname=client_dict['LastName'],
                                            phone=client_dict['Phone'], email=client_dict['Email'],
                                            idsecurity=client_dict['SecurityQ'],
                                            securityanswer=client_dict['SecurityAns'],
                                            password=sha256(client_dict['Password'].encode('utf-8')).hexdigest())
                print(query)
                cursor.execute(query)
                db.commit()
            elif req == "LGIN":
                #TODO: simultaneus
                query = login_query.format(username=client_dict['Username'])
                cursor.execute(query)
                result = cursor.fetchall()
                for x in result:
                    if sha256(client_dict['Password'].encode('utf-8')).hexdigest() == x[0]:
                        userid = x[1]
                        response = {'Code': "Success", 'UserID': userid}
                        c.send(json.dumps(response).encode('ascii'))
                        logged_in(c, cursor, db, userid)
                        return
            elif req == "FORGOT":
                query = getuser_query.format(client_dict['Username'])
                cursor.execute(query)
                username_result = cursor.fetchall()
                if(username_result[0][6] == client_dict['SecurityQ'] and username_result[0][7] == client_dict['SecurityAns']):
                    query = changepass_query.format(username=client_dict['Username'], password=client_dict['NewPass'])
                    cursor.execute(query)
                    db.commit()
            elif req == "STOP":
                return
        # elif logged == 1:

        print(client_dict)

    # connection closed
    c.close()


def Main():
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="1234",
        database="messaging"
    )
    mycursor = mydb.cursor()

    host = ""

    port = 8080
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))

    s.listen(5)

    try:
        while True:
            c, addr = s.accept()

            print('Connected to :', addr[0], ':', addr[1])
            start_new_thread(run, (c, mycursor, mydb))
    except KeyboardInterrupt:
        s.close()


if __name__ == '__main__':
    Main()
