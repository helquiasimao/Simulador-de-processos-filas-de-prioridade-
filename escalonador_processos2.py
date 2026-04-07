"""
Trabalho Prático 1.7 - Simulador de Processos com Filas de Prioridade
Escalonador de processos com interface gráfica usando Tkinter
"""

import heapq
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, field
from typing import Optional
import random


# ============================================================
# CLASSE PROCESSO
# ============================================================

@dataclass
class Processo:
    """
    Representa um processo do sistema operativo.

    Atributos:
        id          : Identificador único do processo
        prioridade  : Nível de prioridade (menor valor = maior prioridade)
        tempo_execucao: Tempo necessário para executar o processo (segundos)
        nome        : Nome descritivo do processo
        estado      : Estado atual ('Aguardando', 'Executando', 'Concluído')
    """
    id: int
    prioridade: int
    tempo_execucao: float
    nome: str
    estado: str = "Aguardando"

    # Necessário para heapq — compara por (prioridade, id) para desempate
    def __lt__(self, outro: "Processo") -> bool:
        if self.prioridade != outro.prioridade:
            return self.prioridade < outro.prioridade
        return self.id < outro.id

    def __repr__(self) -> str:
        return (f"Processo(id={self.id}, nome='{self.nome}', "
                f"prioridade={self.prioridade}, "
                f"tempo={self.tempo_execucao}s)")


# ============================================================
# FILA DE PRIORIDADE (min-heap via heapq)
# ============================================================

class FilaPrioridade:
    """
    Fila de prioridade implementada com heapq (min-heap).
    Menor valor de prioridade = maior urgência de execução.
    """

    def __init__(self):
        self._heap: list = []          # heap interno
        self._contador: int = 0        # desempate por ordem de inserção

    def inserir(self, processo: Processo) -> None:
        """Insere um processo na fila de prioridade."""
        # Tupla: (prioridade, contador_insercao, processo)
        # O contador garante ordem FIFO entre processos de mesma prioridade
        heapq.heappush(self._heap, (processo.prioridade, self._contador, processo))
        self._contador += 1

    def remover_maior_prioridade(self) -> Optional[Processo]:
        """Remove e retorna o processo de maior prioridade (menor valor)."""
        if self.esta_vazia():
            return None
        _, _, processo = heapq.heappop(self._heap)
        return processo

    def esta_vazia(self) -> bool:
        """Verifica se a fila está vazia."""
        return len(self._heap) == 0

    def tamanho(self) -> int:
        """Retorna o número de processos na fila."""
        return len(self._heap)

    def listar_processos(self) -> list:
        """Retorna lista ordenada por prioridade (sem remover)."""
        return [p for (_, _, p) in sorted(self._heap)]


# ============================================================
# ESCALONADOR
# ============================================================

