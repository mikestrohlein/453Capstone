import csv
import datetime
import time
from playsound import playsound

start_time = time.time()
# define file names
filename_readfrom = "FLT.csv"
filename_writeto = "PRF.csv"
error_codes = "ErrorCodes.csv"
# define time range that will determine flight groupings
TIME_INTERVAL_HOUR = 1
TIME_INTERVAL_MIN = 30

GROUNDING_ERRORS = []

# Open and create file readers
f1 = open(filename_readfrom)
f2 = open(filename_writeto)
f3 = open(error_codes)
csv_f1 = csv.reader(f1)
csv_f2 = csv.reader(f2)
csv_f3 = csv.reader(f3)

# initialize empty list
serial_date_listflt = []

# read relevant features from file into list as tuples
for line in csv_f1:
    addition = (line[0], line[2], line[8], line[7])
    serial_date_listflt.append(addition)

# initialize empty list
serial_date_listprf = []

# read relevant features from file into list as tuples
for line2 in csv_f2:
    addition2 = (line2[0], line2[2], line2)
    serial_date_listprf.append(addition2)

error_code_list = []
for line3 in csv_f3:
    addition3 = (line3[0], line3[1], line3[3])
    error_code_list.append(addition3)

# close files
f1.close()
f2.close()
f3.close()

# delete column titles so it does not interfere with the matching of these files
del serial_date_listprf[0]
del serial_date_listflt[0]


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


# create flight class to group flights and their attributes
class Flight:
    # engine serial number, range of times in the flight, list of grouped flights, and corresponding error
    def __init__(self, esn, start_datetime, end_datetime, flight_list, error):
        self.esn = esn
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.flight_list = flight_list
        self.error = error


# create engine class to group engines and the flights that correspond to it
class Engine:
    def __init__(self, esn, list_flights):
        self.esn = esn
        self.list_flights = list_flights


class Error:
    def __init__(self, code, name, severity, code_list, name_list, severity_list):
        self.code = code
        self.name = name
        self.severity = severity
        self.code_list = code_list
        self.name_list = name_list
        self.severity_list = severity_list

    def finalize(self):
        i = 0
        max_value = -99999999
        max_index = -99999999
        for element in self.severity_list:
            if int(element) > int(max_value):
                max_index = i
                max_value = element
            i += 1
        if int(max_index) < -999 or int(max_value) < -999:
            max_index = 0
        self.code = self.code_list[int(max_index)]
        self.name = self.name_list[int(max_index)]
        self.severity = self.severity_list[int(max_index)]


# function for grouping flights based on time instances, assumes organized by time
def group_flights(prf_list):
    grouped_flight_list = []
    i = 0
    for element in prf_list:
        if i == 0:
            # on the first instance a flight object must be initiated
            grouped_flight_list.append(Flight(element[0], element[1], element[1], [], Error(0, "Blank", -1, [], [], [])))
            grouped_flight_list[-1].flight_list.append(element)
        else:
            # if the esn is the same as the last flight and the time corresponds: add the current instance to the
            # flight list of the last flight object in the list of flight objects
            if grouped_flight_list[-1].esn == element[0] and (
                    within_5(grouped_flight_list[-1].start_datetime, element[1], TIME_INTERVAL_HOUR,
                             TIME_INTERVAL_MIN) or within_5(grouped_flight_list[-1].end_datetime, element[1],
                                                            TIME_INTERVAL_HOUR, TIME_INTERVAL_MIN)):
                grouped_flight_list[-1].flight_list.append(element)
                # update start and end time if necessary
                if convertdt(element[1]) < convertdt(grouped_flight_list[-1].start_datetime):
                    grouped_flight_list[-1].start_datetime = element[1]
                if convertdt(element[1]) > convertdt(grouped_flight_list[-1].end_datetime):
                    grouped_flight_list[-1].end_datetime = element[1]
            else:
                # otherwise initialize a new flight object and add it to the list of flight objects
                grouped_flight_list.append(Flight(element[0], element[1], element[1], [], Error(0, "Blank", -1, [], [], [])))
                grouped_flight_list[-1].flight_list.append(element)

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
            if engine.esn == flight.esn:
                engine.list_flights.append(flight)
    return engine_list


# assigns error to flight by matching instance to esn then finding if there is a corresponding flight and labels it
def assign_errors(grouped_engines, flt_list):
    for row in flt_list:
        for engine in grouped_engines:
            # first checks if esn values line up, if not on to the next engine
            if engine.esn == row[0]:
                for flight in engine.list_flights:
                    # checks if error instance lines up with a flight in the engine object
                    if within_5(flight.start_datetime, row[1], TIME_INTERVAL_HOUR, TIME_INTERVAL_MIN) or within_5(
                            flight.end_datetime, row[1], TIME_INTERVAL_HOUR, TIME_INTERVAL_MIN):
                        flight.error.name_list.append(row[2])
                        flight.error.code_list.append(row[3])


def update_errors(error_list, grouped_engines):
    added = False
    for engine in grouped_engines:
        for flight in engine.list_flights:
            flight_error_codes = flight.error.code_list
            for element in flight_error_codes:
                added = False
                for row in error_list:
                    if row[0] == element:
                        flight.error.severity_list.append(row[2])
                        added = True
                if not added:
                    flight.error.severity_list.append(0)
            flight.error.finalize()


# checks size of instances per flight (labeled flight number)
# ----------------------------------------------------------------
# checks size of flights per engine
# ----------------------------------------------------------------
# checks size of how many engines are present
def metadata_check(prf_list):
    i = 0
    answer44 = group_flights(prf_list)
    for flight in answer44:
        size = len(flight.flight_list)
        print(str(size) + "  " + str(i))
        i += 1

    print("---------------------")

    answer47 = group_engines(answer44)
    for engine in answer47:
        print(len(engine.list_flights))

    print("---------------------")

    print(len(answer47))


# mode 1: preserve flight instances
# mode 2: esn, start, end, error
def runit(serial_prf_list, serial_flt_list, mode):
    answer = group_flights(serial_date_listprf)
    answer2 = group_engines(answer)
    assign_errors(answer2, serial_date_listflt)
    update_errors(error_code_list, answer2)

    # gets today's date and current time then turns it to a string
    today = datetime.datetime.now()
    filler = str(today).replace(" ", "_").split(".")[0].replace(":", "--")

    # uses current date and time and mode to name the csv result file
    file1 = open("C:/Users/C20Michael.Strohlein/Desktop/Labeler Runs/labelrun__m" + str(mode) + "__" + filler + ".csv", "w")
    for engine in answer2:
        for flight in engine.list_flights:
            # mode 2: esn, start, end, error
            if mode == 2:
                file1.write(flight.esn + "," + flight.start_datetime + "," + flight.end_datetime + "," + str(
                    flight.error.name) + "," + str(flight.error.code) + "," + str(flight.error.severity) + "\n")
            for row in flight.flight_list:
                # mode 1: preserve flight instances
                if mode == 1:
                    file1.write(
                        str(row[2]).replace("'", "").strip("[").strip("]") + "," + str(flight.error.name) + "," + str(flight.error.code) + "," + str(flight.error.severity) + "\n")
    file1.close()


# track the time it took to run the program and record it in a separate csv file
def track_time():
    print("--- %s seconds ---" % (time.time() - start_time))
    filetrack = open("listofruntimes.csv", "a")
    filetrack.write(str(time.time() - start_time) + "\n")


runit(serial_date_listprf, serial_date_listflt, 2)
track_time()

