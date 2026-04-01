const overlay = document.getElementById("overlay");
const btn_add_task = document.getElementById("btn-add-task")

// modal de add elemento
btn_add_task.addEventListener("click", () => {
  overlay.classList.add("mostrar");
});

document.getElementById("fechar-modal").addEventListener("click", () => {
  overlay.classList.remove("mostrar");
});




function abrirModalEdicao(id,nome,disciplina) {
    // id da tarefa, nome da tarefa atual, disciplina da tarefa atual
    
    // carrega esses atributos no form
    const form = document.getElementById('modal-edit');
    form.setAttribute('hx-post', `/atualizar_task/${id}`);
    form.setAttribute('hx-target', `#task-${id}`);
    htmx.process(form);
    
    
    document.getElementById('edit-nome').value = nome;
    document.getElementById('edit-disciplina').value = disciplina;   
    document.getElementById('overlay-edit').style.display = 'flex';
}

function fecharModalEdicao() {
    document.getElementById('overlay-edit').style.display = 'none';
}


