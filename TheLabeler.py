import csv
import datetime
import time

start_time = time.time()
# define file names
filename_readfrom = "FLT.csv"
filename_writeto = "PRF.csv"
# define time range that will determine flight groupings
TIME_INTERVAL_HOUR = 1
TIME_INTERVAL_MIN = 30

# Open and create file readers
f1 = open(filename_readfrom)
f2 = open(filename_writeto)
csv_f1 = csv.reader(f1)
csv_f2 = csv.reader(f2)

# initialize empty list
serial_date_listflt = []

# read relevant features from file into list as tuples
for line in csv_f1:
    addition = (line[0], line[2], line[8])
    serial_date_listflt.append(addition)

# initialize empty list
serial_date_listprf = []

# read relevant features from file into list as tuples
for line2 in csv_f2:
    addition2 = (line2[0], line2[2], line2)
    serial_date_listprf.append(addition2)

# close files
f1.close()
f2.close()

del serial_date_listprf[0]
del serial_date_listflt[0]


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
    def __init__(self, esn, start_datetime, end_datetime, flight_list, error_indicator):
        self.esn = esn
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.flight_list = flight_list
        self.error_indicator = error_indicator


class Engine:
    def __init__(self, esn, list_flights):
        self.esn = esn
        self.list_flights = list_flights


# function for grouping flights based on time instances, assumes organized by time
def group_flights(prf_list):
    grouped_flight_list = []
    i = 0
    for element in prf_list:
        if i == 0:
            grouped_flight_list.append(Flight(element[0], element[1], element[1], [], []))
        else:
            if grouped_flight_list[-1].esn == element[0] and (
                    within_5(grouped_flight_list[-1].start_datetime, element[1], TIME_INTERVAL_HOUR,
                             TIME_INTERVAL_MIN) or within_5(grouped_flight_list[-1].end_datetime, element[1],
                                                            TIME_INTERVAL_HOUR, TIME_INTERVAL_MIN)):
                grouped_flight_list[-1].flight_list.append(element)
                if convertdt(element[1]) < convertdt(grouped_flight_list[-1].start_datetime):
                    grouped_flight_list[-1].start_datetime = element[1]
                if convertdt(element[1]) > convertdt(grouped_flight_list[-1].end_datetime):
                    grouped_flight_list[-1].end_datetime = element[1]
            else:
                grouped_flight_list.append(Flight(element[0], element[1], element[1], [], []))
        i += 1
    return grouped_flight_list


def group_engines(grouped_flight_list):
    engine_list = []
    temp_list_e = []
    for element in grouped_flight_list:
        if element.esn not in temp_list_e:
            engine_list.append(Engine(element.esn, []))
            temp_list_e.append(element.esn)
    for flight in grouped_flight_list:
        for engine in engine_list:
            if engine.esn == flight.esn:
                engine.list_flights.append(flight)
    return engine_list


def assign_errors(grouped_engines, flt_list):
    for row in flt_list:
        for engine in grouped_engines:
            if engine.esn == row[0]:
                for flight in engine.list_flights:
                    if within_5(flight.start_datetime, row[1], TIME_INTERVAL_HOUR, TIME_INTERVAL_MIN) or within_5(
                            flight.end_datetime, row[1], TIME_INTERVAL_HOUR, TIME_INTERVAL_MIN):
                        flight.error_indicator.append(row[2])

# answer = group_flights(serial_date_listprf[:2])
# for piece in answer:
#     for row in piece.flight_list:
#         print(str(row[2]).replace("'", "").strip("[").strip("]"))

answer = group_flights(serial_date_listprf)
answer2 = group_engines(answer)
assign_errors(answer2, serial_date_listflt)


print("--- %s seconds ---" % (time.time() - start_time))


file1 = open("myfile2.csv", "w")
for engine in answer2:
    for flight in engine.list_flights:
        for row in flight.flight_list:
            file1.write(str(row[2]).replace("'", "").strip("[").strip("]") + "," + str(flight.error_indicator).replace("'", "").strip("[").strip("]") + "\n")
        # file1.write(flight.esn + "," + flight.start_datetime + "," + flight.end_datetime + "," + str(flight.error_indicator).replace("'", "").strip("[").strip("]") + "\n")

file1.close()  # to change file access modes