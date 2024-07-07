from tkinter import *
from PIL import ImageTk, Image
import tkinter.messagebox
from tkinter import simpledialog
import os
import sqlite3
import re
import random
import datetime

##DATABASE Functions

def create_registration_table():
    con = sqlite3.connect("ATMdatabase.db")

    cur = con.cursor()
    cur.execute("""
    CREATE TABLE Registration_data(
        Name text,
        gender text,
        age text,
        dob integer,
        Mobile_No text,
        Card_No integer,
        username text,
        Account_number integer,
        PIN integer
    )""")
    con.commit()
    con.close()

def create_transation_table():
    con = sqlite3.connect("ATMdatabase.db")

    cur = con.cursor()
    cur.execute("""
    CREATE TABLE transaction_data(
        username text,
        account_balance integer,
        transactions text
    )""")
    con.commit()
    con.close()

####GUI
root=Tk()
root.geometry('600x500')
root.resizable(0,0)

global account_userName 
account_userName = StringVar()
# #Functions############
def transaction_init():
    global account_userName
    username = account_userName.get()
    acBal = 0
    time_now = datetime.datetime.now().strftime("%Y/%m/%d %H-%M-%S")
    transactions = f"{time_now}: 0 Account Created|"
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO transaction_data VALUES (?,?,?)",(username,acBal,transactions))
        #allready Created Table, data Added
    except sqlite3.OperationalError:
        #Not created!! Now Creating
        create_transation_table()
        cur.execute("INSERT INTO transaction_data VALUES (?,?,?)",(username,acBal,transactions))
    con.commit()
    con.close()

def check_user_exist(un):
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    try:
        cur.execute("SELECT username from Registration_data")
        li = cur.fetchall()


        li = [i for i in li if i[0]==un]
        return len(li)
    except:
        pass

def get_balance(username):
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()   
    try:
        cur.execute("SELECT account_balance from transaction_data WHERE username=?",(username,))
        balance = cur.fetchone()

        return balance[0]
    except TypeError:
        pass

def balanceEnq():
    global account_userName
    bal = get_balance(account_userName.get())
    tkinter.messagebox.showinfo(title=f"Balanta utilizatorului {account_userName.get()}" ,message=f"Balanta dumneavostra este. {bal}")

def get_PIN(username):
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    try:
        cur.execute("SELECT PIN FROM Registration_data WHERE username=?",(username,))
        return cur.fetchone()[0]
    except sqlite3.OperationalError:
        pass
    con.close()

def changePIN():
    global account_userName
    username = account_userName.get()
    curPIN = simpledialog.askinteger(title="Change PIN STEP 1/2",prompt="Current PIN:")
    dbPIN = get_PIN(username)

    if curPIN!=None:
        if curPIN == dbPIN:
            newPIN = simpledialog.askinteger(title="Change PIN STEP 2/2",prompt="New PIN:")

            con = sqlite3.connect("ATMdatabase.db")
            cur = con.cursor()

            cur.execute("UPDATE Registration_data set PIN = ?  WHERE username=?",(newPIN,username))
            
            con.commit()
            con.close()      
            tkinter.messagebox.showinfo(title="Success",message="PIN-UL s-a schimbat")  
        else:
            tkinter.messagebox.showwarning(title="Error",message="PIN introdus gresit")

def mini_statement():
    global account_userName
    username = account_userName.get()
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    cur.execute("SELECT transactions FROM transaction_data WHERE username=?",(username,))
    transactions = cur.fetchone()[0]

    transaction_list =  transactions.split('|') 
    transaction_list = transaction_list[:-1] 
    
    mini_state = f"Mini Statement of {username}:\n"
    for item in transaction_list:
        mini_state+=item +"\n"
    time_now = datetime.datetime.now().strftime("%Y/%m/%d %H-%M-%S")
    mini_state +=f"Clear Balance lei.{get_balance(username)}-as on {time_now}" 
    tkinter.messagebox.showinfo(title="Mini Statement",message=mini_state)
   
