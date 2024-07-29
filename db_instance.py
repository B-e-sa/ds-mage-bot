import sqlite3


class DbInstance():
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True

            self.__con = sqlite3.connect("database.db")
            self.__cur = self.__con.cursor()
            self.__cur.execute("""
                CREATE TABLE IF NOT EXISTS vendas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    character VARCHAR(50) UNIQUE NOT NULL,
                    price INTEGER,
                    author varchar(50)
                );
                """)

    def create_venda(self, character, author, price):
        if not character:
            return False

        if not price:
            price = 0

        try:
            self.__cur.execute("""
                INSERT INTO vendas (character, price, author) 
                VALUES (?, ?, ?);
                """, (character, price, author))
            self.__con.commit()

        except sqlite3.IntegrityError:
            return """ CUIDAR DO ERRO DE UNIQUE """

    def delete_venda(self, character):
        self.__cur.execute("""
            DELETE FROM vendas WHERE character = ?
        """, (character,))
        self.__con.commit()

    def get_vendas(self):
        return self.__cur.execute("SELECT * FROM vendas").fetchall()
