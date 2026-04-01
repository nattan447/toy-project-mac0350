const overlay = document.getElementById("overlay");
const btn_add_task = document.getElementById("btn-add-task")

// modal de add elemento
btn_add_task.addEventListener("click", () => {
  overlay.classList.add("mostrar");
});

document.getElementById("fechar-modal").addEventListener("click", () => {
  overlay.classList.remove("mostrar");
});




function abrirModalEdicao(id, nome, data, disciplina) {
    document.getElementById('edit-id').value = id;
    document.getElementById('edit-nome').value = nome;
    document.getElementById('edit-data').value = data;
    document.getElementById('edit-disciplina').value = disciplina;   
    document.getElementById('overlay-edit').style.display = 'flex';
}

function fecharModalEdicao() {
    document.getElementById('overlay-edit').style.display = 'none';
}