def cash_depo():
    global account_userName
    username = account_userName.get()

    amount_to_add = simpledialog.askinteger(title="Cash Deposit",prompt="Introduceti suma pe care o adaugati:")

    if amount_to_add!=None:
        con = sqlite3.connect("ATMdatabase.db")
        cur = con.cursor()
        #balanta curenta
        cur_bal = get_balance(account_userName.get())    

        #update account balance
        updated_bal = cur_bal + amount_to_add
        cur.execute("UPDATE transaction_data set account_balance = ?  WHERE username=?",(updated_bal,username))

        ##Create Transaction Detail###################
        time_now = datetime.datetime.now().strftime("%Y/%m/%d %H-%M-%S")
        current_transaction = f"{time_now}: {amount_to_add} Cr|"
        cur.execute("SELECT transactions FROM transaction_data WHERE username = ?",(username,))
        past_transaction = cur.fetchone() #fetching old transactions
        updated_transaction = past_transaction[0]+current_transaction
        cur.execute("UPDATE transaction_data SET transactions = ? WHERE username = ?",(updated_transaction,username))
        

        con.commit()
        con.close()      
        tkinter.messagebox.showinfo(title="Adaugam",message="Suma este adaugata")  

def cach_withdrawl():
    global account_userName
    username = account_userName.get()

    amount_to_withdrawl = simpledialog.askinteger(title="Cash Withdrawl",prompt="Introduceti cat doriti sa retrageti:")

    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    #Balanta curenta
    cur_bal = get_balance(account_userName.get())    

    #update account balance
    try:
        if cur_bal<amount_to_withdrawl:
            tkinter.messagebox.showwarning(title="Error",message="insufficient Balance")
        else:
            updated_bal = cur_bal - amount_to_withdrawl
            cur.execute("UPDATE transaction_data set account_balance = ?  WHERE username=?",(updated_bal,username))
            ##Create Transaction Detail
            time_now = datetime.datetime.now().strftime("%Y/%m/%d %H-%M-%S")
            current_transaction = f"{time_now}: {amount_to_withdrawl} Dr|"
            cur.execute("SELECT transactions FROM transaction_data WHERE username = ?",(username,))
            past_transaction = cur.fetchone() #fetching old transactions
            updated_transaction = past_transaction[0]+current_transaction
            cur.execute("UPDATE transaction_data SET transactions = ? WHERE username = ?",(updated_transaction,username))
            
            con.commit()
            con.close()      
            tkinter.messagebox.showinfo(title="Retragem",message="Am scos")  
    except TypeError:
        pass

def transfer():
    global account_userName
    receiver_username = simpledialog.askstring(title="Cash Transfer STEP 1/2",prompt="Introduceti usernameul cui doriti sa ii trimiteti:")
    if receiver_username!=None:

        if check_user_exist(receiver_username) == 0:
            tkinter.messagebox.showwarning(title="Error",message="Account Not Found")

        else:
            sending_amount = simpledialog.askinteger(title="Cash Transfer STEP 1/2",prompt="Cat doriti sa transferati:")
            
            SenderUserName = account_userName.get()
            sender_cur_bal = get_balance(account_userName.get())
            receiver_cur_bal = get_balance(receiver_username)

            try:        
                if sending_amount>sender_cur_bal:
                    tkinter.messagebox.showwarning(title="Error",message="insufficient Balance")
                else:
                    sender_updated_amount = sender_cur_bal - sending_amount 
                    receiver_updated_amount = receiver_cur_bal + sending_amount

                    con = sqlite3.connect("ATMdatabase.db")
                    cur = con.cursor()
                    cur.execute("UPDATE transaction_data set account_balance = ?  WHERE username=?",(sender_updated_amount,SenderUserName))
                    cur.execute("UPDATE transaction_data set account_balance = ?  WHERE username=?",(receiver_updated_amount,receiver_username))
                    
                    ##Sender Transaction 
                    time_now = datetime.datetime.now().strftime("%Y/%m/%d %H-%M-%S")
                    sender_current_transaction = f"{time_now}: {sending_amount} Sr Transferred To {receiver_username}|"
                    cur.execute("SELECT transactions FROM transaction_data WHERE username = ?",(SenderUserName,))
                    sender_past_transaction = cur.fetchone() #Tranzactii
                    sender_updated_transaction = sender_past_transaction[0]+sender_current_transaction
                    cur.execute("UPDATE transaction_data SET transactions = ? WHERE username = ?",(sender_updated_transaction,SenderUserName))
                    
                    ##Receiver Transaction 
                    receiver_current_transaction = f"{time_now}: {sending_amount} Rc Transaferred From {SenderUserName}|"
                    cur.execute("SELECT transactions FROM transaction_data WHERE username = ?",(receiver_username,))
                    receiver_past_transaction = cur.fetchone() #Tranzactii
                    receiver_updated_transaction = receiver_past_transaction[0]+receiver_current_transaction
                    cur.execute("UPDATE transaction_data SET transactions = ? WHERE username = ?",(receiver_updated_transaction,receiver_username))
                    ###
                    con.commit()
                    con.close()      
                    tkinter.messagebox.showinfo(title="Ati realizat transferul",message="Suma este transferata")  
            except TypeError:
                pass

