import math
import tkinter as tk
from tkinter import messagebox, ttk
from collections import deque

class SpēlesKoks:
    def __init__(self, skaitlis, cilvēka_punkti=0, datora_punkti=0, banka=0, gājiens=None, vecāks=None, ir_faktiskais=False):
        self.skaitlis = skaitlis
        self.cilvēka_punkti = cilvēka_punkti
        self.datora_punkti = datora_punkti
        self.banka = banka
        self.gājiens = gājiens
        self.vecāks = vecāks
        self.bērni = []
        self.heiristika = 0
        self.dziļums = 0
        self.ir_faktiskais = ir_faktiskais
        self.spēlētāja_vārds = "Cilvēks" if vecāks and vecāks.spēlētāja_vārds == "Dators" else "Dators" if vecāks else "Cilvēks"
        
    def pievienot_bērnu(self, bērns):
        self.bērni.append(bērns)
        bērns.dziļums = self.dziļums + 1
        
    def aprēķināt_heiristiku(self):
        if self.skaitlis >= 5000:
            # Pēdējais gājiens saņem banku
            if self.spēlētāja_vārds == "Cilvēks":
                cilvēka_punkti = self.cilvēka_punkti + self.banka
                datora_punkti = self.datora_punkti
            else:
                cilvēka_punkti = self.cilvēka_punkti
                datora_punkti = self.datora_punkti + self.banka
            
            if cilvēka_punkti > datora_punkti:
                return -1000  # Cilvēks uzvar
            elif datora_punkti > cilvēka_punkti:
                return 1000   # Dators uzvar
            else:
                return 0      # Neizšķirts
        
        punktu_starpība = self.datora_punkti - self.cilvēka_punkti
        tuvuma_bonuss = self.skaitlis / 1000
        paritātes_sods = -2 if self.skaitlis % 2 == 0 else 2
        
        self.heiristika = punktu_starpība * 10 + tuvuma_bonuss + paritātes_sods
        return self.heiristika

