from flask import Flask, render_template, request
import mysql.connector, random, xlsxwriter, openpyxl

app = Flask(__name__)
app.config["DEBUG"] = True

numelementi = 10 # imposta il numero di elementi da creare casualmente
assegnatari = round(numelementi / 2) # calcola quanti dipendenti riceveranno il differenziale economico

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/elaborazione", methods=["GET", "POST"])
def elaborazione():
    if request.method == "GET":
        # Definizione della classe DomandaDEP
        class DomandaDEP:
            def __init__(self, ID_domanda, puntiValPers, puntiEspProf, puntiCapProfCult, punteggioTot, attrDEP,\
                               matricola, nome, cognome, genere, email, telefono):
                self.ID_domanda = "DEP_" + str(random.randrange(1,9999)).rjust(4,'0')
                self.puntiValPers = random.randrange(0,50)
                self.puntiEspProf = random.randrange(0,40)
                self.puntiCapProfCult = random.randrange(0,10)
                self.punteggioTot = self.puntiValPers + self.puntiEspProf + self.puntiCapProfCult
                self.matricola = chr(random.randrange(65, 65 + 26)) + str(random.randrange(1,9999)).rjust(4,'0')
                self.nome = nome
                self.cognome = cognome
                self.genere = genere
                # Generazione dell'indirizzo email
                self.email=(self.nome+"."+self.cognome+"@dominio.com").lower()
                # Serie di sostituzioni all'interno dell'indirizzo email per eliminare i caratteri non consentiti
                self.email=self.email.replace(" ", "") # eliminazione gli spazi
                self.email=self.email.replace("'", "") # eliminazione degli apici
                # Generazione del numero di telefono
                self.telefono=3100000000+random.randrange(0,89999999)

            def __lt__(self, other): # Metodo per l'ordinamento decrescente per punteggio totale
                return self.punteggioTot > other.punteggioTot

        # Configurazione per la connessione al database
        connessioneDB = mysql.connector.connect(
                host="",
                port=3306,
                database="",
                user="",
                password="")

        # Imposta il Cursor
        cur = connessioneDB.cursor()

        # Esecuzione della query per selezionare i nomi in modo casuale dalla tabella Nomi
        # Ogni riga contiene, nell'ordine, il nome, il genere e la diffusione del nome
        cur.execute("SELECT * FROM Nomi WHERE Diffusione=1 ORDER BY RAND() LIMIT "+str(numelementi))
        nomi = cur.fetchall() # Acquisizione del risultato della query

        # Esecuzione della query per selezionare casualmente i cognomi dalla tabella Cognomi
        cur.execute("SELECT * FROM Cognomi ORDER BY RAND() LIMIT "+str(numelementi))
        cognomi = cur.fetchall()

        DomandeDEP=[]
        for i in range(numelementi):
            Nome=str(nomi[i][0]) # Assegnazione del nome
            Genere=str(nomi[i][1]) # Assegnazione del genere
            Cognome=str(cognomi[i][0]) # Assegnazione del cognome
            DomandeDEP.append(DomandaDEP('','','','','','','',Nome,Cognome,Genere,'' ,'' ))

        # Ordinamento per punteggio totale decrescente
        DomandeDEP.sort()

        # Attribuzione del DEP
        for i in range(numelementi):
            DomandeDEP[i].attrDEP="SI" if i < assegnatari else "NO"

        # CREAZIONE DEL DOCUMENTO EXCEL
        workbook = xlsxwriter.Workbook("/home/rmadeddu/projectwork/static/DomandeDEP.xlsx")
        worksheet = workbook.add_worksheet()
        worksheet.hide_gridlines(2)

        formato_intestazione = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': 'blue', 'border': 1}) # Formattazione della riga di intestazione
        formato_dati = workbook.add_format({'border': 1}) # Formattazione delle altre celle

        # Scrivo la riga d'intestazione
        worksheet.write_string("A1", "ID domanda", formato_intestazione)
        worksheet.write_string("B1", "Punteggio valutazioni personali", formato_intestazione)
        worksheet.write_string("C1", "Punteggio esperienze professionali", formato_intestazione)
        worksheet.write_string("D1", "Punteggio capacità professionali e culturali", formato_intestazione)
        worksheet.write_string("E1", "Punteggio totale", formato_intestazione)
        worksheet.write_string("F1", "Attribuzione DEP", formato_intestazione)

        worksheet.write_string("G1", "Matricola", formato_intestazione)
        worksheet.write_string("H1", "Nome", formato_intestazione)
        worksheet.write_string("I1", "Cognome", formato_intestazione)
        worksheet.write_string("J1", "Genere", formato_intestazione)
        worksheet.write_string("K1", "Email", formato_intestazione)
        worksheet.write_string("L1", "Telefono", formato_intestazione)

        # Imposto la larghezza delle colonne
        worksheet.set_column('A:A', 12) # Larghezza della colonna ID domanda
        worksheet.set_column('B:F', 8) # Larghezza colonne per punteggi ed esito
        worksheet.set_column('G:G', 10) # Larghezza della colonna Matricola
        worksheet.set_column('H:I', 25) # Larghezza delle colone Nome e Cognome
        worksheet.set_column('J:J', 8) # Larghezza della colonna Genere
        worksheet.set_column('K:K', 35) # Larghezza della colonna Email
        worksheet.set_column('L:L', 12) # Larghezza della colonna Telefono

        # Aggiungo una riga per ogni domanda DEP
        riga = 1
        for DomandaDEP in DomandeDEP:
            worksheet.write(riga, 0, DomandaDEP.ID_domanda, formato_dati)
            worksheet.write(riga, 1, DomandaDEP.puntiValPers, formato_dati)
            worksheet.write(riga, 2, DomandaDEP.puntiEspProf, formato_dati)
            worksheet.write(riga, 3, DomandaDEP.puntiCapProfCult, formato_dati)
            worksheet.write(riga, 4, DomandaDEP.punteggioTot, formato_dati)
            worksheet.write(riga, 5, DomandaDEP.attrDEP, formato_dati)
            worksheet.write(riga, 6, DomandaDEP.matricola, formato_dati)
            worksheet.write(riga, 7, DomandaDEP.nome, formato_dati)
            worksheet.write(riga, 8, DomandaDEP.cognome, formato_dati)
            worksheet.write(riga, 9, DomandaDEP.genere, formato_dati)
            worksheet.write(riga, 10, DomandaDEP.email, formato_dati)
            worksheet.write(riga, 11, DomandaDEP.telefono, formato_dati)
            riga = riga +1

        workbook.close()

        # Percorso del documento Excel
        percorso_xls = "https://rmadeddu.pythonanywhere.com/static/DomandeDEP.xlsx"

        # LETTURA DEL DOCUMENTO EXCEL E GENERAZIONE DEL CODICE SQL PER LA CREAZIONE DELLA TABELLA

        workbook2 = openpyxl.load_workbook('/home/rmadeddu/projectwork/static/DomandeDEP.xlsx')
        foglio = workbook2.active
        numrighe = foglio.max_row
        numcolonne = foglio.max_column

        sql_crea_tabella="CREATE TABLE DomandeDEP ( ID_domanda VARCHAR(8) NOT NULL, PuntiValPers TINYINT UNSIGNED NOT NULL, PuntiEspProf TINYINT UNSIGNED NOT NULL, PuntiCapProfCult TINYINT UNSIGNED NOT NULL, PunteggioTot TINYINT UNSIGNED NOT NULL, AttrDEP VARCHAR(2), Matricola VARCHAR(5) NOT NULL, Nome VARCHAR(100) NOT NULL, Cognome VARCHAR(100) NOT NULL, Genere VARCHAR(1) NOT NULL, Email VARCHAR(150) NOT NULL, Telefono VARCHAR(10) NOT NULL, PRIMARY KEY(ID_domanda) );"
        sql_popola_tabella="INSERT INTO DomandeDEP (ID_domanda, PuntiValPers, PuntiEspProf, PuntiCapProfCult, PunteggioTot, AttrDEP, Matricola, Nome, Cognome, Genere, Email, Telefono) VALUES "
        # LETTURA DELLE CELLE DI OGNI RIGA ESCLUDENDO LA PRIMA D'INTESTAZIONE
        for r in range(2, numrighe + 1):
            sql_popola_tabella+="("
            for c in range(1, numcolonne + 1):
                cella = foglio.cell(row=r, column=c)
                sql_popola_tabella+="\""+str(cella.value)+"\""
                if c < numcolonne:
                    sql_popola_tabella+=","
            sql_popola_tabella+=")"
            if r < numrighe:
                sql_popola_tabella+=","
            else:
                sql_popola_tabella+=";"

        # Scrittura dei dati nella tabella SQL

        cur.execute("DROP TABLE IF EXISTS DomandeDEP") # Se esiste si elimina la tabella 'DomandeDEP'
        cur.execute(sql_crea_tabella) # Creazione della tabella 'DomandeDEP'
        cur.execute(sql_popola_tabella) # Popolazione della tabella 'DomandeDEP'
        connessioneDB.commit() # Applicazione delle modifiche

        # Chiusura della connessione al database
        connessioneDB.close()

        return render_template("index.html",DomandeDEP=DomandeDEP, percorso_xls=percorso_xls, sql_tabella=sql_crea_tabella, sql_popola_tabella=sql_popola_tabella)