def generateAcNo(e):
    acNo = random.randint(11111111,99999999)
    e.delete(0,END)
    e.insert(0,acNo)

def check_acNo_exist(un):
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    try:
        cur.execute("SELECT Account_number from Registration_data")
        li = cur.fetchall()

        un = int(un)
        li = [i for i in li if i[0]==un]
        return len(li)
    except:
        pass

def login(e1,e2):
    global account_userName
    username = e1.get()
    password = e2.get()

    if "" in (username,password):
        tkinter.messagebox.showerror('Error Message','Missing fields')
    else:
        try:
            dbPass = get_PIN(username)
            if password == str(dbPass):
                tkinter.messagebox.showinfo('Bravo','Ati intrat in cont')
                account_userName.set(username)
                main_window()
            else:
                tkinter.messagebox.showerror('Error Message','Invalid Username/PIN')
        except:
            tkinter.messagebox.showerror('Error Message','Invalid Username/PIN')

def registration_data(en1,en2,en3,en4,en5,en6,en7,en8):
    global account_userName
    pin = random.randint(1111,9999)
    name = en1.get()

    gender = en2.get()
    if gender == 1:
        gender = "Male"
    elif gender == 2:
        gender = "Female"
    else :
        gender = "Others"

    age = en3.get()
    dob = en4.get()
    cNo = en5.get()
    CardNo = en6.get()
    Username = en7.get()
    acNo = en8.get()

    if "" in (name,gender,age,dob,cNo,CardNo,Username,acNo):
        tkinter.messagebox.showerror(title="error",message="Missing Fields")
    else:
        try: 
            age = int(age)
            if age<18:
                tkinter.messagebox.showerror(title="Error",message=f"You are Underage! Wait for {18-age} years.")
                return
            else:
                if len(cNo)==10:
                    try:
                        cNo = int(cNo)
                    except ValueError:
                        tkinter.messagebox.showerror(title="Error",message="Mobile Number is invalid")
                    
                    if len(CardNo)==12:
                        try:
                            cNo = int(cNo)
                        except ValueError:
                            tkinter.messagebox.showerror(title="Error",message=" Number is invalid")
                            return

                        if check_user_exist(Username)==1:
                            tkinter.messagebox.showerror(title="Error",message="Username is already Exist. Try New!")
                            return
                        if check_acNo_exist(acNo)==1:
                            tkinter.messagebox.showerror(title="Error",message="Account Number already Exist. Try New!")
                            return
                        
                        else:
                            account_userName.set(Username)
                            # Database
                            con = sqlite3.connect("ATMdatabase.db")
                            cur = con.cursor()
                            try:
                                cur.execute("INSERT INTO Registration_data VALUES (?,?,?,?,?,?,?,?,?)",(name,gender,age,dob,cNo,CardNo,Username,acNo,pin))
                                #Tabel data Added
                            except sqlite3.OperationalError:
                                #Nu se creaza conditii !! si crem!
                                create_registration_table()
                                cur.execute("INSERT INTO Registration_data VALUES (?,?,?,?,?,?,?,?,?)",(name,gender,age,dob,cNo,CardNo,Username,acNo,pin))
                            con.commit()
                            con.close()
                            tkinter.messagebox.showinfo(title="Success",message=f"Contul este create, iar  PIN-UL este {pin}")
                            transaction_init()
                            Home()

                    else:
                        tkinter.messagebox.showerror(title="Error",message=" Number este invalid")
                        return
                else:
                    tkinter.messagebox.showerror(title="Error",message="Numarul de telefon este invalid") ##casute mesaj !

        except ValueError:
            tkinter.messagebox.showerror(title="Error",message="Varsta este invalida")

def RegistrationWindow():
    varGen = IntVar() #Varsta

    #Framuri
    signUpFrame=Frame(root,width=600,height=500)
    signUpFrame.place(x=0,y=0)
    root.title("Registration")

    
    # ______Imagini_______________       
    img=ImageTk.PhotoImage(Image.open('Additional_Files/s.jpg'))
    lbImg=Label(signUpFrame,bg='#a9a9a9',width=600,height=500,image=img)
    lbImg.place(x=0,y=0)
    # ____Welcome Message Label___________
    lbIntr=Label(signUpFrame,width=20,text='Registration Form',fg="white",font='Helvetica 18 bold',bg="#FFBB64")
    lbIntr.place(x=20,y=20)

    # # ____LABELS________________________

    enAcNo=Entry(width=14,font='Helvetica 12',bd=3)
    enAcNo.place(x=150,y=370)

    ##Creere cont
    getNewAcNo= Button(text="Get New",width=6,font="arial 8 bold",command=lambda:generateAcNo(enAcNo))
    getNewAcNo.place(x=295,y=370)

    lbName=Label(signUpFrame,width=11,text='Name',fg="white",font='Helvetica 12 bold',bg="#FFBB64")
    lbName.place(x=20,y=90)

    lbGen=Label(signUpFrame,width=11,text='Gender',fg="white",font='Helvetica 12 bold',bg="#FFBB64")
    lbGen.place(x=20,y=130)
        
    lbAge=Label(signUpFrame,width=11,text='Age',fg="white",font='Helvetica 12 bold',bg="#FFBB64")
    lbAge.place(x=20,y=170)
        
    lbDob=Label(signUpFrame,width=11,text='Date of Birth',fg="white",font='Helvetica 12 bold',bg="#FFBB64")
    lbDob.place(x=20,y=210)

    
    lbCont=Label(signUpFrame,width=11,text="Mobile No",fg="white",font='Helvetica 12 bold',bg="#FFBB64")
    lbCont.place(x=20,y=250)

    lbAdhar=Label(signUpFrame,width=11,text="Card Nu",fg="white",font='Helvetica 12 bold',bg="#FFBB64")
    lbAdhar.place(x=20,y=290)

    lblUsername=Label(signUpFrame,width=11,text="User Name",fg="white",font='Helvetica 12 bold',bg="#FFBB64")
    lblUsername.place(x=20,y=330)

    lblAcNumber=Label(signUpFrame,width=11,text="Account No",fg="white",font='Helvetica 12 bold',bg="#FFBB64")
    lblAcNumber.place(x=20,y=370)

    # # Pagina de tranzactii   
    enName=Entry(width=21,font='Helvetica 12',bd=3)
    enName.place(x=150,y=90)

    ##Radio Buttons

    genRadioMale = Radiobutton(text="Male",font='Helvetica 8', variable = varGen,value=1)
    genRadioMale.place(x=150,y=130)

    genRadioFemale = Radiobutton(text="Female",font='Helvetica 8', variable = varGen,value=2)
    genRadioFemale.place(x=210,y=130)

    genRadioOther = Radiobutton( text="Others",font='Helvetica 8',variable = varGen, value=3)
    genRadioOther.place(x=280,y=130)
    ###
    enAge=Entry(width=21,font='Helvetica 12',bd=3)
    enAge.place(x=150,y=170)

    enDob=Entry(width=21,font='Helvetica 12',bd=3)
    enDob.place(x=150,y=210)
    
    enCno=Entry(width=21,font='Helvetica 12',bd=3)
    enCno.place(x=150,y=250)

    Card=Entry(width=21,font='Helvetica 12',bd=3)
    Card.place(x=150,y=290)

    enUsername=Entry(width=21,font='Helvetica 12',bd=3)
    enUsername.place(x=150,y=330)

    #Submit Button
    
    submitButton= Button(text="Submit",width=10,font="arial 10 bold",command=lambda: registration_data(enName,varGen,enAge,enDob,enCno,Card,enUsername,enAcNo))
    submitButton.place(x=50,y=420)

    #Reset Button
    resetButton= Button(text="Reset",width=10,font="arial 10 bold",command=RegistrationWindow)
    resetButton.place(x=150,y=420)

    BackButton= Button(text="Back",width=10,font="arial 10 bold",command=Home)
    BackButton.place(x=250,y=420)

    signUpFrame.mainloop()
    
