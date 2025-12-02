This is a recipe for installing Textcavator on Debian 10 Buster. It uses [Linux containers via LXD](https://linuxcontainers.org/lxd/getting-started-cli/) to keep things isolated from the host system, or you can skip the LXD part and move to installing the prerequisites. Modify as needed.

# LXD Container setup

Install LXD, add your user to the `lxd` group, and setup LXD with `lxd init`.

Refresh group membership by logging out and back in (or via `su - yourname`). Then:

    lxc launch images:debian/10 IAnalyzer
    lxc start IAnalyzer

Login as root:

`lxc exec IAnalyzer -- /bin/bash`

From within the container:

    apt-get install sudo
    adduser yourname
    usermod -aG sudo yourname

Optional: copy files you need into the container. For example:

`lxc file push -r ~/.ssh IAnalyzer/home/yourname/`

Login as user `yourname`:

`lxc exec IAnalyzer -- su --login yourname`

Proxy container ports that you want to be available on your host system:

    lxc config device add IAnalyzer mysql proxy listen=tcp:0.0.0.0:3307 connect=tcp:127.0.0.1:3306
    lxc config device add IAnalyzer elastic proxy listen=tcp:0.0.0.0:9200 connect=tcp:127.0.0.1:9200
    lxc config device add IAnalyzer angular proxy listen=tcp:0.0.0.0:4200 connect=tcp:127.0.0.1:4200


# Install prerequisites on Debian 10

As root:

## Basics

`apt-get install wget curl git ssh nano vim unzip gnupg apt-transport-https lsb-release python3 python3-pip libxml2-dev libxmlsec1-dev libxmlsec1-openssl pkg-config`

## NodeJS and NPM

    curl -sL https://deb.nodesource.com/setup_14.x | bash -
    apt-get install nodejs gcc g++ make
    nodejs --version
    npm --version

## Yarn

    curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
    apt-get update && apt-get install yarn

## PostgreSQL

See https://www.postgresql.org/docs/current/installation.html

## Java

`apt-get install openjdk-11-jre`


## ElasticSearch

https://www.elastic.co/guide/en/elasticsearch/reference/8.5/index.html


    wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
    echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" > /etc/apt/sources.list.d/elastic-8.x.list
    apt-get update && apt-get install elasticsearch
    systemctl start elasticsearch
    systemctl status elasticsearch
    curl http://127.0.0.1:9200 # Check the installation


## Redis

https://redis.io/docs/getting-started/installation/install-redis-from-source/

    wget https://download.redis.io/redis-stable.tar.gz
    tar -xzvf redis-stable.tar.gz
    cd redis-stable
    make
    make install


## Chrome

Chrome / chromedriver seems to be needed as well?

    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    apt-get install ./google-chrome-stable_current_amd64.deb
    CHROME_MAIN_VERSION=$(google-chrome-stable --version | sed -E 's/(^Google Chrome |\.[0-9]+ )//g')
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_MAIN_VERSION")
    curl "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" -O
    unzip chromedriver_linux64.zip -d /usr/local/bin


## Python and virtualenv

    python3 --version # Python 3.7 seems to work as well
    pip3 install virtualenv # virtualenv may not be needed if using a container?


# Textcavator setup

If using LXD, login as the user you created: `lxc exec IAnalyzer -- su --login yourname`

Now follow the installation as described in the [README](https://github.com/CentreForDigitalHumanities/Textcavator/blob/develop/README.md).
