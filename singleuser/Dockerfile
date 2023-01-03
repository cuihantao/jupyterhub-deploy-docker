ARG DOCKER_NOTEBOOK_IMAGE
FROM $DOCKER_NOTEBOOK_IMAGE
ARG JUPYTERHUB_VERSION

RUN python3 -m pip install --no-cache \
    jupyterhub==$JUPYTERHUB_VERSION \
    andes[all] kvxopt \
    git+https://github.com/sensl/nbvscode.git#master

USER root

# Install system essentials

RUN apt-get update && apt-get install -y \
    vim tmux rclone \
    && rm -rf /var/lib/apt/lists/*

# Julia installation
# Default values can be overridden at build time
# (ARGS are in lower case to distinguish them from ENV)
# Check https://julialang.org/downloads/
ARG julia_version="1.8.4"
# SHA256 checksum

# Julia dependencies
# install Julia packages in /opt/julia instead of $HOME
ENV JULIA_DEPOT_PATH=/opt/julia \
    JULIA_VERSION="${julia_version}"

WORKDIR /tmp

# hadolint ignore=SC2046
RUN mkdir -p "/opt/julia-${JULIA_VERSION}" && \
    wget -q https://julialang-s3.julialang.org/bin/linux/x64/$(echo "${JULIA_VERSION}" | cut -d. -f 1,2)"/julia-${JULIA_VERSION}-linux-x86_64.tar.gz" && \
    tar xzf "julia-${JULIA_VERSION}-linux-x86_64.tar.gz" -C "/opt/julia-${JULIA_VERSION}" --strip-components=1 && \
    rm "/tmp/julia-${JULIA_VERSION}-linux-x86_64.tar.gz" && \
    ln -fs /opt/julia-${JULIA_VERSION}/bin/julia /usr/local/bin/julia

# Show Julia where conda libraries are \
RUN mkdir -p /etc/julia && \
    echo "push!(Libdl.DL_LOAD_PATH, \"$CONDA_DIR/lib\")" >> /etc/julia/juliarc.jl && \
    # Create JULIA_PKGDIR \
    mkdir -p "${JULIA_PKGDIR}" && \
    chown "${NB_USER}" "${JULIA_PKGDIR}" && \
    fix-permissions "${JULIA_PKGDIR}"

RUN rm -r "${CONDA_DIR}/share/jupyter/kernels/julia-1.8"

# Code server installation
ENV CODESERVER_URL="https://github.com/coder/code-server/releases/download/v4.9.1/code-server_4.9.1_amd64.deb" \
    CODESERVER="code-server_4.9.1_amd64.deb"


RUN wget ${CODESERVER_URL} && \
    dpkg -i ${CODESERVER} && \
    rm ${CODESERVER} ** \
    rm -rf code-server* && \
    rm -rf /tmp/* && \
    rm -rf $HOME/.cache && \
    rm -rf $HOME/.node-gyp

USER $NB_UID

# Add Julia packages.
# Install IJulia as jovyan and then move the kernelspec out
# to the system share location. Avoids problems with runtime UID change not
# taking effect properly on the .local folder in the jovyan home dir.
RUN julia -e 'import Pkg; Pkg.update()' && \
    julia -e 'using Pkg; pkg"add IJulia"; pkg"build IJulia"; pkg"precompile"' && \
    # move kernelspec out of home \
    mv "${HOME}/.local/share/jupyter/kernels/julia"* "${CONDA_DIR}/share/jupyter/kernels/" && \
    chmod -R go+rx "${CONDA_DIR}/share/jupyter" && \
    rm -rf "${HOME}/.local" && \
    fix-permissions "${JULIA_PKGDIR}" "${CONDA_DIR}/share/jupyter"

# Add additional Julia packages.

# RUN julia -e 'import Pkg; Pkg.add(["Andes", "Revise"])'

# Prepend user's homedir to JULIA_DEPOT
# Allows user-specific package installation

ENV JULIA_DEPOT_PATH="${HOME}/.julia":"${JULIA_DEPOT_PATH}"

# Install and configure jupyter notebook extensions
# These need to be installed in the user mode.

RUN python3 -m pip install --no-cache \
    ipywidgets widgetsnbextension jupyter_contrib_nbextensions \
    ipysheet

RUN jupyter nbextension enable --py widgetsnbextension --sys-prefix && \
    jupyter contrib nbextension install --sys-prefix

WORKDIR $HOME
