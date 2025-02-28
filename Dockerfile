# choose the image
FROM python:3.10

# choose work directory
WORKDIR /app

# copy dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy all files of project
COPY . .

# run migrate and runserver
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
