import os
import re
import time
import json
import threading
from tkinter import messagebox

import customtkinter as ctk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configurações visuais modernas
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
URL_LOGIN = "https://www.multitracks.com.br/login/"
URL_BASE_SECOES = "https://www.multitracks.com.br/premium/library/cloud/tracks/sections.aspx?libraryID="

# --- Funções Auxiliares de URL e ID ---

def formatar_url_secoes(entrada):
    """
    Aceita tanto apenas o ID numérico (ex: 4721009)
    quanto o link completo, extraindo o ID e montando a URL padronizada.
    """
    entrada = entrada.strip()
    match = re.search(r"libraryID=(\d+)", entrada)
    if match:
        lib_id = match.group(1)
    else:
        # Pega apenas os dígitos digitados
        lib_id = re.sub(r"\D", "", entrada)
        
    if not lib_id:
        return None
    return f"{URL_BASE_SECOES}{lib_id}"

# --- Gerenciamento de Credenciais ---

def carregar_credenciais_salvas():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao ler config.json: {e}")
            return {}
    return {}

def guardar_credenciais(email_ori, pass_ori, email_dest, pass_dest):
    dados = {
        "email_ori": email_ori,
        "pass_ori": pass_ori,
        "email_dest": email_dest,
        "pass_dest": pass_dest
    }
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4)
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")
        return False

# --- Tratamento de Cookies e Banners ---

def tratar_e_aceitar_cookies(driver, log_cb=None):
    try:
        botoes_aceitar = driver.find_elements(By.CSS_SELECTOR, ".js-cookie-accept-all, button.js-cookie-accept-all")
        for btn in botoes_aceitar:
            if btn.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                driver.execute_script("arguments[0].click();", btn)
                if log_cb:
                    log_cb("Banner de cookies aceito com sucesso!")
                time.sleep(0.5)
                return
    except Exception:
        pass

    try:
        driver.execute_script("""
            const elementos = document.querySelectorAll(
                '.cookie-banner, .js-cookie-banner, [data-modal-id="cookie-preferences-modal"], .remodal-overlay'
            );
            elementos.forEach(el => el.remove());
        """)
    except Exception:
        pass

# --- Automação Selenium ---

def realizar_login(driver, email, senha, log_cb):
    log_cb(f"Abrindo tela de login para {email}...")
    driver.get(URL_LOGIN)
    wait = WebDriverWait(driver, 15)

    tratar_e_aceitar_cookies(driver, log_cb)

    if "/login" not in driver.current_url.lower():
        log_cb(f"Sessão já ativa para {email}.")
        tratar_e_aceitar_cookies(driver, log_cb)
        return

    try:
        campo_email = wait.until(EC.element_to_be_clickable((By.ID, "Email")))
        campo_email.click()
        campo_email.clear()
        campo_email.send_keys(email)

        campo_senha = driver.find_element(By.ID, "password")
        campo_senha.click()
        campo_senha.clear()
        campo_senha.send_keys(senha)

        try:
            btn_entrar = driver.find_element(By.ID, "lnkLogin")
            driver.execute_script("arguments[0].click();", btn_entrar)
        except Exception:
            campo_senha.send_keys(Keys.ENTER)

        WebDriverWait(driver, 20).until(lambda d: "/login" not in d.current_url.lower())
        log_cb(f"Login validado com sucesso para {email}.")

        time.sleep(1.5)
        tratar_e_aceitar_cookies(driver, log_cb)

    except Exception:
        log_cb("Aviso: Conclua a validação na tela caso necessário...")
        WebDriverWait(driver, 60).until(lambda d: "/login" not in d.current_url.lower())
        log_cb(f"Login detectado para {email}.")
        time.sleep(1.5)
        tratar_e_aceitar_cookies(driver, log_cb)

def extrair_secoes(driver, url, log_cb):
    log_cb(f"Acessando música de origem ({url})...")
    driver.get(url)
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.track-names, #chartData")))

    tratar_e_aceitar_cookies(driver, log_cb)

    try:
        chart_data = driver.find_element(By.ID, "chartData").get_attribute("value")
        if chart_data:
            data = json.loads(chart_data)
            sections = data.get("sections", [])
            if sections:
                log_cb(f"Encontradas {len(sections)} seções no JSON embutido.")
                return sections
    except Exception:
        pass

    secoes = []
    linhas = driver.find_elements(By.CSS_SELECTOR, "li.track-names--row.js-form-row")
    for linha in linhas:
        select_elem = Select(linha.find_element(By.CSS_SELECTOR, "select.js-form-section"))
        input_time = linha.find_element(By.CSS_SELECTOR, "input.js-form-time")
        
        secoes.append({
            "section_text": select_elem.first_selected_option.text.strip(),
            "section_val": select_elem.first_selected_option.get_attribute("value"),
            "timecode": input_time.get_attribute("value").strip(),
            "is_readonly": input_time.get_attribute("readonly") is not None
        })
    log_cb(f"Encontradas {len(secoes)} seções via DOM.")
    return secoes

