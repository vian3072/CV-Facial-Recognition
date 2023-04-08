from cgi import test
from msilib.schema import AdminExecuteSequence
from tkinter import *
from tkinter.ttk import Treeview
from turtle import color, width
from typing import Literal
from imutils import paths
from PIL import Image, ImageTk
from datetime import datetime
import pandas as pd
import cv2
import face_recognition
import pickle
import os
import tkinter
import shutil
import tkinter as tk
from numpy import place
import csv

registered_username = "1"
registered_password = "2"

namesaved = "str"

def cv(): #adapted from https://www.mygreatlearning.com/blog/face-recognition/
    daynow=datetime.today()
    timenow=datetime.now()
    date_now = daynow.strftime("%d/%m/%Y")
    time_now = timenow.strftime("%H:%M:%S")
    global namesaved
    #find path of xml file containing haarcascade file 
    cascPathface = os.path.dirname(
     cv2.__file__) + "/data/haarcascade_frontalface_alt2.xml"
    # load the harcaascade in the cascade classifier
    faceCascade = cv2.CascadeClassifier(cascPathface)
    # load the known faces and embeddings saved in last file
    data = pickle.loads(open('face_enc', "rb").read())
    print(data)
     
    print("Streaming started") 
    video_capture = cv2.VideoCapture(0)
    # loop over frames from the video file stream
    while True:
        # grab the frame from the threaded video stream
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray,
                                             scaleFactor=1.1,
                                             minNeighbors=5,
                                             minSize=(60, 60),
                                             flags=cv2.CASCADE_SCALE_IMAGE)
     
        # convert the input frame from BGR to RGB 
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # the facial embeddings for face in input
        encodings = face_recognition.face_encodings(rgb)
        names = []
        # loop over the facial embeddings incase
        # we have multiple embeddings for multiple fcaes
        for encoding in encodings:
           #Compare encodings with encodings in data["encodings"]
           #Matches contain array with boolean values and True for the embeddings it matches closely
           #and False for rest
            matches = face_recognition.compare_faces(data["encodings"],              
             encoding)
            #set name =inknown if no encoding matches
            name = "Unknown"
            # check to see if we have found a match
            if True in matches:
                #Find positions at which we get True and store them
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                # loop over the matched indexes and maintain a count for
                # each recognized face face
                for i in matchedIdxs:
                    #Check the names at respective indexes we stored in matchedIdxs
                    name = data["names"][i]
                    #increase count for the name we got
                    counts[name] = counts.get(name, 0) + 1
                #set name which has highest count
                name = max(counts, key=counts.get)
     
     
            # update the list of names
            names.append(name)
            # loop over the recognized faces
            for ((x, y, w, h), name) in zip(faces, names):
                # rescale the face coordinates
                # draw the predicted face name on the image
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                 0.75, (0, 255, 0), 2)
                namesaved=name
                entry = pd.DataFrame([[date_now, time_now, namesaved]], columns=["Date", "Time", "User"])
                entry.to_csv("ScanData.csv", mode = "a", index=FALSE, header = FALSE)
                print(namesaved)
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    video_capture.release()
    cv2.destroyAllWindows()

def encodeimages(): # adapted from https://www.mygreatlearning.com/blog/face-recognition/
    #get paths of each file in folder named Images
    #Images here contains my data(folders of various persons)
    imagePaths = list(paths.list_images('Images'))
    knownEncodings = []
    knownNames = []
    # loop over the image paths
    for (i, imagePath) in enumerate(imagePaths):
        # extract the person name from the image path
        name = imagePath.split(os.path.sep)[-2]
        # load the input image and convert it from BGR (OpenCV ordering)
        # to dlib ordering (RGB)
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        #Use Face_recognition to locate faces
        boxes = face_recognition.face_locations(rgb,model='hog')
        # compute the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb, boxes)
        # loop over the encodings
        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)
    #save emcodings along with their names in dictionary data
    data = {"encodings": knownEncodings, "names": knownNames}
    #use pickle to save data into a file for later use
    f = open("face_enc", "wb")
    f.write(pickle.dumps(data))
    f.close()

