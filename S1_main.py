import socket
import threading
import time
import random
import pymysql
import datetime
import pickle
import sqlite3
import json
from payments import make_payment 

global id_limit 
id_limit= 297

class Claim_Session(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        pass


class TR_Session(threading.Thread):

    session_timeout = 300
    status = ''
    prev_msg = ''
    bet_id = ''
    req_msg = ''
    

    def __init__(self,details,db,cur,p_socket,name,messages):
        threading.Thread.__init__(self)
        self.name = name
        self.details = details
        self.db = db
        self.cur = cur
        self.p_socket = p_socket
        self.messages = messages

    #@classmethod  
    def new_message(self ,message):
        
        self.prev_msg = ''
        self.req_msg = ''        
        self.status = 'open'
        self.bet_id = ''
        self.messages.append(message)
        #print('new message : ' , message, 'for : ', self.name)
        #print(self.messages)
        #print('new message  to : ' , threading.current_thread().name)
        
        #self.cur.execute("select * from bett_user where user_id = '{}'".format(self.name))
        #cr = self.cur.fetchone()

        #if cr == None:
            #response1 = "You are not registered"
            #response2 = "to register please send message [reg*{youname and surname}]"


        for text in message[2].split('*'):

            if 'newbet' == text[0]:
                amt_tobet = text[1]
                self.cur.execute("select * from bett_user where user_id = '{}'".format(self.name))
                cs_data = self.cur.fetchone()
                if cs_data[3]>amt_tobet:
                    message = "You have insufficeint balance : ${}".format(cs_data[3])
                    status = 'neg balance*reject'
                    #self.kill()
                else:
                            
                    status = 'betting'
                    req_msg = 'betlist'
                    
                    gen_id = random.random()
                    bet_id  = 'b0' + str(gen_id)[-6:-1]
                    message = 'Your bet id : {}\n'.format(bet_id)
                    self.cur.execute("""create table {}(game varchar(10),
                                        home varchar(10),away varchar(10),draw varchar(10),
                                        home_goals varchar(10),away_goals varchar(10),
                                        btts varchar(10),gain varchar(9))""".format(bet_id))
            
            elif 'edibet' == text[0]:
                message = "Invalid Option selected"
                #self.kill()

            elif text[0][0:1] == 'b0':
                if req_msg == 'betlist':
                    pass
                    #gprocess bett list
                else:
                    message = 'please make new bet'
                    #self.kill()
            elif 'save' == text[0]:
                password = text[1]
                self.cur.execute("select * from bett_user where user_id = '{}'".format(self.name))
                password1 = self.cur.fetchone()[1]
                if password1 == password:
                    if self.status == 'betting':
                        #close bet
                        self.status = 'closed'        
                        self.req_msg = ''
                        self.cur.execute("insert into {} values('closed','-','-','-','-','-','-','gain')".format(self.bet_id))
                        db.commit()
                        #self.kill()
                    else:
                        message = "Please place a bet to save"
                        #self.kill()
                else:
                    message = "Wrong Password\nNext wrong password will lock account"
       

        #self.kill()

    def run(self):

        def start_clock():
            message = 'Session will expire in 15 minutes\nTo reduce traffic'
            time.sleep(self.session_timeout)
            #self.kill()
        start_clock()

        self.name = '{}'.format(self.details[1])
        self.new_message(self.details)

    @classmethod
    def kill(self):
        message = 'Session Expired'
        self.killed = True
        
class PAY_SERVER(threading.Thread):

    def __init__(self,*details):
        threading.Thread.__init__(self)
        self.details = details
    
    def run(self):
        for str1 in self.data:
            if 'dict' in str(type(str1)):
                str2 = str1

                usernmae = str2['uname']
                approvalcode = str2['appr-code']
                payee = str2['payee']
                amt = str2['am-paid']

                db = str2['DB-DB']
                cur = str2['DB-CURSOR']

                cur.execute("select payee, amount from transfers where approval_code = '{}'".format(approvalcode))
                rzltz_data = db.fetchall()
                
                if rzltz_data == None:
                    client.send(('payment not found:{0}'.format(username)).encode('utf-8'))
                    #db.close()

                else:
                    #wait for 2 hrs for another claim
                    current_hr = datetime.datetime.today().hour
                    current_min = datetime.datetime.today().minute
                    day_hour = '{}:{}'.format(current_hr,current_min)

                    try:
                        cur.execute()
                    except Exception as ex:
                        client.send(('Error while processing payment\nTry again later:{0}'.format(username)).encode('utf-8'))
                        db.close()


class REG_SERVER(threading.Thread):

    def __init__(self,*details):
        threading.Thread.__init__(self)
        self.details = details

    def run(self):
        for str1 in self.data:
            if 'dict' in str(type(str1)):
                str2 = str1
                usernmae = str2['uname']
                password = str2['secret-word']
                
                db = str2['DB-DB']
                cur = str2['DB-CURSOR']

                try:
                    cur.execute("create table {0} (ticket unique varchar(20), give_in varchar(6), take_out varchar(10))".format(usernmae))
                    db.commit()
                    
                    ##users-table ## username[phone number] - password - balance[$$] - totalpaid[$$]## 
                    cur.execute("insert into users values('{}','{}','{}','{}')".format(usernmae,password,'0.00','0.00'))
                    db.commit()
                except Exception as ex:
                    client.send(('request not found:{0}'.format(str2[1])).encode('utf-8'))
                    db.close()
                finally:
                    db.close()

class TR_SERVER(threading.Thread):

    def __init__(self,*data):
        threading.Thread.__init__(self)
        self.data = data
        


    def run(self):
        id_limit= 297

        cur = ''
        db = ''
        client = ''

        str5 = '[]'
        _address = ''
        for str1 in self.data:
            if 'dict' in str(type(str1)):
                client = str1['CLIENT']
                db = str1['DB-DB']
                cur = str1['DB-CURSOR']
                #client.send('req-resp-auth'.encode('utf-8'))
                while 1:
                    str2  = pickle.dumps(client.recv(2048))
                    print(str2)
                    continue

                    for _dict in list(str2):
                        #print('messages : ',str2)
                        try:
                            _id = _dict['_id']
                        except:
                            continue

                        if int(_id) > int(id_limit):

                            id_limit = _id

                            print('id limit : ',id_limit)
                            msg_details = _dict
                            _date = msg_details['date']
                            _address = msg_details['address']
                            _body = msg_details['body']
                            str5 = '{}::{}::{}::{}'.format(_id,_address,_body,_date) 
                            try:
                                cur.execute("insert into log values('{}','{}','{}','{}')".format(_id,_date,_body,_address))
                                db.commit()
                            except Exception as ex:
                                error  = ex
                            #print(str5)
                        else:
                            continue

                        if 'reg' in str5.split(':')[2]:
                            
                            reg_code = str5.split(':')[2]
                            reg_details = reg_code.split('*')

                            #reg*fullname*
                            cur.execute("insert into bett_customer values('{}','{}','{}','{}')".format(str5.split(':')[1],reg_details[1],'0','0'))
                            db.commit()

                            response_1 = "Account created successfully \nBalance RTGS $0.00"
                            response_2 = """Deposit any amount using ecocash \na
                                            nd get 20% 
                                            free bonus on your deposit"""
                            
                            #create table u263774611839(bet_id varchar(20) unique, paid varchar(9), gain varchar(9))
                            bettname = 'u{}'.format(_address)
                            cur.execute("create table '{}'(bet_id varchar(20) unique,paid varchar(9),gain varchar(9))".format(bettname))
                            db.commit()

                            #cur.execute("insert into current_message ")


                        elif 'pay' in str5.split('::')[2]:
                            pass
                        elif 'claim' in str5.split('::')[2]:
                            nt = Claim_Session(str5)
                            nt.start()

                        else:
                            found_thread = False

                            p_socket = socket.socket()
                            ip = '192.168.1.117'
                            port = 0
                            p_socket.bind((ip,port))

                            for thread in threading.enumerate():
                                print('Thread Name : ' , thread.name)
                                if thread.name == '{}'.format(_address):
                                    found_thread = True
                                    thread.new_message(str5)
                            if found_thread:
                                pass

                            else:
                                new_thread = TR_Session(str5,db,cur,p_socket)
                                new_thread.name = '{}'.format(_address)
                                new_thread.start()

        str1['DB-DB'].close()

def main():

    SOCKET_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _IP = '192.168.1.116'
    _PORT_NUM = 1134
    _ADDRESS = (_IP,_PORT_NUM)
    SOCKET_SERVER.bind(_ADDRESS)
    SOCKET_SERVER.listen(3)
    print('lsitening statred')
    while True:
        _DATA = {}
        
        _DB = pymysql.connect('localhost','pythonroot422913','claire6772147','smsbetting')
        _CR = _DB.cursor()
        _CLIENT, _ADDR = SOCKET_SERVER.accept()
        print('new con : ', _ADDR)

        _DATA['CLIENT'] = _CLIENT
        _DATA['DB-DB'] = _DB
        _DATA['DB-CURSOR'] = _CR
        #_CONNECTION = TR_SERVER(_DATA,)
        #_CONNECTION.start()

        while SOCKET_SERVER.connect:
            pm = _CLIENT.recv(9000000)
            data = pm.decode('ascii')
            #print(data)
            file = open('msg','r')
            data = file.read()
            #code = []
            #print("data from socket type : ## : ", json.dumps(data))
            
            dict_ = eval(data)
            id_limit = 0
            for _dict in dict_:
                        _id = ''
                        #print('messages : ',_dict)
                    
                        if  'int' in str(type(_dict['_id'])):
                            continue

                        _id = _dict['_id']
                        if int(_id) > int(id_limit):

                            id_limit = _id

                            #print('id limit : ',id_limit)
                            msg_details = _dict
                            _date = msg_details['date']
                            _address = msg_details['address']
                            _body = msg_details['body']
                            str5 = '{}::{}::{}::{}'.format(_id,_address,_body,_date) 
                            try:
                                _CR.execute("insert into log values('{}','{}','{}','{}')".format(_id,_date,_body,_address))
                                _DB.commit()
                            except Exception as ex:
                                error  = ex
                            #print(str5)
                        else:
                            continue
                        if _address == '+263164':
                            b = make_payment.NewPayment(str5,_DB,_CR)
                            b.start()
                            continue

                        if _address == '+263125' or _address == '+263143' or 'Yomix':
                            continue

                        if 'reg' in str5.split('::')[2]:
                            
                            reg_code = str5.split('::')[2]
                            reg_details = reg_code.split('*')

                            #reg*fullname*
                            try:
                                _CR.execute("insert into bett_user values('{}','1234','{}','{}','{}')".format(str5.split(':')[1],reg_details[1],'0','0'))
                                _DB.commit()

                                response_1 = "Account created successfully \nBalance RTGS $0.00"
                                response_2 = """Deposit any amount using ecocash \na
                                                nd get 20% 
                                                free bonus on your deposit"""
                                
                                #create table u263774611839(bet_id varchar(20) unique, paid varchar(9), gain varchar(9))
                                bettname = 'u{}'.format(_address[1:])
                                _CR.execute("create table {}(bet_id varchar(20) unique,paid varchar(9),gain varchar(9))".format(bettname))
                                _DB.commit()

                            except Exception as ex:
                                if 'plicate' in str(ex):
                                    response1 = "Failed to register \nResaon : You are already registered"
                                else:
                                    response1 = "Error : Registratioj not completed "

                            #cur.execute("insert into current_message ")


                        elif 'pay' in str5.split('::')[2]:
                            pass
                        elif 'claim' in str5.split('::')[2]:
                            a = make_payment.ConfirmPayment(str5,_DB,_CR)
                            a.start()

                        else:
                            found_thread = False

                            p_socket = socket.socket()
                            ip = '192.168.1.116'
                            port = 0
                            p_socket.bind((ip,port))

                            for thread in threading.enumerate():
                                #print('Thread Name : ' , thread.name)
                                if thread.name == '{}'.format(_address):
                                    found_thread = True
                                    thread.new_message(str5)
                            if found_thread:
                                pass

                            else:
                                name = '{}'.format(_address)
                                messages = []
                                new_thread = TR_Session(str5,_DB,_CR,p_socket,name,messages)   
                                new_thread.name = name                             
                                new_thread.start()

                    
main()