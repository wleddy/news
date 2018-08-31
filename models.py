# news models.py
from users.models import SqliteTable


class Article(SqliteTable):
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'article'
        self.order_by_col = 'publictation_date'
        self.defaults = {'status': 'draft'}
        
    def create_table(self):
        """Define and create the article table"""
        
        sql = """
            status TEXT DEFAULT 'draft',
            publictation_date DATETIME,
            title TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            words TEXT
            """
        super().create_table(sql)
        
    def init_table(self):
        """Create the table and initialize data"""
        self.create_table()


def init_tables(db):
    Article(db).init_table()