def Delete_User():
    canvas = Tk()
    canvas.geometry ("500x600")
    canvas.title("Access Control")
    path = ("Images")

    menubar = Menu(canvas)

    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Add User", command=lambda:[canvas.destroy(), Add_User()])
    filemenu.add_separator()
    filemenu.add_command(label="Home", command=lambda:[canvas.destroy(),home_screen()])
    filemenu.add_command(label="Log Out", command=lambda:[canvas.destroy(),lock_screen()])
    menubar.add_cascade(label="File", menu=filemenu)
   
    canvas.config(menu=menubar)

    directory_contents = os.listdir(path)
    print(directory_contents)
    nameindir = tkinter.StringVar(value=directory_contents)
    listnames = Listbox(canvas, listvariable=nameindir, width = 50,height=37)
    listnames.grid(column=0, row=0)
    def dirdelfunc():
        selectednames = str(listnames.get(ANCHOR))
        print(selectednames)
        dirpaths = str("Images/" + selectednames)
        print(dirpaths)
        if os.path.exists(dirpaths):
            shutil.rmtree(dirpaths)
            top = Toplevel()
            top.geometry("400x70")
            top.title("Success")
            l2 = Label(top, text = "User Succesfully deleted, please exit this tab for re encoding", font = ("Arial", 11))
            l2.pack()
            top.mainloop()
            home_screen()
            return
        else:
            top = Toplevel()
            top.geometry("300x70")
            top.title("Error")
            l2 = Label(top, text = "Something happened", font = ("Arial", 11))
            l2.pack()
            top.mainloop()


    dirdel = Button(canvas, text = "Delete User", command=lambda:[dirdelfunc(), canvas.destroy()], font=("Arial", 13)).place(x=350, y=550)
    label1 = Label(canvas, text="click username and click delete", font=("Arial",10)).place(x=310, y=520)

    canvas.mainloop()

