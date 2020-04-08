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
import random
import shutil

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

# train, test and evaluate sizes (used as percentages)
train_size = 60
test_size = 20
eval_size = 20


# creates folder to store output files in
def create_folder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)

# open output folder
def open_it():
    results = os.path.abspath(output_title + " results")
    os.startfile(results)


# close the progress interface window and exit the program
def get_out2():
    root.quit()
    print("You quit the program")
    exit(0)


# configure the progress window
root = Tk()
root.title('The Labeler v4')
root.configure(background='black')
size = 500
root.geometry(str(size + 200) + "x" + str(size + 250) + "+5+5")

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
titler = Label(root, text='The Labeler v4', font='bold', foreground='white', background='black')
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
def convert_dt(datetime1):
    date_tester1 = datetime1.split()
    first_test = datetime.datetime(int(date_tester1[0].split('/')[2]), int(date_tester1[0].split('/')[0]),
                                   int(date_tester1[0].split('/')[1]), int(date_tester1[1].split(':')[0]),
                                   int(date_tester1[1].split(':')[1]))

    return first_test


# accepts two strings from lists created and time interval which indicates range for same flight
def within_5(datetime1, datetime2, time_interval_hour, time_interval_min):
    # split date and time by the space between them
    first_test = convert_dt(datetime1)
    second_test = convert_dt(datetime2)

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
# final_e = most severe error from flight, designation = random number used for train test evaluate split
# designation is the random number that assigns the instance to the train test or evaluate files
class Flight:
    def __init__(self, esn, start, end, instance_list, errors, final_e, designation):
        self.esn = esn
        self.start = start
        self.end = end
        self.instance_list = instance_list
        self.errors = errors
        self.final_e = final_e
        self.designation = designation


# define engine object (serial_number = engine serial number, flight_list = list of flights with corresponding esn)
# designation_1 is the random number that assigns the instance to the train test or evaluate files
class Engine:
    def __init__(self, serial_number, flight_list, designation_1):
        self.serial_number = serial_number
        self.flight_list = flight_list
        self.designation_1 = designation_1


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
            grouped_flight_list.append(
                Flight(element[0], element[2], element[2], [], [], Error("NONE", "NONE", 0), random.randint(1, 101)))
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
                if convert_dt(element[2]) < convert_dt(grouped_flight_list[-1].start):
                    grouped_flight_list[-1].start = element[2]
                if convert_dt(element[2]) > convert_dt(grouped_flight_list[-1].end):
                    grouped_flight_list[-1].end = element[2]
            else:
                grouped_flight_list.append(
                    Flight(element[0], element[2], element[2], [], [], Error("NONE", "NONE", 0),
                           random.randint(1, 101)))
                grouped_flight_list[-1].instance_list.append(i + 1)

        # update progress bar value to mirror current progress
        progress2['value'] += chunk

        # update label to indicate the function has started (including number of instances and % complete)
        fgrouper.configure(text='Grouping Flights... ({:,}'.format(len(prf_list)) + ' instances) --> {:6.2f}'.format(
            progress2['value']) + '%', foreground='white')
        root.update()
        i += 1

    # update label to show progress is complete
    fgrouper.configure(text='Grouping Flights Complete. ({:,}'.format(len(prf_list)) + ' instances) --> {:6.2f}'.format(
        progress2['value']) + '%', foreground='green')
    root.update()
    return grouped_flight_list


