
def dividir_archivo_porcentaje(path, porcentaje):

    file_dat = open(path)

    primer_fragmento = open(path + "_" + str(porcentaje), 'w')
    segundo_fragmento = open(path + "_" + str(100 - porcentaje), 'w')

    content = file_dat.readlines()

    total_registros = len(content)

    print("El archivo contiene: " + str(total_registros) + " registros")

    lineas_porcentaje = int(total_registros * porcentaje / 100)

    counter = 0

    for line in content:
        counter += 1
        if counter < lineas_porcentaje:
            primer_fragmento.write(line)
        else:
            segundo_fragmento.write(line)

    file_dat.close()
    primer_fragmento.close()
    segundo_fragmento.close()

if __name__ == '__main__':

    # Parametros
    porcentaje = 80
    path = "/home/ignacio/Escritorio/Respaldo/tesis/src/house_1/channel_12.dat"

    dividir_archivo_porcentaje(path, porcentaje)
