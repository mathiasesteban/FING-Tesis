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


def separar_meses(path_to_dat_file):

    f = open(path_to_dat_file)

    content = f.readlines()
    content = [x.strip() for x in content]

    mes_actual = -1
    anio_actual = -1

    for line in content:

        dia_medicion = line.split()
        unix_date = int(dia_medicion[0])

        if mes_actual == -1 or anio_actual == -1:

            mes_actual = datetime.utcfromtimestamp(unix_date).strftime('%m')
            anio_actual = datetime.utcfromtimestamp(unix_date).strftime('%Y')

            file_mediciones = open(path_to_dat_file + "ANO" + anio_actual + '-MES' + mes_actual,'w')
            file_mediciones.write(dia_medicion[0] + ' ' + dia_medicion[1] + '\n')

        else:

            if datetime.utcfromtimestamp(unix_date).strftime('%m') != mes_actual or datetime.utcfromtimestamp(unix_date).strftime('%Y') != anio_actual:
                file_mediciones.close()
                mes_actual = datetime.utcfromtimestamp(unix_date).strftime('%m')
                anio_actual = datetime.utcfromtimestamp(unix_date).strftime('%Y')
                file_mediciones = open(path_to_dat_file + "ANO" + anio_actual + '-MES' + mes_actual, 'w')

            file_mediciones.write(dia_medicion[0] + ' ' + dia_medicion[1] + '\n')


if __name__ == '__main__':

    dia = int(sys.argv[1])
    mes = int(sys.argv[2])
    ano = int(sys.argv[3])

    path = sys.argv[4]

    dividir_archivo_dat(dia, mes, ano, path)