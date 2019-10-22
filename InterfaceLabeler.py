import csv
import datetime
import time
import math
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
from functools import partial

root = Tk()
root.title('The Labeler')
# root.iconbitmap('Bolt.ico')
root.configure(background='black')
size = 500
root.geometry(str(size + 200) + "x" + str(size + 300) + "+50+50")

w = Canvas(root, width=size+300, height=1, background='white')

# Progress bar widget

progress = Progressbar(root, orient=HORIZONTAL,
                       length=size, mode='determinate')

progress2 = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')

progress3 = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')

progress4 = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')

progress5 = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')

progress6 = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')

progress7 = Progressbar(root, orient=HORIZONTAL, length=size, mode='determinate')


titler = Label(root, text='The Labeler', font='bold', foreground='white', background='black')
titler.configure(font=("Arial Black", 50))
titler.pack(pady=20)

w.pack()

reader = Label(root, text='Reading Files...', foreground='white', background='black')
reader.pack(pady=10)
progress.pack(pady=5)

fgrouper = Label(root, text='Grouping Flights...', foreground='white', background='black')
fgrouper.pack(pady=10)
progress2.pack(pady=5)

egrouper = Label(root, text='Grouping Engines...', foreground='white', background='black')
egrouper.pack(pady=10)
progress3.pack(pady=5)

assigner = Label(root, text='Assigning Errors...', foreground='white', background='black')
assigner.pack(pady=10)
progress4.pack(pady=5)

updater = Label(root, text='Updating Errors...', foreground='white', background='black')
updater.pack(pady=10)
progress5.pack(pady=5)

severer = Label(root, text='Updating Severity...', foreground='white', background='black')
severer.pack(pady=10)
progress6.pack(pady=5)

printer = Label(root, text='Printing to csv...', foreground='white', background='black')
printer.pack(pady=10)
progress7.pack(pady=5)

timer = Label(root, text='Awaiting Completion...', foreground='white', background='black')
timer.pack(pady=15)

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
    chunk = 100 / len(prf_list)
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
        root.update_idletasks()
        i += 1
    fgrouper.configure(text='Grouping Flights Complete.', foreground='green')
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
    for flight in grouped_flight_list:
        # second assigns flights to corresponding engine objects
        for engine in engine_list:
            if engine.serial_number == flight.esn:
                engine.flight_list.append(flight)
        progress3['value'] += chunk2
        root.update_idletasks()
    egrouper.configure(text='Grouping Engines Complete.', foreground='green')
    root.update_idletasks()
    return engine_list


# assigns error to flight by matching instance to esn then finding if there is a corresponding flight and labels it
def assign_errors(engine_list, flt_list):
    root.update_idletasks()
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
        progress4['value'] += chunk3
        root.update_idletasks()
    assigner.configure(text='Assigning Errors Complete.', foreground='green')
    root.update_idletasks()

# assigns error severities based on error code
def update_errors(engine_list, ec_list):
    # update one engine at a time
    chunk4 = 100 / len(engine_list)
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
        root.update_idletasks()
    updater.configure(text='Updating Errors Complete.', foreground='green')
    root.update_idletasks()

def update_severity(engine_list):
    i = 0
    chunk5 = 100 / len(engine_list)
    for engine in engine_list:
        for flight in engine.flight_list:
            top_sev = 0
            for error in flight.errors:
                if int(error.severity) > int(top_sev):
                    flight.final_e = error
                    top_sev = error.severity
        i += 1
        progress6['value'] += chunk5
        root.update_idletasks()
    severer.configure(text='Updating Severity Complete.', foreground='green')
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
    out1.write("Error Code, Error Name, Error Severity \n")
    chunk7 = 100 / len(engine_list)
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
            out1.write(str(flight.final_e.code) + "," + flight.final_e.name + "," + str(flight.final_e.severity) + "\n")
        progress7['value'] += chunk7
        root.update_idletasks()
    printer.configure(text='Printing to ' + output_filename + ' Complete.', foreground='green')
    root.update_idletasks()

def runit(instance_file, error_occurrences_file, error_class_file, output_file):

    progress['value'] += 0
    root.update_idletasks()
    start_time = time.time()
    print("Reading Files...")
    instance_list = try_ito(instance_file)
    progress['value'] += 33
    root.update_idletasks()
    error_o_list = try_ito(error_occurrences_file)
    progress['value'] += 33
    root.update_idletasks()
    ec_list = try_ito(error_class_file)
    progress['value'] += 34
    reader.configure(text='Reading Files Complete.', foreground='green')
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


if __name__ == "__main__":
    # a = str(sys.argv[1])
    # b = str(sys.argv[2])
    # c = str(sys.argv[3])
    # d = str(sys.argv[4])

    messagebox.showinfo("Flight Instance", "Please Select the Flight Instance File (PRF)")
    root.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                               filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
    prf = root.filename
    messagebox.showinfo("Error Instance", "Please Select the Error Instance File (FLT)")
    root.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                               filetypes=(("csv files", "*.csv"), ("all files", "*.*")))

    flt = root.filename
    messagebox.showinfo("Error Code", "Please Select the Error Code File")
    root.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                               filetypes=(("csv files", "*.csv"), ("all files", "*.*")))

    ec = root.filename
    today = datetime.datetime.now()
    filler = str(today).replace(" ", "_").split(".")[0].replace(":", "--")
    output_title = "labelrun" + filler + ".csv"
    messagebox.showinfo("Output File Name", "The Output File for this process will be called: " + output_title + "\nThis file will be located in the same folder that the source csv files were stored in.")


    a = 'PRF.csv'
    b = 'FLT.csv'
    c = 'ErrorCodes.csv'
    d = 'FTry2.csv'
    runit(prf, flt, ec, output_title)
    root.mainloop()
