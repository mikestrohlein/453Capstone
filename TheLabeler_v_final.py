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


# mode 1 = all interface
# mode 2 = only interface progress (cmd file inputs)
# mode 3 = no interface (cmd file inputs)
# mode 4 = file selector interface inputs, no interface progress

# columns to exclude and columns that contain text
exclude = [0, 1, 2, 4, 5, 8, 12, 14, 21, 23, 36, 37, 50, 54, 55, 56, 57, 58, 87, 88, 90, 97]

# columns that contain text
text_cols = [55, 87, 88]

# number of columns in the original prf document
prf_col_size = 99


# open output file
def open_it():
    os.startfile(output_title)


# close the progress interface window and exit the program
def get_out2():
    root.quit()
    exit(0)


# configure the progress window
root = Tk()
root.title('The Labeler')
root.configure(background='black')
size = 500
root.geometry(str(size + 200) + "x" + str(size + 300) + "+50+50")

# create a line to divide the progress window and separate the label
w = Canvas(root, width=size + 300, height=1, background='white')

# initialize progress bar for file reading process
progress = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')

# initialize progress bar for flight grouping process
progress2 = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')

# initialize progress bar for engine grouping process
progress3 = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')

# initialize progress bar for error assigning process
progress4 = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')

# initialize progress bar for error updating process
progress5 = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')

# initialize progress bar for severity updating process
progress6 = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')

# initialize progress bar for printing output file process
progress7 = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')

# hide the progress window
root.withdraw()

# initialize title Label and pack to window
titler = Label(root, text='The Labeler', font='bold', foreground='white', background='black')
titler.configure(font=("Arial Black", 50))
titler.pack(pady=20)

# pack line divider to window
w.pack()

# initialize Reading Files Label and pack label and progress bar to window
reader = Label(root, text='Waiting to Read Files...', foreground='yellow', background='black')
reader.pack(pady=10)
progress.pack(pady=5)

# initialize Grouping Flights Label and pack label and progress bar to window
fgrouper = Label(root, text='Waiting to Group Flights...', foreground='yellow', background='black')
fgrouper.pack(pady=10)
progress2.pack(pady=5)

# initialize Grouping Engines Label and pack label and progress bar to window
egrouper = Label(root, text='Waiting to Group Engines...', foreground='yellow', background='black')
egrouper.pack(pady=10)
progress3.pack(pady=5)

# initialize Assigning Errors Label and pack label and progress bar to window
assigner = Label(root, text='Waiting to Assign Errors...', foreground='yellow', background='black')
assigner.pack(pady=10)
progress4.pack(pady=5)

# initialize Updating Errors Label and pack label and progress bar to window
updater = Label(root, text='Waiting to Update Errors...', foreground='yellow', background='black')
updater.pack(pady=10)
progress5.pack(pady=5)

# initialize Updating Severity Label and pack label and progress bar to window
severer = Label(root, text='Waiting to Update Severity...', foreground='yellow', background='black')
severer.pack(pady=10)
progress6.pack(pady=5)

# initialize Printing Output Label and pack label and progress bar to window
printer = Label(root, text='Waiting to Print to csv...', foreground='yellow', background='black')
printer.pack(pady=10)
progress7.pack(pady=5)

# initialize completion label and pack to window
timer = Label(root, text='Awaiting Completion...', foreground='yellow', background='black')
timer.pack(pady=15)

# initialize tip text label and pack to window
quiter = Label(root, text='TO QUIT BEFORE COMPLETION:\nCTRL + C (when clicked into command window)', foreground= 'white', background= 'black')
quiter.pack(side=LEFT)

# global variables defining length of standard flight
TIME_INTERVAL_HOUR = 1
TIME_INTERVAL_MIN = 30


# read file to list of rows then list of columns
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


# define flight object (esn = engine serial number, start = start datetime, end = end datetime,
# instance_list = row numbers that make up the flight, errors = list of errors of instances,
# final_e = most severe error from flight
class Flight:
    def __init__(self, esn, start, end, instance_list, errors, final_e):
        self.esn = esn
        self.start = start
        self.end = end
        self.instance_list = instance_list
        self.errors = errors
        self.final_e = final_e


