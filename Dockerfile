FROM python:3.10-slim


# 임시폴더 삭제
RUN rm -rf /tmp/.com.google.Chrome*
RUN rm -rf /tmp/.org.chromium.Chromium*

# 시스템 패키지 및 크롬/크롬드라이버 설치


WORKDIR /usr/src
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
    unzip \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

RUN dpkg -i google-chrome-stable_current_amd64.deb || apt-get -f install -y

# RUN apt-get -y install ./google-chrome-stable_current_amd64.deb

RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/` curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN mkdir chrome
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/src/chrome
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python3", "index.py"]

# FROM python:3.10-slim

# WORKDIR /usr/src

# # 필수 패키지 설치 및 Chromium 설치
# RUN apt-get update && apt-get install -y \
#     chromium \
#     chromium-driver \
#     python3-pip \
#     unzip \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# # selenium과 필요한 파이썬 패키지 설치
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# # 환경 변수 설정
# ENV PYTHONUNBUFFERED=1
# ENV CHROME_BIN=/usr/bin/chromium
# ENV CHROMEDRIVER=/usr/bin/chromedriver

# CMD ["python3", "index.py"]