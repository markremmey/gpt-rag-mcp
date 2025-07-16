FROM mcr.microsoft.com/devcontainers/python:dev-3.12

RUN apt-get update && apt-get install -y build-essential
RUN apt-get install unixodbc -y

RUN python3 -m venv ~/pyvenv --system-site-packages
RUN . ~/pyvenv/bin/activate
#RUN pip install --upgrade pip

COPY . /

RUN pip install -r requirements.txt 
#--break-system-packages

RUN python3 -m spacy download en_core_web_lg
 
# Expose the port your app runs on
EXPOSE 80
 
# Define the command to run your app
#CMD ["gunicorn", "-b", "0.0.0.0:80", "-k", "uvicorn.workers.UvicornWorker", "server:app"]
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]