FROM ubuntu:latest
RUN apt update
RUN apt -y install apt-utils wget software-properties-common && \
    wget -O - https://dl.openfoam.org/gpg.key > /etc/apt/trusted.gpg.d/openfoam.asc && \
	add-apt-repository http://dl.openfoam.org/ubuntu
RUN	apt update
RUN	apt -y install openfoam12 && echo " " >> ~/.bashrc && echo ". /opt/openfoam12/etc/bashrc" >> ~/.bashrc
RUN apt -y install python3-full python3-pip
RUN mkdir /foam && python3 -m venv /foam && /foam/bin/pip3 install flask
WORKDIR /foam