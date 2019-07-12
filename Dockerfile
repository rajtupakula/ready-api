FROM centos:7
FROM python:2.7
FROM java:openjdk-8-jdk

#  Version
#ENV   SOAPUI_VERSION  5.4.0
ENV ls_address=104.209.209.104

COPY entry_point.sh /opt/bin/entry_point.sh
COPY server.py /opt/bin/server.py
COPY server_index.html /opt/bin/server_index.html

RUN chmod +x /opt/bin/entry_point.sh
RUN chmod +x /opt/bin/server.py

# Download and unarchive Readyapi
RUN mkdir ./opt/readyapi
RUN mkdir ./opt/readyapi/reports
COPY ./licensing/ready-api-license-manager-1.2.2.jar ./opt/readyapi/licensing/
COPY PartServiceRestApi-readyapi-project.xml ./opt/readyapi/project/run.xml

# Download 2.3.0 tarball from Smartbear + unpack
ADD http://dl.eviware.com/ready-api/2.5.0/ReadyAPI-x64-2.5.0.sh ./opt/readyapi
RUN chmod +x ./opt/readyapi/ReadyAPI-x64-2.5.0.sh
RUN ./opt/readyapi/ReadyAPI-x64-2.5.0.sh -q -dir ./ReadyAPI-2.5.0

# Clean up
RUN rm ./opt/readyapi/ReadyAPI-x64-2.5.0.sh

# Acquire license, make testrunner executable
RUN ((echo "1")) | java -jar ./opt/readyapi/licensing/ready-api-license-manager-1.2.2.jar -s ${ls_address}:1099

# Set working directory
WORKDIR /opt/bin

# Set environment
ENV PATH ${PATH}:/opt/readyapi/ReadyAPI-2.5.0/bin

EXPOSE 3000
CMD ["/opt/bin/entry_point.sh"]
