#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Rotinas Diárias
Aplicativo para cadastro e gerenciamento de atividades diárias com filtro por dia
Autor: Sistema de IA
Data: 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime, date
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class GerenciadorRotinas:
    """Classe principal para gerenciar rotinas diárias"""
    
    def __init__(self):
        """Inicializa o gerenciador de rotinas"""
        self.arquivo_csv = "rotinas_diarias.csv"
        self.atividades = []
        self.data_filtro = date.today().strftime('%Y-%m-%d')  # sempre inicia no dia atual
        self.root = tk.Tk()
        self.setup_interface()
        self.carregar_dados()
        self.atualizar_lista()
        
    def setup_interface(self):
        """Configura a interface gráfica principal"""
        self.root.title("Gerenciador de Rotinas Diárias")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        style = ttk.Style()
        style.theme_use('clam')
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        titulo = ttk.Label(main_frame, text="Gerenciador de Rotinas Diárias", 
                          font=('Arial', 16, 'bold'))
        titulo.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Seletor de data
        ttk.Label(main_frame, text="Data (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W)
        self.entrada_data = ttk.Entry(main_frame, width=12)
        self.entrada_data.insert(0, self.data_filtro)
        self.entrada_data.grid(row=1, column=1, sticky=tk.W, padx=(5, 20))
        
        ttk.Button(main_frame, text="Filtrar", 
                  command=self.aplicar_filtro_data).grid(row=1, column=2, sticky=tk.W)
        
        # Frame de entrada de atividade
        self.setup_entrada_frame(main_frame)
        
        # Frame da lista
        self.setup_lista_frame(main_frame)
        
        # Frame dos botões
        self.setup_botoes_frame(main_frame)
        
        # Frame das estatísticas
        self.setup_estatisticas_frame(main_frame)
        
        # Configurar redimensionamento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
    
    def setup_entrada_frame(self, parent):
        entrada_frame = ttk.LabelFrame(parent, text="Nova Atividade", padding="10")
        entrada_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(entrada_frame, text="Descrição:").grid(row=0, column=0, sticky=tk.W)
        self.entrada_atividade = ttk.Entry(entrada_frame, width=50)
        self.entrada_atividade.grid(row=0, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
        
        btn_adicionar = ttk.Button(entrada_frame, text="Adicionar", 
                                 command=self.adicionar_atividade)
        btn_adicionar.grid(row=0, column=2, padx=(10, 0))
        
        self.entrada_atividade.bind('<Return>', lambda e: self.adicionar_atividade())
        entrada_frame.columnconfigure(1, weight=1)
    
    def setup_lista_frame(self, parent):
        lista_frame = ttk.LabelFrame(parent, text="Atividades", padding="10")
        lista_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        colunas = ('ID', 'Descrição', 'Data', 'Status')
        self.tree = ttk.Treeview(lista_frame, columns=colunas, show='headings', height=12)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Descrição', text='Descrição')
        self.tree.heading('Data', text='Data')
        self.tree.heading('Status', text='Status')
        
        self.tree.column('ID', width=50, anchor=tk.CENTER)
        self.tree.column('Descrição', width=300, anchor=tk.W)
        self.tree.column('Data', width=100, anchor=tk.CENTER)
        self.tree.column('Status', width=100, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(lista_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        lista_frame.columnconfigure(0, weight=1)
        lista_frame.rowconfigure(0, weight=1)
    
    def setup_botoes_frame(self, parent):
        botoes_frame = ttk.Frame(parent)
        botoes_frame.grid(row=4, column=0, columnspan=4, pady=(0, 10))
        
        ttk.Button(botoes_frame, text="Marcar Concluída", 
                  command=self.marcar_concluida).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(botoes_frame, text="Excluir", 
                  command=self.excluir_atividade).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(botoes_frame, text="Estatísticas", 
                  command=self.mostrar_estatisticas).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(botoes_frame, text="Gráfico", 
                  command=self.mostrar_grafico).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(botoes_frame, text="Atualizar", 
                  command=self.atualizar_lista).pack(side=tk.LEFT, padx=5)
    
    def setup_estatisticas_frame(self, parent):
        self.stats_frame = ttk.LabelFrame(parent, text="Estatísticas do Dia", padding="10")
        self.stats_frame.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E))
        
        self.label_stats = ttk.Label(self.stats_frame, text="", font=('Arial', 10))
        self.label_stats.pack()
    
    def aplicar_filtro_data(self):
        """Aplica o filtro de data digitada"""
        data_digitada = self.entrada_data.get().strip()
        try:
            datetime.strptime(data_digitada, '%Y-%m-%d')
            self.data_filtro = data_digitada
            self.atualizar_lista()
        except ValueError:
            messagebox.showerror("Erro", "Data inválida. Use o formato YYYY-MM-DD.")
    
    def filtrar_por_data(self, data=None):
        """Retorna as atividades do dia especificado (ou do dia atual)"""
        if data is None:
            data = self.data_filtro
        return [a for a in self.atividades if a['data'] == data]
    
    def adicionar_atividade(self):
        descricao = self.entrada_atividade.get().strip()
        if not descricao:
            messagebox.showwarning("Aviso", "Digite uma descrição para a atividade.")
            return
        
        nova_atividade = {
            'id': len(self.atividades) + 1,
            'descricao': descricao,
            'data': self.data_filtro,
            'status': 'Pendente',
            'data_conclusao': ''
        }
        
        self.atividades.append(nova_atividade)
        self.salvar_dados()
        self.atualizar_lista()
        self.atualizar_estatisticas()
        self.entrada_atividade.delete(0, tk.END)
    
    def marcar_concluida(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma atividade.")
            return
        
        item = self.tree.item(selecionado[0])
        atividade_id = int(item['values'][0])
        
        for atividade in self.atividades:
            if atividade['id'] == atividade_id:
                if atividade['status'] == 'Concluída':
                    return
                atividade['status'] = 'Concluída'
                atividade['data_conclusao'] = date.today().strftime('%Y-%m-%d')
                break
        
        self.salvar_dados()
        self.atualizar_lista()
        self.atualizar_estatisticas()
    
    def excluir_atividade(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma atividade para excluir.")
            return
        
        item = self.tree.item(selecionado[0])
        atividade_id = int(item['values'][0])
        
        self.atividades = [a for a in self.atividades if a['id'] != atividade_id]
        self.salvar_dados()
        self.atualizar_lista()
        self.atualizar_estatisticas()
    
    def atualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        atividades_dia = self.filtrar_por_data()
        
        for atividade in atividades_dia:
            status_emoji = "✅" if atividade['status'] == 'Concluída' else "⏳"
            status_text = f"{status_emoji} {atividade['status']}"
            
            self.tree.insert('', tk.END, values=(
                atividade['id'],
                atividade['descricao'],
                atividade['data'],
                status_text
            ))
        
        self.atualizar_estatisticas()
    
    def atualizar_estatisticas(self):
        atividades_dia = self.filtrar_por_data()
        total = len(atividades_dia)
        concluidas = len([a for a in atividades_dia if a['status'] == 'Concluída'])
        pendentes = total - concluidas
        percentual = (concluidas / total * 100) if total > 0 else 0
        
        stats_text = f"Total: {total} | Concluídas: {concluidas} | Pendentes: {pendentes} | Conclusão: {percentual:.1f}%"
        self.label_stats.config(text=stats_text)
    
    def mostrar_estatisticas(self):
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Estatísticas Detalhadas")
        stats_window.geometry("500x400")
        
        main_frame = ttk.Frame(stats_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Estatísticas Detalhadas", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        historico = defaultdict(lambda: {'total': 0, 'concluidas': 0})
        for atividade in self.atividades:
            data = atividade['data']
            historico[data]['total'] += 1
            if atividade['status'] == 'Concluída':
                historico[data]['concluidas'] += 1
        
        stats_text = ""
        for data in sorted(historico.keys(), reverse=True):
            info = historico[data]
            perc_dia = (info['concluidas'] / info['total'] * 100) if info['total'] > 0 else 0
            stats_text += f"{data}: {info['concluidas']}/{info['total']} ({perc_dia:.1f}%)\n"
        
        text_widget = tk.Text(main_frame, wrap=tk.WORD, font=('Courier', 10))
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, stats_text)
        text_widget.config(state=tk.DISABLED)
    
    def mostrar_grafico(self):
        if not self.atividades:
            messagebox.showinfo("Info", "Não há atividades.")
            return
        
        graph_window = tk.Toplevel(self.root)
        graph_window.title("Gráfico de Atividades")
        graph_window.geometry("800x600")
        
        total = len(self.atividades)
        concluidas = len([a for a in self.atividades if a['status'] == 'Concluída'])
        pendentes = total - concluidas
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        labels = ['Concluídas', 'Pendentes']
        sizes = [concluidas, pendentes]
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Status Geral')
        
        historico = defaultdict(lambda: {'total': 0, 'concluidas': 0})
        for atividade in self.atividades:
            data = atividade['data']
            historico[data]['total'] += 1
            if atividade['status'] == 'Concluída':
                historico[data]['concluidas'] += 1
        
        datas = sorted(historico.keys())[-7:]
        totais = [historico[data]['total'] for data in datas]
        concluidas_dia = [historico[data]['concluidas'] for data in datas]
        
        x = range(len(datas))
        ax2.bar(x, totais, label='Total', alpha=0.6)
        ax2.bar(x, concluidas_dia, label='Concluídas', alpha=0.8)
        ax2.set_xticks(x)
        ax2.set_xticklabels(datas, rotation=45)
        ax2.legend()
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def salvar_dados(self):
        try:
            with open(self.arquivo_csv, 'w', newline='', encoding='utf-8') as arquivo:
                fieldnames = ['id', 'descricao', 'data', 'status', 'data_conclusao']
                writer = csv.DictWriter(arquivo, fieldnames=fieldnames)
                writer.writeheader()
                for atividade in self.atividades:
                    writer.writerow(atividade)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar dados: {str(e)}")
    
    def carregar_dados(self):
        if not os.path.exists(self.arquivo_csv):
            return
        try:
            with open(self.arquivo_csv, 'r', newline='', encoding='utf-8') as arquivo:
                reader = csv.DictReader(arquivo)
                self.atividades = []
                for row in reader:
                    atividade = {
                        'id': int(row['id']),
                        'descricao': row['descricao'],
                        'data': row['data'],
                        'status': row['status'],
                        'data_conclusao': row['data_conclusao']
                    }
                    self.atividades.append(atividade)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")
    
    def executar(self):
        self.root.mainloop()


def main():
    app = GerenciadorRotinas()
    app.executar()


if __name__ == "__main__":
    main()
