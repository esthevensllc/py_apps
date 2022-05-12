remote_dir=$1
local_dir=$2
mget_pather=$3

lftp << END_SCRIPT
open sftp://10.96.209.54
user ftpuser Changeme_123
cd "${remote_dir}"
lcd "${local_dir}"
mget "${mget_pather}"
bye
END_SCRIPT