# define engine object (serial_number = engine serial number, flight_list = list of flights with corresponding esn)
class Engine:
    def __init__(self, serial_number, flight_list):
        self.serial_number = serial_number
        self.flight_list = flight_list


# define error object (code = error code number, name = error name, severity = defined error severity)
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

    # divide function into pieces that will add up to 100%
    chunks_siz = len(prf_list)
    chunk = 100 / chunks_siz

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

        # update progress bar value to mirror current progress
        progress2['value'] += chunk

        # update label to indicate the function has started (including number of instances and % complete)
        fgrouper.configure(text='Grouping Flights... ({:,}'.format(len(prf_list)) + ' instances) --> {:6.2f}'.format(
            progress2['value']) + '%', foreground='white')
        root.update_idletasks()
        i += 1

    # update label to show progress is complete
    fgrouper.configure(text='Grouping Flights Complete. ({:,}'.format(len(prf_list)) + ' instances) --> {:6.2f}'.format(
        progress2['value']) + '%', foreground='green')
    root.update_idletasks()
    return grouped_flight_list


# takes grouped flight list and creates a list of engines that contain grouped flights
def group_engines(grouped_flight_list):
    # initialize lists
    engine_list = []
    temp_list_e = []

    for element in grouped_flight_list:
        # first creates engine objects of all unique esn
        if element.esn not in temp_list_e:
            engine_list.append(Engine(element.esn, []))
            temp_list_e.append(element.esn)

    # find chunk size that will add up to 100% upon completion of this function
    chunk2 = 100 / len(grouped_flight_list)

    for flight in grouped_flight_list:
        # second assigns flights to corresponding engine objects
        for engine in engine_list:
            if engine.serial_number == flight.esn:
                engine.flight_list.append(flight)

        # update progress value and label to indicate progress
        progress3['value'] += chunk2
        egrouper.configure(
            text='Grouping Engines... ({:,}'.format(len(grouped_flight_list)) + ' flights) --> {:6.2f}'.format(
                progress3['value']) + '%', foreground='white')
        root.update_idletasks()

    # update label to indicate completion
    egrouper.configure(
        text='Grouping Engines Complete. ({:,}'.format(len(grouped_flight_list)) + ' flights) --> {:6.2f}'.format(
            progress3['value']) + '%', foreground='green')
    root.update_idletasks()
    return engine_list


# assigns error to flight by matching instance to esn then finding if there is a corresponding flight and labels it
def assign_errors(engine_list, flt_list):
    # find chunk size that will add up to 100% upon completion of this function
    chunk3 = 100 / len(flt_list)

    for row in flt_list:
        for engine in engine_list:

            # first checks if esn values line up, if not on to the next engine
            if engine.serial_number == row[0]:
                for flight in engine.flight_list:

                    # checks if error instance lines up with a flight in the engine object
                    if within_5(flight.start, row[2], TIME_INTERVAL_HOUR, TIME_INTERVAL_MIN) or within_5(
                            flight.end, row[2], TIME_INTERVAL_HOUR, TIME_INTERVAL_MIN):
                        flight.errors.append(Error(row[7], "NONE", 0))

        # update progress value and label to indicate progress
        progress4['value'] += chunk3
        assigner.configure(
            text='Assigning Errors... ({:,}'.format(len(flt_list)) + ' occurrences) --> {:6.2f}'.format(
                progress4['value']) + '%', foreground='white')
        root.update_idletasks()

    # update label to indicate completion
    assigner.configure(
        text='Assigning Errors Complete. ({:,}'.format(len(flt_list)) + ' occurrences) --> {:6.2f}'.format(
            progress4['value']) + '%', foreground='green')
    root.update_idletasks()


