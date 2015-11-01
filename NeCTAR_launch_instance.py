#!/usr/bin/python

'''
Copyright (c) 2015 Meng Li

Student number: | Student name:

This program is part of the 25 point distributed computing project.
This program is used to launch instances and export their ip address.
It also could create valume and attach them to instances.

'''

################ begin import modules ################
import sys
import time
import boto
from boto.ec2.regioninfo import *
from boto.ec2.connection import EC2Connection
import commands

################ end import modules ################


def main(argv):


######################### begin parameter block ################################

    # aws_access_key_id and aws_secret_access_key are parts of the EC2 credentials
    #   the default values are my project account EC2 credentials
    # region_name is the region where the instance would be launched
    #   the default value is the melbourne-np
    # key_name is the name of the key that is used to launch images
    #   the default value is NecTAR_key which we have created
    # ami_id is the name of the name of image 
    #   the default value is ami-000022b3 that is Ubuntu 14.04.2
    # instance_type is the type of the instance
    #   the default value is m1.medium
    # security_groups is list of the security groups used
    #   the default value is ['couchdb', 'ssh', 'http']
    # num_instance is the number of the instance you want to launch
    #   the default value is 1
    # volume_size is the size of the new volume
    #   since the big storage is not required for this project, there is no valume created

 
    # use the default parameters
    if len(sys.argv) == 1:
        aws_access_key_id = ""
        aws_secret_access_key = ""

        region_name = ""
        keyName = ""
        ami_id = "ami-000022b3" #name: NeCTAR Ubuntu 14.04 (Trusty) amd64
#        ami_id = "ami-00003206"  #name: Ubuntu 14.04.2
        instanceType = "m1.medium"
        securityGroups = ['couchdb', 'ssh', 'http']
        # volume_size = 60
        num_instance = 1
    
    # customize aws keys and regions
    elif len(sys.argv) == 4:
        aws_access_key_id = sys.argv[1]
        aws_secret_access_key = sys.argv[2]
        region_name = sys.argv[3]

    # customize all parameters
    elif len(sys.argv) == 10:
        aws_access_key_id = sys.argv[1]
        aws_secret_access_key = sys.argv[2]
        region_name = sys.argv[3]
        keyName = sys.argv[4]
        ami_id = sys.argv[5]
        instanceType = sys.argv[6]
        securityGroups = sys.argv[7]
        num_instance = sys.argv[8]
        volume_size = sys.argv[9]

    else:
        print 'Input again! The number of arguments is wrong!'

 ######################### end parameter block ################################


######################### begin invoking block ################################

    ec2_conn = connect_ec2(aws_access_key_id, aws_secret_access_key, region_name)

    # launch several instances
    instances = []
    i = 0
    while (i < num_instance):
        instance = launch_instance(ec2_conn, ami_id, keyName, instanceType, securityGroups)
        instances.append(instance)
        i+=1

    reservations = ec2_conn.get_all_reservations()

#    export_ip_address(reservations)

#    run_Ansible_Playbook()

    # if the valume is requied, then uncomment this line
    # create_attach_volume(ec2_conn, instances, volume_size)

######################### end invoking block ################################


######################### begin functions definitions ######################### 

# create a connection to NecTAR server
def connect_ec2(aws_access_key_id, aws_secret_access_key, region_name):
    region=RegionInfo(region_name, endpoint='nova.rc.nectar.org.au')
    ec2_conn = boto.connect_ec2(aws_access_key_id, aws_secret_access_key, is_secure=True, region=region, port=8773, path='/services/Cloud', validate_certs=False)
    return ec2_conn


# launch instance
def launch_instance(ec2_conn, ami_id, keyName, instanceType, securityGroups):
    reservation = ec2_conn.run_instances(ami_id, key_name=keyName, instance_type=instanceType, security_groups=securityGroups)
    # get the instance object inside the reservation object
    instance = reservation.instances[0]

    # the instance has been launched but it's not yet up and running  
    print 'waiting for instance'
    while instance.state != 'running':
        print '=='
        time.sleep(5)
        instance.update()
    print 'done'

    return instance



# export all of the ip address to a file 
# this file could be used by other software
def export_ip_address(reservations):
    print 'Exporting the ip address to Ansible hosts file.'
    ip_list = []
    for res in reservations:
        ip_list.append(res.instances[0].ip_address)
    f = open('/etc/ansible/hosts', 'a')
    f.write('[twitterservers]\n')
    for ip in ip_list:
        ip_str = str(ip)
        f.write(ip_str + '\n')
    f.close()

def run_Ansible_Playbook():
    print 'Configuring the instances now.'
    (status, output) = commands.getstatusoutput('ansible-playbook ./ansible/playbooks/boss_playbook.yml')
    print output



# create and attach volume
def create_attach_volume(ec2_conn, instances, volume_size):
    for instance in instances:

        # the volume zone should be same as the instance region
        vzone = instance.placement

        # create volume
        volume = ec2_conn.create_volume(volume_size, vzone)

        # Wait for the volume to be created.
        while volume.status != 'available':
            print '=='
            time.sleep(5)
            volume.update()

        # attach the volume to the instance
        volume.attach(instance.id, '/dev/vdc')

######################### end funcitons definitions ######################### 

if __name__ == '__main__':
    main(sys.argv)





















