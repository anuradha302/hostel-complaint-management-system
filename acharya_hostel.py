#!/usr/bin/env python
# coding: utf-8

# In[2]:


import sqlite3   #lets the program create/use a local SQLite database to store stu,in-charge and complaints   
from tkinter import *   #use to make GUI(graphical user interface) toolkite to build windows,buttons,labels,enteries
from tkinter import messagebox  #simple model dialogs(error/info)
from datetime import datetime  #used to record date n time of complaint                     

#Database Setup (SQlite-it is a lytwgt,serverless,self contained n highly reliable srt query lang db engine implemented as a c-lang library)
conn = sqlite3.connect('acharya_hostel.db')  #connects to (or create) the database file named (acharya_hostel.db)
c = conn.cursor() #to execute any SQL queries

#Create Students table
c.execute('''CREATE TABLE IF NOT EXISTS Students(  
            AUID TEXT PRIMARY KEY,
            Name TEXT,
            HostelID TEXT)''')#creates a stu table to store each student's auid,name n roomno.(IF NOT EXIST:prevent error if the table already exist)

#Create Incharge table
c.execute('''CREATE TABLE IF NOT EXISTS Incharge(
            ID TEXT PRIMARY KEY,
            Name TEXT,
            Password TEXT,
            Category TEXT)''')  #stores login credential for incharge(Id-pass) and their catogory(Mess,Room,Hygiene).

#Create Complaints table   #table to store all complaint with auto id,stu AUID link,status n timestamps
c.execute('''CREATE TABLE IF NOT EXISTS Complaints(
            ComplaintID INTEGER PRIMARY KEY AUTOINCREMENT,
            StudentAUID TEXT,
            Category TEXT,
            SubCategory TEXT,     
            Description TEXT,    
            Status TEXT,
            DateSubmitted TEXT,
            DateResolved TEXT,
            Rating INTEGER,
            FOREIGN KEY(StudentAUID) REFERENCES Students(AUID))''') #(foreign key):link complaint to the students who submitted it

conn.commit()   #saves any DDL(data defination language) chnges to the DB file. 
print("Database and tables created successfully!")

#Add Sample In-Charge Data 
c.execute("INSERT OR IGNORE INTO Incharge(ID, Name, Password, Category) VALUES ('mess01','Mess Incharge','mess123','Mess')")
c.execute("INSERT OR IGNORE INTO Incharge(ID, Name, Password, Category) VALUES ('room01','Room Incharge','room123','Room')")
c.execute("INSERT OR IGNORE INTO Incharge(ID, Name, Password, Category) VALUES ('hyg01','Hygiene Incharge','hyg123','Hygiene')")
conn.commit()   #adds sample incharge for testing
print("Sample in-charge data added!")   #(INSERT OR IGNORE : means add this only if its not already in the table)

#Student App
def student_app(): 
    global conn, c      #this function creates the student login window
    login_window = Tk()   #open a new app window
    login_window.title("Student Login")  #create small Tk window to let a student enter there AUID 
    login_window.geometry("400x250")  

    Label(login_window, text="Enter Your Acharya AUID:").pack(pady=10)  #creats a label asking the student to enter their AUID
    entry_auid = Entry(login_window)  #ENTRY:it is a text box where student type their AUID
    entry_auid.pack()  #PACK(PADDY):add some space around element 

    def login():  #when student click "login" this code run
        global conn, c
        student_auid = entry_auid.get().upper()  #it reads the AUID from the text box

        #Validate AUID format
        if not student_auid.startswith("AIT") or len(student_auid) != 12: #check if its start from AIT
            messagebox.showerror("Error", "AUID must start with 'AIT' and be 12 characters long")  #if its wrong it show an error message
            return

        #Check if student exists   
        c.execute("SELECT * FROM Students WHERE AUID=?", (student_auid,))
        student = c.fetchone()    #the app looks in the student table for that AUID..(fetchone:picks only the first row from that result)
        if not student:
            #if its not found,it add a New student, insert with blank Name and room number
            c.execute("INSERT INTO Students(AUID, Name, HostelID) VALUES (?,?,?)", (student_auid, '', ''))
            conn.commit()
        login_window.destroy() #then it closes the login window
        open_student_dashboard(student_auid) #n open the student dashboard for that AUID

    Button(login_window, text="Login", command=login).pack(pady=10)
    login_window.mainloop() 

