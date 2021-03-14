import manager
db=manager.Manager()  
from my_db import Base, Intention, Prayer, Rose, Patron, Mystery, User, AssociationUR 
#input from facebook api but can be automated also(get all users with nulls, get real name from api, update)
d=[{'name': 'Anna Łukasiak', 'id': '1527443617450420'},{'name': 'Anna Szeliga', 'id': '3746021852144030'},{'name': 'Anna Kotarska', 'id': '2710790862283180'},{'name': 'Gośka Szpak', 'id': '5491729747507707'},{'name': 'Zdzisława Brzozowska', 'id': '733456810483209'}]
for el in d:
    q=db.session.query(User).filter(User.global_id == el['id']).first()
    q.fullname=el['name']
db.session.commit()
