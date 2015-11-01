#!/usr/bin/python
# -*- coding: utf-8 -*-


'''
Copyright (c) 2015 Meng Li

Student number: | Student name:

This program is part of the 25 point distributed computing project.
This program is used to monitor the instances status of the system.
'''

################ begin import modules ################

from novaclient import client as nv_client
from keystoneclient.v2_0.client import Client as ks_client
# from ceilometerclient.v2 import Client as ceil_client
# import ceilomoterclient.client as ceil_client
from ceilometerclient import client as ceil_client
import os, sys, json
import commands,time
import re,datetime

################# end import modules ################

# get the ENV variables imported by OpenstackRC.sh
# credentials is a dictionary used save these tokens
def getNeCTARCredentialsFromOS_Env():
    credentials = {}
    try:
        credentials['USERNAME'] = os.environ['OS_USERNAME']
        credentials['PASSWORD'] = os.environ['OS_PASSWORD']
        credentials['TENANT_NAME'] = os.environ['OS_TENANT_NAME']
        credentials['AUTH_URL'] = os.environ['OS_AUTH_URL']
    except KeyError as e:
        print "Got an error!"
        print e.message, e.args
        sys.exit(-1)

    return credentials


def get_token(credentials):
    keystone = ks_client(username=credentials['USERNAME'],
            password=credentials['PASSWORD'],
            tenant_name=credentials['TENANT_NAME'],
            auth_url= credentials['AUTH_URL']
        )
    token = keystone.service_catalog.catalog['token']['id']
    return token



def main(args):
    ec2_isWorking = 0
    credentials = getNeCTARCredentialsFromOS_Env()
    print credentials
    tokenFromKeystone = get_token(credentials)
    # print tokenFromKeystone
    nt = nv_client.Client(2, credentials['USERNAME'], credentials['PASSWORD'], credentials['TENANT_NAME'], credentials['AUTH_URL'])
    cclient = ceil_client.get_client(2, os_username=credentials['USERNAME'], os_password=credentials['PASSWORD'], os_tenant_name=credentials['TENANT_NAME'], os_auth_url=credentials['AUTH_URL'])
    print(nt.servers.list())
    while True:
        sum = 0
        count = 0
        server_in_group = []
        for server in nt.servers.list():
            if len(server.networks.values())==0:
                continue
            ip=server.networks.values()[0][0]
            if ip:
                server_in_group.append(server)
                query = [dict(field='resource_id', op='eq', value=server.id)]
#                print query
#                print cclient.samples.list()
#                print cclient.statistics.list("cpu_util", q=query)
                if len(cclient.statistics.list(meter_name='cpu_util', period=60, q=query))==0:
                    cpu_stat=0
                else:
                    cpu_stat=cclient.statistics.list(meter_name='cpu_util', period=60,q=query)[-1]._info['avg']
                
                sum += float(cpu_stat)
                count += 1
                
#                print ip
#                print server.id
#                print "sum: ", sum
#                print "count: ", count

        avg=sum/count
        print "Monitoring, current cpu usage is: ", avg, count

        if avg < 30:
            if count == 1:
                print "NeCTAR Instances are healthy!"
            elif (ec2_isWorking == 0) and count > 1: #condition for scaling down within NeCTAR
                print "Triggered the scaling down alarm! Stop an instance on NeCTAR!"
                id = server_in_group[-1].id
                try:
                    server_in_group[-1].stop()
                except:
                    server_in_group[-1].delete()
                print "Instance ", id, " is stopped!"
            elif ec2_isWorking == 1: #codition for stop AWS EC2
                print "Do not need AWS EC2, stop it!"
                (status, output) = commands.getstatusoutput('sudo python ./AWS_stop_autoscaling.py')
                print output
                time.sleep(120) #wait for complete stop operation

        elif avg > 70:
            if count == 4: #condition for burst into AWS cloud
                print "Resource on NeCTAR exhausted!!"
                print "Burst into AWS cloud!"
                print "Creating the AWS AutoScalingGroup!"
                (status, output) = commands.getstatusoutput('sudo python ./AWS_autoscaling.py')
                print output
                ec2_isWorking = 1
                time.sleep(120) #wait for comlete create the autoscaling group

            elif count < 4: #condition for scaling up within NeCTAR
                print "Triggered the scaling up alarm! Launch a new instance on NeCTAR"
                (status, output) = commands.getstatusoutput('sudo python /Users/limeng/Desktop/25ptsProject/script/BotoCode/NeCTARscript/NeCTAR_launch_instance.py')
                print output
                time.sleep(120) #wait for complete launch a new instance

        else:
            print "NeCTAR instances are healthy!" 

        time.sleep(120) #wait 120 seconds and begin next turn check


if __name__ == "__main__":
    main(sys.argv)