# assigns error severities based on error code
def update_errors(engine_list, ec_list):
    # find chunk size that will add up to 100% upon completion of this function
    chunk4 = 100 / len(engine_list)

    # update one engine at a time
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

        # update progress value and label to indicate progress
        progress5['value'] += chunk4
        updater.configure(
            text='Updating Errors... ({:,}'.format(len(engine_list)) + ' engines) --> {:6.2f}'.format(
                progress5['value']) + '%', foreground='white')
        root.update_idletasks()

    # update label to indicate completion
    updater.configure(
        text='Updating Errors Complete. ({:,}'.format(len(engine_list)) + ' engines) --> {:6.2f}'.format(
            progress5['value']) + '%', foreground='green')
    root.update_idletasks()


# updates flight severity by looking through error severities
def update_severity(engine_list):
    i = 0
    # find chunk size that will add up to 100% upon completion of this function
    chunk5 = 100 / len(engine_list)

    for engine in engine_list:
        for flight in engine.flight_list:
            top_sev = 0
            for error in flight.errors:
                if int(error.severity) > int(top_sev):
                    flight.final_e = error
                    top_sev = error.severity
        i += 1

        # update progress value and label to indicate progress
        progress6['value'] += chunk5
        severer.configure(
            text='Updating Severity... ({:,}'.format(len(engine_list)) + ' engines) --> {:6.2f}'.format(
                progress6['value']) + '%', foreground='white')
        root.update_idletasks()

    # update label to indicate completion
    severer.configure(
        text='Updating Severity Complete. ({:,}'.format(len(engine_list)) + ' engines) --> {:6.2f}'.format(
            progress6['value']) + '%', foreground='green')
    root.update_idletasks()


# writes results to output file
def output_csv(engine_list, output_filename, prf_titles, prf_col):
    out1 = open(output_filename, 'w')
    i = 0

    # write titles to columns
    out1.write("ESN, Start, End,")
    for piece in prf_titles:
        if i in text_cols:
            out1.write(piece + ",")
        if i not in exclude:
            out1.write(str(piece) + " min,")
            out1.write(str(piece) + " max,")
            out1.write(str(piece) + " avg,")
            out1.write(str(piece) + " st dev,")
        i += 1
    out1.write("Error Classifier \n")

    # find chunk size that will add up to 100% upon completion of this function
    chunk7 = 100 / len(engine_list)

    # go engine by engine
    for enginer in engine_list:

        # flight by flight in current engine
        for flight in enginer.flight_list:

            # start with esn start and end
            out1.write(flight.esn + "," + flight.start + "," + flight.end + ",")
            current_in = flight.instance_list

            # cut out esn, asn, download time (first 3 col)
            i = 3
            while i < prf_col_size:

                # make list of values that correspond to column and flight
                ma_list = []

                # do not perform calculations on columns containing text values
                if i in text_cols:
                    out1.write(prf_col[i][current_in[0]] + ",")
                if i not in exclude:

                    # add applicable values by column and flight to temporary list
                    for col in current_in:
                        if prf_col[i][col] == '':
                            ma_list.append('0')
                        else:
                            ma_list.append(prf_col[i][col])

                    # initial values to assist with calculations
                    total = 0
                    length = 0
                    mini = 999999
                    maxi = -999999

                    # find max, min, total, and length of current values
                    for part in ma_list:
                        if float(part) < float(mini):
                            mini = float(part)
                        if float(part) > float(maxi):
                            maxi = float(part)
                        total = float(total) + float(part)
                        length += 1

                    # write min and max values found to output file
                    out1.write(str(mini) + ",")
                    out1.write(str(maxi) + ",")

                    # calculate average
                    meaner = total / float(length)

                    # calculate standard deviation
                    im_to = 0
                    for part in ma_list:
                        im_to = float(im_to) + (float(part) - meaner) ** 2
                    ready = im_to / float(length)
                    stde = math.sqrt(ready)

                    # write average and standard deviation values found to output file
                    out1.write(str(meaner) + ",")
                    out1.write(str(stde) + ",")
                i += 1

            # write grounding errors or non grounding by flight depending on error severity
            if flight.final_e.severity == '2':
                out1.write('Grounding\n')
            else:
                out1.write("Non-grounding\n")

        # update progress value and label to indicate progress
        progress7['value'] += chunk7
        printer.configure(
            text='Printing to csv... ({:,}'.format(len(engine_list)) + ' engines) --> {:6.2f}'.format(
                progress7['value']) + '%', foreground='white')
        root.update_idletasks()

    # update label to indicate completion
    printer.configure(text='Printing to: "' + output_filename + '" Complete. ({:,}'.format(
        len(engine_list)) + ' engines) --> {:6.2f}'.format(
        progress7['value']) + '%', foreground='green')
    root.update_idletasks()


