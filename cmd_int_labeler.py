import csv
import datetime
import time
import math
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
import os
from functools import partial

# mode 1 = all interface
# mode 2 = only interface progress (cmd file inputs)
# mode 3 = no interface (cmd file inputs)
# mode 4 = file selector interface inputs, no interface progress


def open_it():
    os.startfile(output_title)


def get_out2():
    root.quit()
    exit(0)


root = Tk()
root.title('The Labeler')
# root.iconbitmap('Bolt.ico')
root.configure(background='black')
size = 500
root.geometry(str(size + 200) + "x" + str(size + 300) + "+50+50")

w = Canvas(root, width=size + 300, height=1, background='white')

# Progress bar widget

progress = Progressbar(root, orient=HORIZONTAL,
                       length=size, mode='determinate')

progress2 = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')

progress3 = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')

progress4 = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')

progress5 = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')

progress6 = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')

progress7 = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')

root.withdraw()

titler = Label(root, text='The Labeler', font='bold', foreground='white', background='black')
titler.configure(font=("Arial Black", 50))
titler.pack(pady=20)

w.pack()

reader = Label(root, text='Waiting to Read Files...', foreground='yellow', background='black')
reader.pack(pady=10)
progress.pack(pady=5)

fgrouper = Label(root, text='Waiting to Group Flights...', foreground='yellow', background='black')
fgrouper.pack(pady=10)
progress2.pack(pady=5)

egrouper = Label(root, text='Waiting to Group Engines...', foreground='yellow', background='black')
egrouper.pack(pady=10)
progress3.pack(pady=5)

assigner = Label(root, text='Waiting to Assign Errors...', foreground='yellow', background='black')
assigner.pack(pady=10)
progress4.pack(pady=5)

updater = Label(root, text='Waiting to Update Errors...', foreground='yellow', background='black')
updater.pack(pady=10)
progress5.pack(pady=5)

severer = Label(root, text='Waiting to Update Severity...', foreground='yellow', background='black')
severer.pack(pady=10)
progress6.pack(pady=5)

printer = Label(root, text='Waiting to Print to csv...', foreground='yellow', background='black')
printer.pack(pady=10)
progress7.pack(pady=5)

timer = Label(root, text='Awaiting Completion...', foreground='yellow', background='black')
timer.pack(pady=15)

quiter = Label(root, text='TO QUIT: CTRL + C (or stop in IDE)')
quiter.pack(side=LEFT)

# global variables defining length of standard flight
TIME_INTERVAL_HOUR = 1
TIME_INTERVAL_MIN = 30


def try_ito(filename13):
    with open(filename13) as csv_file:
        rows_by = []
        csv_reader = csv.reader(csv_file)

        for lines in csv_reader:
            rows_by.append(lines)

        col_by = []

        for x in range(len(rows_by[0])):
            addition = []
            for lines2 in rows_by:
                addition.append(lines2[x])

            col_by.append(addition)
    return rows_by, col_by


# string in datetime format to datetime object
def convertdt(datetime1):
    date_tester1 = datetime1.split()
    first_test = datetime.datetime(int(date_tester1[0].split('/')[2]), int(date_tester1[0].split('/')[0]),
                                   int(date_tester1[0].split('/')[1]), int(date_tester1[1].split(':')[0]),
                                   int(date_tester1[1].split(':')[1]))

    return first_test


# accepts two strings from lists created and time interval which indicates range for same flight
def within_5(datetime1, datetime2, time_interval_hour, time_interval_min):
    # split date and time by the space between them
    first_test = convertdt(datetime1)
    second_test = convertdt(datetime2)
    # find difference between times ensuring positive result
    if second_test > first_test:
        answer = second_test - first_test
    else:
        answer = first_test - second_test
    # determines if time falls within time interval
    if answer <= datetime.timedelta(hours=time_interval_hour, minutes=time_interval_min):
        return True
    else:
        return False


class Flight:
    def __init__(self, esn, start, end, instance_list, errors, final_e):
        self.esn = esn
        self.start = start
        self.end = end
        # self.columns = columns
        self.instance_list = instance_list
        self.errors = errors
        self.final_e = final_e


class Engine:
    def __init__(self, serial_number, flight_list):
        self.serial_number = serial_number
        self.flight_list = flight_list


class Error:
    def __init__(self, code, name, severity):
        self.code = code
        self.name = name
        self.severity = severity


