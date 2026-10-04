<div align="center">

# 🎵 MultiTracks Section Cloner

### *Sincronização e automação desktop de seções e timecodes para MultiTracks*

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.15%2B-43B02A.svg?style=for-the-badge&logo=selenium&logoColor=white)](https://www.selenium.dev/)
[![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blueviolet.svg?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![Platform](https://img.shields.io/badge/Plataforma-Windows-0078D6.svg?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/)
[![License](https://img.shields.io/badge/License-MIT-black.svg?style=for-the-badge)](LICENSE)

<p align="center">
  Ferramenta desktop moderna desenvolvida em Python para transferir e replicar automaticamente marcações de tempo (timecodes) e seções de músicas (Introdução, Versos, Refrão, etc.) entre contas distintas no MultiTracks.com.br.
</p>

[Visão Geral](#-visão-geral) •
[Funcionalidades e Regras de Negócio](#-funcionalidades-e-regras-de-negócio) •
[Pré-requisitos](#-pré-requisitos) •
[Configuração e Habilitação do Selenium](#-configuração-e-habilitação-do-selenium) •
[Instalação do Ambiente](#-instalação-do-ambiente-passo-a-passo) •
[Como Usar](#-como-usar) •
[Estrutura de Arquivos](#-estrutura-de-arquivos-do-projeto) •
[Resolução de Problemas](#-resolução-de-problemas-comuns) •
[Segurança](#-segurança-e-boas-práticas)

---

</div>

## 📌 Visão Geral

Copiar manualmente as marcações de seções de uma música para outra no editor do MultiTracks exige dezenas de cliques repetitivos e conferência manual de compassos. 

O **MultiTracks Section Cloner** executa todo o fluxo de ponta a ponta: conecta-se simultaneamente à conta de origem e à conta de destino, extrai a estrutura original e reconstrói cada linha no destino de forma precisa em poucos segundos.

---

## 🚀 Funcionalidades e Regras de Negócio

### 1. Dupla Sessão Isolada Simultânea
- **Conta de Origem:** Abre em uma instância regular do Google Chrome para leitura e extração.
- **Conta de Destino:** Abre em uma instância paralela em modo anônimo (`--incognito`), permitindo autenticar duas contas diferentes no mesmo computador sem conflitos de cookies ou quedas de sessão.

### 2. Autenticação Adaptada
- Utiliza a rota moderna `/login/`.
- Seletores específicos para o formulário ASP.NET da plataforma:
  - E-mail / Usuário: `#Email`
  - Senha: `#password`
  - Botão de Login: `#lnkLogin` (com fallback de submissão por `Enter`).
- Tolerância para verificação manual de segurança (CAPTCHA / confirmação em duas etapas).

### 3. Tratamento Automático do Banner de Cookies
- Detecção em tempo real e clique no botão oficial com a classe `.js-cookie-accept-all`.
- Injeção de script de segurança para remover sobreposições do DOM (`.cookie-banner`, `[data-modal-id='cookie-preferences-modal']`), prevenindo erros de `ElementClickInterceptedException`.

### 4. Regras de Estruturação das Seções
- **Linha 1 do Destino:** Forçada automaticamente para a seção `Contagem` (seletor valor `7`) com tempo zerado (`00:00:000`).
- **Filtragem Inteligente:** A contagem inicial da música de origem é descartada para evitar duplicidade.
- **Criação Dinâmica:** O robô compara o número de linhas existentes e clica repetidamente no botão `Adicionar Seção` (`a.js-add-section`), preenchendo os seletores (`select.js-form-section`) e os campos de tempo (`input.js-form-time`).
- **Salvamento Automático:** Aciona o botão de salvar (`a.js-form-save`) ao término do processo.

### 5. Entrada Flexível de Músicas
- Aceita apenas o ID numérico da música (ex: `4721009`).
- Aceita o link completo da página (ex: `https://www.multitracks.com.br/premium/library/cloud/tracks/sections.aspx?libraryID=4721009`). O extrator via expressão regular captura o `libraryID` e monta o endereço padronizado automaticamente.

### 6. Persistência Automática de Credenciais
- Os campos de e-mail e senha são gravados em tempo real (`<KeyRelease>`) no arquivo local `config.json` usando caminho absoluto (`os.path.dirname(os.path.abspath(__file__))`).
- Ao reabrir o aplicativo, os dados são carregados automaticamente.

### 7. Interface Gráfica Moderna
- Desenvolvida com `CustomTkinter` em tema escuro nativo (*Dark Mode*).
- Cards separados para as contas de Origem e Destino.
- Barra de progresso dinâmica calculada pelo total de seções processadas.
- Terminal embutido com fonte monoespaçada exibindo logs detalhados em tempo real.

---

## 📋 Pré-requisitos

1. **Sistema Operacional:** Windows 10 ou Windows 11 (64 bits).
2. **Navegador:** [Google Chrome](https://www.google.com/chrome/) instalado e atualizado.
3. **Python:** Versão 3.10 ou superior.

---

## 🌐 Configuração e Habilitação do Selenium

O projeto dispensa a instalação e configuração manual de drivers de navegação no Windows.

### Como o ChromeDriver é gerenciado
A biblioteca `webdriver-manager` identifica a versão exata do Google Chrome instalada no seu sistema operacional e baixa o binário correspondente do ChromeDriver automaticamente:

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
```

### Comunicação e Firewall
* Na primeira execução, o `webdriver-manager` faz o download do executável para `%USERPROFILE%\.wdm`.
* Caso o Firewall do Windows solicite autorização para o `chromedriver.exe`, clique em **Permitir acesso**.
* Para manter a compatibilidade, certifique-se de que o Google Chrome esteja atualizado acessando **Menu (três pontos) > Ajuda > Sobre o Google Chrome**.

---

## 🛠️ Instalação do Ambiente (Passo a Passo)

### 1. Instalar o Python no Windows

1. Baixe o instalador no site oficial: [python.org/downloads](https://www.python.org/downloads/).
2. Execute o instalador.
3. ⚠️ **OBRIGATÓRIO:** No primeiro painel, marque a caixa:
   - **`Add python.exe to PATH`** (Adicionar python.exe ao PATH).
4. Clique em **Install Now** e aguarde a finalização.
5. Abra um novo terminal do Prompt de Comando (CMD) ou PowerShell e teste:
   ```cmd
   python --version
   ```

---

### 2. Obter os Arquivos do Projeto

Clone o repositório ou descompacte o arquivo do projeto em um diretório de sua escolha:
```bash
git clone https://github.com/SEU_USUARIO/multitracks-section-sync.git
cd multitracks-section-sync
```

---

### 3. Criar e Ativar o Ambiente Virtual (Recomendado)

O ambiente virtual isola as dependências do projeto:

1. Crie o ambiente virtual:
   ```cmd
   python -m venv venv
   ```
2. Ative o ambiente:
   - No **Prompt de Comando (CMD)**:
     ```cmd
     venv\Scripts\activate
     ```
   - No **PowerShell**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   *(O prefixo `(venv)` aparecerá na linha de comando).*

> **Nota para PowerShell:** Se surgir o erro de script desabilitado, abra o PowerShell como Administrador e execute:  
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

### 4. Instalar as Dependências

Com o ambiente virtual ativado, instale os pacotes necessários:

```cmd
pip install -r requirements.txt
```

As dependências instaladas serão:
* `customtkinter`: Interface gráfica moderna.
* `selenium`: Controle e automação do navegador.
* `webdriver-manager`: Download e gestão automática do ChromeDriver.

---

## 🎮 Como Usar

### 1. Iniciar o Aplicativo

No terminal dentro da pasta do projeto com o ambiente ativo:
```cmd
python main.py
```

---

### 2. Preenchimento dos Dados

1. **Conta de Origem:**
   - Digite o e-mail e a senha da conta que possui a música pronta.
   - Digite o ID da música (ex: `4721009`) ou cole o link da página de seções.
2. **Conta de Destino:**
   - Digite o e-mail e a senha da conta que receberá a estrutura.
   - Digite o ID da música de destino (ex: `2584846`) ou cole o link da página de seções.
3. **Persistência:**
   - As credenciais são salvas automaticamente em tempo real no `config.json`.
4. **Execução:**
   - Clique em **"Iniciar Clonagem de Seções"**.
   - As janelas serão abertas, a autenticação será validada e as seções serão configuradas e salvas no destino.

---

## 📂 Estrutura de Arquivos do Projeto

```text
multitracks-section-sync/
│
├── .gitignore              # Impede envio de credenciais (config.json) e pastas de build
├── config.example.json      # Modelo de referência para o arquivo de credenciais
├── requirements.txt        # Dependências do Python (customtkinter, selenium, etc.)
├── README.md               # Documentação completa do repositório
└── main.py                 # Código principal contendo a interface e o robô Selenium
```

---

## 💡 Dica: Criar Atalho sem Terminal

Para iniciar o programa diretamente com um clique no Windows:

1. Renomeie o arquivo `main.py` para **`main.pyw`** (executa com `pythonw.exe` sem abrir a janela preta do console).
2. Clique com o botão direito em `main.pyw` > **Mostrar mais opções** > **Enviar para** > **Área de trabalho (criar atalho)**.
3. Nas propriedades do atalho, você pode alterar o ícone escolhendo qualquer arquivo `.ico`.

---

## ❓ Resolução de Problemas Comuns

### 1. `ElementClickInterceptedException` (Clique Bloqueado)
* O código possui rotinas que limpam o banner de cookies (`.js-cookie-accept-all`) e executam cliques com `scrollIntoView` e injeção de JavaScript para contornar overlays do site.

### 2. `SessionNotCreatedException` (ChromeDriver Desatualizado)
* Ocorre se o Google Chrome foi atualizado e o cache local do driver ficou antigo. Para corrigir, basta apagar a pasta `.wdm` localizada em `C:\Users\SEU_USUARIO\.wdm`. O programa fará o download da versão compatível na próxima inicialização.

### 3. "python não é reconhecido como um comando interno ou externo"
* O Python foi instalado sem marcar a opção **Add python.exe to PATH**. Reinstale o Python marcando a caixa de seleção correspondente.

---

## 🔒 Segurança e Boas Práticas

> [!WARNING]
> O arquivo `config.json` armazena e-mails e senhas localmente no seu computador.
> **Nunca remova o `config.json` do seu `.gitignore`** e nunca envie suas credenciais para repositórios públicos no GitHub.