class Spēle:
    def __init__(self, sākuma_skaitlis, algoritms):
        self.pārejams_skaitlis = sākuma_skaitlis
        self.cilvēka_punkti = 0
        self.datora_punkti = 0
        self.banka = 0
        self.gājiena_nr = 0
        self.MAX_SKATĪŠANAS_DZIĻUMS = 3
        self.algoritms = algoritms
        self.spēles_koks = SpēlesKoks(sākuma_skaitlis, ir_faktiskais=True)
        self.pašreizējais_mezgls = self.spēles_koks
        self.visi_mezgli = [self.spēles_koks]
    
    def veikt_gājienu(self, reizinātājs):
        jauns_skaitlis = self.pārejams_skaitlis * reizinātājs
        jauna_banka = self.banka
        jauni_cilvēka_punkti = self.cilvēka_punkti
        jauni_datora_punkti = self.datora_punkti
        
        # Punktu aprēķins
        if jauns_skaitlis % 2 == 0:
            punktu_izmaiņa = -1
        else:
            punktu_izmaiņa = 1
        
        if self.gājiena_nr % 2 == 0:  # Cilvēka gājiens
            jauni_cilvēka_punkti += punktu_izmaiņa
        else:  # Datora gājiens
            jauni_datora_punkti += punktu_izmaiņa
        
        # Bankas punkti
        if jauns_skaitlis % 10 in [0, 5]:
            jauna_banka += 1
        
        # Meklējam vai izveidojam jaunu mezglu
        jauns_mezgls = None
        for bērns in self.pašreizējais_mezgls.bērni:
            if bērns.skaitlis == jauns_skaitlis and bērns.gājiens == reizinātājs:
                jauns_mezgls = bērns
                break
        
        if jauns_mezgls is None:
            jauns_mezgls = SpēlesKoks(
                jauns_skaitlis,
                jauni_cilvēka_punkti,
                jauni_datora_punkti,
                jauna_banka,
                reizinātājs,
                self.pašreizējais_mezgls,
                ir_faktiskais=True
            )
            self.pašreizējais_mezgls.pievienot_bērnu(jauns_mezgls)
            self.visi_mezgli.append(jauns_mezgls)
        
        self.pašreizējais_mezgls = jauns_mezgls
        self.pārejams_skaitlis = jauns_skaitlis
        self.cilvēka_punkti = jauni_cilvēka_punkti
        self.datora_punkti = jauni_datora_punkti
        self.banka = jauna_banka
        self.gājiena_nr += 1
        
        # Pēc katra gājiena ģenerējam pilnu koku
        self.ģenerēt_pilno_koku()
    
    def ģenerēt_pilno_koku(self):
        # Ģenerējam visus iespējamos variantus no pašreizējā stāvokļa
        if self.pašreizējais_mezgls.bērni and all(b.ir_faktiskais for b in self.pašreizējais_mezgls.bērni):
            return  # Jau ir ģenerēti
            
        for reizinātājs in self.iespējamie_gājieni():
            jauns_skaitlis = self.pašreizējais_mezgls.skaitlis * reizinātājs
            jauna_banka = self.pašreizējais_mezgls.banka
            jauni_cilvēka_punkti = self.pašreizējais_mezgls.cilvēka_punkti
            jauni_datora_punkti = self.pašreizējais_mezgls.datora_punkti
            
            if jauns_skaitlis % 2 == 0:
                punktu_izmaiņa = -1
            else:
                punktu_izmaiņa = 1
            
            if self.gājiena_nr % 2 == 0:  # Nākamais gājiens būs datora
                jauni_datora_punkti += punktu_izmaiņa
            else:  # Nākamais gājiens būs cilvēka
                jauni_cilvēka_punkti += punktu_izmaiņa
            
            if jauns_skaitlis % 10 in [0, 5]:
                jauna_banka += 1
            
            # Pārbaudam, vai šāds mezgls jau eksistē
            mezgls_eksistē = False
            for bērns in self.pašreizējais_mezgls.bērni:
                if bērns.skaitlis == jauns_skaitlis and bērns.gājiens == reizinātājs:
                    mezgls_eksistē = True
                    break
            
            if not mezgls_eksistē:
                jauns_mezgls = SpēlesKoks(
                    jauns_skaitlis,
                    jauni_cilvēka_punkti,
                    jauni_datora_punkti,
                    jauna_banka,
                    reizinātājs,
                    self.pašreizējais_mezgls,
                    ir_faktiskais=False  # Šis ir tikai iespējamais variants
                )
                jauns_mezgls.aprēķināt_heiristiku()
                self.pašreizējais_mezgls.pievienot_bērnu(jauns_mezgls)
                self.visi_mezgli.append(jauns_mezgls)
    
    def spēle_beigusies(self):
        return self.pārejams_skaitlis >= 5000
    
    def noteikt_uzvarētāju(self):
        if self.gājiena_nr % 2 == 0:  # Pēdējais gājiens bija cilvēka
            self.cilvēka_punkti += self.banka
        else:  # Pēdējais gājiens bija datora
            self.datora_punkti += self.banka
        
        if self.cilvēka_punkti > self.datora_punkti:
            return "Cilvēks"
        elif self.datora_punkti > self.cilvēka_punkti:
            return "Dators"
        else:
            return "Neizšķirts"
    
    def iespējamie_gājieni(self):
        return [2, 3, 4]
    
    def kopija(self):
        jauna_spēle = Spēle(self.pārejams_skaitlis, self.algoritms)
        jauna_spēle.cilvēka_punkti = self.cilvēka_punkti
        jauna_spēle.datora_punkti = self.datora_punkti
        jauna_spēle.banka = self.banka
        jauna_spēle.gājiena_nr = self.gājiena_nr
        return jauna_spēle
    
    def heiristiskā_vērtējuma_funkcija(self):
        if self.spēle_beigusies():
            uzvarētājs = self.noteikt_uzvarētāju()
            if uzvarētājs == "Dators":
                return 1000
            elif uzvarētājs == "Cilvēks":
                return -1000
            else:
                return 0
        
        punktu_starpība = self.datora_punkti - self.cilvēka_punkti
        tuvuma_bonuss = self.pārejams_skaitlis / 1000
        paritātes_sods = -2 if self.pārejams_skaitlis % 2 == 0 else 2
        
        return punktu_starpība * 10 + tuvuma_bonuss + paritātes_sods
    
    def minimaks(self, dziļums, maksimizē):
        if dziļums == 0 or self.spēle_beigusies():
            return self.heiristiskā_vērtējuma_funkcija(), None
        
        labākais_gājiens = None
        
        if maksimizē:
            max_vērtējums = -math.inf
            for gājiens in self.iespējamie_gājieni():
                spēles_kopija = self.kopija()
                spēles_kopija.veikt_gājienu(gājiens)
                vērtējums, _ = spēles_kopija.minimaks(dziļums-1, False)
                
                if vērtējums > max_vērtējums:
                    max_vērtējums = vērtējums
                    labākais_gājiens = gājiens
            
            return max_vērtējums, labākais_gājiens
        else:
            min_vērtējums = math.inf
            for gājiens in self.iespējamie_gājieni():
                spēles_kopija = self.kopija()
                spēles_kopija.veikt_gājienu(gājiens)
                vērtējums, _ = spēles_kopija.minimaks(dziļums-1, True)
                
                if vērtējums < min_vērtējums:
                    min_vērtējums = vērtējums
                    labākais_gājiens = gājiens
            
            return min_vērtējums, labākais_gājiens
    
    def alfa_beta(self, dziļums, alpha, beta, maksimizē):
        if dziļums == 0 or self.spēle_beigusies():
            return self.heiristiskā_vērtējuma_funkcija(), None
        
        labākais_gājiens = None
        
        if maksimizē:
            max_vērtējums = -math.inf
            for gājiens in self.iespējamie_gājieni():
                spēles_kopija = self.kopija()
                spēles_kopija.veikt_gājienu(gājiens)
                vērtējums, _ = spēles_kopija.alfa_beta(dziļums-1, alpha, beta, False)
                
                if vērtējums > max_vērtējums:
                    max_vērtējums = vērtējums
                    labākais_gājiens = gājiens
                
                alpha = max(alpha, vērtējums)
                if beta <= alpha:
                    break
            
            return max_vērtējums, labākais_gājiens
        else:
            min_vērtējums = math.inf
            for gājiens in self.iespējamie_gājieni():
                spēles_kopija = self.kopija()
                spēles_kopija.veikt_gājienu(gājiens)
                vērtējums, _ = spēles_kopija.alfa_beta(dziļums-1, alpha, beta, True)
                
                if vērtējums < min_vērtējums:
                    min_vērtējums = vērtējums
                    labākais_gājiens = gājiens
                
                beta = min(beta, vērtējums)
                if beta <= alpha:
                    break
            
            return min_vērtējums, labākais_gājiens
    
    def datora_gājiens(self):
        if self.algoritms == "Minimax":
            _, labākais_gājiens = self.minimaks(self.MAX_SKATĪŠANAS_DZIĻUMS, True)
        else:  # Alfa-beta
            _, labākais_gājiens = self.alfa_beta(self.MAX_SKATĪŠANAS_DZIĻUMS, -math.inf, math.inf, True)
        return labākais_gājiens

