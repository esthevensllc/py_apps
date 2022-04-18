#!/bin/sh
var_fecha_ini=`date +%d/%m/%Y' '%H:%M:%S`

source /index1/tareas/proyectos_python/env/bin/activate
cd /index1/tareas/proyectos_python/apps/py_apps/
#equipos
python3 main.py src.apic.nodes.services.LoadNodes
echo ""
#tenants
python3 main.py src.apic.tenants.services.LoadTenants

var_fecha_fin=`date +%d/%m/%Y' '%H:%M:%S`
echo "Fecha inicio - fin: ${var_fecha_ini} - ${var_fecha_fin}"