def Add_User():
    width, height = 516, 228 
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    canvas = tk.Tk()
    canvas.bind('<Escape>', lambda e: canvas.quit())
    canvas.geometry("650x500")
    lmain = tk.Label(canvas)
    lmain.pack()
    lmain.place(x=1, y=1)
    
    parent = "Images/"

    menubar = Menu(canvas)

    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Delete User", command=lambda:[canvas.destroy(), Delete_User()])
    filemenu.add_separator()
    filemenu.add_command(label="Home", command=lambda:[canvas.destroy(),home_screen()])
    filemenu.add_command(label="Log Out", command=lambda:[canvas.destroy(),lock_screen()])
    menubar.add_cascade(label="File", menu=filemenu)
   
    canvas.config(menu=menubar)
    

    def show_frame():     #This part of the code is adapted from Kieleth's code from Stack overflow thread: https://stackoverflow.com/questions/16366857/show-webcam-sequence-tkinter
        _, frame = cap.read()
        frame = cv2.flip(frame, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
        lmain.after(10, show_frame)
    
    def take_picture():
        result, image=cap.read()
        if result:
            path = str(parent + (namevariable.get()))
            print(path)
            if os.path.exists(path):
                print("Found FIle")
                cv2.imwrite(os.path.join(path, ((picname.get()) + ".jpg")), image)
            else:
                print("file not found, making a new dir")
                os.mkdir(path)
                cv2.imwrite(os.path.join(path, ((picname.get()) + ".jpg")), image)
    
    show_frame()
    
    label1 = tk.Label(canvas, text = "Position the User's face in the middle of the frame, then type the name of the user, and press the ADD button", justify="center", anchor="center").place(x=35, y=370)
    namevariable = tk.StringVar()
    picname = tk.StringVar()
    nameinput = tk.Entry(canvas, textvariable=namevariable).place(x=325, y=400)
    picnameinput = tk.Entry(canvas, textvariable=picname).place(x=325,y=425)
    label2 = tk.Label(canvas, text="New Username").place(x=235, y=400)
    label3 = tk.Label(canvas, text="Picture Name").place(x=235, y=425)
    photobutton = tk.Button(canvas, text="ADD", command=lambda:[take_picture()], justify="center", width=15).place(x=330, y=450)
    
    canvas.mainloop()

def home_screen():
    encodeimages() ###############################################
    canvas = Tk()
    canvas.geometry ("500x600")
    canvas.title("Home Page")

    menubar = Menu(canvas)

    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Add User", command=lambda:[canvas.destroy(), Add_User()])
    filemenu.add_command(label="Delete User", command=lambda:[canvas.destroy(), Delete_User()])
    filemenu.add_separator()
    filemenu.add_command(label="Log Out", command=lambda:[canvas.destroy(),lock_screen()])
    menubar.add_cascade(label="File", menu=filemenu)

    columns = ("1", "2", "3")
    pohon = Treeview(canvas, show = "headings", columns=columns, height=28)
    pohon.column("1", width=100, stretch=NO)
    pohon.column("2", width=80, stretch=NO)
    pohon.column("3", width=100, stretch=NO)
    pohon.heading("1", text = "Date")
    pohon.heading("2", text = "Time")
    pohon.heading("3", text = "entry")
    yscrollbar = Scrollbar(canvas, command = pohon.yview)
    pohon.configure(yscroll=yscrollbar.set)

    with open("ScanData.csv", newline="")as file:
        for entry in csv.reader(file):
            pohon.insert("", END, values = entry)
    pohon.grid(row=0, column=0, sticky="nsew")
    yscrollbar.grid(row=0, column=1, sticky=N + S)

    
    button1 = Button(canvas, text = "Start Logging", command=lambda:cv(), width=25, height=2, font=("Arial", 9)).place(x=305,y=550)
    label1 = Label(canvas, text="press 'Q' key to exit logging", font=("Arial",10)).place(x=313, y=520)

    canvas.config(menu=menubar)
    canvas.mainloop()

def lock_screen():
    def verify():
        if (username_input.get()) == registered_username and (password_input.get()) == registered_password:
            print("Password is correct") # Debugging purposes
            canvas.destroy()
            print("goto home page")
            home_screen()        
        elif (username_input.get()) == "" or (password_input.get()) == "" or (username_input.get()) == "" and (password_input.get()) == "":
            print("password or username or both empty") # Debugging purposes
            top = Toplevel()
            top.geometry("300x70")
            top.title("Error")
            l2 = Label(top, text = "Username and Password empty!", font = ("Arial", 11))
            l2.pack()
            top.mainloop()
        else:
            print("password and username combo incorrect") # Debugging purposes
            top = Toplevel()
            top.geometry("300x70")
            top.title("Error")
            l2 = Label(top, text = "Username and Password wrong or error!", font = ("Arial", 11))
            l2.pack()
            top.mainloop()

    canvas = Tk()
    canvas.geometry ("900x500")
    canvas.title("Login Page")
 
    Label(canvas, text='Home Security Systems', font=("Arial", 20), anchor=CENTER, justify=CENTER).place(x=90, y=25)
    Label(canvas, text='Username').place(x=80, y=200)
    Label(canvas, text='Password').place(x=80, y=250)

    username_input = tkinter.StringVar()
    password_input = tkinter.StringVar()
    username = tkinter.Entry(canvas, textvariable=username_input)
    password = tkinter.Entry(canvas, textvariable=password_input)
    username.place(x=150, y=200, width=200, height=30, bordermode=OUTSIDE)
    password.place(x=150, y=250, width=200, height=30, bordermode=INSIDE)

    sideimage = Image.open("code images\DJI_0066.JPG")
    resized_img= sideimage.resize((450, 500), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(resized_img)
    Label(canvas, image=img).place(x=450)

    login = Button(canvas, text="LOGIN", command=lambda: verify()).place(x=225, y=370, width=110, height=40, anchor=CENTER)

    canvas.mainloop()

lock_screen()
