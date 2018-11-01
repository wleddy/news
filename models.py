# news models.py
from users.models import SqliteTable
from takeabeltof.utils import cleanRecordID

class Article(SqliteTable):
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'article'
        self.order_by_col = 'publication_date desc '
        self.defaults = {}
        
    def create_table(self):
        """Define and create the article table"""
        
        sql = """
            publication_date DATETIME,
            title TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            words TEXT
            """
        super().create_table(sql)
        
    def init_table(self):
        """Create the table and initialize data"""
        self.create_table()
        
        
    def get(self,handle):
        """Get a single Article record by id or slug line"""
        rec_id = cleanRecordID(handle)
        if rec_id >= 0:
            # it looks like an id
            return super().get(rec_id)
            
        else:
            sql = 'select * from {} where slug = ?'.format(self.table_name)
            return self.select_one_raw(sql,(handle,))

def init_tables(db):
    Article(db).init_table()
