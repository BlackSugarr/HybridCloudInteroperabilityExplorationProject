#!/usr/bin/python

'''
Copyright (c) 2015 Meng Li

Student number: | Student name: 

This program is part of the 25 point distributed computing project.
This program is used to initiate the NeCTAR account.
It defines the security groups which would be used to launch instances.
It checks the key state, and creates it if it does not exsit.

'''

################ begin import modules ################
import sys
import time
import boto
from boto.ec2.regioninfo import *
from boto.ec2.connection import EC2Connection

################ end import modules ################


def main(argv):


######################### begin parameter block ################################

    # aws_access_key_id and aws_secret_access_key are parts of the EC2 credentials
    #   the default values are my project account EC2 credentials
    # region_name is the region where the instance would be launched
    #   the default value is the melbourne-np
    # key_name is the name of the key that is used to launch images
    #   the default value is NecTAR_key which we have created

 
    # use the default parameters
    if len(sys.argv) == 1:
        aws_access_key_id = ""
        aws_secret_access_key = ""

        region_name = ""
        keyName = ""


    # customize aws keys and regions
    elif len(sys.argv) == 4:
        aws_access_key_id = sys.argv[1]
        aws_secret_access_key = sys.argv[2]
        region_name = sys.argv[3]

    # customize all parameters
    elif len(sys.argv) == 5:
        aws_access_key_id = sys.argv[1]
        aws_secret_access_key = sys.argv[2]
        region_name = sys.argv[3]
        keyName = sys.argv[4]

    else:
        print 'Input again! The number of arguments is wrong!'

########################## end parameter block ################################


######################### begin invoking block ################################

    ec2_conn = connect_ec2(aws_access_key_id, aws_secret_access_key, region_name)
    define_security_groups(ec2_conn)

    # uncomment this line to call the key create function
    # check_key(key_name)


######################### end invoking block ################################


######################### begin functions definitions ######################### 

# create a connection to NecTAR server
def connect_ec2(aws_access_key_id, aws_secret_access_key, region_name):
    region=RegionInfo(region_name, endpoint='nova.rc.nectar.org.au')
    ec2_conn = boto.connect_ec2(aws_access_key_id, aws_secret_access_key, is_secure=True, region=region, port=8773, path='/services/Cloud', validate_certs=False)
    return ec2_conn


# define the security groups used in the project
def define_security_groups(ec2_conn):
    sshAccess = ec2_conn.create_security_group('ssh', 'allow SSH connection')
    sshAccess.authorize('tcp', 22, 22, '0.0.0.0/0')

    couchDBAccess = ec2_conn.create_security_group('couchdb', 'allow remote access couchDB')
    couchDBAccess.authorize('tcp', 5984, 5984, '0.0.0.0/0')

    # httpAccess = ec2_conn.create_security_group('http', 'allow HTTP/S')
    # httpAccess.authorize('tcp', 80, 80, '0.0.0.0/0')
    # httpAccess.authorize('tcp', 443, 443, '0.0.0.0/0')

    # icmpAccess = ec2_conn.create_security_group('icmp', 'allow ICMP..ping..')
    # icmpAccess.authorize('icmp', 0, 65535, '0.0.0.0/0')

    # print the security groups that have defined
    rs = ec2_conn.get_all_security_groups()
    print rs


# check the key we want to use when launch instances
# if it does not exsit then create it
def check_key(keyName):
    try:
        key = ec2.get_all_key_pairs(keynames=[keyName])[0]
    except ec2.ResponseError, e:
        if e.code == 'InvalidKeyPair.NotFound':
            print 'Creating keypair: %s' % keyName

            # Create an SSH key to use when logging into instances.
            key = ec2.create_key_pair(keyName)
            
            # NecTAR could store the public key but the private key nedds to save locally
            # The save method would chmod the file to protect your private key.
            key.save(key_dir)
        else:
            raise


######################### end funcitons definitions ######################### 

if __name__ == '__main__':
    main(sys.argv)





















