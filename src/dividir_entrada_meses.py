from datetime import datetime
import sys

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
    path = sys.argv[1]
    separar_meses(path)