# function for grouping flights based on time instances, assumes organized by time
def group_flights(prf_list):
    # initialize empty grouped flight list
    grouped_flight_list = []
    i = 0
    chunks_siz = len(prf_list)
    chunk = 100 / chunks_siz
    fgrouper.configure(
        text='Grouping Flights... ({:,}'.format(len(prf_list)) + ' instances) --> ' + str(progress2['value']) + '%',
        foreground='white')
    # root.update_idletasks()

    for element in prf_list:

        if i == 0:
            # on the first instance a flight object must be initialized
            grouped_flight_list.append(Flight(element[0], element[2], element[2], [], [], Error("NONE", "NONE", 0)))
            grouped_flight_list[-1].instance_list.append(i + 1)
        else:

            # if the esn is the same as the last flight and the time corresponds: add the current instance to the
            # flight list of the last flight object in the list of flight objects
            if grouped_flight_list[-1].esn == element[0] and (
                    within_5(grouped_flight_list[-1].start, element[2], TIME_INTERVAL_HOUR,
                             TIME_INTERVAL_MIN) or within_5(grouped_flight_list[-1].end, element[2],
                                                            TIME_INTERVAL_HOUR, TIME_INTERVAL_MIN)):
                grouped_flight_list[-1].instance_list.append(i + 1)
                # update start and end time if necessary
                if convertdt(element[2]) < convertdt(grouped_flight_list[-1].start):
                    grouped_flight_list[-1].start = element[2]
                if convertdt(element[2]) > convertdt(grouped_flight_list[-1].end):
                    grouped_flight_list[-1].end = element[2]
            else:
                grouped_flight_list.append(
                    Flight(element[0], element[2], element[2], [], [], Error("NONE", "NONE", 0)))
                grouped_flight_list[-1].instance_list.append(i + 1)

        progress2['value'] += chunk

        fgrouper.configure(text='Grouping Flights... ({:,}'.format(len(prf_list)) + ' instances) --> {:6.2f}'.format(
            progress2['value']) + '%', foreground='white')
        root.update_idletasks()
        i += 1
    fgrouper.configure(text='Grouping Flights Complete. ({:,}'.format(len(prf_list)) + ' instances) --> {:6.2f}'.format(
        progress2['value']) + '%', foreground='green')
    root.update_idletasks()
    return grouped_flight_list


# takes grouped flight list and creates a list of engines that contain grouped flights
def group_engines(grouped_flight_list):
    engine_list = []
    temp_list_e = []
    for element in grouped_flight_list:
        # first creates engine objects of all unique esn
        if element.esn not in temp_list_e:
            engine_list.append(Engine(element.esn, []))
            temp_list_e.append(element.esn)
    chunk2 = 100 / len(grouped_flight_list)
    egrouper.configure(
        text='Grouping Engines... ({:,}'.format(len(grouped_flight_list)) + ' flights) --> {:6.2f}'.format(
            progress3['value']) + '%', foreground='white')
    root.update_idletasks()
    for flight in grouped_flight_list:
        # second assigns flights to corresponding engine objects
        for engine in engine_list:
            if engine.serial_number == flight.esn:
                engine.flight_list.append(flight)
        progress3['value'] += chunk2
        egrouper.configure(
            text='Grouping Engines... ({:,}'.format(len(grouped_flight_list)) + ' flights) --> {:6.2f}'.format(
                progress3['value']) + '%', foreground='white')
        root.update_idletasks()

    egrouper.configure(
        text='Grouping Engines Complete. ({:,}'.format(len(grouped_flight_list)) + ' flights) --> {:6.2f}'.format(
            progress3['value']) + '%', foreground='green')
    root.update_idletasks()
    return engine_list


# assigns error to flight by matching instance to esn then finding if there is a corresponding flight and labels it
def assign_errors(engine_list, flt_list):
    # root.update_idletasks()
    chunk3 = 100 / len(flt_list)
    assigner.configure(
        text='Assigning Errors... ({:,}'.format(len(flt_list)) + ' occurrences) --> {:6.2f}'.format(
            progress4['value']) + '%', foreground='white')
    root.update_idletasks()
    for row in flt_list:
        for engine in engine_list:
            # first checks if esn values line up, if not on to the next engine
            if engine.serial_number == row[0]:
                for flight in engine.flight_list:
                    # checks if error instance lines up with a flight in the engine object
                    if within_5(flight.start, row[2], TIME_INTERVAL_HOUR, TIME_INTERVAL_MIN) or within_5(
                            flight.end, row[2], TIME_INTERVAL_HOUR, TIME_INTERVAL_MIN):
                        flight.errors.append(Error(row[7], "NONE", 0))
        progress4['value'] += chunk3
        assigner.configure(
            text='Assigning Errors... ({:,}'.format(len(flt_list)) + ' occurrences) --> {:6.2f}'.format(
                progress4['value']) + '%', foreground='white')
        root.update_idletasks()
    assigner.configure(
        text='Assigning Errors Complete. ({:,}'.format(len(flt_list)) + ' occurrences) --> {:6.2f}'.format(
            progress4['value']) + '%', foreground='green')
    root.update_idletasks()


