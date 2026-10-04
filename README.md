<div align="center">

# 🎵 MultiTracks Section Cloner

### *Sincronização e replicação automatizada de secções e timecodes para MultiTracks*

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.15%2B-43B02A.svg?style=for-the-badge&logo=selenium&logoColor=white)](https://www.selenium.dev/)
[![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blueviolet.svg?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![Platform](https://img.shields.io/badge/Plataforma-Windows-0078D6.svg?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/)
[![License](https://img.shields.io/badge/License-MIT-black.svg?style=for-the-badge)](LICENSE)

<p align="center">
  Uma ferramenta desktop moderna desenvolvida em Python para transferir e clonar automaticamente marcações de tempo (timecodes) e secções (Introdução, Versos, Refrão, etc.) entre músicas na plataforma MultiTracks.
</p>

[Funcionalidades](#-funcionalidades) •
[Pré-requisitos](#-pré-requisitos) •
[Instalação do Ambiente](#-instalação-do-ambiente-passo-a-passo) •
[Como Usar](#-como-usar) •
[Estrutura do Projeto](#-estrutura-do-projeto) •
[Resolução de Problemas](#-resolução-de-problemas-comuns) •
[Segurança](#-segurança)

---

</div>

## 🚀 Funcionalidades

- **⚡ Entrada Simplificada por ID:** Apenas digite o `libraryID` numérico da música (ex.: `4721009`) ou cole o link direto da página de secções.
- **🎭 Dupla Sessão Simultânea e Isolada:**
  - **Origem:** Abre numa janela padrão do Chrome para leitura dos dados.
  - **Destino:** Abre numa janela em modo anónimo (`--incognito`), permitindo a transferência entre contas distintas em simultâneo sem conflito de autenticação.
- **🛡️ Tratamento Automático de Banners de Cookies:** Deteta e clica automaticamente no botão de aceitação de cookies da plataforma para evitar o bloqueio e interceção de cliques.
- **🎼 Normalização Inteligente de Secções:**
  - Força a primeira secção da música de destino para `Contagem (00:00:000)`.
  - Filtra e ignora a contagem inicial da música de origem para evitar duplicados.
  - Cria dinamicamente as novas secções clicando no botão oficial `Adicionar Seção`.
- **🔑 Persistência Automática de Credenciais:** Guarda os dados de acesso no ficheiro local `config.json` à medida que digita, evitando que tenha de inserir o e-mail e palavra-passe sempre que abre o programa.
- **🎨 Interface Moderna:** Desenvolvida em `CustomTkinter`, com modo escuro (*Dark Mode*), barra de progresso em tempo real e consola de depuração integrada.

---

## 📋 Pré-requisitos

Antes de iniciar, certifique-se de que tem:
1. **Sistema Operativo:** Windows 10 ou Windows 11.
2. **Navegador:** [Google Chrome](https://www.google.com/chrome/) instalado e atualizado.
3. **Python:** Versão 3.10 ou superior.

---

## 🛠️ Instalação do Ambiente (Passo a Passo)

Siga estas instruções com atenção se estiver a configurar a máquina pela primeira vez.

### 1. Instalação e Configuração do Python no Windows

1. Aceda ao site oficial e descarregue o instalador: [python.org/downloads](https://www.python.org/downloads/).
2. Abra o executável descarregado.
3. ⚠️ **MUITO IMPORTANTE:** No primeiro ecrã da instalação, marque a caixa de seleção:
   - **`Add python.exe to PATH`** (ou `Adicionar python.exe ao PATH`).
4. Clique em **Install Now** e conclua a instalação.
5. Feche e volte a abrir o **Prompt de Comando (CMD)** ou o **PowerShell** para carregar as novas variáveis de ambiente.

Para verificar se o Python foi reconhecido, execute:
```cmd
python --version
