// Theme Toggle
const themeBtn = document.getElementById('theme-toggle');
themeBtn.addEventListener('click', () => {
    document.documentElement.classList.toggle('light');
    themeBtn.textContent = document.documentElement.classList.contains('light') ? '🌙' : '☀️';
});

// Tabs / Sidebar Navigation
document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        btn.classList.add('active');
        document.getElementById(btn.dataset.tab).classList.add('active');
    });
});

// UI Elements
const btnAbrir = document.getElementById('btn_abrir');
const btnLer = document.getElementById('btn_ler');
const btnIniciar = document.getElementById('btn_iniciar');
const btnParar = document.getElementById('btn_parar');
const btnCopiar = document.getElementById('btn_copiar_erro');
const logTextarea = document.getElementById('log_textarea');
const sidebarLogs = document.getElementById('sidebar_logs');
const listaUnidades = document.getElementById('lista_unidades');
const buscaInput = document.getElementById('busca');
const overlay = document.getElementById('loading_overlay');
const overlayText = document.getElementById('loading_text');

// State
let allUnidades = [];

function showLoading(text) {
    overlayText.textContent = text;
    overlayText.style.whiteSpace = 'pre-line';
    overlay.classList.add('active');
}
function hideLoading() {
    overlay.classList.remove('active');
}

function setStatus(msg) {
    const bar = document.getElementById('status_leitura');
    if (!msg) {
        bar.style.display = 'none';
        return;
    }
    bar.textContent = msg;
    bar.style.display = 'block';
}

// EEL Exposed Python Calls
btnAbrir.addEventListener('click', async () => {
    const user = document.getElementById('usuario').value.trim();
    const pwd = document.getElementById('senha').value.trim();

    if (!user || !pwd) {
        alert("Por favor, preencha Usuário e Senha!");
        return;
    }

    btnAbrir.disabled = true;
    showLoading("Iniciando Chrome e logando...");
    
    // Salva login localmente
    const lembrarLogin = document.getElementById('lembrar_login').checked;
    await eel.salvar_login(user, pwd, '', lembrarLogin, false)();

    // Call Python
    await eel.abrir_sistema(user, pwd, '')();
    
    hideLoading();
    btnAbrir.disabled = false;
});

btnLer.addEventListener('click', async () => {
    btnLer.disabled = true;
    btnLer.textContent = '⏳ Verificando...';
    setStatus('🔍 Lendo tabela de unidades, aguarde...');
    showLoading('🔍 Verificando unidades na tabela...\nIsso pode levar alguns segundos.');
    
    // Inicia a leitura em background — hideLoading() é chamado dentro de atualizar_lista_unidades
    await eel.ler_unidades()();
});

btnIniciar.addEventListener('click', async () => {
    // Coleta o mapeamento de condomínios por bloco
    const mapaCondominios = {};
    let algumVazio = false;

    document.querySelectorAll('.mapa-row').forEach(row => {
        const bloco = row.dataset.bloco;
        const val = row.querySelector('input').value.trim();
        if (bloco) {
            if (!val) {
                algumVazio = true;
            } else {
                mapaCondominios[bloco] = val;
            }
        }
    });

    if (algumVazio) {
        alert("Preencha o condomínio de todos os blocos antes de iniciar o robô!");
        return;
    }
    if (Object.keys(mapaCondominios).length === 0) {
        alert("Primeiro leia as unidades para o robô detectar os blocos!");
        return;
    }

    // Coletar selecionados
    const selecionadas = [];
    document.querySelectorAll('.chk-unidade:checked').forEach(cb => {
        selecionadas.push(cb.value);
    });

    if (selecionadas.length === 0) {
        alert("Selecione pelo menos uma unidade na lista!");
        return;
    }

    const vincAgregadas = document.getElementById('vincular_agregadas').checked;

    btnIniciar.disabled = true;
    btnLer.disabled = true;
    btnParar.disabled = false;

    await eel.iniciar_robo(mapaCondominios, selecionadas, vincAgregadas)();
});

btnParar.addEventListener('click', async () => {
    btnParar.disabled = true;
    await eel.parar_robo()();
});

btnCopiar.addEventListener('click', async () => {
    const err = await eel.obter_ultimo_erro()();
    navigator.clipboard.writeText(err);
    alert("Erro copiado!");
});

// Enter key to login
['usuario', 'senha'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
        el.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') btnAbrir.click();
        });
    }
});

