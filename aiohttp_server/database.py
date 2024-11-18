from config import settings

DATABASE_URL = "postgresql://{user}:{password}@{host}:{port}/{db}".format(
    user=settings.postgres.user,
    password=settings.postgres.password,
    host=settings.postgres.host,
    port=settings.postgres.port,
    db=settings.postgres.database,
)
