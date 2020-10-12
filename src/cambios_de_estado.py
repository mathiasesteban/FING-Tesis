def calculo_cambios_de_estado(predicciones, reales):
	if len(predicciones) != len(reales):
		return False
	cambios_estado_real_enc = 0
	cambios_estado_real_apg = 0
	cambios_estado_pred_enc = 0
	cambios_estado_pred_apg = 0
	cambios_estado_acer_enc = 0
	cambios_estado_acer_apg = 0
	for i in range(1,len(predicciones)):
		if reales[i] == 0 and reales[i-1] != 0:
			cambios_estado_real_apg += 1
		if reales[i] != 0 and reales[i-1] == 0:
			cambios_estado_real_enc += 1

		if predicciones[i] == 0 and predicciones[i-1] != 0:
			cambios_estado_pred_apg += 1
			if predicciones[i] == reales[i] and reales[i] != reales[i-1]:
				cambios_estado_acer_apg += 1
				
		if predicciones[i] != 0 and predicciones[i-1] == 0:
			cambios_estado_pred_enc += 1
			if predicciones[i-1] == reales[i-1] and reales[i] != reales[i-1]:
				cambios_estado_acer_enc += 1
	return cambios_estado_real_enc, cambios_estado_real_apg, cambios_estado_pred_enc, cambios_estado_pred_apg, cambios_estado_acer_enc, cambios_estado_acer_apg 
		
		


