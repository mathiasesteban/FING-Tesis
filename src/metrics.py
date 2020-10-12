from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from cambios_de_estado import *
from sklearn.metrics import accuracy_score


# Desactivar warnings SCI LEARN
def warn(*args, **kwargs):
    pass


import warnings
warnings.warn = warn


def obtener_metricas(real_output, predictions):

    encendidos = 0
    apagados = 0
    encendidos_reales = 0
    apagados_reales = 0

    for i in range(len(real_output)):

        # Predicciones de clase
        if predictions[i] == 0:
            apagados += 1
        else:
            encendidos += 1

        # Totales
        if real_output[i] == 0:
            apagados_reales += 1
        else:
            encendidos_reales += 1

    target_names = ['Apagado', 'Prendido']
    report = classification_report(real_output, predictions, target_names=target_names, output_dict=True)

    TN, FP, FN, TP = confusion_matrix(real_output, predictions).ravel()

    accuracy_calculetd = (TP + TN) / (TP + TN + FP + FN)

    accuracy = accuracy_score(real_output, predictions)

    cambios_estado_real_enc, cambios_estado_real_apg, cambios_estado_pred_enc, cambios_estado_pred_apg, cambios_estado_acer_enc, cambios_estado_acer_apg = calculo_cambios_de_estado(predictions, real_output)

    res = {
        'TP': TP,
        'TN': TN,
        'FP': FP,
        'FN': FN,
        'accuracy': accuracy,
        'accuracy_calculetd': accuracy_calculetd,
        'precision': report['Prendido']['precision'],
        'recall': report['Prendido']['recall'],
        'f1': report['Prendido']['f1-score'],
        'encendidos_pred': encendidos,
        'encendidos_real': encendidos_reales,
        'apagados_pred': apagados,
        'apagados_real': apagados_reales,
        'cambios_estado_real_enc': cambios_estado_real_enc,
        'cambios_estado_real_apg': cambios_estado_real_apg,
        'cambios_estado_acer_enc': cambios_estado_acer_enc,
        'cambios_estado_acer_apg': cambios_estado_acer_apg
    }

    return res


def imprimir_metricas(real_output, predictions):

    metricas = obtener_metricas(real_output, predictions)

    print("\n")
    print("*********************************************************************")
    print("RESULTADOS")
    print("*********************************************************************\n")

    print("TP: " + str(metricas['TP']))
    print("TN: " + str(metricas['TN']))
    print("FP: " + str(metricas['FP']))
    print("FN: " + str(metricas['FN']))
    print("")

    print("Accuracy: " + str(metricas['accuracy']))
    print("Accuracy Calculada: " + str(metricas['accuracy_calculetd']))
    print("Precision: " + str(metricas['precision']))
    print("Recall: " + str(metricas['recall']))
    print("")

    print("Encendidos predichos: " + str(metricas['encendidos_pred']))
    print("Apagados predichos: " + str(metricas['apagados_pred']))
    print("Encendidos reales: " + str(metricas['encendidos_real']))
    print("Apagados reales: " + str(metricas['apagados_real']))
    print("")

    print("Cambios de estado reales encendidos: " + str(metricas['cambios_estado_real_enc']))
    print("Cambios de estado reales apagados: " + str(metricas['cambios_estado_real_apg']))
    print("Cambios de estado acertados encendidos: " + str(metricas['cambios_estado_acer_enc']))
    print("Cambios de estado acertados apagados: " + str(metricas['cambios_estado_acer_apg']))
    print("")

    total_cambios = metricas['cambios_estado_real_enc'] + metricas['cambios_estado_real_apg']
    total_aciertos = metricas['cambios_estado_acer_enc'] + metricas['cambios_estado_acer_apg']
    porcentaje = round((total_aciertos * 100) / total_cambios)

    print("F1: " + str(metricas['f1']))
    print("Porcentaje acierto c/e: " + str(porcentaje))
    print("")


def obtener_metricas_estados(real_output, predictions, states):
    accuracy = accuracy_score(real_output, predictions)

    cambios_estado_real_enc, cambios_estado_real_apg, cambios_estado_pred_enc, cambios_estado_pred_apg, cambios_estado_acer_enc, cambios_estado_acer_apg = calculo_cambios_de_estado(predictions, real_output) 
    
    res = {
        'accuracy': accuracy,
        'cambios_estado_real_enc': cambios_estado_real_enc,
        'cambios_estado_real_apg': cambios_estado_real_apg,
        'cambios_estado_pred_enc': cambios_estado_pred_enc,
        'cambios_estado_pred_apg': cambios_estado_pred_apg,
        'cambios_estado_acer_enc': cambios_estado_acer_enc,
        'cambios_estado_acer_apg': cambios_estado_acer_apg
    }

    return res    


def imprimir_metricas_estados(real_output, predictions, states):

    metricas = obtener_metricas_estados(real_output, predictions, states)

    for key in metricas.keys():
        print(str(key) + ": " + str(metricas[key]))