#Student Dashboard 
def open_student_dashboard(student_auid):  #opens a big new window for that specific student
    global conn, c
    dash = Toplevel()   #show stu function update info submit complaints,view status(if remove stu cann't interact after login)
    dash.title(f"Student Dashboard - AUID: {student_auid}")  #show their AUID in the title bar
    dash.geometry("450x250")

    # Fetch student info
    c.execute("SELECT Name, HostelID FROM Students WHERE AUID=?", (student_auid,))
    student = c.fetchone()   #fetches the student's name and room number from the database 
    student_name = student[0]
    student_hostel = student[1]  #saves them in varriable so we can display them

    Label(dash, text="Acharya Hostel Complaint App", font=("Arial", 16)).pack(pady=10)  #adds the main heading at the top of the window

    # Student Info Frame 
    info_frame = Frame(dash)
    info_frame.pack(pady=10)  #creates a sec(frame) to hold name and room input box

    Label(info_frame, text="Name:").grid(row=0, column=0)
    entry_name = Entry(info_frame)    #lable and entry box for the Name
    entry_name.grid(row=0, column=1)
    entry_name.insert(0, student_name)  #Pre-fills the box wid the student's name from the database

    Label(info_frame, text="Room/Hostel Number:").grid(row=1, column=0)  
    entry_hostel = Entry(info_frame)   
    entry_hostel.grid(row=1, column=1)
    entry_hostel.insert(0, student_hostel)  #lable and entry box for the Room or Hostel number

    def update_info():  #this function runs when student clicks "update info"
        name = entry_name.get().strip()
        hostel = entry_hostel.get().strip()  
        if not name or not hostel:
            messagebox.showerror("Error", "Please enter both Name and Room/Hostel number")
            return
        c.execute("UPDATE Students SET Name=?, HostelID=? WHERE AUID=?", (name, hostel, student_auid))
        conn.commit()    #if updates their name and hostel number in the student table
        messagebox.showinfo("Success", "Info updated!") #show a sucess messagewhen done

    Button(info_frame, text="Update Info", command=update_info).grid(row=2, column=0, columnspan=2, pady=5)

    # Complaint Submission Frame 
    frame = Frame(dash)
    frame.pack(pady=10)

    Label(frame, text="Category:").grid(row=0, column=0)
    category_var = StringVar()
    category_menu = OptionMenu(frame, category_var, "Mess Related", "Room Related", "Hygiene Related")
    category_menu.grid(row=0, column=1)  #let stu choose the category and describe the problem

    Label(frame, text="Sub-Category (if Room):").grid(row=1, column=0)
    sub_var = StringVar()
    sub_menu = OptionMenu(frame, sub_var, "Roommate Issues", "Furniture/Keys Issues", "Electricity Issues")
    sub_menu.grid(row=1, column=1) #if the complaint is room-related,they can also select a sub-category 

    Label(frame, text="Complaint Description:").grid(row=2, column=0)
    desc_entry = Entry(frame, width=50)
    desc_entry.grid(row=2, column=1)  #entry box where the student write the complaint details

    def submit_complaint(): #this function name runs when student clicks the submit complaint button
        global conn, c   #this lets us run SQL command here
        cat = category_var.get()  #read the currently selected value from the catogory
        subcat = sub_var.get() if cat == "Room Related" else ""  
        desc = desc_entry.get()  #gets the text that the std typed into the description entry box(the main complaibn std wants to submit
        if not cat or not desc:  
            messagebox.showerror("Error", "Please fill all required fields")
            return
        now = datetime.now().strftime("%Y-%m-%d %H:%M") #gets the current date and time and formates it as a string
        c.execute("INSERT INTO Complaints(StudentAUID, Category, SubCategory, Description, Status, DateSubmitted) VALUES (?,?,?,?,?,?)",
                  (student_auid, cat, subcat, desc, "Received", now)) #runs an SQL INSERT command to add a new row into the Complaint table
        conn.commit()  #save n chng the database file permanently...without COMT(),the new complaint would not persist
        messagebox.showinfo("Success", "Complaint Submitted!") #show a popup informing a std that the complaint was saved succesfully
        desc_entry.delete(0, END)  #clears the description input box so the stu can type a new complaint
        load_complaints() #this immediadtly display the newly submitted complaint in the UI

    Button(frame, text="Submit Complaint", command=submit_complaint).grid(row=3, column=0, columnspan=2, pady=10)

    #  Complaint Status List
    table_frame = Frame(dash) #creates a new frame widget inside the dash window
    table_frame.pack(pady=10)  #place the table_frame into the window 

    complaint_listbox = Listbox(table_frame, width=100) #creates a listbox widget placed inside table_frame 
    complaint_listbox.pack()  #places the listbox inside the table_frame using pack()

    def load_complaints():  #this function is responsible for fetching complaints from the database 
        global conn, c    #declare the function will use the global variables(conn n c) that lets the function execute SQL queries using the same connection
        complaint_listbox.delete(0, END)    #clears the listbox before reloading items.
        c.execute("SELECT ComplaintID, Category, SubCategory, Description, Status FROM Complaints WHERE StudentAUID=?", (student_auid,))
        for comp in c.fetchall():
            complaint_listbox.insert(END, f"ID:{comp[0]} | Category:{comp[1]} | SubCategory:{comp[2]} | Desc:{comp[3]} | Status:{comp[4]}")

    load_complaints()  #queries all complaints by that stu n displays them in a listbox for tracking status.
    dash.mainloop()

