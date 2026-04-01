from datetime import date

from fastapi import FastAPI,Request,status, Form,Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from database.database import Aluno,Aluno_tarefa,Tarefa,Disciplina ,Matricula , create_db_and_tables,engine
from sqlmodel import SQLModel, Field, Session, create_engine,select
from fastapi.templating import Jinja2Templates

app = FastAPI()
# Monta a pasta "static" na rota "/static"
app.mount("/static", StaticFiles(directory="../static"), name="static")
templates = Jinja2Templates(directory="../templates")

@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()

@app.get("/")
async def root(request: Request):
    response = templates.TemplateResponse(request=request, name="signup.html")
    response.delete_cookie(key="conta_id")
    return response

@app.post("/alunos")
def criar_aluno(nome : str = Form(...),email: str = Form(...),senha: str = Form(...), curso: str = Form(...)):
    with Session(engine) as session:
        conta = Aluno(nome=nome,email=email,senha=senha,curso=curso)
        session.add(conta)
        session.commit()
        session.refresh(conta)
    
    redirect = RedirectResponse(url="/home", status_code=303)
    redirect.set_cookie(key="conta_id", value=str(conta.id), httponly=True)
    return redirect
    
@app.get("/home")
def carrega_home(request: Request,conta_id: str = Cookie(None)):
    conta =  Session(engine).get(Aluno, int(conta_id)) ## pega o id do cookie do cara que logou
    if not conta:
        return {"erro": "conta não encontrado"}
    with Session(engine) as session:
        query =  select(Tarefa).join(Aluno_tarefa).where(Aluno_tarefa.aluno_id == int(conta_id))
        tasks_aluno = session.exec(query).all()
        return templates.TemplateResponse(request=request,name="home.html",context={"tasks_aluno":tasks_aluno})


@app.get("/login")
def carrega_login(request: Request):
    response = templates.TemplateResponse(request=request,name="login.html") 
    response.delete_cookie(key="conta_id") #deleta qualquer cookie de usuário antigo
    return response


@app.post("/logar")
def login_home(request: Request, nome: str = Form(...),email: str = Form(...),senha: str = Form(...),):
    with Session(engine) as session:
        query = select(Aluno).where(Aluno.email == email)
        result = session.exec(query).first()
        if not result:
            return templates.TemplateResponse(request=request,name = "login.html",context={"msg_error": "Conta inexistente"})
        if result.nome == nome and result.senha == senha:

            response = RedirectResponse(url="/home", status_code=303)
            response.set_cookie(key="conta_id", value=str(result.id), httponly=True)
            return response
        else:
            return templates.TemplateResponse(request=request,name = "login.html",context={"msg_error": "Dados incorretos"})




@app.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/", status_code=303)
    return response

@app.post("/add_tarefa")
def add_tarefa(
    request: Request,
    tarefa_nome: str = Form(...),
    data_final_tarefa: str = Form(...),
    disciplina_nome: str = Form(...),
    conta_id: str = Cookie(None)
):
    if not conta_id:
        return RedirectResponse(url="/login", status_code=303)
    
    data_convertida = date.fromisoformat(data_final_tarefa)

    with Session(engine) as session:
        nova_disciplina = Disciplina(nome=disciplina_nome)
        session.add(nova_disciplina)
        session.commit()
        session.refresh(nova_disciplina) 

        nova_tarefa = Tarefa(
            nome=tarefa_nome, 
            data_finalizacao=data_convertida, 
            disciplina_id=nova_disciplina.id
        )
        session.add(nova_tarefa)
        session.commit() 
        session.refresh(nova_tarefa) 

        vinculo = Aluno_tarefa(
            aluno_id=int(conta_id), 
            tarefa_id=nova_tarefa.id
        )
        
        nova_matricula = Matricula(
            aluno_id=int(conta_id), 
            disciplina_id=nova_disciplina.id
        )

        session.add(vinculo)
        session.add(nova_matricula)
        session.commit()

        return templates.TemplateResponse(
            request=request,
            name="task.html",
            context={
                "task_data_final": data_final_tarefa,
                "task_nome": tarefa_nome,
                "disciplina_nome": disciplina_nome,
                "id_task": nova_tarefa.id,
            }
        )
    
@app.get("/editar_tarefa_form/{tarefa_id}")
def editar_tarefa_form(request: Request, tarefa_id: int):
    with Session(engine) as session:
        tarefa = session.get(Tarefa, tarefa_id)
        disciplina = session.get(Disciplina, tarefa.disciplina_id)
        
        return templates.TemplateResponse(
            "edit_form.html", 
            {
                "request": request, 
                "tarefa": tarefa, 
                "disciplina_nome": disciplina.nome
            }
        )