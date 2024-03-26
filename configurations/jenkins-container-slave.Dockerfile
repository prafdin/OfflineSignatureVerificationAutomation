FROM docker.io/jenkins/inbound-agent:3148.v532a_7e715ee3-1-jdk11

USER root
COPY jenkins_agent_requirements.txt requirements.txt
RUN apt update && apt install -y python3 python3-pip
RUN pip3 install -r requirements.txt

USER jenkins