class SpēlesAplikācija(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Reizinātāju sacensības ar pilno koku")
        self.geometry("1000x800")
        self.resizable(True, True)
        
        self.sākuma_skaitlis = None
        self.spēle = None
        self.algoritms = None
        
        # Stili
        self.style = {
            "title_font": ("Arial", 20, "bold"),
            "subtitle_font": ("Arial", 14),
            "normal_font": ("Arial", 12),
            "button_font": ("Arial", 12),
            "info_font": ("Arial", 12, "italic"),
            "bg_color": "#f0f0f0",
            "button_color": "#e1e1e1",
            "highlight_color": "#d4e6f1",
            "text_color": "#333333"
        }
        
        self.configure(bg=self.style["bg_color"])
        self.izveidot_sākuma_ekrānu()
    
    def izveidot_sākuma_ekrānu(self):
        self.clear_frame()
        
        title_frame = tk.Frame(self, bg=self.style["bg_color"])
        title_frame.pack(pady=20)
        
        tk.Label(title_frame, text="Reizinātāju sacensības", 
                font=self.style["title_font"], bg=self.style["bg_color"], fg=self.style["text_color"]).pack()
        
        noteikumi_frame = tk.Frame(self, bg=self.style["bg_color"])
        noteikumi_frame.pack(pady=10)
        
        tk.Label(noteikumi_frame, text="Spēles noteikumi:", 
                font=self.style["subtitle_font"], bg=self.style["bg_color"], fg=self.style["text_color"]).pack()
        
        noteikumi = """- Sākumā izvēlies skaitli no 25 līdz 40
- Pēc kārtas veicam gājienus, reizinot skaitli ar 2, 3 vai 4
- Pāra rezultāts: -1 punkts
- Nepāra rezultāts: +1 punkts
- Ja skaitlis beidzas ar 0 vai 5: +1 punkts bankai
- Spēle beidzas, kad skaitlis ≥ 5000
- Pēdējais spēlētājs saņem bankas punktus
- Uzvar tas, kam vairāk punktu"""
        
        tk.Label(noteikumi_frame, text=noteikumi, justify=tk.LEFT, 
                font=self.style["normal_font"], bg=self.style["bg_color"], fg=self.style["text_color"]).pack(pady=10)
        
        input_frame = tk.Frame(self, bg=self.style["bg_color"])
        input_frame.pack(pady=20)
        
        tk.Label(input_frame, text="Ievadiet sākuma skaitli (25-40):", 
                font=self.style["normal_font"], bg=self.style["bg_color"], fg=self.style["text_color"]).pack()
        
        self.skaitlis_entry = tk.Entry(input_frame, font=self.style["normal_font"], width=10)
        self.skaitlis_entry.pack(pady=5)
        
        # Algoritma izvēle
        algo_frame = tk.Frame(self, bg=self.style["bg_color"])
        algo_frame.pack(pady=10)
        
        tk.Label(algo_frame, text="Izvēlieties datora algoritmu:", 
                font=self.style["normal_font"], bg=self.style["bg_color"]).pack()
        
        self.algo_var = tk.StringVar(value="Alfa-beta")
        
        tk.Radiobutton(algo_frame, text="Alfa-beta", variable=self.algo_var, value="Alfa-beta",
                      font=self.style["normal_font"], bg=self.style["bg_color"]).pack()
        tk.Radiobutton(algo_frame, text="Minimax", variable=self.algo_var, value="Minimax",
                      font=self.style["normal_font"], bg=self.style["bg_color"]).pack()
        
        button_frame = tk.Frame(self, bg=self.style["bg_color"])
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Sākt spēli", command=self.sākt_spēli, 
                 font=self.style["button_font"], bg=self.style["button_color"], 
                 activebackground=self.style["highlight_color"]).pack(pady=10)
    
    def sākt_spēli(self):
        try:
            skaitlis = int(self.skaitlis_entry.get())
            if 25 <= skaitlis <= 40:
                self.sākuma_skaitlis = skaitlis
                self.algoritms = self.algo_var.get()
                self.spēle = Spēle(skaitlis, self.algoritms)
                self.izveidot_spēles_ekrānu()
            else:
                messagebox.showerror("Kļūda", "Skaitlim jābūt no 25 līdz 40!")
        except ValueError:
            messagebox.showerror("Kļūda", "Lūdzu ievadiet derīgu skaitli!")
    
    def izveidot_spēles_ekrānu(self):
        self.clear_frame()
        
        # Galvene
        header_frame = tk.Frame(self, bg=self.style["highlight_color"])
        header_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(header_frame, text="Reizinātāju sacensības", 
                font=self.style["title_font"], bg=self.style["highlight_color"]).pack(pady=10)
        
        # Informācijas panelis
        info_frame = tk.Frame(self, bg=self.style["bg_color"])
        info_frame.pack(pady=20, padx=20, fill=tk.X)
        
        self.skaitlis_label = tk.Label(info_frame, 
                                     text=f"Pašreizējais skaitlis: {self.spēle.pārejams_skaitlis}", 
                                     font=("Arial", 16, "bold"), bg=self.style["bg_color"])
        self.skaitlis_label.pack(pady=5)
        
        stats_frame = tk.Frame(info_frame, bg=self.style["bg_color"])
        stats_frame.pack(pady=10)
        
        self.cilvēks_label = tk.Label(stats_frame, 
                                     text=f"Cilvēka punkti: {self.spēle.cilvēka_punkti}", 
                                     font=self.style["subtitle_font"], bg=self.style["bg_color"])
        self.cilvēks_label.grid(row=0, column=0, padx=20)
        
        self.dators_label = tk.Label(stats_frame, 
                                   text=f"Datora punkti: {self.spēle.datora_punkti}", 
                                   font=self.style["subtitle_font"], bg=self.style["bg_color"])
        self.dators_label.grid(row=0, column=1, padx=20)
        
        self.banka_label = tk.Label(stats_frame, 
                                  text=f"Banka: {self.spēle.banka}", 
                                  font=self.style["subtitle_font"], bg=self.style["bg_color"])
        self.banka_label.grid(row=0, column=2, padx=20)
        
        # Algoritma indikators
        self.algoritms_label = tk.Label(info_frame, 
                                      text=f"Datora algoritms: {self.spēle.algoritms}", 
                                      font=self.style["info_font"], bg=self.style["bg_color"], fg="#0066cc")
        self.algoritms_label.pack(pady=5)
        
        # Gājiena indikators
        self.gājiens_label = tk.Label(self, text="", font=("Arial", 14, "bold"), bg=self.style["bg_color"])
        self.gājiens_label.pack(pady=10)
        
        # Koka vizualizācijas rāmis
        self.tree_frame = tk.Frame(self, bg=self.style["bg_color"])
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.koka_canvas = tk.Canvas(self.tree_frame, bg="white")
        hscroll = tk.Scrollbar(self.tree_frame, orient="horizontal", command=self.koka_canvas.xview)
        vscroll = tk.Scrollbar(self.tree_frame, orient="vertical", command=self.koka_canvas.yview)
        self.koka_canvas.configure(xscrollcommand=hscroll.set, yscrollcommand=vscroll.set)
        
        hscroll.pack(side="bottom", fill="x")
        vscroll.pack(side="right", fill="y")
        self.koka_canvas.pack(side="left", fill="both", expand=True)
        
        # Pogas
        button_frame = tk.Frame(self, bg=self.style["bg_color"])
        button_frame.pack(pady=20)
        
        self.poga_2 = tk.Button(button_frame, text="×2", width=8, height=2,
                               font=("Arial", 14, "bold"), 
                               bg="#4CAF50", fg="white", activebackground="#45a049",
                               command=lambda: self.veikt_gājienu(2))
        self.poga_2.grid(row=0, column=0, padx=10)
        
        self.poga_3 = tk.Button(button_frame, text="×3", width=8, height=2,
                               font=("Arial", 14, "bold"), 
                               bg="#2196F3", fg="white", activebackground="#0b7dda",
                               command=lambda: self.veikt_gājienu(3))
        self.poga_3.grid(row=0, column=1, padx=10)
        
        self.poga_4 = tk.Button(button_frame, text="×4", width=8, height=2,
                               font=("Arial", 14, "bold"), 
                               bg="#f44336", fg="white", activebackground="#da190b",
                               command=lambda: self.veikt_gājienu(4))
        self.poga_4.grid(row=0, column=2, padx=10)
        
        # Atpakaļ pogas
        tk.Button(self, text="Atpakaļ uz sākumu", 
                 font=self.style["button_font"], bg=self.style["button_color"],
                 command=self.izveidot_sākuma_ekrānu).pack(pady=20)
        
        self.atjaunināt_ekrānu()
    
    def veikt_gājienu(self, reizinātājs):
        if self.spēle.gājiena_nr % 2 == 0:  # Tikai cilvēka gājiena laikā
            self.spēle.veikt_gājienu(reizinātājs)
            self.atjaunināt_ekrānu()
            
            if not self.spēle.spēle_beigusies():
                self.after(1000, self.datora_gājiens)
    
    def datora_gājiens(self):
        if self.spēle.gājiena_nr % 2 == 1:  # Datora gājiens
            reizinātājs = self.spēle.datora_gājiens()
            self.spēle.veikt_gājienu(reizinātājs)
            self.atjaunināt_ekrānu()
            
            if self.spēle.spēle_beigusies():
                self.parādīt_rezultātu()
    
    def zīmēt_koku(self):
        if not hasattr(self, 'spēle') or not hasattr(self.spēle, 'spēles_koks'):
            return
            
        self.koka_canvas.delete("all")
        
        # Izmantojam platumu pirmo meklēšanu, lai izvietotu mezglus
        mezgli = []
        rinda = deque()
        rinda.append(self.spēle.spēles_koks)
        
        while rinda:
            mezgls = rinda.popleft()
            mezgli.append(mezgls)
            for bērns in mezgls.bērni:
                rinda.append(bērns)
        
        # Izvietojam mezglus kokā
        max_dziļums = max(m.dziļums for m in mezgli) if mezgli else 0
        vertikālais_atstarpe = 100
        horizontālais_atstarpe = 100
        
        # Aprēķinam nepieciešamo platumu
        max_mezgli_līmenī = max(
            sum(1 for m in mezgli if m.dziļums == līmenis) 
            for līmenis in range(max_dziļums + 1)
        ) if mezgli else 1
        
        canvas_width = max(1000, max_mezgli_līmenī * horizontālais_atstarpe + 200)
        self.koka_canvas.config(width=canvas_width)
        
        mezglu_pozīcijas = {}
        for līmenis in range(max_dziļums + 1):
            līmeņa_mezgli = [m for m in mezgli if m.dziļums == līmenis]
            if not līmeņa_mezgli:
                continue
                
            start_x = (canvas_width - (len(līmeņa_mezgli) - 1) * horizontālais_atstarpe) / 2
            
            for i, mezgls in enumerate(līmeņa_mezgli):
                x = start_x + i * horizontālais_atstarpe
                y = 50 + līmenis * vertikālais_atstarpe
                mezglu_pozīcijas[mezgls] = (x, y)
        
        # Zīmējam savienojumus
        for mezgls, (x, y) in mezglu_pozīcijas.items():
            if mezgls.vecāks and mezgls.vecāks in mezglu_pozīcijas:
                vecāka_x, vecāka_y = mezglu_pozīcijas[mezgls.vecāks]
                savienojuma_krāsa = "green" if mezgls.ir_faktiskais else "lightgray"
                self.koka_canvas.create_line(
                    x, y-20, vecāka_x, vecāka_y+20, 
                    fill=savienojuma_krāsa, 
                    width=2 if mezgls.ir_faktiskais else 1,
                    dash=(5,3) if not mezgls.ir_faktiskais else None
                )
        
        # Zīmējam mezglus
        for mezgls, (x, y) in mezglu_pozīcijas.items():
            # Izvēlamies krāsu atkarībā no tā, vai tas ir faktiskais vai iespējamais variants
            if mezgls == self.spēle.pašreizējais_mezgls:
                fill_color = "#ff9999"  # Pašreizējais mezgls
                outline_color = "red"
                outline_width = 3
            elif mezgls.ir_faktiskais:
                fill_color = "#99ccff"  # Faktiskie gājieni
                outline_color = "blue"
                outline_width = 2
            else:
                fill_color = "#e0e0e0"  # Iespējamie varianti
                outline_color = "gray"
                outline_width = 1
            
            # Mezglu kastīte
            self.koka_canvas.create_rectangle(
                x-40, y-30, x+40, y+30,
                fill=fill_color, 
                outline=outline_color, 
                width=outline_width
            )
            
            # Mezglu informācija
            self.koka_canvas.create_text(
                x, y-15,
                text=f"Sk: {mezgls.skaitlis}",
                font=("Arial", 10)
            )
            
            self.koka_canvas.create_text(
                x, y,
                text=f"C: {mezgls.cilvēka_punkti} D: {mezgls.datora_punkti}",
                font=("Arial", 8)
            )
            
            self.koka_canvas.create_text(
                x, y+15,
                text=f"B: {mezgls.banka} H: {mezgls.heiristika:.1f}",
                font=("Arial", 8)
            )
            
            # Gājiens, kas izveidoja šo mezglu
            if mezgls.gājiens:
                self.koka_canvas.create_text(
                    x-45, y,
                    text=f"×{mezgls.gājiens}",
                    font=("Arial", 10, "bold"),
                    anchor="e"
                )
        
        # Atjauninam ritjoslas, lai ietilptu viss koks
        self.koka_canvas.configure(scrollregion=self.koka_canvas.bbox("all"))
        self.koka_canvas.xview_moveto(0)
        self.koka_canvas.yview_moveto(0)
    
    def atjaunināt_ekrānu(self):
        self.skaitlis_label.config(text=f"Pašreizējais skaitlis: {self.spēle.pārejams_skaitlis}")
        self.cilvēks_label.config(text=f"Cilvēka punkti: {self.spēle.cilvēka_punkti}")
        self.dators_label.config(text=f"Datora punkti: {self.spēle.datora_punkti}")
        self.banka_label.config(text=f"Banka: {self.spēle.banka}")
        self.algoritms_label.config(text=f"Datora algoritms: {self.spēle.algoritms}")
        
        if self.spēle.spēle_beigusies():
            self.gājiens_label.config(text="Spēle beigusies!", fg="purple")
            self.poga_2.config(state=tk.DISABLED)
            self.poga_3.config(state=tk.DISABLED)
            self.poga_4.config(state=tk.DISABLED)
            self.parādīt_rezultātu()
        else:
            if self.spēle.gājiena_nr % 2 == 0:
                self.gājiens_label.config(text="Tavs gājiens!", fg="green")
                self.poga_2.config(state=tk.NORMAL)
                self.poga_3.config(state=tk.NORMAL)
                self.poga_4.config(state=tk.NORMAL)
            else:
                self.gājiens_label.config(text="Datora gājiens...", fg="red")
                self.poga_2.config(state=tk.DISABLED)
                self.poga_3.config(state=tk.DISABLED)
                self.poga_4.config(state=tk.DISABLED)
        
        self.zīmēt_koku()
    
    def parādīt_rezultātu(self):
        uzvarētājs = self.spēle.noteikt_uzvarētāju()
        messagebox.showinfo("Spēle beigusies", 
                          f"Uzvarētājs: {uzvarētājs}!\n\n"
                          f"Cilvēka punkti: {self.spēle.cilvēka_punkti}\n"
                          f"Datora punkti: {self.spēle.datora_punkti}\n"
                          f"Bankas punkti: {self.spēle.banka}")
    
    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = SpēlesAplikācija()
    app.mainloop()