# takes grouped flight list and creates a list of engines that contain grouped flights
def group_engines(grouped_flight_list):
    # initialize lists
    engine_list = []
    temp_list_e = []

    for element in grouped_flight_list:
        # first creates engine objects of all unique esn
        if element.esn not in temp_list_e:
            current_designation = random.randint(1, 100)
            engine_list.append(Engine(element.esn, [], current_designation))
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
        root.update()

    # update label to indicate completion
    egrouper.configure(
        text='Grouping Engines Complete. ({:,}'.format(len(grouped_flight_list)) + ' flights) --> {:6.2f}'.format(
            progress3['value']) + '%', foreground='green')
    root.update()
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
        root.update()

    # update label to indicate completion
    assigner.configure(
        text='Assigning Errors Complete. ({:,}'.format(len(flt_list)) + ' occurrences) --> {:6.2f}'.format(
            progress4['value']) + '%', foreground='green')
    root.update()


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
                        print(error.code)

                # if error does not appear in error classification
                if updated == 0:
                    error.name = "NONE"
                    error.severity = 0

        # update progress value and label to indicate progress
        progress5['value'] += chunk4
        updater.configure(
            text='Updating Errors... ({:,}'.format(len(engine_list)) + ' engines) --> {:6.2f}'.format(
                progress5['value']) + '%', foreground='white')
        root.update()

    # update label to indicate completion
    updater.configure(
        text='Updating Errors Complete. ({:,}'.format(len(engine_list)) + ' engines) --> {:6.2f}'.format(
            progress5['value']) + '%', foreground='green')
    root.update()


# updates flight severity by looking through error severities
def update_severity(engine_list):
    # find chunk size that will add up to 100% upon completion of this function
    chunk5 = 100 / len(engine_list)
    i = 0
    for engine in engine_list:
        flt_error_list = []
        for flight in engine.flight_list:
            top_sev = 0
            for error in flight.errors:
                if int(error.severity) > int(top_sev):
                    flight.final_e = error
                    top_sev = error.severity
            flt_error_list.append(flight.final_e.severity)
        j = 0
        last_error = '0'
        for flight in engine.flight_list:
            if j - 1 > 0 and j < len(flt_error_list):
                if flt_error_list[j - 1] == '2' and last_error != '47':
                    flight.final_e.severity = '47'
            last_error = flight.final_e.severity
            j += 1

        i += 1

        # update progress value and label to indicate progress
        progress6['value'] += chunk5
        severer.configure(
            text='Updating Severity... ({:,}'.format(len(engine_list)) + ' engines) --> {:6.2f}'.format(
                progress6['value']) + '%', foreground='white')
        root.update()

    # update label to indicate completion
    severer.configure(
        text='Updating Severity Complete. ({:,}'.format(len(engine_list)) + ' engines) --> {:6.2f}'.format(
            progress6['value']) + '%', foreground='green')
    root.update()


