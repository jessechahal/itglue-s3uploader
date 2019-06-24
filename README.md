IT Glue Interview Project
===


Project
---
Create a web application with a single endpoint, /upload. When someone sends a POST request to
/upload with a file included in the request body the application should upload the file to S3 and return
to the caller a URL where the file can be publicly accessed.
Deploy this application on AWS. You can assume that there is an existing VPC with a public subnet.
You may use IAM, EC2, ECS, CloudFormation, S3, and VPC but no other AWS services. Include
instructions for how to deploy the application. It should be possible to update the code for the
application without disrupting its use. We should be able to deploy the application from scratch to our
AWS account without too many manual steps.


Implementation Notes
---
- I've implemented a simple Python flask app that uses boto3 library to talk to aws.
- Cloudformation will be used to deploy the app
    - I assume there is a VPC with 2 public subnet that I can deploy into
        - for testing purposes I used a cloudformation template called _vpc.yaml
    - cloudformation template is called cloudformation/s3uploader.yaml
        - it pulls docker image from docker.io that I pushed earlier. I didn't use ECR but normally i would have
- I'm leveraging docker to build the project so the end user (or build system) does not need to actually install python or anything else (other then docker)
- I am using AWS ECS + EC2 to launch and host the service
- SSH access is configured by default for 0.0.0.0 access. This is terrible practice and it should be configured to local office_ip
    - this is documented in cloudformation template
    - I had to do this as i didn't know IT Glues office IP address
    - I didn't use a bastion host since that is only needed for private EC2 instances
        - You can use ACL's + security groups to get the same level of security as bastion host for SSH into public EC2 VMs
- EC2 instances are configured to run in multi-az. This is assuming that the 2 provided public subnets are in 2 different AZ's

Running locally
---
```docker-compose build && docker-compose up -d```
The command will build a local docker image and run it locally on port 5000

Calling api
---
- by default the app runs on port 5000 locally. If running on aws it is port 80. Use the ALB DNS entry to send requests
    - ALB DNS entry can be found as an output to the cloudformation stack
- Make a post call. Submit form-data with the key of 'file' and the value being file data
    - i used postman to simulate this call. It worked well


Ways to update running service
---
- update cloudformation template parameters and set the docker image to be a different version (or other parts of the template/parameters)
- kill a running ECS task and it will automatically be relaunched/autoheal
- kill any or all running EC2 services and everything will autoheal
