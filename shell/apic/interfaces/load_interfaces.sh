#!/bin/sh
var_fecha_ini=`date +%d/%m/%Y' '%H:%M:%S`

source /index1/tareas/proyectos_python/env/bin/activate
cd /index1/tareas/proyectos_python/apps/py_apps/
python3 main.py src.apic.interfaces.services.LoadAllInterfaces

var_fecha_fin=`date +%d/%m/%Y' '%H:%M:%S`
echo "Fecha inicio - fin: ${var_fecha_ini} - ${var_fecha_fin}"
