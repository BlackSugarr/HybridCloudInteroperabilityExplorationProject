#!/usr/bin/python

'''
Copyright (c) 2015 Meng Li

Student number: | Student name:

This program is part of the 25 point distributed computing project.
This program is used to shutdown the instances on AWS EC2
and delete the auto scaling group and launch configure.
'''

################ begin import modules ################

import os
from time import sleep

import boto.ec2

import boto.ec2.elb
from boto.ec2.elb import ELBConnection
from boto.ec2.elb import HealthCheck

from boto.ec2.autoscale import AutoScaleConnection
from boto.ec2.autoscale import LaunchConfiguration
from boto.ec2.autoscale import AutoScalingGroup
from boto.ec2.autoscale import ScalingPolicy

import boto.ec2.cloudwatch
from boto.ec2.cloudwatch import MetricAlarm


################ end import modules ################


######################### begin parameter block ################################

# AWS keys
AWS_ACCESS_KEY = ''
AWS_SECRET_KEY = ''
regionName = ''


# autoscaling group information
autoscaling_group = {
    'name' : 'my_group',
    'minSize' : 1,
    'maxSize' : 4,
}


 ######################### end parameter block ################################


######################### begin configuration ################################
# make the connections
conn_ec2 = boto.ec2.connect_to_region(
        regionName,
        aws_access_key_id = AWS_ACCESS_KEY,
        aws_secret_access_key = AWS_SECRET_KEY
    )
conn_reg = boto.ec2.elb.connect_to_region(regionName)
conn_elb = ELBConnection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
conn_as = AutoScaleConnection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
conn_cw = boto.ec2.cloudwatch.connect_to_region(regionName)
conn_cw = boto.ec2.cloudwatch.connect_to_region(
        regionName,
        aws_access_key_id = AWS_ACCESS_KEY,
        aws_secret_access_key = AWS_SECRET_KEY
    )
######################### end configuration ################################




# balancers = elb.get_all_load_balancers()
# print balancers[0]

# retrieve the instances in the autoscale group
group = conn_as.get_all_groups(names=[autoscaling_group['name']])[0]
instanceids = [i.instance_id for i in group.instances]
instances = conn_ec2.get_only_instances(instanceids)
print instances



# # shutdown all the instances in the autogroup instances
ag = conn_as.get_all_groups()[0]
print "shutdown the instances in the autoscaling group"
ag.shutdown_instances()
sleep(20)

# # delete the autoscale group
print "delete the autoscaling group"
ag.delete()
# # delete the launch configuration
# lc.delete()


# clear the last execution results
# print 'Deleting the auto scaling group'
# conn_as.delete_auto_scaling_group('my_group')
print 'Deleting the launch configure'
conn_as.delete_launch_configuration('my_launch_config')





# if __name__ == '__main__':
#     main(sys.argv)





















