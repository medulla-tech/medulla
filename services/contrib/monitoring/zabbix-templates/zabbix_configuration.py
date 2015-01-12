import zabbix_api
import argparse
from os.path import basename

parser = argparse.ArgumentParser(description='Configure Zabbix Server')
parser.add_argument('--url', dest='url', default='http://localhost/zabbix', help='Zabbix server address')
parser.add_argument('-u', '--user', dest='user', default='admin', help='Zabbix user')
parser.add_argument('-p', '--password', dest='password', required=True, help='Zabbix password')
parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Verbose')

subparsers = parser.add_subparsers(dest='subparser_name')

parser_template = subparsers.add_parser('template', help="Add a template")
parser_template.add_argument('template', type=argparse.FileType('r'), help='Template XML file')

parser_template = subparsers.add_parser('autoregistration', help="Create a autoregistration action")
parser_template.add_argument('-t', '--template-name', dest='template_name', default=None, help='Auto registred host is linked to this template name')

args = parser.parse_args()

zapi = zabbix_api.ZabbixAPI(server=args.url, path="", log_level=0)
zapi.login(args.user, args.password)


if args.subparser_name == "template":
    try:
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
    except zabbix_api.ZabbixAPIException as e:
        if args.verbose:
            print e
        print "Error: template import failed."
        exit(1)
    print "Importing template: %s" % basename(args.template.name)
    exit(0)


if args.subparser_name == "autoregistration":
    operations = [{
        # Default operation: add host
        "operationtype": 2}]
    
    # If a template name is provided, an operation that will
    # automaticaly link the template to the autodiscovered host is
    # created
    if args.template_name:
        ret = zapi.template.get({
            "output": "extend",
            "filter": {
                "host": [
                    args.template_name
                    #"Template App Zabbix Agent",
                ]}})
        if len(ret)>0 and 'hostid' in ret[0]:
            operations.append({
                "operationtype": 6,
                "optemplate": [
                    {"templateid": 10050}]})
        else:
            print "Error: template '%s' does not exist" % args.template_name

    ret = zapi.action.create({
        "name": "Auto Registration action",
        "eventsource": 2,
        "status": 0,
        "esc_period": 0,
        "evaltype": 0,
        "operations": operations
    })
    print ret
