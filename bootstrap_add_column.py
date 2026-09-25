from db import engine

# with engine.begin() as connection:
#     connection.exec_driver_sql("""
#         ALTER TABLE tickets
#         ADD COLUMN completed_by_admin INTEGER
#         REFERENCES users(id)
#     """)