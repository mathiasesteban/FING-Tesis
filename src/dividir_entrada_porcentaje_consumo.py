import pandas as pd

def dividir_entrada_porcentaje_consumo(path_data, path_aggregate):


    agg_file_panda = pd.read_csv(path_aggregate, sep=" ", header=None)
    agg_file_panda.columns = ["Timestamp", "Consumo"]
    agg_file_panda = agg_file_panda.set_index("Timestamp")

    app_file_panda = pd.read_csv(path_data, sep=" ", header=None)
    app_file_panda.columns = ["Timestamp", "Consumo"]
    app_file_panda = app_file_panda.set_index("Timestamp")

    app_file_reduced = []

    for index, row in app_file_panda.iterrows():

        # Si existe timestamp en el archivo de consumo agregado
        if index in agg_file_panda.index:
            vector_entrada = [index, row["Consumo"]]
            app_file_reduced.append(vector_entrada)

    length_file = len(app_file_reduced)

    line_to_divide = 80 * length_file / 100

    file_porcentaje_consumo_train = open(path_data + "_80_filtrado_consumo",'w')
    file_porcentaje_consumo_validate = open(path_data + "_20_filtrado_consumo",'w')

    cont = 1
    for line in app_file_reduced:
        if cont <= line_to_divide:
            file_porcentaje_consumo_train.write(str(line[0]) + ' ' + str(line[1]) + '\n')
        else:
            file_porcentaje_consumo_validate.write(str(line[0]) + ' ' + str(line[1]) + '\n')
        cont = cont + 1

    file_porcentaje_consumo_train.close()
    file_porcentaje_consumo_validate.close()


if __name__ == '__main__':

    path_data = "/home/nacho/Escritorio/FING/Proyecto/ukdale/house_1/channel_5.dat"
    path_aggregate = "/home/nacho/Escritorio/FING/Proyecto/ukdale/house_1/channel_1.dat"

    dividir_entrada_porcentaje_consumo(path_data, path_aggregate)
