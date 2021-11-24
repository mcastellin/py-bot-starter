from botstarter.db.base import Base, register_model, get_interceptors, InterceptorHooks


@register_model("users")
class User(Base):
    """
    A class to represent users collection
    """


def get_user_by_id(user_id):
    return User.find_one({"id": user_id})


def create_user(msg):
    user = User({
        "id": msg.from_user.id,
        "is_admin": False,
        "username": msg.from_user.username,
        "first_name": msg.from_user.first_name,
        "last_name": msg.from_user.last_name
    })

    create_interceptor = get_interceptors(InterceptorHooks.SAVE_USER_CREATE)
    if create_interceptor:
        create_interceptor(user, msg)

    user.save()
    user.reload()
    return user


def set_user_waiting_on(user_id, waiting_on=None):
    User.update_one({"id": user_id}, {"$set": {"waiting_on": waiting_on}})


def is_admin(user_id):
    user = User.find_one({"id": user_id, "is_admin": True})
    return bool(user)