def preencher_secoes(driver, url, lista_secoes, log_cb, progress_cb):
    log_cb(f"Acessando música de destino ({url})...")
    driver.get(url)
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.track-names")))

    tratar_e_aceitar_cookies(driver, log_cb)

    # 1. Configurar linha 1 como Contagem zerada
    linhas = driver.find_elements(By.CSS_SELECTOR, "li.track-names--row.js-form-row")
    if not linhas:
        btn_add = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.js-add-section")))
        driver.execute_script("arguments[0].click();", btn_add)
        time.sleep(0.4)
        linhas = driver.find_elements(By.CSS_SELECTOR, "li.track-names--row.js-form-row")

    primeira_linha = linhas[0]
    select_primeira = Select(primeira_linha.find_element(By.CSS_SELECTOR, "select.js-form-section"))
    
    try:
        select_primeira.select_by_value("7")
    except Exception:
        select_primeira.select_by_visible_text("Contagem")

    input_tempo_prim = primeira_linha.find_element(By.CSS_SELECTOR, "input.js-form-time")
    if not input_tempo_prim.get_attribute("readonly"):
        input_tempo_prim.click()
        input_tempo_prim.send_keys(Keys.CONTROL + "a")
        input_tempo_prim.send_keys("00:00:000")

    log_cb("Linha 1 definida como: Contagem (00:00:000)")

    # 2. Filtrar seções de origem (pula contagem prévia)
    secoes_para_inserir = []
    for item in lista_secoes:
        nome = item.get("section_text", "")
        sec_id = str(item.get("sectionID", item.get("section_val", "")))
        tempo = item.get("timecode", "")

        if sec_id == "7" or nome.lower() == "contagem" or tempo == "00:00:000":
            continue
        secoes_para_inserir.append(item)

    total = len(secoes_para_inserir)
    log_cb(f"Replicando {total} seções a partir da Contagem...")

    # 3. Adicionar e preencher seções subsequentes
    for i, item in enumerate(secoes_para_inserir):
        tratar_e_aceitar_cookies(driver)
        
        indice_alvo = i + 1
        linhas = driver.find_elements(By.CSS_SELECTOR, "li.track-names--row.js-form-row")

        if indice_alvo >= len(linhas):
            btn_add = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.js-add-section")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_add)
            time.sleep(0.2)
            try:
                btn_add.click()
            except Exception:
                driver.execute_script("arguments[0].click();", btn_add)

            time.sleep(0.4)
            linhas = driver.find_elements(By.CSS_SELECTOR, "li.track-names--row.js-form-row")

        linha_alvo = linhas[indice_alvo]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", linha_alvo)

        select_elem = Select(linha_alvo.find_element(By.CSS_SELECTOR, "select.js-form-section"))
        
        if "section_text" in item and item["section_text"]:
            try:
                select_elem.select_by_visible_text(item["section_text"])
            except Exception:
                select_elem.select_by_value(str(item.get("section_val", "")))
        elif "sectionID" in item:
            select_elem.select_by_value(str(item["sectionID"]))

        input_tempo = linha_alvo.find_element(By.CSS_SELECTOR, "input.js-form-time")
        tempo_valor = item.get("timecode", "00:00:000")
        try:
            input_tempo.click()
        except Exception:
            driver.execute_script("arguments[0].focus();", input_tempo)

        input_tempo.send_keys(Keys.CONTROL + "a")
        input_tempo.send_keys(tempo_valor)

        log_cb(f"[{i+1}/{total}] {item.get('section_text', item.get('sectionID'))} -> {tempo_valor}")
        progress_cb((i + 1) / total)

    # 4. Salvar formulário
    log_cb("Salvando formulário final...")
    tratar_e_aceitar_cookies(driver)
    btn_salvar = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.js-form-save")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_salvar)
    time.sleep(0.3)
    try:
        btn_salvar.click()
    except Exception:
        driver.execute_script("arguments[0].click();", btn_salvar)

    log_cb("Sincronização salva no destino!")

# --- Interface Gráfica Moderna ---

class ModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MultiTracks Sync Pro")
        self.geometry("760x820")
        self.resizable(False, False)

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=25, pady=(20, 10))

        self.lbl_title = ctk.CTkLabel(
            self.header_frame, 
            text="MultiTracks Section Cloner", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.lbl_title.pack(anchor="w")

        self.lbl_subtitle = ctk.CTkLabel(
            self.header_frame, 
            text="Copie seções digitando apenas o ID da música (libraryID)", 
            text_color="gray",
            font=ctk.CTkFont(size=13)
        )
        self.lbl_subtitle.pack(anchor="w")

        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=5)

        # Card 1: Origem
        self.card_origem = ctk.CTkFrame(self.main_container, corner_radius=12)
        self.card_origem.pack(fill="x", pady=8, padx=5)

        lbl_card1 = ctk.CTkLabel(
            self.card_origem, 
            text="MÚSICA DE ORIGEM (Janela Normal)", 
            font=ctk.CTkFont(size=12, weight="bold"), 
            text_color="#3B8ED0"
        )
        lbl_card1.pack(anchor="w", padx=15, pady=(12, 8))

        row1 = ctk.CTkFrame(self.card_origem, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=4)
        
        self.ent_email_ori = ctk.CTkEntry(row1, placeholder_text="E-mail Origem", width=340)
        self.ent_email_ori.pack(side="left", padx=(0, 10))

        self.ent_pass_ori = ctk.CTkEntry(row1, placeholder_text="Senha", show="•", width=340)
        self.ent_pass_ori.pack(side="left")

        self.ent_id_ori = ctk.CTkEntry(self.card_origem, placeholder_text="ID da Música de Origem (Ex: 4721009 ou link)")
        self.ent_id_ori.pack(fill="x", padx=15, pady=(6, 15))

        # Card 2: Destino
        self.card_destino = ctk.CTkFrame(self.main_container, corner_radius=12)
        self.card_destino.pack(fill="x", pady=8, padx=5)

        lbl_card2 = ctk.CTkLabel(
            self.card_destino, 
            text="MÚSICA DE DESTINO (Janela Anônima)", 
            font=ctk.CTkFont(size=12, weight="bold"), 
            text_color="#2CC985"
        )
        lbl_card2.pack(anchor="w", padx=15, pady=(12, 8))

        row2 = ctk.CTkFrame(self.card_destino, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=4)

        self.ent_email_dest = ctk.CTkEntry(row2, placeholder_text="E-mail Destino", width=340)
        self.ent_email_dest.pack(side="left", padx=(0, 10))

        self.ent_pass_dest = ctk.CTkEntry(row2, placeholder_text="Senha", show="•", width=340)
        self.ent_pass_dest.pack(side="left")

        self.ent_id_dest = ctk.CTkEntry(self.card_destino, placeholder_text="ID da Música de Destino (Ex: 2584846 ou link)")
        self.ent_id_dest.pack(fill="x", padx=15, pady=(6, 15))

        # Ações de Credenciais
        frame_cred = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame_cred.pack(fill="x", padx=10, pady=(4, 10))

        self.btn_salvar_manual = ctk.CTkButton(
            frame_cred,
            text="Salvar Credenciais Agora",
            width=180,
            height=30,
            fg_color="#333333",
            hover_color="#444444",
            font=ctk.CTkFont(size=12),
            command=self.acao_salvar_credenciais
        )
        self.btn_salvar_manual.pack(side="left")

        self.lbl_salvo_status = ctk.CTkLabel(
            frame_cred,
            text="",
            text_color="#2CC985",
            font=ctk.CTkFont(size=12)
        )
        self.lbl_salvo_status.pack(side="left", padx=15)

        # Botão de Execução e Barra de Progresso
        self.btn_run = ctk.CTkButton(
            self.main_container, 
            text="Iniciar Clonagem de Seções", 
            height=45, 
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8,
            command=self.iniciar_processo
        )
        self.btn_run.pack(fill="x", padx=5, pady=(10, 10))

        self.progress_bar = ctk.CTkProgressBar(self.main_container, height=6)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=5, pady=(0, 10))

        # Logs
        self.txt_log = ctk.CTkTextbox(
            self.main_container, 
            height=150, 
            corner_radius=10, 
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.txt_log.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        self.preencher_credenciais_guardadas()
        self.conectar_eventos_digitacao()

    def conectar_eventos_digitacao(self):
        for entry in [self.ent_email_ori, self.ent_pass_ori, self.ent_email_dest, self.ent_pass_dest]:
            entry.bind("<KeyRelease>", lambda event: self.auto_salvar_silencioso())

    def auto_salvar_silencioso(self):
        em_ori = self.ent_email_ori.get().strip()
        pw_ori = self.ent_pass_ori.get().strip()
        em_dest = self.ent_email_dest.get().strip()
        pw_dest = self.ent_pass_dest.get().strip()
        
        if em_ori or pw_ori or em_dest or pw_dest:
            guardar_credenciais(em_ori, pw_ori, em_dest, pw_dest)
            self.lbl_salvo_status.configure(text="Credenciais salvas automaticamente ✓")

    def acao_salvar_credenciais(self):
        em_ori = self.ent_email_ori.get().strip()
        pw_ori = self.ent_pass_ori.get().strip()
        em_dest = self.ent_email_dest.get().strip()
        pw_dest = self.ent_pass_dest.get().strip()

        if guardar_credenciais(em_ori, pw_ori, em_dest, pw_dest):
            self.lbl_salvo_status.configure(text="Salvo com sucesso em config.json ✓")
            self.log(f"Configurações gravadas em: {CONFIG_FILE}")

    def preencher_credenciais_guardadas(self):
        dados = carregar_credenciais_salvas()
        if dados:
            if dados.get("email_ori"):
                self.ent_email_ori.insert(0, dados["email_ori"])
            if dados.get("pass_ori"):
                self.ent_pass_ori.insert(0, dados["pass_ori"])
            if dados.get("email_dest"):
                self.ent_email_dest.insert(0, dados["email_dest"])
            if dados.get("pass_dest"):
                self.ent_pass_dest.insert(0, dados["pass_dest"])
            self.lbl_salvo_status.configure(text="Credenciais carregadas ✓")

    def log(self, mensagem):
        self.txt_log.insert("end", f"▸ {mensagem}\n")
        self.txt_log.see("end")

    def update_progress(self, valor):
        self.progress_bar.set(valor)

    def iniciar_processo(self):
        id_ori_raw = self.ent_id_ori.get().strip()
        id_dest_raw = self.ent_id_dest.get().strip()

        url_ori = formatar_url_secoes(id_ori_raw)
        url_dest = formatar_url_secoes(id_dest_raw)

        if not url_ori or not url_dest:
            messagebox.showwarning("IDs Inválidos", "Por favor, informe IDs numéricos válidos (ex: 4721009) para Origem e Destino.")
            return

        dados = {
            "email_ori": self.ent_email_ori.get().strip(),
            "pass_ori": self.ent_pass_ori.get().strip(),
            "url_ori": url_ori,
            "email_dest": self.ent_email_dest.get().strip(),
            "pass_dest": self.ent_pass_dest.get().strip(),
            "url_dest": url_dest
        }

        if not dados["email_ori"] or not dados["pass_ori"] or not dados["email_dest"] or not dados["pass_dest"]:
            messagebox.showwarning("Credenciais", "Por favor, preencha os e-mails e senhas de ambas as contas.")
            return

        guardar_credenciais(dados["email_ori"], dados["pass_ori"], dados["email_dest"], dados["pass_dest"])

        self.btn_run.configure(state="disabled", text="Processando...")
        self.progress_bar.set(0)
        self.txt_log.delete("1.0", "end")

        threading.Thread(target=self.worker, args=(dados,), daemon=True).start()

    def worker(self, d):
        driver_origem = None
        driver_destino = None
        service = Service(ChromeDriverManager().install())

        try:
            # Sessão 1: Origem
            self.log("Abrindo Chrome (Sessão de Origem)...")
            opt_normal = Options()
            opt_normal.add_argument("--start-maximized")
            driver_origem = webdriver.Chrome(service=service, options=opt_normal)

            realizar_login(driver_origem, d["email_ori"], d["pass_ori"], self.log)
            secoes = extrair_secoes(driver_origem, d["url_ori"], self.log)

            if not secoes:
                raise Exception("Nenhuma seção foi encontrada na música de origem.")

            # Sessão 2: Destino (Anônima)
            self.log("Abrindo Chrome Anônimo (Sessão de Destino)...")
            opt_incognito = Options()
            opt_incognito.add_argument("--incognito")
            opt_incognito.add_argument("--start-maximized")
            driver_destino = webdriver.Chrome(service=service, options=opt_incognito)

            realizar_login(driver_destino, d["email_dest"], d["pass_dest"], self.log)
            preencher_secoes(driver_destino, d["url_dest"], secoes, self.log, self.update_progress)

            self.update_progress(1.0)
            messagebox.showinfo("Sucesso", "Todas as seções foram clonadas e salvas com sucesso!")
        except Exception as e:
            self.log(f"ERRO: {str(e)}")
            messagebox.showerror("Erro de Execução", f"Ocorreu uma falha:\n{str(e)}")
        finally:
            if driver_origem:
                driver_origem.quit()
            if driver_destino:
                driver_destino.quit()
            self.btn_run.configure(state="normal", text="Iniciar Clonagem de Seções")

if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()
