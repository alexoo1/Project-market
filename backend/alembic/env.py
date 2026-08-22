from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.database.base import Base

# Import explicite de tous les modèles pour qu'Alembic les détecte
# via Base.metadata. Chaque nouveau modèle (Listing, Order, ...) devra
# être importé ici au fur et à mesure des phases suivantes.
from app.models.user import User  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.brand import Brand  # noqa: F401
from app.models.listing import Listing, ListingImage  # noqa: F401
from app.models.favorite import Favorite  # noqa: F401
from app.models.conversation import Conversation, Message  # noqa: F401
from app.models.offer import Offer  # noqa: F401
from app.models.order import Order, Payment, Delivery  # noqa: F401
from app.models.review import Review  # noqa: F401
from app.models.follow import Follow  # noqa: F401
from app.models.boost import ListingBoost  # noqa: F401
from app.models.notification import Notification  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