# In-Charge App 
def incharge_app():  #this runs the login interface for hostel in charges
    global conn, c  #allow the function to use the existing database connection and cursor created earlier
    login_window = Tk()   #creates the main Tkinter window
    login_window.title("In-Charge Login")  #sets the window's title
    login_window.geometry("500x380")   #sets the window size 

    Label(login_window, text="In-Charge ID:").pack(pady=5)  #creates the label promoting the user for their incahrge id
    entry_id = Entry(login_window)  #adds an entry text box for entering the id
    entry_id.pack()        #adds the vertical padding (spacing)
    Label(login_window, text="Password:").pack(pady=5)  #another label prompts for a password
    entry_pass = Entry(login_window, show="*")  #the pass entry field uses "show=*" to mask input
    entry_pass.pack()    #creates GUI for in charges to enter ID n password

    def login():  #define an inner function "login()"-its called when the user click the login button
        global conn, c   
        incharg_id = entry_id.get()  #retrives the values from the two text boxes
        password = entry_pass.get()
        c.execute("SELECT * FROM Incharge WHERE ID=? AND Password=?", (incharg_id, password))  #execute the SQL query that checks if the entered ID n pass match any record in the table
        incharge = c.fetchone()   #it returns one record if found or none if no match
        if incharge:  #if a valid record (incharge) exits
            login_window.destroy()  #closes the login window
            open_incharge_dashboard(incharg_id, incharge[3])  #open the incharge dashboard by calling open_inc_dashb n passes
        else:                                                                #incharge[3]-the 4th column in the table
            messagebox.showerror("Error", "Invalid ID or Password")  #if no record found show error

    Button(login_window, text="Login", command=login).pack(pady=10)    #adds a login button which calls the login() function when clicked
    login_window.mainloop()   #starts the tkinter main event loop,which keeps the window open and responsive