#Interfata tranzactii
def main_window():
    global account_userName
    f1=Frame(root,width=600,height=500)
    f1.place(x=0,y=0)
    root.title("Account")
    # Imagine on label    
    img=ImageTk.PhotoImage(Image.open('Additional_Files/main.jpg'))
    lbImg=Label(f1,width=600,height=500,image=img)
    lbImg.place(x=0,y=0)

    lblWel = Label(f1, text=f'Welcome\n{account_userName.get()}',bg="#FF6868",fg="white",font='Helvetica 10 bold')
    lblWel.place(x=470,y=35)

    
    btnBal=Button(f1,width=15,text='Balance Enquiry',fg="white",font='arial 16 bold',bg="#FF6868",borderwidth=5,command=balanceEnq)
    btnBal.place(x=0,y=182)

    btnMiniStat=Button(f1,width=15,text='Mini Statement',fg="white",font='arial 16 bold',bg="#FF6868",borderwidth=5,command=mini_statement)
    btnMiniStat.place(x=390,y=182)

    btnPINChange=Button(f1,width=15,text='Change PIN',fg="white",font='arial 16 bold',bg="#FF6868",borderwidth=5,command=changePIN)
    btnPINChange.place(x=0,y=290)

    btnWithdral=Button(f1,width=15,text='Cash Withdrawl',fg="white",font='arial 16 bold',bg="#FF6868",borderwidth=5,command=cach_withdrawl)
    btnWithdral.place(x=390,y=290)

    btnDeposit=Button(f1,width=15,text='Cash Deposit',fg="white",font='arial 16 bold',bg="#FF6868",borderwidth=5,command=cash_depo)
    btnDeposit.place(x=0,y=400)

    btnTrans=Button(f1,width=15,text='Cash Transfer',fg="white",font='arial 16 bold',bg="#FF6868",borderwidth=5,command=transfer)
    btnTrans.place(x=390,y=398)

    LogoutBTN=Button(f1,width=8,text='Logout',fg="white",font='arial 10 bold',bg="#FF6868",borderwidth=5,command=Home)
    LogoutBTN.place(x=260,y=465)

    f1.mainloop()

# Home window 
def Home():
    # Creating main window Frame
    mainFrame = Frame(root, height=500, width=600)
    mainFrame.place(x=0,y=0)

    #image Labeling
    img= ImageTk.PhotoImage(Image.open("Additional_Files/home.jpg"))
    labelForImage = Label(mainFrame,height=500,width=600,image=img)
    labelForImage.place(x=0,y=0)

    lblIntro = Label(mainFrame, text='Banca Toader',width=23,height=2,bg="#ffd60c",font='arial 18 bold')
    lblIntro.place(x=240,y=40)
    
    # LABELS
    #label for AC Number
    lblAcNo = Label(mainFrame, text='User Name',width=15,font='Times 12')
    lblAcNo.place(x=250,y=150)

    #label for PIN
    lblPIN = Label(mainFrame, text='PIN',width=15,font='times 12')
    lblPIN.place(x=250,y=200)

    enUser = Entry(width=20,font='times 12',bd=3)
    enUser.place(x=400,y=150)
    
    #Entry For password
    enPass = Entry(width=20,font='times 12',bd=3,show="*")
    enPass.place(x=400,y=200)

    #Buttons__
    #login Button
    loginButton= Button(text="Login",width=10,font="arial 10 bold",command=lambda:login(enUser,enPass))
    loginButton.place(x=360,y=250)
    #SignUp Button
    signupButton= Button(text="New User? Create an Account",width=30,font="arial 10 bold",command=RegistrationWindow)
    signupButton.place(x=280,y=300)

    mainFrame.mainloop()

Home()