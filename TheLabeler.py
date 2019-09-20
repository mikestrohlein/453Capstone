import csv
import datetime

filename_readfrom = "FLT.csv"
filename_writeto = "PRF.csv"

# with open(filename_readfrom, 'r') as csv_file:
#     csv_reader = csv.reader(csv_file)
#     serial_date_listflt = []
#
#     for line in csv_reader:
#         addition = (line[0], line[2])
#         serial_date_listflt.append(addition)
#     print(serial_date_listflt)
#
# csv_file.close()
#
# with open(filename_writeto, 'r') as csv_file:
#     csv_reader = csv_reader(csv_file)
#     serial_date_listprf = []
#
#     for liner in csv_reader:
#         addition2 = (liner[0], liner[2])
#         serial_date_listprf.append(addition2)
#     print(serial_date_listprf)

f1 = open(filename_readfrom)
f2 = open(filename_writeto)
csv_f1 = csv.reader(f1)
csv_f2 = csv.reader(f2)

serial_date_listflt = []

for line in csv_f1:
    addition = (line[0], line[2], line[8])
    serial_date_listflt.append(addition)

serial_date_listprf = []

for line2 in csv_f2:
    addition2 = (line2[0], line2[2])
    serial_date_listprf.append(addition2)

f1.close()
f2.close()


def within_5(datetime1, datetime2, time_intervalh, time_intervalm):
    date_tester1 = datetime1.split()
    date_tester2 = datetime2.split()
    first_test = datetime.datetime(int(date_tester1[0].split('/')[2]), int(date_tester1[0].split('/')[0]),
                                   int(date_tester1[0].split('/')[1]), int(date_tester1[1].split(':')[0]),
                                   int(date_tester1[1].split(':')[1]))
    second_test = datetime.datetime(int(date_tester2[0].split('/')[2]), int(date_tester2[0].split('/')[0]),
                                    int(date_tester2[0].split('/')[1]), int(date_tester2[1].split(':')[0]),
                                    int(date_tester2[1].split(':')[1]))

    if second_test > first_test:
        answer = second_test - first_test
    else:
        answer = first_test - second_test

    print(answer)

    if answer <= datetime.timedelta(hours=time_intervalh, minutes=time_intervalm):
        print("yes")
    else:
        print("no")


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
test1 = '12/31/2017 13:33'
test2 = '12/31/2017 12:00'
within_5(test1, test2, 1, 30)
