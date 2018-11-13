import os


class BotConfig:
    base_url = os.environ.get('BASE_URL', None) or "wss://api.bale.ai/v1/bots/"
    # bot_token = os.environ.get('TOKEN', None) or "ab876eea51b5fd8121e2c20f8baed500c260add5"
    bot_token = os.environ.get('TOKEN', None) or "0d0a1ca179684e075814ae4a8319b064ee84f28c"
    system_local = os.environ.get('SYSTEM_LOCAL', None) or "fa_IR"
    resending_max_try = int(os.environ.get('RESENDING_MAX_TRY', 5))
    reuploading_max_try = int(os.environ.get('REUPLOADING_MAX_TRY', 5))


class DbConfig:
    db_hash_key = os.environ.get('HASH_KEY', None) or "balegram_hash_key"
    db_user = os.environ.get('POSTGRES_USER', "postgres")
    db_password = os.environ.get('POSTGRES_PASSWORD', "nader1993")
    db_host = os.environ.get('POSTGRES_HOST', "localhost")
    db_name = os.environ.get('POSTGRES_DB', "balegram_db")
    db_port = os.environ.get('POSTGRES_PORT', "5432")
    database_url = "postgresql://{}:{}@{}:{}/{}".format(db_user, db_password, db_host, db_port, db_name) or None