# writes results to output file
def output_csv(engine_list, output_filename, prf_titles, prf_col):
    out1 = open(output_filename, 'w')
    i = 0

    # create train test and evaluate files
    out2 = open("fg_train_" + output_filename, 'w')
    out3 = open("fg_test_" + output_filename, 'w')
    out4 = open("fg_eval_" + output_filename, 'w')
    out5 = open("eg_train_" + output_filename, 'w')
    out6 = open("eg_test_" + output_filename, 'w')
    out7 = open("eg_eval_" + output_filename, 'w')

    # write titles to columns
    out1.write("ESN, Start, End,")
    out2.write("ESN, Start, End,")
    out3.write("ESN, Start, End,")
    out4.write("ESN, Start, End,")
    out5.write("ESN, Start, End,")
    out6.write("ESN, Start, End,")
    out7.write("ESN, Start, End,")

    for piece in prf_titles:
        if i in text_cols:
            out1.write(piece + ",")
            out2.write(piece + ",")
            out3.write(piece + ",")
            out4.write(piece + ",")
            out5.write(piece + ",")
            out6.write(piece + ",")
            out7.write(piece + ",")
        if i not in exclude:
            out1.write(str(piece) + " min,")
            out2.write(str(piece) + " min,")
            out3.write(str(piece) + " min,")
            out4.write(str(piece) + " min,")
            out5.write(str(piece) + " min,")
            out6.write(str(piece) + " min,")
            out7.write(str(piece) + " min,")

            out1.write(str(piece) + " max,")
            out2.write(str(piece) + " max,")
            out3.write(str(piece) + " max,")
            out4.write(str(piece) + " max,")
            out5.write(str(piece) + " max,")
            out6.write(str(piece) + " max,")
            out7.write(str(piece) + " max,")

            out1.write(str(piece) + " avg,")
            out2.write(str(piece) + " avg,")
            out3.write(str(piece) + " avg,")
            out4.write(str(piece) + " avg,")
            out5.write(str(piece) + " avg,")
            out6.write(str(piece) + " avg,")
            out7.write(str(piece) + " avg,")

            out1.write(str(piece) + " st dev,")
            out2.write(str(piece) + " st dev,")
            out3.write(str(piece) + " st dev,")
            out4.write(str(piece) + " st dev,")
            out5.write(str(piece) + " st dev,")
            out6.write(str(piece) + " st dev,")
            out7.write(str(piece) + " st dev,")
        i += 1
    out1.write("Error Classifier, Severity \n")
    out2.write("Error Classifier, Severity \n")
    out3.write("Error Classifier, Severity \n")
    out4.write("Error Classifier, Severity \n")
    out5.write("Error Classifier, Severity \n")
    out6.write("Error Classifier, Severity \n")
    out7.write("Error Classifier, Severity \n")

    # find chunk size that will add up to 100% upon completion of this function
    chunk7 = 100 / len(engine_list)

    # go engine by engine
    for engine1 in engine_list:

        # flight by flight in current engine
        for flight in engine1.flight_list:

            # start with esn start and end to output plus respective train test eval file
            out1.write(flight.esn + "," + flight.start + "," + flight.end + ",")
            if flight.designation <= train_size:
                out2.write(flight.esn + "," + flight.start + "," + flight.end + ",")
            if train_size < flight.designation <= (train_size + test_size):
                out3.write(flight.esn + "," + flight.start + "," + flight.end + ",")
            if flight.designation > (train_size + test_size):
                out4.write(flight.esn + "," + flight.start + "," + flight.end + ",")
            if engine1.designation_1 <= train_size:
                out5.write(flight.esn + "," + flight.start + "," + flight.end + ",")
            if train_size < engine1.designation_1 <= (train_size + test_size):
                out6.write(flight.esn + "," + flight.start + "," + flight.end + ",")
            if engine1.designation_1 > (train_size + test_size):
                out7.write(flight.esn + "," + flight.start + "," + flight.end + ",")

            current_in = flight.instance_list

            # cut out esn, asn, download time (first 3 col)
            i = 3
            while i < prf_col_size:

                # make list of values that correspond to column and flight
                ma_list = []

                # do not perform calculations on columns containing text values
                if i in text_cols:
                    out1.write(prf_col[i][current_in[0]] + ",")

                    if flight.designation <= train_size:
                        out2.write(prf_col[i][current_in[0]] + ",")
                    if train_size < flight.designation <= (train_size + test_size):
                        out3.write(prf_col[i][current_in[0]] + ",")
                    if flight.designation > (train_size + test_size):
                        out4.write(prf_col[i][current_in[0]] + ",")
                    if engine1.designation_1 <= train_size:
                        out5.write(prf_col[i][current_in[0]] + ",")
                    if train_size < engine1.designation_1 <= (train_size + test_size):
                        out6.write(prf_col[i][current_in[0]] + ",")
                    if engine1.designation_1 > (train_size + test_size):
                        out7.write(prf_col[i][current_in[0]] + ",")

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

                    if flight.designation <= train_size:
                        out2.write(str(mini) + ",")
                        out2.write(str(maxi) + ",")
                    if train_size < flight.designation <= (train_size + test_size):
                        out3.write(str(mini) + ",")
                        out3.write(str(maxi) + ",")
                    if flight.designation > (train_size + test_size):
                        out4.write(str(mini) + ",")
                        out4.write(str(maxi) + ",")
                    if engine1.designation_1 <= train_size:
                        out5.write(str(mini) + ",")
                        out5.write(str(maxi) + ",")
                    if train_size < engine1.designation_1 <= (train_size + test_size):
                        out6.write(str(mini) + ",")
                        out6.write(str(maxi) + ",")
                    if engine1.designation_1 > (train_size + test_size):
                        out7.write(str(mini) + ",")
                        out7.write(str(maxi) + ",")

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

                    if flight.designation <= train_size:
                        out2.write(str(meaner) + ",")
                        out2.write(str(stde) + ",")
                    if train_size < flight.designation <= (train_size + test_size):
                        out3.write(str(meaner) + ",")
                        out3.write(str(stde) + ",")
                    if flight.designation > (train_size + test_size):
                        out4.write(str(meaner) + ",")
                        out4.write(str(stde) + ",")
                    if engine1.designation_1 <= train_size:
                        out5.write(str(meaner) + ",")
                        out5.write(str(stde) + ",")
                    if train_size < engine1.designation_1 <= (train_size + test_size):
                        out6.write(str(meaner) + ",")
                        out6.write(str(stde) + ",")
                    if engine1.designation_1 > (train_size + test_size):
                        out7.write(str(meaner) + ",")
                        out7.write(str(stde) + ",")
                i += 1

            # write grounding errors or non grounding by flight depending on error severity
            if flight.final_e.severity == '2':
                out1.write('Grounding, 1\n')

                if flight.designation <= train_size:
                    out2.write('Grounding, 1\n')
                if train_size < flight.designation <= (train_size + test_size):
                    out3.write('Grounding, 1\n')
                if flight.designation > (train_size + test_size):
                    out4.write('Grounding, 1\n')
                if engine1.designation_1 <= train_size:
                    out5.write('Grounding, 1\n')
                if train_size < engine1.designation_1 <= (train_size + test_size):
                    out6.write('Grounding, 1\n')
                if engine1.designation_1 > (train_size + test_size):
                    out7.write('Grounding, 1\n')

            elif flight.final_e.severity == '47':
                out1.write("Non-grounding, 0\n")

                if flight.designation <= train_size:
                    out2.write('Non-grounding, 0\n')
                if train_size < flight.designation <= (train_size + test_size):
                    out3.write('Non-grounding, 0\n')
                if flight.designation > (train_size + test_size):
                    out4.write('Non-grounding, 0\n')
                if engine1.designation_1 <= train_size:
                    out5.write('Non-grounding, 0\n')
                if train_size < engine1.designation_1 <= (train_size + test_size):
                    out6.write('Non-grounding, 0\n')
                if engine1.designation_1 > (train_size + test_size):
                    out7.write('Non-grounding, 0\n')

            else:
                out1.write("Non-grounding, 0\n")

                if flight.designation <= train_size:
                    out2.write("Non-grounding, 0\n")
                if train_size < flight.designation <= (train_size + test_size):
                    out3.write("Non-grounding, 0\n")
                if flight.designation > (train_size + test_size):
                    out4.write("Non-grounding, 0\n")
                if engine1.designation_1 <= train_size:
                    out5.write("Non-grounding, 0\n")
                if train_size < engine1.designation_1 <= (train_size + test_size):
                    out6.write("Non-grounding, 0\n")
                if engine1.designation_1 > (train_size + test_size):
                    out7.write("Non-grounding, 0\n")

        # update progress value and label to indicate progress
        progress7['value'] += chunk7
        printer.configure(
            text='Printing to csvs... ({:,}'.format(len(engine_list)) + ' engines) --> {:6.2f}'.format(
                progress7['value']) + '%', foreground='white')
        root.update()

    # update label to indicate completion
    printer.configure(
        text='Printing to: "' + "./" + output_filename.split(".")[0] + " results/" + '" Folder Complete. ({:,}'.format(
            len(engine_list)) + ' engines) --> {:6.2f}'.format(
            progress7['value']) + '%', foreground='green')
    root.update()


