from app import db
from models import User, Chatroom, Roomassignment,Chatmessage
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

alex = User(id='alexid', name='Alex', color='f2ab63', email='alxdveil04@gmail.com',
            password_hash=generate_password_hash('password'))
kat = User(id='katid', name='Kat', color='a1ede8', email='alxdveil04@gmail.com',
           password_hash=generate_password_hash('password'))
jamie = User(id='jamieid', name='Jamie', color='f72a4c', email='alxdveil04@gmail.com',
             password_hash=generate_password_hash('password'))

kajroom = Chatroom(id='KAJroom1', roomname='Kat,Alex,Jamie', numusers=3, socketroomname='KAJ0a0erc1',
                   mostrecentmessageid='')
ajroom = Chatroom(id='AJroom2', roomname='Alex,Jamie', numusers=2, socketroomname='AJ00cvfgb1', mostrecentmessageid='')

roomassignment1 = Roomassignment(id='abcd000001', userid=alex.id, roomid=kajroom.id)
roomassignment2 = Roomassignment(id='abcd000002', userid=kat.id, roomid=kajroom.id)
roomassignment3 = Roomassignment(id='abcd000003', userid=jamie.id, roomid=kajroom.id)
roomassignment4 = Roomassignment(id='abcd000004', userid=alex.id, roomid=ajroom.id)
roomassignment5 = Roomassignment(id='abcd000005', userid=jamie.id, roomid=ajroom.id)

# db.session.add(alex)
# db.session.add(kat)
# db.session.add(jamie)
# db.session.add(kajroom)
# db.session.add(ajroom)
# db.session.add(roomassignment1)
# db.session.add(roomassignment2)
# db.session.add(roomassignment3)
# db.session.add(roomassignment4)
# db.session.add(roomassignment5)
#
# db.session.commit()

kajroom = Chatroom.query.get(kajroom.id)
ajroom = Chatroom.query.get(ajroom.id)


# messages = []
# messages.append(Chatmessage(id='0000000001', fromuserid=alex.id, roomid=kajroom.id, messagetext = 'hi guys',
#                           timesent=datetime.strptime("2022/08/16 23:01:10", "%Y/%m/%d %H:%M:%S")))
# messages.append(Chatmessage(id='0000000002', fromuserid=alex.id, roomid=kajroom.id, messagetext = 'how are you',
#                           timesent=datetime.strptime("2022/08/16 23:01:20", "%Y/%m/%d %H:%M:%S")))
# messages.append(Chatmessage(id='0000000003', fromuserid=kat.id, roomid=kajroom.id, messagetext = 'doing fine, wbu',
#                          timesent=datetime.strptime("2022/08/16 23:01:30", "%Y/%m/%d %H:%M:%S")))
# messages.append(Chatmessage(id='0000000004', fromuserid=jamie.id, roomid=kajroom.id, messagetext = 'im good too',
#                           timesent=datetime.strptime("2022/08/16 23:01:40", "%Y/%m/%d %H:%M:%S")))
# messages.append(Chatmessage(id='0000000005', fromuserid=jamie.id, roomid=ajroom.id, messagetext = 'do u have the answer to q5',
#                           timesent=datetime.strptime("2022/08/16 23:01:11", "%Y/%m/%d %H:%M:%S")))
# messages.append(Chatmessage(id='0000000006', fromuserid=alex.id, roomid=ajroom.id, messagetext = 'its answered on piazza',
#                           timesent=datetime.strptime("2022/08/16 23:01:21", "%Y/%m/%d %H:%M:%S")))
# messages.append(Chatmessage(id='0000000007', fromuserid=jamie.id, roomid=ajroom.id, messagetext = 'ok got it',
#                           timesent=datetime.strptime("2022/08/16 23:01:31", "%Y/%m/%d %H:%M:%S")))
#
# for message in messages:
#     db.session.add(message)
#


# kajroom.mostrecentmessageid = '0000000004'
# ajroom.mostrecentmessageid = '0000000007'
#
# db.session.commit()
#

# earliermessage = Chatmessage(id='0000000008', fromuserid=alex.id, roomid=kajroom.id, messagetext = 'some random irrelevant message from earlier',
#                           timesent=datetime.strptime("2022/08/16 20:01:31", "%Y/%m/%d %H:%M:%S"))
# earliermessage2 = Chatmessage(id='0000000009', fromuserid=jamie.id, roomid=kajroom.id, messagetext = 'some random irrelevant message from earlier',
#                           timesent=datetime.strptime("2022/08/16 20:01:32", "%Y/%m/%d %H:%M:%S"))
# earliermessage3 = Chatmessage(id='0000000010', fromuserid=kat.id, roomid=kajroom.id, messagetext = 'some random irrelevant message from earlier',
#                           timesent=datetime.strptime("2022/08/16 20:01:33", "%Y/%m/%d %H:%M:%S"))
# earliermessage4 = Chatmessage(id='0000000011', fromuserid=jamie.id, roomid=kajroom.id, messagetext = 'some random irrelevant message from earlier',
#                           timesent=datetime.strptime("2022/08/16 20:01:34", "%Y/%m/%d %H:%M:%S"))
# earliermessage5 = Chatmessage(id='0000000012', fromuserid=alex.id, roomid=kajroom.id, messagetext = 'some random irrelevant message from earlier',
#                           timesent=datetime.strptime("2022/08/16 20:01:35", "%Y/%m/%d %H:%M:%S"))
# db.session.add(earliermessage)
# db.session.add(earliermessage2)
# db.session.add(earliermessage3)
# db.session.add(earliermessage4)
# db.session.add(earliermessage5)
#
# db.session.commit()