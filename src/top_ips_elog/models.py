SOURCE_COLUMNS = (
    'event_time',
    'start_time',
    'end_time',
    'router_ip',
    'router_port',
    'protocol_id',
    'protocol',
    'private_ip',
    'private_port',
    'public_ip',
    'public_port',
    'destination_ip',
    'destination_port',
    'packet_size',
)

DNS_IPS = (
    '179.6.231.3', '190.113.207.125', '190.113.207.126',
    '190.113.220.18', '190.113.220.26', '190.113.220.51',
    '190.113.220.52', '190.113.220.53', '190.113.220.54',
    '190.113.222.10', '190.113.222.11', '190.113.222.8',
    '190.113.222.9', '190.114.250.34', '190.114.251.2',
    '200.108.96.212', '200.108.96.213', '200.24.191.10',
    '200.24.191.11', '200.24.191.12', '200.24.191.8',
    '200.62.191.11', '200.62.191.12', '190.113.220.17',
    '200.62.191.10', '190.116.132.126', '190.116.132.127',
)


class TopQueryDefinition(object):
    def __init__(self, key, target_table, title):
        self.key = key
        self.target_table = target_table
        self.title = title


TOP_QUERY_DEFINITIONS = (
    TopQueryDefinition('destination_no_dns', 'Top_IPs_Dst_NO_DNS', 'Top IPs destino no DNS por uso'),
    TopQueryDefinition('private_dns', 'Top_IPs_Priv_con_Dst-DNS', 'Top IPs privadas con destino DNS por uso'),
    TopQueryDefinition('private_smtp_25', 'Top_IPs_Priv_SMTP_25', 'Top IPs privadas por uso de puerto SMTP 25'),
    TopQueryDefinition('private_usage', 'Top_IPs_Priv_Uso', 'Top IPs privadas por uso'),
)
