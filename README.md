# MultiTracks Section Cloner

Aplicação desktop em Python com interface moderna (CustomTkinter) e automação via Selenium para replicar automaticamente estruturas de seções e tempos (*timecodes*) entre músicas na plataforma MultiTracks.

## Funcionalidades

- **Dupla Sessão Simultânea:** Abre a conta de origem em sessão regular e a de destino em modo anônimo (`--incognito`), permitindo transferência entre contas distintas sem conflito de login.
- **Tratamento Automático de Cookies:** Detecta e aceita os banners de cookies da plataforma para evitar travamentos de clique.
- **Normalização de Estrutura:** Garante a seção inicial "Contagem (00:00:000)" no destino e replica dinamicamente as seções subsequentes ("Introdução", "Versos", "Refrão", etc.).
- **Entrada Simplificada por ID:** Permite informar apenas o `libraryID` numérico da música (ex: `4721009`) ou colar o link completo.
- **Persistência de Credenciais:** Salva e-mails e senhas localmente no arquivo `config.json` para agilizar execuções futuras.

## Pré-requisitos

- Python 3.10 ou superior
- Google Chrome instalado

## Instalação

1. Clone o repositório:
   ```bash
   git clone [https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git](https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git)
   cd NOME_DO_REPOSITORIO
   ```

2. Crie e ative um ambiente virtual (recomendado):
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. Instale as dependências:
   ```cmd
   pip install -r requirements.txt
   ```

## Como Executar

Execute o arquivo principal:

```cmd
python main.py
```

1. Informe o e-mail, senha e ID da música da **Conta de Origem**.
2. Informe o e-mail, senha e ID da música da **Conta de Destino**.
3. Clique em **"Iniciar Clonagem de Seções"**.
