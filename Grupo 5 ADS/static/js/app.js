let prova = null;
let tentativaId = null;
let respostas = {};
let tempoRestante = 300;
let intervalo = null;
let provaFinalizada = false;


// ==========================================
// AUTENTICAÇÃO
// ==========================================

function getToken() {
    return localStorage.getItem("token");
}

function checarLogin() {
    if (!getToken()) {
        window.location.href = "/login";
    }
}

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("usuario_id");
    window.location.href = "/login";
}

// Headers com token para rotas protegidas
function headersAuth() {
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + getToken()
    };
}


// ==========================================
// INICIALIZAÇÃO
// ==========================================

async function carregarProva() {
    checarLogin();

    try {
        const listaResposta = await fetch("/provas");
        const provas = await listaResposta.json();

        if (provas.length === 0) {
            alert("Nenhuma prova cadastrada.");
            return;
        }

        const provaResposta = await fetch(`/provas/${provas[0].id}`);
        prova = await provaResposta.json();

        document.getElementById("titulo").textContent = prova.titulo;

        // Inicia tentativa enviando o token do usuário logado
        const tentativaResposta = await fetch("/iniciar", {
            method: "POST",
            headers: headersAuth(),
            body: JSON.stringify({ prova_id: prova.id })
        });

        if (tentativaResposta.status === 401) {
            logout();
            return;
        }

        const tentativa = await tentativaResposta.json();
        tentativaId = tentativa.id;

        tempoRestante = prova.tempo_limite || 300;
        mostrarQuestoes();
        iniciarCronometro();

    } catch (erro) {
        console.error("Erro ao carregar prova:", erro);
        alert("Erro ao carregar a prova. Verifique o console.");
    }
}


// ==========================================
// QUESTÕES
// ==========================================

function mostrarQuestoes() {
    const div = document.getElementById("questoes");
    div.innerHTML = "";

    prova.questoes.forEach(questao => {
        const divQuestao = document.createElement("div");
        divQuestao.className = "questao";

        const titulo = document.createElement("h3");
        titulo.textContent = questao.enunciado;
        divQuestao.appendChild(titulo);

        questao.alternativas.forEach(alt => {
            const label = document.createElement("label");
            const input = document.createElement("input");
            input.type = "radio";
            input.name = `q_${questao.id}`;
            input.value = alt.id;
            input.addEventListener("change", () => marcar(questao.id, alt.id));
            label.appendChild(input);
            label.append(` ${alt.texto}`);
            divQuestao.appendChild(label);
            divQuestao.appendChild(document.createElement("br"));
        });

        div.appendChild(divQuestao);
    });
}


// ==========================================
// RESPOSTAS
// ==========================================

function marcar(questaoId, alternativaId) {
    respostas[questaoId] = alternativaId;
}


// ==========================================
// FINALIZAÇÃO
// ==========================================

async function finalizarProva() {
    if (provaFinalizada) return;
    if (!tentativaId) {
        alert("Erro: tentativa não foi iniciada.");
        return;
    }

    provaFinalizada = true;
    clearInterval(intervalo);

    const listaRespostas = Object.entries(respostas).map(([questao_id, alternativa_id]) => ({
        questao_id,
        alternativa_id
    }));

    try {
        const resposta = await fetch("/finalizar", {
            method: "POST",
            headers: headersAuth(),
            body: JSON.stringify({
                tentativa_id: tentativaId,
                respostas: listaRespostas
            })
        });

        if (resposta.status === 401) {
            logout();
            return;
        }

        const resultado = await resposta.json();

        document.getElementById("resultado").innerHTML = `
            <hr>
            <h2>Resultado</h2>
            <p>Acertos: ${resultado.acertos} / ${resultado.total}</p>
            <p>Nota: <strong>${resultado.nota}</strong></p>
            <p>${resultado.aprovado ? "✅ Aprovado!" : "❌ Reprovado."}</p>
            <button onclick="logout()" style="margin-top:20px; background:#888">Sair</button>
        `;

    } catch (erro) {
        console.error("Erro ao finalizar:", erro);
        alert("Erro ao enviar respostas.");
        provaFinalizada = false;
    }
}


// ==========================================
// CRONÔMETRO
// ==========================================

function iniciarCronometro() {
    intervalo = setInterval(() => {
        tempoRestante--;
        const minutos = Math.floor(tempoRestante / 60);
        const segundos = tempoRestante % 60;
        document.getElementById("tempo").textContent =
            `Tempo restante: ${String(minutos).padStart(2, "0")}:${String(segundos).padStart(2, "0")}`;
        if (tempoRestante <= 0) {
            clearInterval(intervalo);
            finalizarProva();
        }
    }, 1000);
}


// ==========================================
// INÍCIO
// ==========================================

carregarProva();