// Sidebar Toggle
document.getElementById('btn_toggle_logs').addEventListener('click', () => {
    sidebarLogs.classList.add('active');
});
document.getElementById('btn_close_logs').addEventListener('click', () => {
    sidebarLogs.classList.remove('active');
});

// Sidebar Collapse (Left Nav)
const btnToggleSidebar = document.getElementById('btn_toggle_sidebar');
if (btnToggleSidebar) {
    btnToggleSidebar.addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('collapsed');
    });
}

// Finalizar Sessão Atual
const btnFinalizarSessao = document.getElementById('btn_finalizar_sessao');
if (btnFinalizarSessao) {
    btnFinalizarSessao.addEventListener('click', async () => {
        showLoading("Finalizando sessão e fechando Chrome...");
        await eel.finalizar_sessao()();
        
        // Reseta estado do layout
        document.querySelector('.app-container').classList.remove('session-active');
        document.getElementById('session_bar').style.display = 'none';
        document.getElementById('controles_operacao').style.display = 'none';
        
        // Limpa lista de unidades e mapeamento
        document.getElementById('lista_unidades').innerHTML = `
            <div class="empty-state">
                <h2>Nenhum dado carregado.</h2>
                <p>Abra o sistema e faça login para carregar as unidades e controles.</p>
            </div>
        `;
        document.getElementById('mapeamento_blocos').style.display = 'none';
        document.getElementById('mapa_rows').innerHTML = '';
        document.getElementById('filtros_container').style.display = 'none';
        
        // Reseta filtros
        document.getElementById('filtro_bloco').value = '';
        document.getElementById('filtro_de').value = '';
        document.getElementById('filtro_ate').value = '';
        buscaInput.value = '';
        
        setStatus('');
        hideLoading();
    });
}

// =============================================
// FILTROS
// =============================================

function applyFilters() {
    const textTerm  = buscaInput.value.toLowerCase();
    const bloco     = document.getElementById('filtro_bloco').value;      // e.g. "01" or ""
    const deVal     = document.getElementById('filtro_de').value;
    const ateVal    = document.getElementById('filtro_ate').value;
    const numDe     = deVal  !== '' ? parseInt(deVal,  10) : null;
    const numAte    = ateVal !== '' ? parseInt(ateVal, 10) : null;

    document.querySelectorAll('.list-item').forEach(item => {
        const cod  = item.dataset.cod  || '';   // "01/Apart/000052"
        const parts = cod.split('/');
        const itemBloco = parts[0] || '';
        const itemNum   = parseInt(parts[2] || '0', 10);
        const label = item.querySelector('.chk-label').textContent.toLowerCase();

        const okText  = label.includes(textTerm);
        const okBloco = bloco === '' || itemBloco === bloco;
        const okDe    = numDe  === null || itemNum >= numDe;
        const okAte   = numAte === null || itemNum <= numAte;

        item.style.display = (okText && okBloco && okDe && okAte) ? 'flex' : 'none';
    });
}

// Busca por texto
buscaInput.addEventListener('input', applyFilters);

// Filtro por bloco
document.getElementById('filtro_bloco').addEventListener('change', applyFilters);

// Filtro por faixa de número
document.getElementById('filtro_de').addEventListener('input', applyFilters);
document.getElementById('filtro_ate').addEventListener('input', applyFilters);

// Limpar filtros
document.getElementById('btn_limpar_filtro').addEventListener('click', () => {
    document.getElementById('filtro_bloco').value = '';
    document.getElementById('filtro_de').value = '';
    document.getElementById('filtro_ate').value = '';
    buscaInput.value = '';
    applyFilters();
});

// =============================================
// BOTÕES DE SELEÇÃO
// =============================================

// Selecionar / Desmarcar TODAS (ignora filtro)
document.getElementById('btn_sel_todas').addEventListener('click', () => {
    document.querySelectorAll('.chk-unidade').forEach(chk => chk.checked = true);
});
document.getElementById('btn_des_todas').addEventListener('click', () => {
    document.querySelectorAll('.chk-unidade').forEach(chk => chk.checked = false);
});

// Selecionar / Desmarcar apenas VISÍVEIS (respeita filtro atual)
document.getElementById('btn_sel_filtro').addEventListener('click', () => {
    document.querySelectorAll('.list-item').forEach(item => {
        if (item.style.display !== 'none') {
            item.querySelector('.chk-unidade').checked = true;
        }
    });
});
document.getElementById('btn_des_filtro').addEventListener('click', () => {
    document.querySelectorAll('.list-item').forEach(item => {
        if (item.style.display !== 'none') {
            item.querySelector('.chk-unidade').checked = false;
        }
    });
});


