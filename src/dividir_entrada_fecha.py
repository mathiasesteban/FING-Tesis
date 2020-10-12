from datetime import datetime
import sys
import time

def dividir_archivo_dat(dia, mes, ano, path):

    file_dat = open(path)
    file_dat_before = open(path + "-BEFORE-" + str(dia) + str(mes) + str(ano) ,'w')
    file_dat_after = open(path + "-AFTER-" + str(dia) + str(mes) + str(ano) ,'w')

    date = datetime(ano, mes, dia)
    date_timestamp = time.mktime(date.timetuple())

    content = file_dat.readlines()

    for line in content:
        medicion = line.split()

        if int(medicion[0]) < date_timestamp:
            file_dat_before.write(line)
        else:
            file_dat_after.write(line)

    file_dat.close()
    file_dat_before.close()
    file_dat_after.close()

if __name__ == '__main__':

    dia = int(sys.argv[1])
    mes = int(sys.argv[2])
    ano = int(sys.argv[3])

    path = sys.argv[4]

    dividir_archivo_dat(dia, mes, ano, path)