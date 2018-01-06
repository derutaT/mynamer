from configparser import SafeConfigParser
import netifaces
import boto3
import pprint
import sys

# Load Config File
config = SafeConfigParser()
config.read('config.ini')

# AWS SDK Client
client = boto3.client('route53')

# Get My Local Ip Address
my_ip_address = None

for iface_name in netifaces.interfaces():
  iface_data = netifaces.ifaddresses(iface_name)
  if_data = iface_data.get(netifaces.AF_INET)
  if if_data is None:
    continue
  ip_addr = if_data[0]['addr']
  if ip_addr.split('.')[0] == '192':
    my_ip_address = ip_addr

if my_ip_address is None:
  print("Unable to Get Local Ip Address")
  print("Exit")
  sys.exit()

print("My Local Ip Address: " + my_ip_address)

# List of Records
response = client.list_resource_record_sets(
    HostedZoneId=config.get('main', 'HostedZoneId'),
    MaxItems='10'
)

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(response['ResourceRecordSets'])

# Update Record
response = client.change_resource_record_sets(
  HostedZoneId=config.get('main', 'HostedZoneId'),
  ChangeBatch={
    'Changes': [
      {
        'Action': 'UPSERT',
        'ResourceRecordSet': {
          'Name': config.get('main', 'NameValue'),
          'Type': 'A',
          'TTL': 300,
          'ResourceRecords': [{'Value': my_ip_address}],
        }
      }
    ]
  }
)

print(response)