# assigns error severities based on error code
def update_errors(engine_list, ec_list):
    # update one engine at a time
    chunk4 = 100 / len(engine_list)
    updater.configure(
        text='Updating Errors... ({:,}'.format(len(engine_list)) + ' engines) --> {:6.2f}'.format(
            progress5['value']) + '%', foreground='white')
    root.update_idletasks()
    for engine in engine_list:
        # go through one flight at a time
        for flight in engine.flight_list:
            # go through errors in flight
            for error in flight.errors:
                updated = 0
                # match up error classification with error instance
                for row in ec_list:
                    if error.code == row[0]:
                        error.name = row[1]
                        error.severity = row[3]
                        updated = 1
                # if error does not appear in error classification
                if updated == 0:
                    error.name = "NONE"
                    error.severity = 0
        progress5['value'] += chunk4

        updater.configure(
            text='Updating Errors... ({:,}'.format(len(engine_list)) + ' engines) --> {:6.2f}'.format(
                progress5['value']) + '%', foreground='white')
        root.update_idletasks()
    updater.configure(
        text='Updating Errors Complete. ({:,}'.format(len(engine_list)) + ' engines) --> {:6.2f}'.format(
            progress5['value']) + '%', foreground='green')
    root.update_idletasks()


def update_severity(engine_list):
    i = 0
    chunk5 = 100 / len(engine_list)
    severer.configure(
        text='Updating Severity... ({:,}'.format(len(engine_list)) + ' engines) --> {:6.2f}'.format(
            progress6['value']) + '%', foreground='white')
    root.update_idletasks()
    for engine in engine_list:
        for flight in engine.flight_list:
            top_sev = 0
            for error in flight.errors:
                if int(error.severity) > int(top_sev):
                    flight.final_e = error
                    top_sev = error.severity
        i += 1
        progress6['value'] += chunk5
        severer.configure(
            text='Updating Severity... ({:,}'.format(len(engine_list)) + ' engines) --> {:6.2f}'.format(
                progress6['value']) + '%', foreground='white')
        root.update_idletasks()
    severer.configure(
        text='Updating Severity Complete. ({:,}'.format(len(engine_list)) + ' engines) --> {:6.2f}'.format(
            progress6['value']) + '%', foreground='green')
    root.update_idletasks()


