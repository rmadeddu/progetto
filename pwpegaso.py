from flask import Flask, render_template, request
import mysql.connector, random, xlsxwriter, openpyxl

app = Flask(__name__)
app.config["DEBUG"] = True

numutenti = 10 # imposta il numero di utenti da creare casualmente

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/elaborazione", methods=["GET", "POST"])
def elaborazione():
    if request.method == "GET":
        # Definizione della classe Utente
        class Utente:
            def __init__(self, ID, nome, cognome, genere, email, telefono):
                self.ID = chr(random.randrange(65, 65 + 26)) + str(random.randrange(1,9999)).rjust(4,'0')
                self.nome = nome
                self.cognome = cognome
                self.genere = genere
                # Generazione dell'indirizzo email
                self.email=(self.nome+"."+self.cognome+"@dominio.com").lower()
                # Serie di sostituzione all'interno dell'indirizzo email per eliminare i caratteri non consentiti
                self.email=self.email.replace(" ", "") # eliminazione gli spazi
                self.email=self.email.replace("'", "") # eliminazione degli apici
                # Generazione del numero di telefono
                self.telefono=3100000000+random.randrange(0,89999999)

        # Configurazione per la connessione al database
        connessioneDB = mysql.connector.connect(
                host="",
                port=3306,
                database="",
                user="",
                password="")

        # Imposta il Cursor
        cur = connessioneDB.cursor()

        # Esecuzione della query per selezionare un nome in modo casuale dalla tabella dei nomi
        # Ogni riga contiene, nell'ordine, il nome, il genere e la diffusione del nome
        cur.execute("SELECT * FROM Nomi WHERE Diffusione=1 ORDER BY RAND() LIMIT "+str(numutenti))
        nomi = cur.fetchall() # Acquisizione del risultato della query

        # Esecuzione della query per selezionare i casualmente i cognomi
        cur.execute("SELECT * FROM Cognomi ORDER BY RAND() LIMIT "+str(numutenti))
        cognomi = cur.fetchall()


        Utenti=[]
        for i in range(numutenti):
            Nome=str(nomi[i][0]) # Assegnazione del nome
            Genere=str(nomi[i][1]) # Assegnazione del genere
            Cognome=str(cognomi[i][0]) # Assegnazione del cognome
            Utenti.append(Utente('',Nome,Cognome,Genere,'' ,'' )) # Aggiungo l'elemento, in automatico verranno creati l'ID, l'indirizzo email e il numero di telefono


        # CREAZIONE DEL DOCUMENTO EXCEL
        workbook = xlsxwriter.Workbook("/home/rmadeddu/projectwork/static/Utenti.xlsx")
        worksheet = workbook.add_worksheet()
        worksheet.hide_gridlines(2)

        formato_intestazione = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': 'blue', 'border': 1}) # Formattazione della riga d'intestazione
        formato_dati = workbook.add_format({'border': 1}) # Formattazione delle altre celle

        # Scrive la riga d'intestazione
        worksheet.write_string("A1", "ID", formato_intestazione)
        worksheet.write_string("B1", "Nome", formato_intestazione)
        worksheet.write_string("C1", "Cogome", formato_intestazione)
        worksheet.write_string("D1", "Genere", formato_intestazione)
        worksheet.write_string("E1", "Email", formato_intestazione)
        worksheet.write_string("F1", "Telefono", formato_intestazione)

        # Imposto la larghezza delle colonne
        worksheet.set_column('A:A', 8) # Larghezza della colonna ID
        worksheet.set_column('B:C', 25) # Larghezza delle colone Nome e Cognome
        worksheet.set_column('D:D', 8) # Larghezza della colonna Genere
        worksheet.set_column('E:E', 35) # Larghezza della colonna Email
        worksheet.set_column('F:F', 12) # Larghezza della colonna Telefono

        # Aggiungi una riga per ogni utente
        riga = 1
        for Utente in Utenti:
            worksheet.write(riga, 0, Utente.ID, formato_dati)
            worksheet.write(riga, 1, Utente.nome, formato_dati)
            worksheet.write(riga, 2, Utente.cognome, formato_dati)
            worksheet.write(riga, 3, Utente.genere, formato_dati)
            worksheet.write(riga, 4, Utente.email, formato_dati)
            worksheet.write(riga, 5, Utente.telefono, formato_dati)
            riga = riga +1

        workbook.close()

        # Percorso del documento Excel
        percorso_xls = "https://rmadeddu.pythonanywhere.com/static/Utenti.xlsx"


        # LETTURA DEL DOCUMENTO EXCEL E GENERAZIONE DEL CODICE SQL PER LA CREAZIONE DELLA TABELLA

        workbook2 = openpyxl.load_workbook('/home/rmadeddu/projectwork/static/Utenti.xlsx')
        foglio = workbook2.active
        numrighe = foglio.max_row
        numcolonne = foglio.max_column

        sql_crea_tabella="CREATE TABLE Utenti ( ID varchar (5) NOT NULL, Nome varchar (100) NOT NULL, Cognome varchar (100) NOT NULL, Genere varchar (1) NOT NULL, Email varchar (150) NOT NULL, Telefono varchar (10) NOT NULL, PRIMARY KEY(ID) );"
        sql_popola_tabella="INSERT INTO Utenti (ID, Nome, Cognome, Genere, Email, Telefono) VALUES "
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

        cur.execute("DROP TABLE IF EXISTS Utenti") # Se esiste si elimina la tabella 'Utenti'
        cur.execute(sql_crea_tabella) # Creazione della tabella 'Utenti'
        cur.execute(sql_popola_tabella) # Popolazione della tabella 'Utenti'
        connessioneDB.commit() # Applicazione delle modifiche

        # Chiusura della connessione al database
        connessioneDB.close()

        return render_template("index.html",Utenti=Utenti, percorso_xls=percorso_xls,sql_tabella=sql_crea_tabella,sql_popola_tabella=sql_popola_tabella)
