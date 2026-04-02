from datetime import date
from fastapi import FastAPI,Request,status, Form,Cookie,HTTPException, Response
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
    if not conta_id:
        return {"erro": "conta não encontrada"}
    with Session(engine) as session:
        conta =  session.get(Aluno, int(conta_id)) ## pega o id do cookie do cara que logou
        query = (
            select(Tarefa, Disciplina)
            .join(Disciplina, Tarefa.disciplina_id == Disciplina.id)
            .join(Aluno_tarefa, Tarefa.id == Aluno_tarefa.tarefa_id)
            .where(Aluno_tarefa.aluno_id == int(conta_id))
        )
        result = session.exec(query).all()
        return templates.TemplateResponse(request=request,name="home.html",context={"tasks_aluno_disciplinas":result})


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
    disciplina_nome: str = Form(...),
    conta_id: str = Cookie(None)
):
    if not conta_id:
        return RedirectResponse(url="/login", status_code=303)

    with Session(engine) as session:
        #  VERIFICAÇÃO: A disciplina já existe?
        query = select(Disciplina).where(Disciplina.nome == disciplina_nome)
        disciplina_existente = session.exec(query).first()

        if disciplina_existente:
            # Se existe, usamos a que já está no banco
            disciplina_final = disciplina_existente
        else:
            # Se não existe, criamos uma nova
            disciplina_final = Disciplina(nome=disciplina_nome)
            session.add(disciplina_final)
            session.commit()
            session.refresh(disciplina_final)

        #  CRIAR A TAREFA (usando o ID da disciplina_final)
        nova_tarefa = Tarefa(
            nome=tarefa_nome, 
            disciplina_id=disciplina_final.id
        )
        session.add(nova_tarefa)
        session.commit()
        session.refresh(nova_tarefa)

        #  CRIAR VÍNCULOS (Aluno-Tarefa e Matrícula)
        vinculo = Aluno_tarefa(
            aluno_id=int(conta_id), 
            tarefa_id=nova_tarefa.id
        )
        
        # Verificamos se o aluno já está matriculado nessa disciplina para não duplicar matrícula
        check_matricula = select(Matricula).where(
            Matricula.aluno_id == int(conta_id),
            Matricula.disciplina_id == disciplina_final.id
        )
        matricula_existe = session.exec(check_matricula).first()

        if not matricula_existe:
            nova_matricula = Matricula(
                aluno_id=int(conta_id), 
                disciplina_id=disciplina_final.id
            )
            session.add(nova_matricula)

        session.add(vinculo)
        session.commit()
        return templates.TemplateResponse(
            request=request,
            name="task.html",
            context={
                "task_nome": tarefa_nome,
                "disciplina_nome": disciplina_final.nome,
                "task_id": nova_tarefa.id,
            }
        )

@app.delete("/deletar_task/{task_id}")
async def deletar_task(request:Request,task_id: int,conta_id: str = Cookie(None)):

    with Session(engine) as session:
        aluno =  session.get(Aluno, int(conta_id)) ## pega o id do cookie do cara que logou
        if not aluno:
            raise HTTPException(
                status_code=401,detail="É necessário estar logado para essa requisição"
            )
        query = select(Tarefa).where(Tarefa.id == task_id)
        task = session.exec(query).first()
        if not task:
            raise HTTPException(
                status_code=404,detail="Tarefa não encontrada"
            )
        query = select(Aluno_tarefa).where(Aluno_tarefa.aluno_id == aluno.id, Aluno_tarefa.tarefa_id ==task_id)
        task_aluno = session.exec(query).first()
        if not task_aluno:
            raise HTTPException(
                status_code=404,detail="Tarefa não tem ligação com aluno"
            )
        session.delete(task_aluno)
        session.commit()
        return Response(status_code=200)  


@app.post("/atualizar_task/{task_id}")
async def atualizar_task(request:Request,task_id: int ,task_nome: str = Form(...),disciplina_nome: str = Form(...)):
    with Session(engine) as session:
        db_task = session.get(Tarefa, task_id)
        if not db_task:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        
        query = select(Disciplina).where(Disciplina.nome == disciplina_nome)
        disciplina = session.exec(query).first()
        if disciplina: ## se a disciplina já existe, só muda o id da discplina da nossa task
            db_task.disciplina_id = disciplina.id
        else: # se não existir cria a disciplina 
            nova_disciplina  = Disciplina(nome=disciplina_nome)
            session.add(nova_disciplina)
            session.commit()
            session.refresh(nova_disciplina)
            db_task.disciplina_id = nova_disciplina.id

        db_task.nome = task_nome
        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        return templates.TemplateResponse( ## retorna a nova task atualizadad
            request=request,
            name = "task.html", 
            context={
                "task_nome": db_task.nome,
                "disciplina_nome": disciplina_nome,
                "task_id": db_task.id
            }
        )
    

@app.get("/listar_disciplinas")
async def list_disciplinas(request:Request,conta_id: str = Cookie(None)):
    if not conta_id:
           raise HTTPException(
                status_code=401,detail="É necessário estar logado para essa requisição"
            )
    with Session(engine) as session:
       query = (
            select(Disciplina)
            .join(Matricula, Disciplina.id == Matricula.disciplina_id)
            .where(Matricula.aluno_id == int(conta_id))
        )
       disciplinas = session.exec(query).all()
       return templates.TemplateResponse(request=request,name="disciplinas.html",context={"disciplinas": disciplinas})



@app.get("/mostrar_perfil")
async def mostrar_perfil(request:Request,conta_id: str = Cookie(None)):
    if not conta_id:
           raise HTTPException(
                status_code=401,detail="É necessário estar logado para essa requisição"
            )
    with Session(engine) as session:
       query = select(Aluno).where(Aluno.id == int(conta_id))
       aluno = session.exec(query).first()
       return templates.TemplateResponse(request=request,name="perfil.html",context={"aluno": aluno})


@app.delete("/remover_disciplina/{disciplina_id}")

async def deletar_disciplia(request: Request,disciplina_id : int ,conta_id : str = Cookie(None)):
    if not conta_id:
        raise HTTPException(
                status_code=401,detail="É necessário estar logado para essa requisição"
            )
    with Session(engine) as session:
        
        query = select(Matricula).where(
            Matricula.aluno_id == int(conta_id),
            Matricula.disciplina_id == disciplina_id
        )
        matricula = session.exec(query).first()

        if not matricula:
                 raise HTTPException(
                status_code=401,detail="Matricula não encontrada"
            )

        session.delete(matricula)
        session.commit()
        ## deleteou        
        return Response(status_code=200)

