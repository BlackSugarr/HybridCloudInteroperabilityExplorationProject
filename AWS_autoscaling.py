#!/usr/bin/python

'''
Copyright (c) 2015 Meng Li

Student number: | Student name:

This program is part of the 25 point distributed computing project.
This program could realize autoscaling on NeCTAR.
The program includes 3 sections:
- setup a new Elastic Load Balancer
- create an Auto Scaling Group and configure it 
- create policies for the Scaling up and Scaling down

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


# launch configur information
lcName = 'my_launch_config'
as_ami = {
    'id': 'ami-69631053', #ubuntu-trusty-14.04-amd64-server-20150325
    'instanceKey': 'AWS_key',
    'securityGroups': ['mengli_SG_Sydney', 'CouchDB'],
    'instanceType': 't2.micro'
}


# elastic load balancer information
elastic_load_balancer = {
    'name': 'my-lb',
    'healthCheckTarget': 'HTTP:8080/health',
    'zones': ['ap-southeast-2b'],
    'ports': [(80, 8080, 'http'), (443, 8443, 'tcp')],
    'interval': 200,
    'healthyThreshold': 3,
    'unhealthyThreshold': 5
}


# autoscaling group information
autoscaling_group = {
    'name' : 'my_group',
    'minSize' : 1,
    'maxSize' : 4,
}


# metric alarms information
metric_alarm = {
    'upAlarmName': 'scale_up_on_cpu',
    'downAlarmName': 'scale_down_on_cpu',
    'nameSpace': 'AWS/EC2',
    'metric': 'CPUUtilization',
    'statistic': 'Average',
    'upThreshold': 15,
    'downThreshold': 10,
    'period': 60,
    'evaluationPeriods': 1
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


# ============================================== #
# configure a health check
hc = HealthCheck(
        interval=elastic_load_balancer['interval'],
        healthy_threshold=elastic_load_balancer['healthyThreshold'],
        unhealthy_threshold=elastic_load_balancer['unhealthyThreshold'],
        target=elastic_load_balancer['healthCheckTarget']
    )
# create a load balancer
lb = conn_elb.create_load_balancer(elastic_load_balancer['name'],
        elastic_load_balancer['zones'],
        elastic_load_balancer['ports'])

lb.configure_health_check(hc)
print lb.dns_name + " created!"
sleep(10)
# ============================================== #



# ============================================== #
# clear the last execution results
# conn_as.delete_auto_scaling_group('my_group')
# conn_as.delete_launch_configuration('my-launch_config')
# ============================================== #




# ============================================== #
# create launch configuration
lc = LaunchConfiguration(
        name=lcName,
        image_id=as_ami['id'],
        key_name=as_ami['instanceKey'],
        security_groups=as_ami['securityGroups'],
        instance_type=as_ami['instanceType']
    )
conn_as.create_launch_configuration(lc)
print 'launch configuration created!'
sleep(10)
# ============================================== #




# ============================================== #
# create autoscaling group
ag = AutoScalingGroup(
        group_name=autoscaling_group['name'],
        load_balancers=[elastic_load_balancer['name']],
        availability_zones=elastic_load_balancer['zones'],
        launch_config=lc,
        min_size=autoscaling_group['minSize'],
        max_size=autoscaling_group['maxSize'],
        connection=conn_as
    )
conn_as.create_auto_scaling_group(ag)
print 'auto scaling group created!'
sleep(10)
# ============================================== #


# ============================================== #
# define and create the scaling policies
scale_up_policy = ScalingPolicy(
        name='scale_up',
        adjustment_type='ChangeInCapacity',
        as_name=autoscaling_group['name'],
        scaling_adjustment=1,
        cooldown=180
    )

scale_down_policy = ScalingPolicy(
        name='scale_down',
        adjustment_type='ChangeInCapacity',
        as_name=autoscaling_group['name'],
        scaling_adjustment=-1,
        cooldown=180
    )
conn_as.create_scaling_policy(scale_up_policy)
conn_as.create_scaling_policy(scale_down_policy)
print 'scaling policies created!'
sleep(10)

# refresh and get back the scaling policies
scale_up_policy = conn_as.get_all_policies(
        as_group=autoscaling_group['name'],
        policy_names=['scale_up'])[0]

scale_down_policy = conn_as.get_all_policies(
        as_group=autoscaling_group['name'],
        policy_names=['scale_down'])[0]

# ============================================== #



# ============================================== #
# create CloudWatch alarms for when to scale up and when to scale down
alarm_dimensions = {"AutoScalingGroupName": autoscaling_group['name']}
scale_up_alarm = MetricAlarm(
        name=metric_alarm['upAlarmName'],
        namespace=metric_alarm['nameSpace'],
        metric=metric_alarm['metric'],
        statistic=metric_alarm['statistic'],
        comparison='>',
        threshold=metric_alarm['upThreshold'],
        period=metric_alarm['period'],
        evaluation_periods=metric_alarm['evaluationPeriods'],
        alarm_actions=[scale_up_policy.policy_arn],
        dimensions=alarm_dimensions
    )
conn_cw.create_alarm(scale_up_alarm)
print 'scale_up_alarm created!'
sleep(10)

scale_down_alarm = MetricAlarm(
        name=metric_alarm['downAlarmName'],
        namespace=metric_alarm['nameSpace'],
        metric=metric_alarm['metric'],
        statistic=metric_alarm['statistic'],
        comparison='<',
        threshold=metric_alarm['downThreshold'],
        period=metric_alarm['period'],
        evaluation_periods=metric_alarm['evaluationPeriods'],
        alarm_actions=[scale_down_policy.policy_arn],
        dimensions=alarm_dimensions
    )
conn_cw.create_alarm(scale_down_alarm)
print 'scale_down_alarm created!'
sleep(10)

# ============================================== #


######################### end configuration ################################



######################### begin invoking block ################################

# balancers = elb.get_all_load_balancers()
# print balancers[0]

# retrieve the instances in the autoscale group
group = conn_as.get_all_groups(names=[autoscaling_group['name']])[0]
instance_ids = [i.instance_id for i in group.instances]
instances = conn_ec2.get_only_instances(instance_ids)
print instances


######################### end invoking block ################################




# if __name__ == '__main__':
#     main(sys.argv)





















