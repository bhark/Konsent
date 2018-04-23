import bcrypt

# FUNCTIONS

def hash_password(passwd):
    hashed_passwd = bcrypt.hashpw(passwd.encode(), bcrypt.gensalt())
    return hashed_passwd


def check_password(canditate, stored):
    return bcrypt.checkpw(canditate.encode(), stored.encode())