# brings it all together
def run_it(moder, instance_file, error_occurrences_file, error_class_file, output_file):

    # displays progress interface according to moder value
    if moder != 4 and moder != 3:
        root.update()
        root.deiconify()

    # updates background color for progress interface
    root.configure(background='black')

    # update progress value and label to indicate progress
    reader.configure(text='Reading Files... (3 files) --> {:6.2f}'.format(
        progress['value']) + '%', foreground='white')
    root.update()
    progress['value'] += 0
    root.update()

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
    root.update()

    # read second file
    error_o_list = try_ito(error_occurrences_file)

    # update progress value and label to indicate progress
    progress['value'] += 33
    reader.configure(text='Reading Files... (3 files) --> {:6.2f}'.format(
        progress['value']) + '%', foreground='white')
    root.update()
    time.sleep(.5)

    # read third file
    ec_list = try_ito(error_class_file)


    # update progress value and label to indicate completion
    progress['value'] += 34
    reader.configure(text='Reading Files Complete. (3 files) --> {:6.2f}'.format(
        progress['value']) + '%', foreground='green')
    root.update()

    # prints progress to window
    print("(1/8) Files Read.\n")
    print("Grouping Flights...")


    # groups flights using rows of prf file (excluding the column titles)
    grouped_flights = group_flights(instance_list[0][1:])

    # prints progress to window
    print("(2/8) Flights grouped.\n")
    print("Grouping Engines...")


    # groups flights by engine
    grouped_engines = group_engines(grouped_flights)

    # prints progress to window
    print("(3/8) Engines Grouped.\n")
    print("Assigning Errors...")


    # assigns errors using rows of flt file (excluding the column titles)
    assign_errors(grouped_engines, error_o_list[0][1:])

    # prints progress to window
    print("(4/8) Errors assigned.\n")
    print("Updating Errors...")


    # updates errors using rows of error code file (excluding the column titles)
    update_errors(grouped_engines, ec_list[0][1:])

    # prints progress to window
    print("(5/8) Errors updated.\n")
    print("Updating Severity...")


    # updates severity of all flights
    update_severity(grouped_engines)

    # prints progress to window (includes output file name)
    print("(6/8) Severity updated.\n")
    print(
        "(7/8) Printing to Folder: " + "./" + output_title.split(".")[0] + " results/\n")


    # prints to output file using column titles from prf file and the values grouped by column from the prf file
    output_csv(grouped_engines, output_file, instance_list[0][0], instance_list[1])


    # updates completion label showing the time it took to complete the program
    timer.configure(text='This took: --- %s seconds --- to complete' % (time.time() - start_time), foreground='green')
    root.update()


    # prints time taken to complete program to window
    print("(8/8) Complete. --- %s seconds ---" % (time.time() - start_time))


    # create folder and move results files to folder
    output_folder = "./" + output_title + " results/"
    create_folder(output_folder)
    shutil.move(output_title, output_folder)
    shutil.move("fg_train_" + output_title, output_folder)
    shutil.move("fg_test_" + output_title, output_folder)
    shutil.move("fg_eval_" + output_title, output_folder)
    shutil.move("eg_train_" + output_title, output_folder)
    shutil.move("eg_test_" + output_title, output_folder)
    shutil.move("eg_eval_" + output_title, output_folder)


    # if moder 4 or 3 then exits here
    if moder == 4 or moder == 3:
        exit(0)

    # initializes a button that can be used to open the output file and packs it to window
    opener = Button(root, text='Open Output Folder', command=open_it)
    opener.pack(side=RIGHT, padx=20)

    # initializes an exit button and packs to window
    exiter = Button(root, text='Exit', command=get_out2)
    exiter.pack(side=RIGHT)



