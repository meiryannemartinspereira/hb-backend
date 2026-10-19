import sqlite3
from datetime import datetime

class VeiculoRepository:
    def __init__(self, db_name: str = "estacionamento.db"):
        self.db_name = db_name
        self._inicializar_banco()

    def _inicializar_banco(self):
        """Cria a tabela no banco de dados SQLite caso ela não exista."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registros_placas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                placa TEXT NOT NULL,
                data_hora DATETIME NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def salvar(self, placa: str) -> None:
        """Salva a placa reconhecida e a data/hora atual no banco."""
        data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO registros_placas (placa, data_hora) VALUES (?, ?)",
            (placa, data_hora_atual)
        )
        conn.commit()
        conn.close()
        print(f"✅ Sucesso! Placa '{placa}' salva no banco às {data_hora_atual}")
