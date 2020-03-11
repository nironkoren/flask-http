import spotinst_sdk

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-d", "--deployment", dest="deployment",
                    help="deployment name")
parser.add_argument("-r", "--ratio", dest="ratio", default=2,
                    help="ratio of rs")

args = parser.parse_args()

client = spotinst_sdk.SpotinstClient(auth_token='0ee164775151ff2119ec1eef25b70e1ed009ce69fc2abcd42cb61fd2e883d953',account_id='act-311c119f')


recs = client.get_all_ocean_sizing('o-57b09a6e','default')

# credit 
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%.0f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.0f%s%s" % (num, 'Yi', suffix)

def get_delta(deployment,ratio):
    x = {}

    for i in recs['suggestions']:
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
