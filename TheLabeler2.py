import csv
import datetime
import time
import math

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

        i += 1
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
    for flight in grouped_flight_list:
        # second assigns flights to corresponding engine objects
        for engine in engine_list:
            if engine.serial_number == flight.esn:
                engine.flight_list.append(flight)
    return engine_list


# assigns error to flight by matching instance to esn then finding if there is a corresponding flight and labels it
def assign_errors(engine_list, flt_list):
    for row in flt_list:
        for engine in engine_list:
            # first checks if esn values line up, if not on to the next engine
            if engine.serial_number == row[0]:
                for flight in engine.flight_list:
                    # checks if error instance lines up with a flight in the engine object
                    if within_5(flight.start, row[2], TIME_INTERVAL_HOUR, TIME_INTERVAL_MIN) or within_5(
                            flight.end, row[2], TIME_INTERVAL_HOUR, TIME_INTERVAL_MIN):
                        flight.errors.append(Error(row[7], "NONE", 0))


# assigns error severities based on error code
def update_errors(engine_list, ec_list):
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


def update_severity(engine_list):
    i = 0
    for engine in engine_list:
        for flight in engine.flight_list:
            top_sev = 0
            for error in flight.errors:
                if int(error.severity) > int(top_sev):
                    flight.final_e = error
                    top_sev = error.severity
                    print(i)
        i += 1


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
                        im_to = float(im_to) + (float(part) - meaner)**2
                    ready = im_to / float(length)
                    stde = math.sqrt(ready)
                    out1.write(str(meaner) + ",")

                    out1.write(str(stde) + ",")
                i += 1
            out1.write(str(flight.final_e.code) + "," + flight.final_e.name + "," + str(flight.final_e.severity) + "\n")


def runit(instance_file, error_occurrences_file, error_class_file, output_file):
    start_time = time.time()
    print("Reading Files...")
    instance_list = try_ito(instance_file)
    error_o_list = try_ito(error_occurrences_file)
    ec_list = try_ito(error_class_file)
    print("(1/9) Files Read.")
    print("Grouping Flights...")
    grouped_flights = group_flights(instance_list[0][1:500])
    print("(2/9) Flights grouped.")
    print("Grouping Engines...")

    grouped_engines = group_engines(grouped_flights)

    print("temp")
    assign_errors(grouped_engines, error_o_list[0][1:])
    print("(5/9) Errors assigned.")
    print("Updating Errors...")
    update_errors(grouped_engines, ec_list[0][1:])
    print("(6/9) Errors updated.")
    print("Updating Severity...")
    update_severity(grouped_engines)
    print("(7/9) Severity updated.")
    print("(8/9) printing to: " + output_file)

    output_csv(grouped_engines, output_file, instance_list[0][0], instance_list[1])
    print("(9/9) Complete. --- %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    # a = str(sys.argv[1])
    # b = str(sys.argv[2])
    # c = str(sys.argv[3])
    # d = str(sys.argv[4])
    a = 'PRF.csv'
    b = 'FLT.csv'
    c = 'ErrorCodes.csv'
    d = 'FTry2.csv'
    runit(a, b, c, d)
