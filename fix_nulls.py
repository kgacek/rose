import manager
db=manager.Manager()  
import facebook, os, yaml
from my_db import Base, Intention, Prayer, Rose, Patron, Mystery, User, AssociationUR 
#input from facebook api but can be automated also(get all users with nulls, get real name from api, update)
d=[{'name': 'Niewiadomo Kto', 'id': '10150002355385864'}]
with open(os.path.join(os.path.dirname(__file__), 'config.yaml')) as f:
    CONFIG = yaml.load(f)
bot = facebook.GraphAPI(access_token=CONFIG['token']['test'], version='6.0')
for user in db.session.query(User).filter(User.fullname==None).all():
    #q=db.session.query(User).filter(User.global_id == el['id']).first()
    user.fullname=bot.get_object(user.global_id)['name']
    #el.fullname=el['name']
db.session.commit()
