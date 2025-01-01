import os
import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as wait_condition

from test_functions import create_webdriver

# http://chinomsoikwuagwu.com/
# <form style="float:right;display:inline-block;margin:0;border:0;padding:0">
#   <label>
#     <input type="text" id="search-form_search-box" class="searchInput" value="" placeholder="Type to search...">
#   </label>
#   <input type="submit" class="emphasis-button" value="Search">
# </form>

# <div id="indexSection" class="containerCenter">
#   <article>
#     <header>
#       <h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2023/11/03/limited-conversations-with-distributed-systems/">Limited conversations with distributed systems.</a></h3>
#       <small>November 03, 2023</small>
#     </header>
#     <section><div>Rate limiting distributed systems for resiliency</div></section>
#   </article>
#   <article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2022/08/10/Modifying-legacy-applications-using-domain-driven-design-DDD/">Modifying legacy applications using domain driven design (DDD)</a></h3><small>August 10, 2022</small></header><section><div>Modifying-legacy-applications-using-domain-driven-design-DDD</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2022/03/25/Gherkin-best-practices/">Gherkin Best Practices</a></h3><small>March 25, 2022</small></header><section><div>Ten best practices when using gherkin syntax</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2022/02/17/Code-review-best-practices/">Code Review Best Practices</a></h3><small>February 17, 2022</small></header><section><div>Code review best practices for authors, reviewers and teams</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2021/06/15/Hacking-cypress-in-9-minutes/">Hacking Cypress in 9 minutes</a></h3><small>June 15, 2021</small></header><section><div>Ten best practices when using gherkin syntax</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2021/02/05/Some-common-mistakes-when-developing-java-based-applications/">Some common mistakes when developing java web applications</a></h3><small>February 05, 2021</small></header><section><div>Quick guide to mitigating common mistakes when developing java web applications</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2021/02/05/How-to-make-a-Spring-Boot-application-production-ready/">How to make a Spring Boot application production ready</a></h3><small>February 05, 2021</small></header><section><div>Steps to making your Spring Boot application production ready.</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/11/19/SQL-JOINS-A-refresher/">SQL JOINS - A Refresher</a></h3><small>November 19, 2020</small></header><section><div>A summary of SQL JOIN</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/09/29/Add-elasticsearch-to-spring-boot-application/">Add Elasticsearch to Spring Boot Application</a></h3><small>September 29, 2020</small></header><section><div>Guide to quickly adding Elasticsearch to as Spring Boot application</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/09/03/Add-tables-to-existing-jhipster-based-project/">Add entities/tables to an existing Jhipster based project</a></h3><small>September 03, 2020</small></header><section><div>Guide to quickly adding entities/tables to an existing Jhipster based project</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/08/12/css3-media-queries-quick-reference/">CSS 3 Media Queries - All over again</a></h3><small>August 12, 2020</small></header><section><div>Quick Reference - CSS 3 Media Queries, Cheat sheet</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/08/06/maven-dependency-convergence-quick-reference/">Maven Dependency Convergence - quick reference</a></h3><small>August 06, 2020</small></header><section><div>Quick Reference - Maven dependency convergene, Cheat sheet</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/06/26/Amazon-Simple-Notification-Service-SNS/">Amazon SNS Quick Reference</a></h3><small>June 26, 2020</small></header><section><div>Quick Reference - Amazon Simple Notification Service (SNS) Cheat sheet</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/06/24/Amazon-Elastic-Container-Service-ECS/">AWS API Gateway Quick Reference</a></h3><small>June 24, 2020</small></header><section><div>Quick Reference - Amazon Elastic Container Service ECS Cheat sheet</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/06/25/Amazon-Simple-Queue-Service-SQS/">Amazon SQS Quick Reference</a></h3><small>June 24, 2020</small></header><section><div>Quick Reference - Amazon Simple Queue Service (SQS) Cheat sheet</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/06/19/Amazon-API-Gateway/">AWS API Gateway Quick Reference</a></h3><small>June 19, 2020</small></header><section><div>Quick Reference, Cheat sheet - AWS API Gateway</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/06/18/AWS-Lambda/">AWS Lambda Quick Reference</a></h3><small>June 18, 2020</small></header><section><div>Quick Reference, Cheat sheet - AWS Lambda</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/06/13/Amazon-DynamoDB/">Amazon DynamoDB - Quick Reference</a></h3><small>June 13, 2020</small></header><section><div>Quick Reference, Cheat sheet - Amazon DynamoDB</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/06/12/Amazon-Aurora/">Amazon Aurora</a></h3><small>June 12, 2020</small></header><section><div>Amazon Aurora</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/06/12/Amazon-Relational-Database-Service/">Amazon Relational Database Service</a></h3><small>June 12, 2020</small></header><section><div>Amazon Relational Database Service</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/06/11/AWS-Database-Services/">AWS Database Services</a></h3><small>June 11, 2020</small></header><section><div>AWS Database Services</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/06/09/AWS-Security-Essentials/">AWS Security Essentials</a></h3><small>June 09, 2020</small></header><section><div>AWS Security Essentials</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/06/08/Amazon-Virtual-Private-Cloud-Connectivity-Options/">Amazon Virtual Private Cloud Connectivity Options</a></h3><small>June 08, 2020</small></header><section><div>Amazon Virtual Private Cloud Connectivity Options</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/05/29/AWS-Services-List/">Summary of AWS Services</a></h3><small>May 29, 2020</small></header><section><div>Summary of each AWS Service to help you get acquainted</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/05/20/AWS-Certified-Solutions-Architect-Quick-Reference/">AWS Certified Solutions Architect - Quick Reference</a></h3><small>May 20, 2020</small></header><section><div>Quick Reference, Cheat sheet - AWS Certified Solutions Architect Certification</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/05/06/AWS-CloudFront-FAQs_curated/">AWS CloudFront FAQs - Curated</a></h3><small>May 06, 2020</small></header><section><div>Curated FAQs on AWS CloudFront + A must read summary for quick start</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/05/04/AWS-VPC-FAQs_curated/">AWS VPC FAQs - Curated</a></h3><small>May 04, 2020</small></header><section><div>Curated FAQs on AWS VPC, plus a must read summary for quick start</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/05/02/AWS-EC2-FAQs_curated/">AWS EC2 FAQs - Curated</a></h3><small>May 02, 2020</small></header><section><div>Curated FAQs on AWS EC2, plus a must read summary for quick start</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/04/30/AWS-Achritect-5_Architecting-for_Cost-Optimization/">AWS Achritect 5 - Architecting for Cost Optimization</a></h3><small>April 30, 2020</small></header><section><div>Game changing tutorial on AWS - Architecting for Cost Optimization</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/04/19/AWS-Achritect-4_Architecting-for_Performance-Efficiency/">AWS Achritect 4 - Architecting for Performance Efficiency</a></h3><small>April 19, 2020</small></header><section><div>Game changing tutorial on AWS - Architecting for Performance Efficiency</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/04/14/AWS-Architect-6_Passing-the-Certification-Exam/">AWS Achritect - 6 - Passing the Certification Exam</a></h3><small>April 14, 2020</small></header><section><div>A guide to help you pass the AWS Certified Solutions Architect Associate exam</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/04/14/AWS-Achritect-3_Architecting-for_Operational-Excellence/">AWS Achitect 3 - Architecting for Operational Excellence</a></h3><small>April 14, 2020</small></header><section><div>Game changing tutorial on AWS - Architecting for Operational Excellence</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/04/14/AWS-Architect-2_Architecting-for-Security/">AWS Achitect 2 - Architecting for Security</a></h3><small>April 14, 2020</small></header><section><div>Game changing tutorial on AWS - Architecting for Security</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/04/14/AWS-Architect-1_Architecting-for-Reliability/">AWS Achitect 1 - Architecting for Reliability</a></h3><small>April 14, 2020</small></header><section><div>Game changing tutorial on AWS - Architecting for Reliability</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/04/04/Amazon-DynamoDB-Accelerator-DAX/">Amazon DynamoDB Accelerator (DAX)</a></h3><small>April 04, 2020</small></header><section><div>Curated information on Amazon DynamoDB Accelerator (DAX)</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/04/03/Answers_AWS-Certified-Cloud-Architect-Associate/">Questions and Answers - AWS Certified Cloud Architect Associate</a></h3><small>April 03, 2020</small></header><section><div>Questions and Answers - AWS Certified Cloud Architect Associate</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/04/03/Questions_AWS-Certified-Cloud-Architect-Associate/">Questions and Answers - AWS Certified Cloud Architect Associate</a></h3><small>April 03, 2020</small></header><section><div>Questions and Answers - AWS Certified Cloud Architect Associate</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/04/02/AWS-Connectivity_PrivateLink_VPC-Peering_Transit-gateway_and_Direct-connect/">AWS Connectivity - PrivateLink, VPC-Peering, Transit-gateway and Direct-connect</a></h3><small>April 02, 2020</small></header><section><div>Simplified - AWS PrivateLink, VPC Peering, Transit Gateway, Direct connect</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/04/02/AWS_VPC-peering_vs_PrivateLink/">AWS - VPC peering vs PrivateLink</a></h3><small>April 02, 2020</small></header><section><div>Easily understand - AWS VPC peering vs PrivateLink</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/04/01/Designing-Low-Latency-Systems/">Designing Low Latency Systems</a></h3><small>April 01, 2020</small></header><section><div>Quickly get started designing low latency systems</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/28/AWS_EFS-vs-FSx/">AWS EFS vs FSx</a></h3><small>March 28, 2020</small></header><section><div>Differences between Amazon EFS vs FSx + when and why to use</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/17/AWS_Regions-Availability-Zones-and-Local-Zones/">AWS Regions, Availability Zones and Local Zones</a></h3><small>March 17, 2020</small></header><section><div>Easy to understand article on AWS Regions, Availability Zones and Local Zones</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/16/AWS_VPC-endpoints-and-VPC-endpoint-services/">AWS VPC Endpoints and VPC Endpoint Services (AWS Private Link)</a></h3><small>March 16, 2020</small></header><section><div>Easy to understand info on AWS: VPC Endpoints and Endpoint services (AWS Private Link)</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/15/AWS_IP-Addresses/">AWS - IP Addresses</a></h3><small>March 15, 2020</small></header><section><div>IP Addresses - Must Read, for AWS Certified Cloud Architect certifications</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/13/AWS_elastic-network-interfaces/">AWS Elastic Network Interfaces</a></h3><small>March 13, 2020</small></header><section><div>Easy to understand tutorial: AWS elastic network interfaces</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/13/AWS-titbits/">AWS Titbits</a></h3><small>March 13, 2020</small></header><section><div>Game changing tips, for AWS Certified Cloud Architect certification</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/10/Jenkins-on-AWS_Automation/">Jenkins on AWS - Automation</a></h3><small>March 10, 2020</small></header><section><div>Easy to understand tutorial: Jenkins on AWS Automation</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/10/Jenkins-on-AWS_Setup/">Jenkins on AWS - Setup</a></h3><small>March 10, 2020</small></header><section><div>Easy to understand tutorial: Jenkins on AWS Setup</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/10/Jenkins-on-AWS_Best-practices/">Jenkins on AWS - Best practices</a></h3><small>March 10, 2020</small></header><section><div>Easy to understand tutorial: Jenkins on AWS Best practices</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/09/CIDR-Blocks/">Introduction to CIDR Blocks</a></h3><small>March 09, 2020</small></header><section><div>Brief Introduction to CIDR Blocks</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/09/AWS-lamda-limitations-and-use-cases/">AWS Lamda - Limitations and Use Cases</a></h3><small>March 09, 2020</small></header><section><div>Easy to understand tutorial: AWS lamda limitations and use cases</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/09/AWS_Certified-Solutions-Architect-Associate_Part-10_Services_and_design_scenarios/">AWS Certified Solutions Architect Associate - Part 10 - Services and design scenarios</a></h3><small>March 09, 2020</small></header><section><div>Easy to understand tutorial: AWS Certified Solutions Architect Associate - Part 10 - Services and design scenarios</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/09/AWS_Certified-Solutions-Architect-Associate_Part-9_Databases/">AWS Certified Solutions Architect Associate - Part 9 - Databases</a></h3><small>March 09, 2020</small></header><section><div>Easy to understand tutorial: AWS Certified Solutions Architect Associate - Part 9 - Databases</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/09/AWS_Certified-Solutions-Architect-Associate_Part-8_Application-deployment/">AWS Certified Solutions Architect Associate - Part - 8 Application deployment</a></h3><small>March 09, 2020</small></header><section><div>Easy to understand tutorial: AWS Certified Solutions Architect Associate - Part 8 - Application deployment</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/09/AWS_Certified-Solutions-Architect-Associate_Part-7_Autoscaling-and-virtual-network-services/">AWS Certified Solutions Architect Associate - Part 7 - Autoscaling and virtual network services</a></h3><small>March 09, 2020</small></header><section><div>Easy to understand tutorial: AWS Certified Solutions Architect Associate - Part 7 - Autoscaling and virtual network services</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/09/AWS_Certified-Solutions-Architect-Associate_Part-6_Identity-and-access-management/">AWS Certified Solutions Architect Associate - Part 6 - Identity and access management</a></h3><small>March 09, 2020</small></header><section><div>Easy to understand tutorial: AWS Certified Solutions Architect Associate - Part 6 - Identity and access management</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/09/AWS_Certified-Solutions-Architect-Associate_Part-5_Compute-services-design/">AWS Certified Solutions Architect Associate - Part 5 - Compute services design</a></h3><small>March 09, 2020</small></header><section><div>Easy to understand tutorial: AWS Certified Solutions Architect Associate - Part 5 - Compute services design</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/09/AWS_Certified-Solutions-Architect-Associate_Part-4_Virtual-Private-Cloud/">AWS Certified Solutions Architect Associate - Part 4 - Virtual Private Cloud</a></h3><small>March 09, 2020</small></header><section><div>Easy to understand tutorial: AWS Certified Solutions Architect Associate - Part 4 - Virtual Private Cloud</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/09/AWS_Certified-Solutions-Architect-Associate_Part-3_Storage-services/">AWS Certified Solutions Architect Associate - Part 3 - Storage services</a></h3><small>March 09, 2020</small></header><section><div>Easy to understand tutorial: AWS Certified Solutions Architect Associate - Part 3 - Storage services</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/09/AWS_Certified-Solutions-Architect-Associate_Part-2_Introduction-to-Security/">AWS Certified Solutions Architect Associate - Part 2 - Introduction to Security</a></h3><small>March 09, 2020</small></header><section><div>Easy to understand tutorial: AWS Certified Solutions Architect Associate - Part 2 - Introduction to Security</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/09/AWS_Certified-Solutions-Architect-Associate_Part-1_Key-services-relating-to-the-Exam/">AWS Certified Solutions Architect Associate - Part 1 - Key services relating to the Exam</a></h3><small>March 09, 2020</small></header><section><div>Easy to understand tutorial: AWS Certified Solutions Architect Associate - Part 1 - Key services relating to the Exam</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/09/AWS-Certifications_Part-1_Certified-solutions-architect-associate/">AWS Certifications - Part 1 - Certified solutions architect associate</a></h3><small>March 09, 2020</small></header><section><div>Easy to understand tutorial: AWS Certifications - Part 1 - Certified solutions architect associate</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/04/AWS_Virtual-Private-Cloud-VPC-examples/">AWS Virtual Private Cloud (VPC) Examples</a></h3><small>March 04, 2020</small></header><section><div>Explains, with diagrams, scenarios for Virtual Private Clouds (VPC)</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/04/AWS_Virtual-Private-Cloud-VPC/">Curated info on AWS Virtual Private Cloud (VPC)</a></h3><small>March 04, 2020</small></header><section><div>Curated info on AWS Virtual Private Cloud (VPC)</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/02/Notes-on-Amazon-Web-Services_8_Command-line-interface/">Notes on Amazon Web Services 8 - Command Line Interface (CLI)</a></h3><small>March 02, 2020</small></header><section><div>Easy to understand tutorial: Notes on Amazon Web Services 8 - Command line interface</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/02/Notes-on-Amazon-Web-Services_7_Elastic-beanstalk/">Notes on Amazon Web Services 7 - Elastic Beanstalk</a></h3><small>March 02, 2020</small></header><section><div>Easy to understand tutorial: Notes on Amazon Web Services 7 - Elastic beanstalk</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/02/Notes-on-Amazon-Web-Services_6_Developer-media-migration-productivity-iot-and-gaming/">Notes on Amazon Web Services 6 - Developer, Media, Migration, Productivity, IoT and Gaming</a></h3><small>March 02, 2020</small></header><section><div>Easy to understand tutorial: Notes on Amazon Web Services 6 - Developer, media, migration, productivity, IoT and gaming</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/02/Notes-on-Amazon-Web-Services_5_Security-identity-and-compliance/">Notes on Amazon Web Services 5 - Security, Identity and Compliance</a></h3><small>March 02, 2020</small></header><section><div>Easy to understand tutorial: Notes on Amazon Web Services 5 - Security identity and compliance</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/02/Notes-on-Amazon-Web-Services_4_Analytics-and-machine-learning/">Notes on Amazon Web Services 4 - Analytics and Machine Learning</a></h3><small>March 02, 2020</small></header><section><div>Easy to understand tutorial: Notes on Amazon Web Services 4 - Analytics and machine learning</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/02/Notes-on-Amazon-Web-Services_3_Managment-tools-app-integration-and-customer-engagement/">Notes on Amazon Web Services 3 - Managment Tools, App Integration and Customer Engagement</a></h3><small>March 02, 2020</small></header><section><div>Easy to understand tutorial: Notes on Amazon Web Services 3 - Managment tools app integration and customer engagement</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/02/Notes-on-Amazon-Web-Services_2_Storages-databases-compute-and-content-delivery/">Notes on Amazon Web Services 2 - Storages databases compute and content delivery</a></h3><small>March 02, 2020</small></header><section><div>Easy to understand tutorial: Notes on Amazon Web Services 2 - Storages databases compute and content delivery</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/03/02/Notes-on-Amazon-Web-Services_1_Introduction/">Notes on Amazon Web Services 1 - Introduction</a></h3><small>March 02, 2020</small></header><section><div>Easy to understand tutorial: Notes on Amazon Web Services 1 - Introduction</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/02/27/AWS-auto-scaling_all-you-need-to-know/">AWS Auto Scaling - All you need to know</a></h3><small>February 27, 2020</small></header><section><div>AWS Auto Scaling - everything you need to know</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/02/14/AWS-Load-Balancers_How-they-work-and-differences-between-them/">AWS Load Balancers - How they work and differences between them</a></h3><small>February 14, 2020</small></header><section><div>AWS Load Balancers - everything you need to know about them</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/02/07/AWS_EC2-Instance-Types_curated/">AWS EC2 Instance Types - Curated</a></h3><small>February 07, 2020</small></header><section><div>Virtually the best, up-to-date summary of AWS EC2 instance types</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/02/05/AWS_Identity-and-Access-Management-Primer/">Amazon Web Services - Identity and Access Management Primer</a></h3><small>February 05, 2020</small></header><section><div>Primer on AWS Identity and Access Management (IAM)</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2020/02/02/Amazon-Web-Services-Create-IAM-User/">Amazon Web Services - Create IAM User</a></h3><small>February 02, 2020</small></header><section><div>Easy to understand tutorial: Amazon Web Services - Create IAM User</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2019/11/23/Preparing-Jenkins-after-installation/">Preparing Jenkins after Installation</a></h3><small>November 23, 2019</small></header><section><div>Easy to understand tutorial: Preparing Jenkins after installation</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2019/11/22/Jenkins-titbits/">Jenkins titbits, and then some</a></h3><small>November 22, 2019</small></header><section><div>Easy to understand tutorial: Jenkins titbits, and then some</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2019/11/13/Docker-titbits/">Docker Titbits</a></h3><small>November 13, 2019</small></header><section><div>Curated information on Docker</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2019/11/12/Add-chat-functionality-to-a-maven-java-web-app/">How to Add Chat Functionality to a Maven Java Web App</a></h3><small>November 12, 2019</small></header><section><div>Easy to understand tutorial: How to add chat functionality to a maven java web app</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2019/10/02/Packer-an-introduction/">Packer - an introduction</a></h3><small>October 02, 2019</small></header><section><div>Quickly get started with Hashicorp's Packer</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2019/10/02/Terraform-an-introduction/">Terraform - an introduction</a></h3><small>October 02, 2019</small></header><section><div>Quickly get started with Hashicorp's Terraform</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2019/08/05/Versioning-REST-Resources-with-Spring-Data-REST/">Versioning REST Resources with Spring Data REST</a></h3><small>August 05, 2019</small></header><section><div>Versioning REST Resources with Spring Data REST</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2018/02/14/Installing-and-running-Jenkins-in-Docker/">Installing and running Jenkins in Docker</a></h3><small>February 14, 2019</small></header><section><div>Easy to understand tutorial: Installing and running Jenkins in Docker</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2018/12/14/Automate-deployment-of-Jenkins-to-AWS_Part-2_Full-automation_Single-EC2-instance/">Automate deployment of Jenkins to AWS - Part 2 - Full automation - Single EC2 instance</a></h3><small>December 14, 2018</small></header><section><div>Automate deployment of Jenkins to AWS - From semi automation of single to full automation of cluster - Part 2</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2018/12/14/Automate-deployment-of-Jenkins-to-AWS_Part-1_Semi-automation_Single-EC2-instance/">Automate deployment of Jenkins to AWS - Part 1 - Semi automation - Single EC2 instance</a></h3><small>December 14, 2018</small></header><section><div>Automate deployment of Jenkins to AWS - From semi automation of single to full automation of cluster - Part 1</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2018/02/05/Introduction-to-Jenkins/">Introduction to Jenkins</a></h3><small>February 05, 2018</small></header><section><div>Easy to understand tutorial: Introduction to Jenkins</div></section></article><article><header><h3 style="margin-bottom:0.4375rem"><a style="box-shadow:none" href="/2018/01/24/Software-Engineers-Reference_Dictionary-Encyclopedia-or-Wiki-for-Software-Engineers/">Software Engineers Reference - Dictionary, Encyclopedia or Wiki - For Software Engineers</a></h3><small>January 24, 2018</small></header><section><div>Curated must-know information for Software Engineers</div></section></article></div>

