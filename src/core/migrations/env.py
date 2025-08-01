from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 1️⃣ Add this:
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))
from core.sqlalchemy_engine import Base
from core.models import *   # This imports all your models

# 2️⃣ Then add this:
target_metadata = Base.metadata
