
def fetch_key_from_env(key_name: str):
    """ fetches the key from the env file """
    with open(".env", 'r') as file:
        for line in file.readlines():
            key, value = line.split('=', 1)
            key = key.strip()
            if key == key_name:
                return value.strip()
    
    return None

class AWS:
    access_key: str = fetch_key_from_env("aws_access_key")
    secret_key: str = fetch_key_from_env("aws_secret_key")
    region: str = fetch_key_from_env("aws_region")
    def __init__(self):
        pass

class Database:
    db_path = fetch_key_from_env("db_path") or "database/skyndle.db"
    db_host = fetch_key_from_env("db_host") or f"sqlite:///{db_path}"
    def __init__(self):
        pass

class Utils:
    log_path = fetch_key_from_env("log_path") or "logs/app.log"
    def __init__(self):
        pass

class Variables:
    aws = AWS()
    db = Database()
    utils = Utils()
    def __init__(self):
        pass





