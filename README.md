<div align="center">

# 🎵 MultiTracks Section Cloner

### *Sincronização e replicação automatizada de seções e timecodes para MultiTracks*

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.15%2B-43B02A.svg?style=for-the-badge&logo=selenium&logoColor=white)](https://www.selenium.dev/)
[![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blueviolet.svg?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![License](https://img.shields.io/badge/License-MIT-black.svg?style=for-the-badge)](LICENSE)

<p align="center">
  Uma ferramenta desktop moderna criada para clonar estruturas de seções (Versos, Refrão, Pontes, etc.) e marcações de tempo entre músicas no MultiTracks em poucos segundos.
</p>

[Funcionalidades](#-funcionalidades) •
[Demonstração](#-como-funciona) •
[Instalação](#-instalação) •
[Como Usar](#-como-usar) •
[Estrutura](#-estrutura-do-projeto) •
[Avisos](#-segurança)

---

</div>

## 🚀 Funcionalidades

- **⚡ Entrada Simplificada por ID:** Apenas digite o `libraryID` da música (ex.: `4721009`) ou cole o link completo — o app extrai e formata o link automaticamente.
- **🎭 Dupla Sessão Isolada:** Abre a conta de origem em navegação regular e a conta de destino em modo anônimo (`--incognito`), permitindo transferência simultânea entre contas diferentes sem conflito de login.
- **🛡️ Tratamento Automático de Cookies:** Detecta e aceita os banners de cookies da plataforma instantaneamente para evitar cliques interceptados ou travamentos de tela.
- **🎼 Normalização Inteligente de Estrutura:**
  - Padroniza a primeira seção como `Contagem (00:00:000)`.
  - Ignora a contagem inicial da origem para evitar duplicidade.
  - Replica todas as seções subsequentes (`Introdução`, `Verso 1`, `Refrão`, etc.) adicionando linhas dinamicamente no destino.
- **🔑 Persistência Local Segura:** Salva suas credenciais em `config.json` no primeiro uso para que você não precise redigitar sempre que abrir a ferramenta.
- **🎨 Interface Moderna:** Visual escuro nativo (*Dark Mode*), barra de progresso em tempo real e terminal de logs integrado feito em `CustomTkinter`.

---

## 🖥️ Como Funciona

```text
[ Conta de Origem ]  ──(Lê seções e timecodes)──┐
                                                 ├─► [ MultiTracks Section Cloner ]
[ Conta de Destino ] ◄──(Cria e salva seções)───┘
