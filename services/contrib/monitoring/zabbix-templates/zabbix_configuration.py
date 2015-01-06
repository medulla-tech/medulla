import zabbix_api
import argparse

parser = argparse.ArgumentParser(description = 'Configure Zabbix Server')
parser.add_argument('--url', dest = 'url', default = 'http://localhost/zabbix', help = 'Zabbix server address')
parser.add_argument('-u', '--user', dest = 'user', default = 'admin', help = 'Zabbix user')
parser.add_argument('-p', '--password', dest = 'password', required=True, help = 'Zabbix password')

subparsers = parser.add_subparsers(dest='subparser_name')

parser_template = subparsers.add_parser('template', help="Add a template")
parser_template.add_argument('template', type=argparse.FileType('r'), help='Template XML file')

parser_template = subparsers.add_parser('autoregistration', help="Create a autoregistration action")

args = parser.parse_args()

zapi = zabbix_api.ZabbixAPI(server=args.url, path="", log_level=0)
zapi.login(args.user, args.password)

if args.subparser_name == "template":
    ret = zapi.configuration.import_(
        {'rules': {
            'templates': {'createMissing': True, 'updateExisting': True},
            'items': {'createMissing': True, 'updateExisting': True},
            'graphs': {'createMissing': True, 'updateExisting': True},
            'hosts': {'createMissing': True, 'updateExisting': True},
            'screens': {'createMissing': True, 'updateExisting': True},
            'triggers': {'createMissing': True, 'updateExisting': True},
            'applications': {'createMissing': True, 'updateExisting': True},
            'discoveryRules': {'createMissing': True, 'updateExisting': True}

        },
         'format': 'xml',
         'source': args.template.read()})
    print ret

if args.subparser_name == "autoregistration":
    ret = zapi.action.create({
        "name": "Auto Registration action",
        "eventsource": 2,
        "status": 0,
        "esc_period": 0,
        "evaltype": 0,
        "operations": [
            {
                "operationtype": 2,
            }
        ]
    })
    print ret
