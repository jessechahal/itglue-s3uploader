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
    - I assume there is a VPC with a public subnet that I can deploy into
- I'm leveraging docker to build the project so the end user (or build system) does not need to actually install python or anything else (other then docker)