# brings it all together
def runit(moder, instance_file, error_occurrences_file, error_class_file, output_file):
    # displays progress interface according to moder value
    if moder != 4 and moder != 3:
        root.update()
        root.deiconify()

    # updates background color for progress interface
    root.configure(background='black')

    # update progress value and label to indicate progress
    reader.configure(text='Reading Files... (3 files) --> {:6.2f}'.format(
        progress['value']) + '%', foreground='white')
    root.update_idletasks()
    progress['value'] += 0
    root.update_idletasks()

    # finds and stores time that the program started
    start_time = time.time()

    # prints current process to window
    print("Reading Files...")

    # read first file
    instance_list = try_ito(instance_file)

    # update progress value and label to indicate progress
    progress['value'] += 33
    reader.configure(text='Reading Files... (3 files) --> {:6.2f}'.format(
        progress['value']) + '%', foreground='white')
    root.update_idletasks()

    # read second file
    error_o_list = try_ito(error_occurrences_file)

    # update progress value and label to indicate progress
    progress['value'] += 33
    reader.configure(text='Reading Files... (3 files) --> {:6.2f}'.format(
        progress['value']) + '%', foreground='white')
    root.update_idletasks()
    time.sleep(.5)

    # read third file
    ec_list = try_ito(error_class_file)

    # update progress value and label to indicate completion
    progress['value'] += 34
    reader.configure(text='Reading Files Complete. (3 files) --> {:6.2f}'.format(
        progress['value']) + '%', foreground='green')
    root.update_idletasks()

    # prints progress to window
    print("(1/8) Files Read.")
    print("Grouping Flights...")

    # groups flights using rows of prf file (excluding the column titles)
    grouped_flights = group_flights(instance_list[0][1:])

    # prints progress to window
    print("(2/8) Flights grouped.")
    print("Grouping Engines...")

    # groups flights by engine
    grouped_engines = group_engines(grouped_flights)

    # prints progress to window
    print("(3/8) Engines Grouped.")
    print("Assigning Errors...")

    # assigns errors using rows of flt file (excluding the column titles)
    assign_errors(grouped_engines, error_o_list[0][1:])

    # prints progress to window
    print("(4/8) Errors assigned.")
    print("Updating Errors...")

    # updates errors using rows of error code file (excluding the column titles)
    update_errors(grouped_engines, ec_list[0][1:])

    # prints progress to window
    print("(5/8) Errors updated.")
    print("Updating Severity...")

    # updates severity of all flights
    update_severity(grouped_engines)

    # prints progress to window (includes output file name)
    print("(6/8) Severity updated.")
    print("(7/8) printing to: " + output_file)

    # prints to output file using column titles from prf file and the values grouped by column from the prf file
    output_csv(grouped_engines, output_file, instance_list[0][0], instance_list[1])

    # updates completion label showing the time it took to complete the program
    timer.configure(text='This took: --- %s seconds --- to complete' % (time.time() - start_time), foreground='green')
    root.update_idletasks()

    # prints time taken to complete program to window
    print("(8/8) Complete. --- %s seconds ---" % (time.time() - start_time))

    # if moder 4 or 3 then exits here
    if moder == 4 or moder == 3:
        exit(0)

    # initializes an exit button and packs to window
    exiter = Button(root, text='Exit', command=get_out2)
    exiter.pack(side=RIGHT)

    # initializes a button that can be used to open the output file and packs it to window
    opener = Button(root, text='Open Output File', command=open_it)
    opener.pack(side=RIGHT, padx=20)


