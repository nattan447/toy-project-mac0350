# Task Manager MAC0350

Uma aplicação web  de uma lista de Tarefas integrada ao gerenciamento de disciplinas acadêmicas. O projeto permite que estudantes organizem suas demandas escolares de forma centralizada
---

##  Tecnologias Utilizadas

* **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
* **Frontend:** HTML5, CSS3  e [HTMX](https://htmx.org/)
* **Banco de Dados:** SQLite (via SQLModel/SQLAlchemy)
* **Template Engine:** Jinja2
---

##  Funcionalidades

* Cadastro e vinculação de matérias ao perfil do aluno.
* Criação, edição e remoção de tarefas específicas.

---

##  Dependências 


* `fastapi[standart]:todas depêndencias do fastapi`
* `sqlmodel`
* `jinja2`

---

##  Como Rodar o Projeto

Siga os passos abaixo para configurar o ambiente local: 
```bash
git clone [https://github.com/seu-usuario/toy-project-mac0350.git](https://github.com/seu-usuario/toy-project-mac0350.git)
cd toy-project-mac0350
cd backend
pip -r install requirements.txt
fastapi dev main.py
