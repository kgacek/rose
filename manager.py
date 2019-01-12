import my_db
def check_if_new_rose_can_be_started(group_count=20):
    pass

def find_all_expired_roses():
    pass

def start_rose(rose):
    pass

def send_information_about_new_cycle():
    pass

def get_all_users_to_remind():
    pass

def main():
    roses_to_start = check_if_new_rose_can_be_started()
    roses_to_start += find_all_expired_roses()
    for rose in roses_to_start:
        start_rose(rose)

    users=get_all_users_to_remind()
    for user_id in users:
        send_remider(user_id)

    exired_users = get_exired_users()
    for user_id in expired_users:

if __name__ == "__main__":
    main()