def output_csv(engine_list, output_filename, prf_titles, prf_col):
    out1 = open(output_filename, 'w')
    i = 0
    out1.write("ESN, Start, End,")
    for piece in prf_titles:
        if i == 55 or i == 87 or i == 88:
            out1.write(piece + ",")
        if i not in [0, 1, 2, 4, 5, 8, 12, 14, 21, 23, 36, 37, 50, 54, 55, 56, 57, 58, 87, 88, 90, 97]:
            out1.write(str(piece) + " min,")
            out1.write(str(piece) + " max,")
            out1.write(str(piece) + " avg,")
            out1.write(str(piece) + " st dev,")
        i += 1
    out1.write("Error Classifier \n")
    chunk7 = 100 / len(engine_list)
    printer.configure(
        text='Printing to csv... ({:,}'.format(len(engine_list)) + ' engines) --> {:6.2f}'.format(
            progress7['value']) + '%', foreground='white')
    root.update_idletasks()
    for enginer in engine_list:
        for flight in enginer.flight_list:
            out1.write(flight.esn + "," + flight.start + "," + flight.end + ",")
            current_in = flight.instance_list
            i = 3
            while i < 99:
                ma_list = []
                if i == 55 or i == 87 or i == 88:
                    out1.write(prf_col[i][current_in[0]] + ",")
                if i not in [0, 1, 2, 4, 5, 8, 12, 14, 21, 23, 36, 37, 50, 54, 55, 56, 57, 58, 87, 88, 90, 97]:
                    for col in current_in:
                        if prf_col[i][col] == '':
                            ma_list.append('0')
                        else:
                            ma_list.append(prf_col[i][col])

                    total = 0
                    length = 0
                    mini = 999999
                    maxi = -999999
                    for part in ma_list:
                        if float(part) < float(mini):
                            mini = float(part)
                        if float(part) > float(maxi):
                            maxi = float(part)
                        total = float(total) + float(part)
                        length += 1

                    out1.write(str(mini) + ",")
                    out1.write(str(maxi) + ",")
                    meaner = total / float(length)
                    im_to = 0
                    for part in ma_list:
                        im_to = float(im_to) + (float(part) - meaner) ** 2
                    ready = im_to / float(length)
                    stde = math.sqrt(ready)
                    out1.write(str(meaner) + ",")

                    out1.write(str(stde) + ",")
                i += 1
            if flight.final_e.severity == '2':
                out1.write('Grounding\n')
            else:
                out1.write("Non-grounding\n")

            # out1.write(str(flight.final_e.code) + "," + flight.final_e.name + "," + str(flight.final_e.severity) + "\n")
        progress7['value'] += chunk7
        printer.configure(
            text='Printing to csv... ({:,}'.format(len(engine_list)) + ' engines) --> {:6.2f}'.format(
                progress7['value']) + '%', foreground='white')
        root.update_idletasks()
    printer.configure(text='Printing to: "' + output_filename + '" Complete. ({:,}'.format(
        len(engine_list)) + ' engines) --> {:6.2f}'.format(
        progress7['value']) + '%', foreground='green')
    root.update_idletasks()


def runit(mode, instance_file, error_occurrences_file, error_class_file, output_file):
    if mode != 4 and mode != 3:
        root.update()
        root.deiconify()
    root.configure(background='black')
    reader.configure(text='Reading Files... (3 files) --> {:6.2f}'.format(
        progress['value']) + '%', foreground='white')
    root.update_idletasks()
    progress['value'] += 0
    root.update_idletasks()
    start_time = time.time()
    print("Reading Files...")
    instance_list = try_ito(instance_file)
    progress['value'] += 33
    reader.configure(text='Reading Files... (3 files) --> {:6.2f}'.format(
        progress['value']) + '%', foreground='white')
    root.update_idletasks()
    root.update_idletasks()
    error_o_list = try_ito(error_occurrences_file)
    progress['value'] += 33
    reader.configure(text='Reading Files... (3 files) --> {:6.2f}'.format(
        progress['value']) + '%', foreground='white')
    root.update_idletasks()
    root.update_idletasks()
    time.sleep(.5)
    ec_list = try_ito(error_class_file)
    progress['value'] += 34
    reader.configure(text='Reading Files Complete. (3 files) --> {:6.2f}'.format(
        progress['value']) + '%', foreground='green')
    root.update_idletasks()

    print("(1/8) Files Read.")
    print("Grouping Flights...")

    grouped_flights = group_flights(instance_list[0][1:])
    print("(2/8) Flights grouped.")
    print("Grouping Engines...")

    grouped_engines = group_engines(grouped_flights)
    print("(3/8) Engines Grouped.")
    print("Assigning Errors...")
    assign_errors(grouped_engines, error_o_list[0][1:])

    print("(4/8) Errors assigned.")
    print("Updating Errors...")

    update_errors(grouped_engines, ec_list[0][1:])
    print("(5/8) Errors updated.")
    print("Updating Severity...")

    update_severity(grouped_engines)
    print("(6/8) Severity updated.")
    print("(7/8) printing to: " + output_file)

    output_csv(grouped_engines, output_file, instance_list[0][0], instance_list[1])
    timer.configure(text='This took: --- %s seconds --- to complete' % (time.time() - start_time), foreground='green')
    root.update_idletasks()
    print("(8/8) Complete. --- %s seconds ---" % (time.time() - start_time))
    if mode == 4 or mode == 3:
        exit(0)

    exiter = Button(root, text='Exit', command=get_out2)
    exiter.pack(side=RIGHT)

    opener = Button(root, text='Open Output File', command=open_it)
    opener.pack(side=RIGHT, padx=20)


