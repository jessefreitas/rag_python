import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
import logging

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

logging.basicConfig(level=logging.INFO)

class Database:
    """Gerencia o pool de conexões com o banco de dados PostgreSQL."""
    _connection_pool = None

    @classmethod
    def initialize_pool(cls):
        """Inicializa o pool de conexões com o banco de dados."""
        if cls._connection_pool is None:
            try:
                cls._connection_pool = psycopg2.pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                    host=os.getenv("DB_HOST"),
                    port=os.getenv("DB_PORT"),
                    database=os.getenv("DB_NAME")
                )
                logging.info("Pool de conexões com o PostgreSQL inicializado com sucesso.")
            except psycopg2.OperationalError as e:
                logging.error(f"Erro ao conectar ao PostgreSQL: {e}")
                raise

    @classmethod
    def get_connection(cls):
        """Obtém uma conexão do pool."""
        if cls._connection_pool is None:
            # Tenta inicializar se ainda não foi feito
            cls.initialize_pool()
        
        if cls._connection_pool:
            return cls._connection_pool.getconn()
        else:
            raise Exception("Pool de conexões não está disponível e não pôde ser inicializado.")


    @classmethod
    def release_connection(cls, conn):
        """Devolve uma conexão ao pool."""
        if cls._connection_pool and conn:
            cls._connection_pool.putconn(conn)

    @classmethod
    def close_all_connections(cls):
        """Fecha todas as conexões no pool."""
        if cls._connection_pool:
            cls._connection_pool.closeall()
            logging.info("Todas as conexões com o PostgreSQL foram fechadas.")

# O bloco de teste `if __name__ == '__main__'` foi removido para evitar
# a execução automática de código e potenciais erros de importação circular
# ou falhas de conexão durante o processo de importação por outros módulos. 