if __name__ == "__main__":
    print("Python v3.8\nThe Labeler v4\n\n")

    # function that quits the program and displays an information message that this action was performed
    def get_out():
        master.quit()
        print("You quit the program.")
        messagebox.showinfo("Quit Message", "You quit the program.")
        exit(0)

    # uses file chooser to find file and populate path name to entry field
    def file_e1():
        master.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                     filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        e1.delete(0, END)
        e1.insert(0, master.filename)
        return

    # uses file chooser to find file and populate path name to entry field
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

    # initializes file chooser window
    master = tk.Tk()
    master.title('Input Files')
    master.configure(background='gray64')

    # create protocol to handle premature closure
    master.protocol("WM_DELETE_WINDOW", get_out2)

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
    output_title = "label_run" + filler + ".csv"

    # displays message showing the name of the output file
    messagebox.showinfo("Output File Name",
                        "The Output Files for this process will be called: \n\n" + output_title + "\nfg_train_" +
                        output_title + "\nfg_test_" + output_title + "\nfg_eval_" + output_title + "\neg_train_" +
                        output_title + "\neg_test_" + output_title + "\neg_eval_" +
                        output_title + "\n\nThese files will be located in:\n" + "./" +
                        output_title.split(".")[0] + " results/\n\n" + "in the same location that the source csv "
                                                                       "files were stored in.")


    run_it(1, e1.get(), e2.get(), e3.get(), output_title)

    root.mainloop()