if __name__ == "__main__":
    # first input after file name indicates mode being used
    moder = int(sys.argv[1])

    # function that quits the program and displays an information message that this action was performed
    def get_out():
        master.quit()
        print("You quit the program.")
        messagebox.showinfo("Quit Message", "You quit the program.")
        exit(0)

    # uses file choser to find file and populate path name to entry field
    def file_e1():
        master.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                     filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        e1.delete(0, END)
        e1.insert(0, master.filename)
        return

    # uses file choser to find file and populate path name to entry field
    def file_e2():
        master.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                     filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        e2.delete(0, END)
        e2.insert(0, master.filename)
        return

    # uses file chooser to find file and populate path name to entry field
    def file_e3():
        master.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                     filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        e3.delete(0, END)
        e3.insert(0, master.filename)
        return

    # assigns default file names to entry fields
    def auto_pop():
        e1.delete(0, END)
        e1.insert(0, 'PRF.csv')
        e2.delete(0, END)
        e2.insert(0, 'FLT.csv')
        e3.delete(0, END)
        e3.insert(0, 'ErrorCodes.csv')
        return

    # uses file chooser interface if not moder 2 or 3
    if moder != 3 and moder != 2:

        # initializes file choser window
        master = tk.Tk()
        master.title('Input Files')
        master.configure(background='gray64')

        # creates labels and dividers for given file type then packs to window
        tk.Label(master,
                 text="Please Select the Flight Instance File (PRF)", foreground='black', background='gray64',
                 font='bold').grid(row=0, pady=10, padx=35)
        tk.Label(master,
                 text="Please Select the Error Instance File (FLT)", foreground='black', background='gray64',
                 font='bold').grid(row=2, pady=10, padx=35)
        tk.Label(master, text="Please Select the Error Code File", foreground='black', background='gray64',
                 font='bold').grid(row=4, pady=10, padx=35)
        fi = Canvas(master, width=1100, height=2, background='black')
        fi.grid(row=1, columnspan=3)
        ji = Canvas(master, width=1100, height=2, background='black')
        ji.grid(row=3, columnspan=3)
        li = Canvas(master, width=1100, height=2, background='black')
        li.grid(row=5, columnspan=3)

        # creates entry fields for file path names
        e1 = tk.Entry(master, width=75)
        e2 = tk.Entry(master, width=75)
        e3 = tk.Entry(master, width=75)

        # packs entry fields to window
        e1.grid(row=0, column=2, padx=5)
        e2.grid(row=2, column=2, padx=5)
        e3.grid(row=4, column=2, padx=5)

        # creates quit, default, and run buttons with their associated functions linked then packs them to window
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

        # packs browse buttons to window with associated functions linked
        tk.Button(master, text='BROWSE', command=file_e1).grid(row=0, column=1, sticky=E)
        tk.Button(master, text='BROWSE', command=file_e2).grid(row=2, column=1, sticky=E)
        tk.Button(master, text='BROWSE', command=file_e3).grid(row=4, column=1, sticky=E)
        tk.mainloop()

        # hides file chooser interface when it is done being used
        master.withdraw()

    # assigns output filename based on current date and time
    today = datetime.datetime.now()
    filler = str(today).replace(" ", "_").split(".")[0].replace(":", "--")
    output_title = "labelrun" + filler + ".csv"

    # displays message showing the name of the output file
    messagebox.showinfo("Output File Name",
                        "The Output File for this process will be called: \n\n" + output_title + "\n\nThis file will "
                                                                                                 "be located in the "
                                                                                                 "same folder that "
                                                                                                 "the source csv "
                                                                                                 "files were stored "
                                                                                                 "in.")

    # if moder 2 or 3 command line accepts file names as arguments instead of using file chooser interface
    if moder == 2 or moder == 3:
        a = str(sys.argv[2])
        b = str(sys.argv[3])
        c = str(sys.argv[4])

    # if not moder 2 or 3 get parameter inputs from entry fields in file chooser interface and run it
    if moder != 3 and moder != 2:
        runit(moder, e1.get(), e2.get(), e3.get(), output_title)

    # otherwise use the input arguments from the command line
    else:
        runit(moder, a, b, c, output_title)

    root.mainloop()
