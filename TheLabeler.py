import csv
import datetime

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
    addition2 = (line2[0], line2[2])
    serial_date_listprf.append(addition2)

# close files
f1.close()
f2.close()

del serial_date_listprf[0]
del serial_date_listflt[0]

# accepts two strings from lists created and time interval which indicates range for same flight
def within_5(datetime1, datetime2, time_interval_hour, time_interval_min):
    # split date and time by the space between them
    date_tester1 = datetime1.split()
    date_tester2 = datetime2.split()
    # input date and time from split string to create datetime objects
    first_test = datetime.datetime(int(date_tester1[0].split('/')[2]), int(date_tester1[0].split('/')[0]),
                                   int(date_tester1[0].split('/')[1]), int(date_tester1[1].split(':')[0]),
                                   int(date_tester1[1].split(':')[1]))
    second_test = datetime.datetime(int(date_tester2[0].split('/')[2]), int(date_tester2[0].split('/')[0]),
                                    int(date_tester2[0].split('/')[1]), int(date_tester2[1].split(':')[0]),
                                    int(date_tester2[1].split(':')[1]))
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

        # list attributes of grouped flight instances
        def characteristics():
            return flight_list, error_indicator


# function for grouping flights based on time instances
def group_flights(flt_list, prf_list):
    # create empty list for flight objects to be placed
    grouped_flights = []
    for element in prf_list:
        date_tester1 = element[1].split()
        empty_flight_list = []
        empty_error = "NONE"
        engine_num = element[0]
        ff1 = Flight(engine_num, element[1], element[1], empty_flight_list, empty_error)

        for element1 in prf_list:
            if ff1.esn == element1[0] and within_5(element[1], element1[1], TIME_INTERVAL_HOUR,
                                                   TIME_INTERVAL_MIN) and element1 not in ff1.flight_list:
                ff1.flight_list.append(element)
        grouped_flights.append(ff1)
        print(ff1.flight_list)

# errorlist = []
# j = 0
# while j < 100:
#
#     for element in serial_date_listprf:
#         j = j + 1
#         i = 0
#         while i < len(serial_date_listflt) and i != -1:
#             for element2 in serial_date_listflt:
#                 i = i + 1
#                 if element[1] == element2[1] and element[0] == element2[0]:
#                     errorlist.append([str(element2[2])])
#                     i = -1
#         errorlist.append(['0'])
#
# with open('Output2.csv', 'w') as csvFile:
#     writer = csv.writer(csvFile)
#     for element3 in errorlist:
#         writer.writerow(element3)
# csvFile.close()

group_flights(serial_date_listflt[:10], serial_date_listprf[:10])
