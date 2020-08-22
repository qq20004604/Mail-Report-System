FROM python:3.8.2
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple/
COPY . .
EXPOSE 49991
CMD ["python", "manage.py", "runserver", "0.0.0.0:49991"]