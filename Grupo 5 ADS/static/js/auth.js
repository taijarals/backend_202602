function mostrarAba(aba) {
    document.getElementById("form-login").style.display = aba === "login" ? "block" : "none";
    document.getElementById("form-cadastro").style.display = aba === "cadastro" ? "block" : "none";
    document.getElementById("aba-login").className = "aba" + (aba === "login" ? " aba-ativa" : "");
    document.getElementById("aba-cadastro").className = "aba" + (aba === "cadastro" ? " aba-ativa" : "");
}

async function login() {
    const email = document.getElementById("login-email").value.trim();
    const senha = document.getElementById("login-senha").value;
    const erroDiv = document.getElementById("erro-login");
    erroDiv.textContent = "";

    if (!email || !senha) {
        erroDiv.textContent = "Preencha email e senha.";
        return;
    }

    const resposta = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, senha })
    });

    const dados = await resposta.json();

    if (!resposta.ok) {
        erroDiv.textContent = dados.erro || "Email ou senha incorretos.";
        return;
    }

    // Salva o token e redireciona para a prova
    localStorage.setItem("token", dados.token);
    localStorage.setItem("usuario_id", dados.usuario_id);
    window.location.href = "/";
}

async function cadastrar() {
    const nome = document.getElementById("cadastro-nome").value.trim();
    const email = document.getElementById("cadastro-email").value.trim();
    const senha = document.getElementById("cadastro-senha").value;
    const erroDiv = document.getElementById("erro-cadastro");
    const sucessoDiv = document.getElementById("sucesso-cadastro");
    erroDiv.textContent = "";
    sucessoDiv.textContent = "";

    if (!nome || !email || !senha) {
        erroDiv.textContent = "Preencha todos os campos.";
        return;
    }

    if (senha.length < 6) {
        erroDiv.textContent = "A senha precisa ter pelo menos 6 caracteres.";
        return;
    }

    const resposta = await fetch("/auth/cadastrar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome, email, senha })
    });

    const dados = await resposta.json();

    if (!resposta.ok) {
        erroDiv.textContent = dados.erro || "Erro ao criar conta.";
        return;
    }

    sucessoDiv.textContent = "Conta criada! Agora faça login.";
    mostrarAba("login");
}
