FROM python:3.12-slim

ARG TERRAFORM_VERSION=1.9.8

WORKDIR /app

COPY requirements.txt .
RUN apt-get update \
	&& apt-get install -y --no-install-recommends curl unzip \
	&& curl -fsSLo /tmp/terraform.zip "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" \
	&& unzip /tmp/terraform.zip -d /usr/local/bin \
	&& rm -f /tmp/terraform.zip \
	&& apt-get purge -y --auto-remove curl unzip \
	&& rm -rf /var/lib/apt/lists/* \
	&& pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
