# HybridCloudInteroperabilityExplorationProject
The programs in this folder are the source code of the 25 points distributed system project.

=================================
Before running the system, the NeCTAR and AWS account credential or authentication information should be modified to your account information in each program.

For ansible, the key location need to be modified in unusable.cfg file. 

AWS account configuration parameters can be export to ENVs or set in the configuration file called .boto.

=================================
ansible is used to deploy the Twitter Harvester

NeCTAR_monitor.py is used to monitor the whole system running status and perform actions 
according to status.

NeCTAR_initiate.py is used to initiate the NeCTAR account, including create security group, define keys.

NeCTAR_launch_instance.py is used to launch instances on NeCTAR cloud.

AWS_autoscaling.py is used to create the autoscaling group on AWS cloud.

AWS_stop_autoscailng.py is used to stop the autoscaling group on AWS cloud.

================================

only the NeCTAR_monitor.py need to be executed
the others are the help program and will be invoked by the monitor 
==================================

run command: python NeCTAR_monitor.py
