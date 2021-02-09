# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
import os

c = get_config()

# We rely on environment variables to configure JupyterHub so that we
# avoid having to rebuild the JupyterHub container every time we change a
# configuration parameter.

# Spawn single-user servers as Docker containers
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
# Spawn containers from this image
c.DockerSpawner.container_image = os.environ['DOCKER_NOTEBOOK_IMAGE']
# JupyterHub requires a single-user instance of the Notebook server, so we
# default to using the `start-singleuser.sh` script included in the
# jupyter/docker-stacks *-notebook images as the Docker run command when
# spawning containers.  Optionally, you can override the Docker run command
# using the DOCKER_SPAWN_CMD environment variable.
spawn_cmd = os.environ.get('DOCKER_SPAWN_CMD', "start-singleuser.sh")
c.DockerSpawner.extra_create_kwargs.update({ 'command': spawn_cmd })
# Connect containers to this Docker network
network_name = os.environ['DOCKER_NETWORK_NAME']
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = network_name
# Pass the network name as argument to spawned containers
c.DockerSpawner.extra_host_config = { 'network_mode': network_name }
# Pass environment variables to the notebook
# -- Neo4j
c.Spawner.env_keep.append('NEO4J_URI')
c.Spawner.env_keep.append('NEO4J_URI_DEV')
# -- Elasticsearch
c.Spawner.env_keep.append('ELASTICSEARCH_URI')
c.Spawner.env_keep.append('ELASTICSEARCH_URI_DEV')
c.Spawner.env_keep.append('ELASTICSEARCH_FEATURE_STORE_URI')
c.Spawner.env_keep.append('ELASTICSEARCH_FEATURE_STORE_URI_DEV')
c.Spawner.env_keep.append('ELASTICSEARCH_PREDICTIONS_URI')
c.Spawner.env_keep.append('ELASTICSEARCH_PREDICTIONS_URI_DEV')
# -- postgres
c.Spawner.env_keep.append('POSTGRESQL_URI')
c.Spawner.env_keep.append('POSTGRESQL_URI_DEV')
c.Spawner.env_keep.append('POSTGRESQL_REPLICA_URI')
c.Spawner.env_keep.append('POSTGRESQL_BACKEND_REPLICA_URI')
# -- Redis
c.Spawner.env_keep.append('REDIS_DATA_HOST')
c.Spawner.env_keep.append('REDIS_DATA_PORT')
c.Spawner.env_keep.append('REDIS_DATA_HOST_DEV')
c.Spawner.env_keep.append('REDIS_DATA_PORT_DEV')
c.Spawner.env_keep.append('REDIS_BACKEND_HOST')
c.Spawner.env_keep.append('REDIS_BACKEND_PORT')
c.Spawner.env_keep.append('REDIS_BACKEND_HOST_DEV')
c.Spawner.env_keep.append('REDIS_BACKEND_PORT_DEV')
# -- ml-master-spain
c.Spawner.env_keep.append('ML_MASTER_SPAIN_URL_PROD')
c.Spawner.env_keep.append('ML_MASTER_SPAIN_URL_DEV')
# -- ml-word2vec-{en,es}
c.Spawner.env_keep.append('ML_WORD2VEC_EN_URL_PROD')
c.Spawner.env_keep.append('ML_WORD2VEC_EN_URL_DEV')
c.Spawner.env_keep.append('ML_WORD2VEC_ES_URL_PROD')
c.Spawner.env_keep.append('ML_WORD2VEC_ES_URL_DEV')
# Explicitly set notebook directory because we'll be mounting a host volume to
# it.  Most jupyter/docker-stacks *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We follow the same convention.
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
c.DockerSpawner.notebook_dir = notebook_dir
# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': notebook_dir }
# volume_driver is no longer a keyword argument to create_container()
# c.DockerSpawner.extra_create_kwargs.update({ 'volume_driver': 'local' })
# Remove containers once they are stopped
c.DockerSpawner.remove_containers = True
# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

# User containers will access hub by container name on the Docker network
c.JupyterHub.hub_ip = 'jupyterhub'
c.JupyterHub.hub_port = 8080

# TLS config
c.JupyterHub.port = 443
c.JupyterHub.ssl_key = os.environ['SSL_KEY']
c.JupyterHub.ssl_cert = os.environ['SSL_CERT']

# Redirect HTTP requests on port 80 to the server on HTTPS
c.ConfigurableHTTPProxy.command = ['configurable-http-proxy', '--redirect-port', '80']

# Authenticate users with GitHub OAuth
c.JupyterHub.authenticator_class = 'oauthenticator.GitHubOAuthenticator'
c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']

# Persist hub data on volume mounted inside container
data_dir = os.environ.get('DATA_VOLUME_CONTAINER', '/data')

c.JupyterHub.cookie_secret_file = os.path.join(data_dir,
    'jupyterhub_cookie_secret')

c.JupyterHub.db_url = 'postgresql://postgres:{password}@{host}/{db}'.format(
    host=os.environ['POSTGRES_HOST'],
    password=os.environ['POSTGRES_PASSWORD'],
    db=os.environ['POSTGRES_DB'],
)

# Whitlelist users and admins
c.Authenticator.whitelist = whitelist = set()
c.Authenticator.admin_users = admin = set()
c.JupyterHub.admin_access = True
pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'userlist')) as f:
    for line in f:
        if not line:
            continue
        parts = line.split()
        # in case of newline at the end of userlist file
        if len(parts) >= 1:
            name = parts[0]
            whitelist.add(name)
            if len(parts) > 1 and parts[1] == 'admin':
                admin.add(name)
