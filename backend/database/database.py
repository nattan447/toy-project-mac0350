from sqlmodel import Field, Relationship, SQLModel,create_engine
from typing import List, Optional
from datetime import date




arquivo_sqlite = "data.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"
engine = create_engine(url_sqlite)
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

class Aluno(SQLModel,table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome:  str
    email: str = Field(unique=True)
    senha: str
    curso: str

class Disciplina(SQLModel,table = True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(unique=True)

class Matricula(SQLModel,table = True):
    aluno_id: Optional[int] = Field(
        default=None,
        foreign_key="aluno.id",
        primary_key=True,
    )
    disciplina_id: Optional[int] = Field(
        default=None,
        foreign_key="disciplina.id",
        primary_key=True,
    )

class Tarefa(SQLModel,table = True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str    
    disciplina_id: Optional[int] = Field(
        default=None,
        foreign_key="disciplina.id",
    )

class Aluno_tarefa(SQLModel,table = True):
    aluno_id: Optional[int] = Field(
        default=None,
        foreign_key="aluno.id",
        primary_key=True,
    )
    tarefa_id: Optional[int] = Field(
        default=None,
        foreign_key="tarefa.id",
        primary_key=True,
    )