if __name__ == "__main__":
    mode = int(sys.argv[1])



    # b = str(sys.argv[2])
    # c = str(sys.argv[3])
    # d = str(sys.argv[4])

    # messagebox.showinfo("Flight Instance", "Please Select the Flight Instance File (PRF)")
    # root.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
    #                                            filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
    # prf = root.filename
    # messagebox.showinfo("Error Instance", "Please Select the Error Instance File (FLT)")
    # root.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
    #                                            filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
    #
    # flt = root.filename
    # messagebox.showinfo("Error Code", "Please Select the Error Code File")
    # root.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
    #                                            filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
    #
    # ec = root.filename
    # today = datetime.datetime.now()
    # filler = str(today).replace(" ", "_").split(".")[0].replace(":", "--")
    # output_title = "labelrun" + filler + ".csv"
    # messagebox.showinfo("Output File Name", "The Output File for this process will be called: " + output_title + "\nThis file will be located in the same folder that the source csv files were stored in.")

    def get_out():
        master.quit()
        print("You quit the program.")
        messagebox.showinfo("Quit Message", "You quit the program.")
        exit(0)


    def file_e1():
        master.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                     filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        e1.delete(0, END)
        e1.insert(0, master.filename)
        return


    def file_e2():
        master.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                     filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        e2.delete(0, END)
        e2.insert(0, master.filename)
        return


    def file_e3():
        master.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                     filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        e3.delete(0, END)
        e3.insert(0, master.filename)
        return


    def auto_pop():
        e1.delete(0, END)
        e1.insert(0, 'PRF.csv')
        e2.delete(0, END)
        e2.insert(0, 'FLT.csv')
        e3.delete(0, END)
        e3.insert(0, 'ErrorCodes.csv')
        return

    if mode != 3 and mode != 2:
        master = tk.Tk()
        master.title('Input Files')
        master.configure(background='gray64')
        tk.Label(master,
                 text="Please Select the Flight Instance File (PRF)", foreground='black', background='gray64',
                 font='bold').grid(row=0, pady=10, padx=35)
        fi = Canvas(master, width=1100, height=2, background='black')
        fi.grid(row=1, columnspan=3)
        ji = Canvas(master, width=1100, height=2, background='black')
        ji.grid(row=3, columnspan=3)
        li = Canvas(master, width=1100, height=2, background='black')
        li.grid(row=5, columnspan=3)
        tk.Label(master,
                 text="Please Select the Error Instance File (FLT)", foreground='black', background='gray64',
                 font='bold').grid(row=2, pady=10, padx=35)
        tk.Label(master, text="Please Select the Error Code File", foreground='black', background='gray64',
                 font='bold').grid(row=4, pady=10, padx=35)

        e1 = tk.Entry(master, width=75)
        e2 = tk.Entry(master, width=75)
        e3 = tk.Entry(master, width=75)

        e1.grid(row=0, column=2, padx=5)
        e2.grid(row=2, column=2, padx=5)
        e3.grid(row=4, column=2, padx=5)

        tk.Button(master,
                  text='Quit',
                  command=get_out, width=20).grid(row=6,
                                                  column=0,
                                                  sticky=tk.W,
                                                  pady=4)
        tk.Button(master,
                  text='RUN IT', command=master.quit, width=20).grid(row=6,
                                                                     column=2,
                                                                     sticky=tk.E,
                                                                     pady=4)
        defaulter = tk.Button(master, text='Default Files', command=auto_pop, width=20)
        defaulter.grid(row=6, column=1)

        tk.Button(master, text='BROWSE', command=file_e1).grid(row=0, column=1, sticky=E)
        tk.Button(master, text='BROWSE', command=file_e2).grid(row=2, column=1, sticky=E)
        tk.Button(master, text='BROWSE', command=file_e3).grid(row=4, column=1, sticky=E)
        tk.mainloop()
        master.withdraw()
    today = datetime.datetime.now()
    filler = str(today).replace(" ", "_").split(".")[0].replace(":", "--")
    output_title = "labelrun" + filler + ".csv"
    messagebox.showinfo("Output File Name",
                        "The Output File for this process will be called: \n\n" + output_title + "\n\nThis file will "
                                                                                                 "be located in the "
                                                                                                 "same folder that "
                                                                                                 "the source csv "
                                                                                                 "files were stored "
                                                                                                 "in.")
    if mode == 2 or mode == 3:
        a = str(sys.argv[2])
        b = str(sys.argv[3])
        c = str(sys.argv[4])

    if mode != 3 and mode != 2:
        runit(mode, e1.get(), e2.get(), e3.get(), output_title)
    else:
        runit(mode, a, b, c, output_title)
    # runit(a,b,c,d)
    root.mainloop()