// EEL Callbacks (Python -> JS)
eel.expose(log_message);
function log_message(msg) {
    logTextarea.value += msg + "\n";
    logTextarea.scrollTop = logTextarea.scrollHeight;
}

eel.expose(habilitar_leitura);
function habilitar_leitura() {
    const user = document.getElementById('usuario').value.trim();
    const pwd = document.getElementById('senha').value.trim();
    document.getElementById('session_info').textContent = `${user} / ${pwd}`;
    document.getElementById('session_bar').style.display = 'flex';
    document.querySelector('.app-container').classList.add('session-active');
    document.getElementById('controles_operacao').style.display = 'block';
    btnLer.disabled = false;
}

eel.expose(atualizar_lista_unidades);
function atualizar_lista_unidades(unidadesData) {
    // Esconde o loading quando os dados chegam do Python
    hideLoading();
    btnLer.disabled = false;
    btnLer.textContent = 'Ler Unidades da Tela';

    listaUnidades.innerHTML = '';
    
    if (unidadesData.length === 0) {
        listaUnidades.innerHTML = '<div class="empty-state">Nenhuma unidade encontrada. Verifique se filtrou o condomínio na tela do sistema.</div>';
        setStatus('⚠️ Nenhuma unidade encontrada.');
        return;
    }

    btnIniciar.disabled = false;
    setStatus(`✅ ${unidadesData.length} unidades carregadas. Selecione as que deseja vincular.`);

    // Extrai blocos únicos para popular o dropdown e o mapeamento
    const blocos = new Set();
    unidadesData.forEach(u => {
        const parts = u.nome.split('/');
        if (parts.length >= 1) blocos.add(parts[0]);
    });

    const selectBloco = document.getElementById('filtro_bloco');
    selectBloco.innerHTML = '<option value="">Todos</option>';
    [...blocos].sort().forEach(b => {
        const opt = document.createElement('option');
        opt.value = b;
        const valInt = parseInt(b, 10);
        opt.textContent = `Bloco ${isNaN(valInt) ? b : valInt}`;
        selectBloco.appendChild(opt);
    });

    // Popula a tabela de mapeamento de condomínios por bloco
    const mapaRows = document.getElementById('mapa_rows');
    mapaRows.innerHTML = '';
    [...blocos].sort().forEach(b => {
        const row = document.createElement('div');
        row.className = 'mapa-row';
        row.dataset.bloco = b;
        const valInt = parseInt(b, 10);
        const labelText = `Bloco ${isNaN(valInt) ? b : valInt}`;
        row.innerHTML = `
            <span class="mapa-bloco-name">${labelText}</span>
            <input type="text" placeholder="Ex: 506" title="Condomínio do ${labelText}">
        `;
        mapaRows.appendChild(row);
    });
    document.getElementById('mapeamento_blocos').style.display = 'block';

    // Mostra os filtros agora que há dados
    document.getElementById('filtros_container').style.display = 'flex';

    unidadesData.forEach(u => {
        const div = document.createElement('label');
        div.className = `list-item checkbox-wrapper ${u.concluido ? 'concluido' : ''}`;
        div.dataset.cod = u.nome;   // armazena o código para filtro
        
        const chk = document.createElement('input');
        chk.type = 'checkbox';
        chk.className = 'chk-unidade';
        chk.value = u.nome;
        chk.checked = !u.concluido;

        const span = document.createElement('span');
        span.className = 'checkmark';

        const txt = document.createElement('span');
        txt.className = 'chk-label';
        let labelText = u.concluido ? `[✅ CONCLUÍDO] ${u.nome}` : `[ ] ${u.nome}`;
        if (u.info) labelText += `    [Agregadas: ${u.info}]`;
        txt.textContent = labelText;

        div.appendChild(chk);
        div.appendChild(span);
        div.appendChild(txt);
        listaUnidades.appendChild(div);
    });

    // Aplica filtros atuais (caso já tenha algo digitado)
    applyFilters();
}

eel.expose(robo_finalizado);
function robo_finalizado() {
    btnIniciar.disabled = false;
    btnLer.disabled = false;
    btnParar.disabled = true;
    alert("Operação Finalizada! Verifique a aba de Histórico.");
}

