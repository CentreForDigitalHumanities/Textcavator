# Distrobox development setup.

This is a guide for setting up a [distrobox](https://distrobox.it/) container with Ubuntu for developing Textcavator. These are notes from my (Luka) experience; modify as needed.

### Distrobox vs. Docker compose containers

This repository also includes a container setup using Docker compose. The docker-compose setup is designed for maximum isolation, separating the application from the host system, as well as using separate containers for different subsystems (frontend, backend, database engines).

By contrast, distrobox is a system for running privileged containers, which are tightly integrated with the host system. Also, this guide will create a single container that includes Textcavator and all its dependencies, instead of isolating subsystems.

Generally speaking, using distrobox offers some but not all of the benefits of containerisation, and some but not all of the drawbacks. Which option you prefer is up to you.

### Using host services

This guide will install PostgreSQL, Elasticsearch, Kibana, and Redis in the container; these will run in the background when the container is up.

Because distrobox are not isolated from the host system, you can also connect to services that are running in the host, instead of running them in the container. For instance, if your host system is already running PostgreSQL, it's probably not necessary (or useful) to install it in the container.

(Of course, if *all* of these services are already running on the host, there really is no point in setting up a container at all.)

## Prerequisites

You need to install [distrobox](https://distrobox.it/). You may also consider installing [DistroShelf](https://flathub.org/en-GB/apps/com.ranfdev.DistroShelf) if you want a GUI manager.

## Container setup

If your container will include PostgreSQL (see below), create it with:

```sh
distrobox create --name textcavator --image ubuntu:24.04 --init --pre-init-hooks "mkdir /var/run/postgresql && chown postgres /var/run/postgresql"
```

Otherwise, you can leave out the pre-init hook:

```sh
distrobox create --name textcavator --image ubuntu:24.04 --init
```

After creating, enter the container with

```sh
distrobox enter textcavator
```

First-time setup will take a while.

## Install basic libraries

Run inside the container:

```sh
sudo apt update
sudo upgrade
sudo apt install nano git git-flow python3-pip python3-virtualenv
```

## PostgreSQL

Running PostgreSQL is the most precarious part of the setup. If you're developing other projects that use PostgreSQL, I recommend against installing it like this, as there is little benefit. Instead, run PostgreSQL on your host system, or run it inside a separate docker/podman container.

If you are going to use PostgreSQL, make sure you included the pre-init hook when creating the container (see above). Enter the container to install postgresql.

To prevent an error in installation, run the following:

```sh
sudo nano /usr/sbin/policy-rc.d
```

Change the file contents to `exit 0`, save and close.

Then install PostgreSQL 16 with:

```sh
sudo apt install postgresql
```

For convenience, the following commands let you run `psql` without switching to the `postgres` user. Substitute `johndoe` with your own username.

```sh
sudo -u postgres createuser johndoe
sudo -u postgres createdb -O johndoe johndoe
sudo -u postgres psql
```

In the psql prompt run:

```sql
alter user johndoe superuser;
```

Use `exit` to quit.


To check that everything it working, stop the container, restart, and type `psql` in the command line. This should open the psql prompt.

The default port for PostgreSQL is 5432, but if that port is occupied (usually because PostgreSQL is already running on the host), it will use a different port. Check the port with:

```sh
cat /etc/postgresql/16/main/postgresql.conf | grep "port ="
```

If this is not 5432, open (or create) `backend/ianalyzer/local_settings.py` in this repository to override your database configuration. Copy the `DATABASES` declaration from `backend/ianalyzer/settings.py` and change the port number.

## Node and yarn

See [nodejs.org](https://nodejs.org/en/download) for instructions. Choose Node 22 / Linux / nvm / yarn in the options, and execute the instructions.

## ElasticSearch

Install Elasticsearch. See [Elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/deb.html):

```sh
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list
sudo apt-get update
sudo apt-get install elasticsearch
sudo systemctl daemon-reload
```

Elasticsearch should now be up and running. To disable security options, run:

```sh
sudo nano /etc/elasticsearch/elasticsearch.yml
```

Change the `xpack.security.enable:` option to `false`, save and close.

Depending on your total RAM, ELasticsearch may reserve a large amount of memory, which is probably not what you want. (See [advanced configuration docs](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/advanced-configuration.html) for more about this step.) Create a file override the default memory settings:

```sh
sudo nano /etc/elasticsearch/jvm.options.d/memory.options
```

Copy-paste the following to set the size to 4GB. Save and close.

```
-Xms4g
-Xmx4g
```

## Kibana (optional)

Kibana provides a GUI interface for Elasticsearch. Textcavator does not depend on Kibana, but we recommended that you install this too, as it's useful for troubleshooting, testing queries, managing indices, etc.

(The steps below should be done *after* the Elasticsearch installation.)

```sh
sudo apt-get install kibana
sudo systemctl enable kibana.service
```

Now run:

```sh
sudo nano /etc/kibana/kibana.yaml
```

Edit the setting `pid.file:` to `/var/run/kibana.pid`

When your container is running, you can open Kibana by going to `https://localhost:5601` in your browser.

## Redis

Install Redis ([APT installation instructions](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/apt/)):

```sh
sudo apt-get install lsb-release curl gpg
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
sudo chmod 644 /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
sudo apt-get update
sudo apt-get install redis
```

## Google Chrome

Chrome is used for browser testing in the frontend. Install with:

```sh
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
sudo apt-get update
sudo apt-get install google-chrome-stable
```

## IDE (optional)

You could use a code editor installed on your host system, but I find it more convenient to install the editor in my container. See https://distrobox.it/posts/integrate_vscode_distrobox/ .

### VSCode

To install VSCode, [VSCode installation instructions](https://code.visualstudio.com/docs/setup/linux#_install-vs-code-on-linux). Choose the option to install the `.deb` package. Then export the application.

For convience, I include a flag to always open on the Textcavator repository:

```sh
distrobox-export --app code --extra-flags "/path/to/this/repository/ --foreground"
```

### VSCodium

See [VSCodium installation instructions](https://vscodium.com/#install-on-debian-ubuntu-deb-package). Then export with:

```sh
distrobox-export --app codium --extra-flags "/path/to/this/repository/ --foreground"
```
