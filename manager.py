import my_db


def replace_user(recipient_id):
    pass
    return ''


def check_if_new_rose_can_be_started(group_count=20):
    pass
    return []


def find_all_expired_roses():
    pass
    return []


def start_rose(rose):
    pass


def send_information_about_new_cycle():
    pass


def get_all_users_to_remind():
    pass
    return []


def send_reminder(user_id):
    pass


def main():
    roses_to_start = check_if_new_rose_can_be_started()
    roses_to_start += find_all_expired_roses()
    for rose in roses_to_start:
        start_rose(rose)

    users = get_all_users_to_remind()
    for user_id in users:
        send_reminder(user_id)

    for user_id in my_db.get_unsubscribed_users():
        pass


if __name__ == "__main__":
    main()