eel.expose(atualizar_historico);
function atualizar_historico(concluidas) {
    const list = document.getElementById('lista_historico');
    list.innerHTML = '';
    if (concluidas.length === 0) {
        list.innerHTML = '<div class="empty-state">Nenhum histórico disponível.</div>';
        return;
    }

    concluidas.forEach(und => {
        const btn = document.createElement('button');
        btn.className = 'hist-item';
        btn.innerHTML = `✅ ${und}`;
        btn.onclick = async () => {
            document.querySelectorAll('.hist-item').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            
            // Carregar preview
            const base64img = await eel.get_print(und)();
            if (base64img) {
                document.getElementById('preview_placeholder').style.display = 'none';
                document.getElementById('preview_img').src = 'data:image/png;base64,' + base64img;
                document.getElementById('preview_img').style.display = 'block';
                document.getElementById('btn_baixar').disabled = false;
                document.getElementById('btn_excluir').disabled = false;
                document.getElementById('btn_baixar').onclick = () => baixarPrint(und, base64img);
                document.getElementById('btn_excluir').onclick = () => excluirPrint(und);
            } else {
                document.getElementById('preview_placeholder').textContent = 'Print indisponível (Sessão anterior)';
                document.getElementById('preview_placeholder').style.display = 'block';
                document.getElementById('preview_img').style.display = 'none';
                document.getElementById('btn_baixar').disabled = true;
                document.getElementById('btn_excluir').disabled = true;
            }
        };
        list.appendChild(btn);
    });
}

function baixarPrint(nome, b64) {
    const a = document.createElement('a');
    a.href = 'data:image/png;base64,' + b64;
    a.download = `Comprovante_${nome.replace('/', '_')}.png`;
    a.click();
}

async function excluirPrint(nome) {
    await eel.excluir_print(nome)();
    document.getElementById('preview_placeholder').textContent = 'Print excluído com sucesso.';
    document.getElementById('preview_placeholder').style.display = 'block';
    document.getElementById('preview_img').style.display = 'none';
    document.getElementById('btn_baixar').disabled = true;
    document.getElementById('btn_excluir').disabled = true;
}

// Init
window.onload = async () => {
    // Carregar histórico
    const concluidas = await eel.get_todas_concluidas()();
    atualizar_historico(concluidas);

    // Carregar login salvo
    const loginData = await eel.obter_login_salvo()();
    if (loginData) {
        if (loginData.usuario) {
            document.getElementById('usuario').value = loginData.usuario;
            document.getElementById('senha').value = loginData.senha;
            document.getElementById('lembrar_login').checked = true;
        } else {
            document.getElementById('lembrar_login').checked = false;
        }
    }
};

// =============================================
// AUTO-UPDATER (Python -> JS callbacks)
// =============================================

eel.expose(notificar_update);
function notificar_update(versao, downloadUrl, notas) {
    const modal = document.getElementById('modal_update');
    document.getElementById('modal_update_version').textContent = `Nova versão disponível: ${versao}`;
    const notesEl = document.getElementById('modal_update_notes');
    notesEl.textContent = notas || '';

    // Guarda a URL de download no dataset do modal para o botão usar
    modal.dataset.downloadUrl = downloadUrl;
    modal.dataset.versao = versao;
    modal.style.display = 'flex';
}

eel.expose(progresso_update);
function progresso_update(percent) {
    const progressWrap = document.getElementById('update_progress_wrap');
    const bar = document.getElementById('update_progress_bar');
    const label = document.getElementById('update_progress_label');

    if (percent === -1) {
        // Erro no download
        progressWrap.style.display = 'none';
        document.getElementById('modal_update_actions').style.display = 'flex';
        alert('Erro ao baixar a atualização. Tente novamente mais tarde.');
        return;
    }

    progressWrap.style.display = 'block';
    bar.style.width = percent + '%';
    label.textContent = percent < 100 ? `Baixando... ${percent}%` : '✅ Concluído! O app será reiniciado...';
}

// Botão "Atualizar Agora"
document.getElementById('btn_update_agora').addEventListener('click', async () => {
    // Oculta botões e mostra barra de progresso
    document.getElementById('modal_update_actions').style.display = 'none';
    document.getElementById('update_progress_wrap').style.display = 'block';

    // Chama o Python para iniciar o download
    await eel.verificar_update_disponivel()();
    // O download é iniciado pelo Python quando ele chama de volta iniciar_download_update
    // Aqui pedimos diretamente:
    const modal = document.getElementById('modal_update');
    await eel.iniciar_download_update(modal.dataset.downloadUrl || '')();
});

// Botão "Depois"
document.getElementById('btn_update_depois').addEventListener('click', () => {
    document.getElementById('modal_update').style.display = 'none';
});
