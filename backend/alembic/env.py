from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context, op
import sqlalchemy as sa

# Alembic Config object
config = context.config

# Interpret the config file for logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your models' metadata
from app.models import Base
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

# ✅ Merge both changes here
def upgrade():
    # Convert integer 0/1 to boolean false/true
    op.alter_column(
        'notifications',
        'read',
        existing_type=sa.Integer(),
        type_=sa.Boolean(),
        postgresql_using="read::boolean"
    )

def downgrade():
    # Convert boolean back to integer if needed
    op.alter_column(
        'notifications',
        'read',
        existing_type=sa.Boolean(),
        type_=sa.Integer(),
        postgresql_using="CASE WHEN read THEN 1 ELSE 0 END"
    )