timeout: float = 10


class XPathTest(unittest.TestCase):
    def test_xpath_from_existing_result(self):
        dir_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        file_path = os.path.join(
            dir_path, "resources", "output", "results", "pictory", "2024", "06", "06",
            "2024-06-06T18-42-06-pictory.download-video.ERROR@STAGE_FAIL-webpage.html")
        # 2024-06-06T20-06-02-pictory.download-video.SUCCESS@STAGE_END-webpage.html
        webdriver = create_webdriver()
        url: str = f"file://{file_path}"
        webdriver.get(url)

        elements = WebDriverWait(webdriver, timeout).until(
            wait_condition.presence_of_all_elements_located(
                (By.XPATH, '/html/body//div[@role="dialog" '
                           'and descendant::*[contains(text(), "Your video is now ready")]]'
                           '//*[contains(text(), "Download")]')))
        self.assertEqual(1, len(elements))
        self.assertIsNotNone(elements[0])
        print(f"Found element outerHTML:\n{elements[0].get_attribute('outerHTML')}")

    # def test_pictory_login_xpath(self):
    #     webdriver = create_webdriver()
    #     webdriver.get('https://app.pictory.ai/login')
    #     username_input = WebDriverWait(webdriver, timeout).until(
    #         wait_condition.presence_of_element_located(
    #             (By.XPATH, "//*[@id=\"mui-1\"]")))
    #     print("Found username_input id: ", username_input.get_attribute("id"))
    #     password_input = WebDriverWait(webdriver, timeout).until(
    #         wait_condition.presence_of_element_located(
    #             (By.XPATH, "//*[@id=\"outlined-adornment-password\"]")))
    #     print("Found password_input id: ", password_input.get_attribute("id"))

    # def test_pictory_textinput_xpath(self):
    #     webdriver = create_webdriver()
    #     webdriver.get('https://app.pictory.ai/textinput')
    #     button = WebDriverWait(webdriver, timeout).until(
    #         wait_condition.presence_of_element_located(
    #             (By.XPATH,
    #              "//*[@id=\"root\"]/div[1]/div[4]/div[1]/div[3]/div[1]/div[1]/div[3]/button")))
    #     print("Found button: ", False if button is None else True)

    def test_chinomsoikwuagwu_xpath(self):
        webdriver = create_webdriver()
        webdriver.get('http://chinomsoikwuagwu.com/')

        # See expected html dom structure above

        found = WebDriverWait(webdriver, timeout).until(
            wait_condition.presence_of_element_located(
                (By.XPATH, "//a[contains(text(), 'Modifying')]")))
        #print(f"\n\nFound: {found.tag_name} with content:\n{found.text}")
        self.assertIsNotNone(found)

        found = WebDriverWait(webdriver, timeout).until(
            wait_condition.presence_of_element_located(
                (By.XPATH, "//*[@id=\"indexSection\" and .//*[contains(text(), 'Modifying')]]//..")))
        #print(f"\n\nFound: {found.tag_name} with content:\n{found.text}")
        self.assertIsNotNone(found)

    # def test_chinomsoikwuagwu_xpath(self):
    #     webdriver = create_webdriver()
    #     webdriver.get('http://chinomsoikwuagwu.com/')
    #
    #     # See expected html dom structure above
    #
    #     search_box = WebDriverWait(webdriver, timeout).until(
    #         wait_condition.presence_of_element_located(
    #             (By.XPATH, "//*[@id=\"search-form_search-box\"]")))
    #     print("Found search_box id: ", search_box.get_attribute("id"))
    #
    #     parent = WebDriverWait(search_box, timeout).until(
    #         wait_condition.presence_of_element_located(
    #             (By.XPATH, ".//..//..")))
    #     print("Found parent: ", parent.tag_name)
    #     self.assertEqual(parent.tag_name, "form")
    #
    #     parent = WebDriverWait(search_box, timeout).until(
    #         wait_condition.presence_of_element_located(
    #             (By.XPATH, "./parent::*/parent::*")))
    #     print("Found parent: ", parent.tag_name)
    #     self.assertEqual(parent.tag_name, "form")


if __name__ == '__main__':
    unittest.main()