class Escalonador:
    """
    Gerencia a adição e execução de processos usando fila de prioridade.
    """

    def __init__(self, callback_log=None, callback_atualizar=None):
        self.fila = FilaPrioridade()
        self.historico_adicao: list[Processo] = []
        self.historico_execucao: list[Processo] = []
        self.processo_atual: Optional[Processo] = None
        self.em_execucao: bool = False
        self._callback_log = callback_log
        self._callback_atualizar = callback_atualizar

    def adicionar_processo(self, processo: Processo) -> None:
        """Insere um processo na fila de prioridade e regista no histórico."""
        self.fila.inserir(processo)
        self.historico_adicao.append(processo)
        self._log(f"[+] Adicionado  → {processo.nome} "
                  f"(ID={processo.id} | Prioridade={processo.prioridade} "
                  f"| Tempo={processo.tempo_execucao}s)")
        self._atualizar()

    def executar_proximo_processo(self) -> Optional[Processo]:
        """
        Remove o processo de maior prioridade da fila e simula sua execução.
        Retorna o processo executado ou None se a fila estiver vazia.
        """
        if self.fila.esta_vazia():
            self._log("⚠ Fila vazia — nenhum processo para executar.")
            return None

        processo = self.fila.remover_maior_prioridade()
        processo.estado = "Executando"
        self.processo_atual = processo
        self._atualizar()

        self._log(f"\n▶ Executando   → {processo.nome} "
                  f"(ID={processo.id} | Prioridade={processo.prioridade} "
                  f"| Duração={processo.tempo_execucao}s)")

        # Simula execução (sleep proporcional ao tempo real)
        time.sleep(processo.tempo_execucao)

        processo.estado = "Concluído"
        self.processo_atual = None
        self.historico_execucao.append(processo)
        self._atualizar()

        self._log(f"✔ Concluído    → {processo.nome} "
                  f"(ID={processo.id})\n")
        return processo

    def executar_todos(self) -> None:
        """Executa todos os processos na fila por ordem de prioridade."""
        self.em_execucao = True
        self._log("\n══════════════════════════════════════")
        self._log("  INÍCIO DA SIMULAÇÃO DO ESCALONADOR")
        self._log("══════════════════════════════════════\n")

        while not self.fila.esta_vazia() and self.em_execucao:
            self.executar_proximo_processo()

        self.em_execucao = False
        self._log("\n══════════════════════════════════════")
        self._log("  SIMULAÇÃO CONCLUÍDA")
        self._log("══════════════════════════════════════")
        self._gerar_relatorio()
        self._atualizar()

    def parar(self) -> None:
        """Interrompe a execução contínua."""
        self.em_execucao = False

    def _log(self, mensagem: str) -> None:
        if self._callback_log:
            self._callback_log(mensagem)

    def _atualizar(self) -> None:
        if self._callback_atualizar:
            self._callback_atualizar()

    def _gerar_relatorio(self) -> None:
        """Imprime relatório final comparando ordem de adição vs execução."""
        self._log("\n──────────────────────────────────────")
        self._log("  RELATÓRIO FINAL")
        self._log("──────────────────────────────────────")
        self._log("\nOrdem de ADIÇÃO à fila:")
        for i, p in enumerate(self.historico_adicao, 1):
            self._log(f"  {i}. {p.nome} (Prioridade={p.prioridade})")

        self._log("\nOrdem de EXECUÇÃO (por prioridade):")
        for i, p in enumerate(self.historico_execucao, 1):
            self._log(f"  {i}. {p.nome} (Prioridade={p.prioridade})")

        self._log("\nConclusão: A fila de prioridade (min-heap) garantiu que")
        self._log("processos com menor valor de prioridade foram executados")
        self._log("primeiro, independentemente da ordem de inserção.")


# ============================================================
# INTERFACE GRÁFICA (TKINTER)
# ============================================================

