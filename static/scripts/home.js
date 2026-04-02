function changeModal(id,open){
  //  altera o modo do modal (mostrar ou fechar), open: caso true, abre o modal, false, fecha
  const modal = document.getElementById(id)
  if (modal)
  {open? modal.classList.add("mostrar") : modal.classList.remove("mostrar")}
}


function abrirModalEdicao(id,nome,disciplina) {
    // id da tarefa, nome da tarefa atual, disciplina da tarefa atual
    
    // carrega esses atributos no form
    const form = document.getElementById('modal-edit');
    form.setAttribute('hx-post', `/atualizar_task/${id}`);
    form.setAttribute('hx-target', `#task-${id}`);
    form.setAttribute('hx-swap', 'outerHTML')
    htmx.process(form);
    
    
    document.getElementById('edit-nome').value = nome;
    document.getElementById('edit-disciplina').value = disciplina;   
    document.getElementById('overlay-edit').style.display = 'flex';
}

function fecharModalEdicao() {
    document.getElementById('overlay-edit').style.display = 'none';
}


