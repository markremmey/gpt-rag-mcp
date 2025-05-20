FROM python:3.11

RUN apt-get update && apt-get install -y build-essential

RUN python3 -m venv ~/pyvenv --system-site-packages
RUN . ~/pyvenv/bin/activate
#RUN pip install --upgrade pip

COPY . /

RUN pip install -r requirements.txt --break-system-packages
 
# Expose the port your app runs on
EXPOSE 8000
 
# Define the command to run your app
CMD ["gunicorn", "-b", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "server:app"]