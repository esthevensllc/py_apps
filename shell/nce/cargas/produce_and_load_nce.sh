#!/bin/sh
var_fecha_ini=`date +%d/%m/%Y' '%H:%M:%S`

source /index1/tareas/proyectos_python/env/bin/activate
cd /index1/tareas/proyectos_python/apps/py_apps/
python3 main.py src.nce.cargas.services.CargasEventProducer
var_fecha_fin=`date +%d/%m/%Y' '%H:%M:%S`
echo "Fecha inicio - fin: ${var_fecha_ini} - ${var_fecha_fin}"

count_process=$(ps -aux | grep src.nce.shared.services.nce_async_event_consumer | wc -l)
count_process=$((count_process-1))
if [ $count_process -lt 1 ]; then
	var_fecha_ini=`date +%d/%m/%Y' '%H:%M:%S`
	python3 main.py src.nce.shared.services.nce_async_event_consumer

	var_fecha_fin=`date +%d/%m/%Y' '%H:%M:%S`
	echo "Fecha inicio - fin: ${var_fecha_ini} - ${var_fecha_fin}"
fi