class AplicacaoEscalonador(tk.Tk):
    """Janela principal da aplicação de simulação."""

    COR_BG        = "#1e1e2e"
    COR_PAINEL    = "#2a2a3e"
    COR_ACENTO    = "#7c3aed"
    COR_ACENTO2   = "#06b6d4"
    COR_TEXTO     = "#e2e8f0"
    COR_TEXTO2    = "#94a3b8"
    COR_VERDE     = "#22c55e"
    COR_AMARELO   = "#eab308"
    COR_VERMELHO  = "#ef4444"
    COR_BORDA     = "#3f3f5a"

    FONTE_TITULO  = ("Segoe UI", 18, "bold")
    FONTE_LABEL   = ("Segoe UI", 10)
    FONTE_BOLD    = ("Segoe UI", 10, "bold")
    FONTE_MONO    = ("Courier New", 10)

    def __init__(self):
        super().__init__()
        self._contador_id = 1
        self._thread_exec: Optional[threading.Thread] = None

        self.escalonador = Escalonador(
            callback_log=self._append_log,
            callback_atualizar=self._atualizar_ui
        )

        self._configurar_janela()
        self._construir_ui()
        self._carregar_processos_demo()

    # ── Configuração da janela ──────────────────────────────

    def _configurar_janela(self):
        self.title("Simulador de Escalonamento de Processos")
        self.geometry("1050x720")
        self.minsize(900, 620)
        self.configure(bg=self.COR_BG)
        self.resizable(True, True)

    # ── Construção da UI ────────────────────────────────────

    def _construir_ui(self):
        # ── Cabeçalho ──
        cab = tk.Frame(self, bg=self.COR_ACENTO, pady=12)
        cab.pack(fill="x")
        tk.Label(cab, text="⚙  Simulador de Escalonamento de Processos",
                 font=self.FONTE_TITULO, bg=self.COR_ACENTO,
                 fg="white").pack()
        tk.Label(cab, text="Fila de Prioridade com min-heap (heapq)",
                 font=("Segoe UI", 9), bg=self.COR_ACENTO,
                 fg="#c4b5fd").pack()

        # ── Corpo principal ──
        corpo = tk.Frame(self, bg=self.COR_BG)
        corpo.pack(fill="both", expand=True, padx=14, pady=10)
        corpo.columnconfigure(0, weight=1)
        corpo.columnconfigure(1, weight=2)
        corpo.rowconfigure(0, weight=1)

        # Coluna esquerda
        esq = tk.Frame(corpo, bg=self.COR_BG)
        esq.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._construir_painel_adicionar(esq)
        self._construir_painel_fila(esq)
        self._construir_painel_controles(esq)

        # Coluna direita
        dir_ = tk.Frame(corpo, bg=self.COR_BG)
        dir_.grid(row=0, column=1, sticky="nsew")
        self._construir_painel_log(dir_)
        self._construir_painel_historico(dir_)

    def _painel(self, pai, titulo: str) -> tk.Frame:
        """Cria um painel com borda e título padronizado."""
        frame = tk.Frame(pai, bg=self.COR_PAINEL,
                         highlightbackground=self.COR_BORDA,
                         highlightthickness=1)
        frame.pack(fill="x", pady=5)
        tk.Label(frame, text=titulo, font=self.FONTE_BOLD,
                 bg=self.COR_ACENTO, fg="white",
                 pady=5, padx=10, anchor="w").pack(fill="x")
        return frame

    # ── Painel: Adicionar Processo ──────────────────────────

    def _construir_painel_adicionar(self, pai):
        p = self._painel(pai, "➕  Adicionar Processo")
        body = tk.Frame(p, bg=self.COR_PAINEL, padx=10, pady=8)
        body.pack(fill="x")

        def campo(label, row):
            tk.Label(body, text=label, font=self.FONTE_LABEL,
                     bg=self.COR_PAINEL, fg=self.COR_TEXTO2,
                     anchor="w").grid(row=row, column=0, sticky="w", pady=2)
            e = tk.Entry(body, font=self.FONTE_LABEL,
                         bg="#3a3a55", fg=self.COR_TEXTO,
                         insertbackground=self.COR_TEXTO,
                         relief="flat", width=18)
            e.grid(row=row, column=1, padx=(8, 0), pady=2, sticky="ew")
            return e

        body.columnconfigure(1, weight=1)
        self._entry_nome      = campo("Nome do processo:", 0)
        self._entry_prioridade = campo("Prioridade (1–10):", 1)
        self._entry_tempo     = campo("Tempo execução (s):", 2)

        tk.Button(body, text="Adicionar à Fila",
                  font=self.FONTE_BOLD, bg=self.COR_ACENTO, fg="white",
                  relief="flat", cursor="hand2", pady=6,
                  command=self._adicionar_processo
                  ).grid(row=3, column=0, columnspan=2,
                         sticky="ew", pady=(10, 2))

        tk.Button(body, text="🎲  Processo Aleatório",
                  font=self.FONTE_LABEL, bg="#374151", fg=self.COR_TEXTO,
                  relief="flat", cursor="hand2",
                  command=self._adicionar_aleatorio
                  ).grid(row=4, column=0, columnspan=2,
                         sticky="ew", pady=2)

    # ── Painel: Fila Atual ──────────────────────────────────

    def _construir_painel_fila(self, pai):
        p = self._painel(pai, "📋  Fila de Prioridade (estado atual)")
        frame = tk.Frame(p, bg=self.COR_PAINEL, padx=6, pady=6)
        frame.pack(fill="both", expand=True)

        cols = ("Pos", "ID", "Nome", "Prior.", "Tempo", "Estado")
        self._tree_fila = ttk.Treeview(frame, columns=cols,
                                        show="headings", height=7)
        for c, w in zip(cols, [35, 35, 130, 55, 55, 80]):
            self._tree_fila.heading(c, text=c)
            self._tree_fila.column(c, width=w, anchor="center")

        self._aplicar_estilo_treeview()
        sb = ttk.Scrollbar(frame, orient="vertical",
                            command=self._tree_fila.yview)
        self._tree_fila.configure(yscrollcommand=sb.set)
        self._tree_fila.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    # ── Painel: Controles ───────────────────────────────────

    def _construir_painel_controles(self, pai):
        p = self._painel(pai, "🎮  Controles")
        body = tk.Frame(p, bg=self.COR_PAINEL, padx=10, pady=8)
        body.pack(fill="x")

        self._btn_exec_proximo = tk.Button(
            body, text="▶  Executar Próximo",
            font=self.FONTE_BOLD, bg=self.COR_VERDE, fg="white",
            relief="flat", cursor="hand2", pady=6,
            command=self._executar_proximo)
        self._btn_exec_proximo.pack(fill="x", pady=2)

        self._btn_exec_todos = tk.Button(
            body, text="⏩  Executar Todos",
            font=self.FONTE_BOLD, bg=self.COR_ACENTO2, fg="white",
            relief="flat", cursor="hand2", pady=6,
            command=self._executar_todos)
        self._btn_exec_todos.pack(fill="x", pady=2)

        self._btn_parar = tk.Button(
            body, text="⏹  Parar",
            font=self.FONTE_BOLD, bg=self.COR_VERMELHO, fg="white",
            relief="flat", cursor="hand2", pady=6, state="disabled",
            command=self._parar)
        self._btn_parar.pack(fill="x", pady=2)

        tk.Button(body, text="🗑  Limpar Tudo",
                  font=self.FONTE_LABEL, bg="#374151", fg=self.COR_TEXTO,
                  relief="flat", cursor="hand2",
                  command=self._limpar_tudo
                  ).pack(fill="x", pady=(8, 2))

        # Indicador de processo em execução
        self._lbl_status = tk.Label(
            body, text="⬤  Aguardando processos",
            font=("Segoe UI", 9), bg=self.COR_PAINEL,
            fg=self.COR_TEXTO2, wraplength=200)
        self._lbl_status.pack(pady=(8, 0))

    # ── Painel: Log ─────────────────────────────────────────

    def _construir_painel_log(self, pai):
        p = self._painel(pai, "📜  Log de Execução")
        frame = tk.Frame(p, bg=self.COR_PAINEL, padx=6, pady=6)
        frame.pack(fill="both", expand=True)

        self._txt_log = tk.Text(
            frame, font=self.FONTE_MONO, bg="#111827",
            fg=self.COR_TEXTO, insertbackground=self.COR_TEXTO,
            relief="flat", state="disabled", height=18, wrap="word")
        sb = ttk.Scrollbar(frame, orient="vertical",
                            command=self._txt_log.yview)
        self._txt_log.configure(yscrollcommand=sb.set)
        self._txt_log.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Tags de cor
        self._txt_log.tag_configure("verde",   foreground=self.COR_VERDE)
        self._txt_log.tag_configure("amarelo", foreground=self.COR_AMARELO)
        self._txt_log.tag_configure("ciano",   foreground=self.COR_ACENTO2)
        self._txt_log.tag_configure("roxo",    foreground="#a78bfa")
        self._txt_log.tag_configure("cinza",   foreground=self.COR_TEXTO2)

    # ── Painel: Histórico ───────────────────────────────────

    def _construir_painel_historico(self, pai):
        p = self._painel(pai, "✅  Histórico de Execução")
        frame = tk.Frame(p, bg=self.COR_PAINEL, padx=6, pady=6)
        frame.pack(fill="both", expand=True)

        cols = ("Ordem", "ID", "Nome", "Prioridade", "Tempo (s)")
        self._tree_hist = ttk.Treeview(frame, columns=cols,
                                        show="headings", height=6)
        for c, w in zip(cols, [50, 40, 160, 80, 70]):
            self._tree_hist.heading(c, text=c)
            self._tree_hist.column(c, width=w, anchor="center")

        sb = ttk.Scrollbar(frame, orient="vertical",
                            command=self._tree_hist.yview)
        self._tree_hist.configure(yscrollcommand=sb.set)
        self._tree_hist.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    # ── Estilos ttk ─────────────────────────────────────────

    def _aplicar_estilo_treeview(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Treeview",
                          background=self.COR_PAINEL,
                          foreground=self.COR_TEXTO,
                          fieldbackground=self.COR_PAINEL,
                          rowheight=24,
                          font=("Segoe UI", 9))
        estilo.configure("Treeview.Heading",
                          background=self.COR_BORDA,
                          foreground=self.COR_TEXTO,
                          font=("Segoe UI", 9, "bold"))
        estilo.map("Treeview", background=[("selected", self.COR_ACENTO)])

    # ── Callbacks dos botões ─────────────────────────────────

    def _adicionar_processo(self):
        nome = self._entry_nome.get().strip()
        try:
            prior = int(self._entry_prioridade.get())
            tempo = float(self._entry_tempo.get())
        except ValueError:
            messagebox.showerror("Erro", "Prioridade deve ser inteiro e "
                                 "tempo deve ser número.")
            return

        if not nome:
            messagebox.showerror("Erro", "Informe o nome do processo.")
            return
        if prior < 1 or prior > 10:
            messagebox.showwarning("Aviso", "Prioridade recomendada: 1–10.")
        if tempo <= 0:
            messagebox.showerror("Erro", "Tempo de execução deve ser > 0.")
            return

        p = Processo(id=self._contador_id, prioridade=prior,
                     tempo_execucao=tempo, nome=nome)
        self._contador_id += 1
        self.escalonador.adicionar_processo(p)

        # Limpar campos
        for e in (self._entry_nome, self._entry_prioridade, self._entry_tempo):
            e.delete(0, tk.END)

    def _adicionar_aleatorio(self):
        nomes = ["Sistema", "Browser", "Editor", "Terminal", "Backup",
                 "Antivírus", "Update", "Player", "Compilador", "DB"]
        nome = random.choice(nomes) + f"-{self._contador_id}"
        prior = random.randint(1, 10)
        tempo = round(random.uniform(0.5, 3.0), 1)
        p = Processo(id=self._contador_id, prioridade=prior,
                     tempo_execucao=tempo, nome=nome)
        self._contador_id += 1
        self.escalonador.adicionar_processo(p)

    def _executar_proximo(self):
        if self.escalonador.fila.esta_vazia():
            messagebox.showinfo("Info", "Fila vazia.")
            return
        self._thread_exec = threading.Thread(
            target=self.escalonador.executar_proximo_processo, daemon=True)
        self._thread_exec.start()
        self._set_controles(executando=True)
        self.after(100, self._verificar_thread)

    def _executar_todos(self):
        if self.escalonador.fila.esta_vazia():
            messagebox.showinfo("Info", "Fila vazia.")
            return
        self._thread_exec = threading.Thread(
            target=self.escalonador.executar_todos, daemon=True)
        self._thread_exec.start()
        self._set_controles(executando=True)
        self.after(100, self._verificar_thread)

    def _parar(self):
        self.escalonador.parar()

    def _limpar_tudo(self):
        self.escalonador = Escalonador(
            callback_log=self._append_log,
            callback_atualizar=self._atualizar_ui
        )
        self._tree_hist.delete(*self._tree_hist.get_children())
        self._txt_log.configure(state="normal")
        self._txt_log.delete("1.0", tk.END)
        self._txt_log.configure(state="disabled")
        self._atualizar_ui()
        self._append_log("🗑  Tudo limpo. Pronto para nova simulação.")

    # ── Utilitários de UI ────────────────────────────────────

    def _set_controles(self, executando: bool):
        estado_normal  = "disabled" if executando else "normal"
        estado_parar   = "normal"   if executando else "disabled"
        self._btn_exec_proximo.configure(state=estado_normal)
        self._btn_exec_todos.configure(state=estado_normal)
        self._btn_parar.configure(state=estado_parar)

    def _verificar_thread(self):
        """Polling para saber se a thread terminou."""
        if self._thread_exec and self._thread_exec.is_alive():
            self.after(200, self._verificar_thread)
        else:
            self._set_controles(executando=False)
            self._atualizar_ui()

    def _append_log(self, mensagem: str):
        """Adiciona linha ao log (thread-safe via after)."""
        def _fazer():
            self._txt_log.configure(state="normal")
            # Escolhe tag de cor com base no conteúdo
            if mensagem.startswith("[+]"):
                tag = "ciano"
            elif mensagem.startswith("▶"):
                tag = "amarelo"
            elif mensagem.startswith("✔"):
                tag = "verde"
            elif mensagem.startswith("⚠"):
                tag = "roxo"
            elif mensagem.startswith("══") or mensagem.startswith("──"):
                tag = "roxo"
            else:
                tag = "cinza"
            self._txt_log.insert(tk.END, mensagem + "\n", tag)
            self._txt_log.see(tk.END)
            self._txt_log.configure(state="disabled")
        self.after(0, _fazer)

    def _atualizar_ui(self):
        """Atualiza as tabelas e indicador de status (thread-safe)."""
        def _fazer():
            self._atualizar_tabela_fila()
            self._atualizar_tabela_historico()
            self._atualizar_status()
        self.after(0, _fazer)

    def _atualizar_tabela_fila(self):
        self._tree_fila.delete(*self._tree_fila.get_children())
        processos = self.escalonador.fila.listar_processos()
        for pos, p in enumerate(processos, 1):
            tag = "exec" if p == self.escalonador.processo_atual else ""
            self._tree_fila.insert("", tk.END, tags=(tag,),
                                    values=(pos, p.id, p.nome,
                                            p.prioridade, p.tempo_execucao,
                                            p.estado))
        self._tree_fila.tag_configure("exec", background="#3b1f6e")

    def _atualizar_tabela_historico(self):
        self._tree_hist.delete(*self._tree_hist.get_children())
        for ordem, p in enumerate(self.escalonador.historico_execucao, 1):
            self._tree_hist.insert("", tk.END,
                                    values=(ordem, p.id, p.nome,
                                            p.prioridade, p.tempo_execucao))

    def _atualizar_status(self):
        pa = self.escalonador.processo_atual
        if pa:
            self._lbl_status.configure(
                text=f"⬤  Executando: {pa.nome} (Prior. {pa.prioridade})",
                fg=self.COR_AMARELO)
        elif self.escalonador.fila.esta_vazia():
            total = len(self.escalonador.historico_execucao)
            msg = (f"✔  Todos os {total} processos concluídos"
                   if total else "⬤  Fila vazia")
            self._lbl_status.configure(text=msg, fg=self.COR_VERDE)
        else:
            n = self.escalonador.fila.tamanho()
            self._lbl_status.configure(
                text=f"⬤  {n} processo(s) aguardando",
                fg=self.COR_TEXTO2)

    # ── Demo inicial ─────────────────────────────────────────

    def _carregar_processos_demo(self):
        """Pré-carrega processos de demonstração."""
        demos = [
            ("Sistema-Init",   1, 0.8),
            ("Antivírus",      3, 1.5),
            ("Browser",        5, 1.0),
            ("Backup-Auto",    7, 2.0),
            ("Media-Player",   8, 0.6),
            ("Update-Mgr",     2, 1.2),
        ]
        self._append_log("═══ Processos de demonstração carregados ═══")
        for nome, prior, tempo in demos:
            p = Processo(id=self._contador_id, prioridade=prior,
                         tempo_execucao=tempo, nome=nome)
            self._contador_id += 1
            self.escalonador.adicionar_processo(p)


# ============================================================
# PONTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    app = AplicacaoEscalonador()
    app.mainloop()
