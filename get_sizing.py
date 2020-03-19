import spotinst_sdk

from argparse import ArgumentParser

parser = ArgumentParser(
    description='Generate kubectl output based on Spotinst Ocean sizing suggestions')
parser.add_argument('-d', '--deployment',
    help='Name of the deployment to grab suggestions for.')
parser.add_argument('-r', '--ratio', default=2,
    help='The number between resource requests divided by the suggestions.')
parser.add_argument('-t', '--auth_token',
    help='Spotinst API Token.')
parser.add_argument('-a', '--account_id',
    help='ID of the Spotinst account.')
parser.add_argument('-o', '--ocean_id',
    help='ID of the Ocean cluster.')
parser.add_argument('-n', '--namespace',
    help='Namespace of the deployment in the cluster.')
args = parser.parse_args()

try:
	client = spotinst_sdk.SpotinstClient(auth_token=args.auth_token,account_id=args.account_id)
except Exception as e:
	print('Failed client init.\n{}'.format(e))
	sys.exit(1)
try:
	sizing_suggestions = client.get_all_ocean_sizing(args.ocean_id,args.namespace)
except Exception as e:
	print('Failed getting suggestions.\n{}'.format(e))
	sys.exit(1)

# credit 
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%.0f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.0f%s%s" % (num, 'Yi', suffix)

def get_delta(deployment,ratio):
    x = {}

    for i in sizing_suggestions['suggestions']:
        cmd = 'kubectl set resources deployment {} --requests='.format(deployment)

        if (i['deployment_name'] == deployment):

            if (i['suggested_c_p_u'] != None and i['requested_c_p_u'] != None
                and i['suggested_c_p_u'] > 0 and i['requested_c_p_u'] > 0):
                x['cpu_delta'] = (i['suggested_c_p_u'] / i['requested_c_p_u'])

            if (i['suggested_memory'] != None and i['requested_memory'] != None
                and i['suggested_memory'] > 0 and i['requested_memory'] > 0):
                x['memory_delta'] = (i['suggested_memory'] / i['requested_memory'])

            if x['memory_delta'] >= ratio and x['cpu_delta'] >= ratio:
                x['cmd'] = '{}cpu={}m,memory={}'.format(
                    cmd,i['suggested_c_p_u'],sizeof_fmt(i['suggested_memory']))
                
            elif x['memory_delta'] >= ratio and x['cpu_delta'] < ratio:
                x['cmd'] = '{}memory={}'.format(
                    cmd,sizeof_fmt(i['suggested_memory']))
                
            elif x['memory_delta'] < ratio and x['cpu_delta'] >= ratio:
                x['cmd'] = '{}cpu={}m'.format(
                    cmd,i['suggested_c_p_u'])

        return x

print(get_delta(args.deployment,float(args.ratio))['cmd'])
