#!/bin/sh
var_fecha_ini=`date +%d/%m/%Y' '%H:%M:%S`

source /index1/tareas/proyectos_python/env/bin/activate
cd /index1/tareas/proyectos_python/apps/alarmas/
python3 main.py load_PM_IG7511_from_oracle_diario

var_fecha_fin=`date +%d/%m/%Y' '%H:%M:%S`
echo "Fecha inicio - fin: ${var_fecha_ini} - ${var_fecha_fin}"