def open_incharge_dashboard(incharge_id, category):  #define the main dshboard function,opened after a successful login 
    global conn, c        #this make sure the fuc can use the existing database connection n cursor created earlier
    dash = Toplevel()      #creats a new main Tkinyer window for the incharge dashboard
    dash.title(f"In-Charge Dashboard - {category}")     #set the title of the window e.g-"incharge dashboard" category
    dash.geometry("950x600")   #set the size 

    Label(dash, text=f"{category} In-Charge Dashboard", font=("Arial", 16)).pack(pady=10)  #creates a lable at the top of the window displaying the incharge's catogory(eg."mess,incharge dashboard")

    table_frame = Frame(dash)  #create a frame inside the main window.
    table_frame.pack(pady=10)   # this window will hold the listbox that show all complaints

    complaint_listbox = Listbox(table_frame, width=130) #creates a listbox widget where all complaints will be listed...width=130 means it can display upto 130 characters per line
    complaint_listbox.pack()

    status_var = StringVar()   #creates a Twinter variable that will store the value of the dropdown menu
    OptionMenu(dash, status_var, "Working", "Pending", "Resolved").pack(pady=5)  #creates a dropdown with three options:working,pending,resolved...the selected value is stored in status_var
                                                                                  #(packpady=5) adds a little vertical spacing
    def load_complaints():   #define a nested function that will load all complaints assingned to this incharge's catag from the database
        global conn, c
        complaint_listbox.delete(0, END) #display complaint n provides a dropdown to choose new status.

#Join Complaints with Students to show room number
        c.execute('''SELECT Complaints.ComplaintID, Complaints.StudentAUID, Students.HostelID, 
                            Complaints.SubCategory, Complaints.Description, Complaints.Status
                     FROM Complaints
                     LEFT JOIN Students ON Complaints.StudentAUID = Students.AUID
                     WHERE Complaints.Category LIKE ?''', (f"%{category}%",)) 

        for comp in c.fetchall():  #returns all results from the last query
            complaint_id, auid, hostel, subcat, desc, status = comp
            complaint_listbox.insert(
                END,
                f"ID:{complaint_id} | Student:{auid} | Room:{hostel or 'N/A'} | SubCategory:{subcat} | Desc:{desc} | Status:{status}"
            )  #for each complaint(comp),it formates the data into a readable string and insert other into the listbox

    def update_status():  #define sanother nested fun that will be used when the incharge wants to change the status of a complaint
        global conn, c   #uses the same database connection
        selected = complaint_listbox.curselection()  #gets the index of the complaint currently selected in the listbox
        if not selected:      
            messagebox.showerror("Error", "Select a complaint first")
            return        #if no complaint is selected show an error popup and exit the fuction
        index = selected[0]
        item_text = complaint_listbox.get(index)  #gets the actual text of the selected complaint entry 
        complaint_id = int(item_text.split("|")[0].split(":")[1])  #extract the complaint id from the selected text
        new_status = status_var.get()                  #gets the status value chosen from the dropdown 
        now = datetime.now().strftime("%Y-%m-%d %H:%M") if new_status == "Resolved" else None  #if the new status is ressolved stire the current data n tym..otherwise leave it as none
        c.execute("UPDATE Complaints SET Status=?, DateResolved=? WHERE ComplaintID=?", (new_status, now, complaint_id))  #runs an SQL UPDATE query to change the complaint status n update the "dataresolved" column if applicable
        conn.commit()           #save the change to the database
        load_complaints()  #reload the complaints list to show the update status immediatly
        messagebox.showinfo("Success", "Status updated!")  #show a popup mess saying that the status was successfully updated

    Button(dash, text="Update Status", command=update_status).pack(pady=5)  #creates a button labelled 'update status'...when clicked it runs the update_status() function
    load_complaints()   #loads all complaints immediately when the dashboard opens(so that the list box isn't empty)
    dash.mainloop() #starts the Twinkter event loop - keeps the window open n responsive untill close

#Run App
#student_app()
#incharge_app()


# In[ ]:




