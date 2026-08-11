# ============================================================
# LH NAUTICAL - INGESTION IMAGE
# ============================================================
#
# Container responsável por:
#
#   - geração do schema
#   - ingestão dos CSVs
#   - validação
#   - transformações futuras
#
# ============================================================


# ------------------------------------------------------------
# BASE IMAGE
# ------------------------------------------------------------
#
# Python slim é suficiente para nosso pipeline.
#
# Não precisamos de uma distribuição Linux completa.
#
FROM python:3.13-slim


# ------------------------------------------------------------
# ENVIRONMENT
# ------------------------------------------------------------
#
# PYTHONDONTWRITEBYTECODE
#
# Evita a criação de arquivos .pyc.
#
ENV PYTHONDONTWRITEBYTECODE=1
#
# PYTHONUNBUFFERED
#
# Faz com que os logs Python apareçam imediatamente no
# stdout/stderr do container.
#
ENV PYTHONUNBUFFERED=1


# ------------------------------------------------------------
# WORKING DIRECTORY
# ------------------------------------------------------------
#
# Todos os comandos posteriores serão executados a partir
# deste diretório.
#
WORKDIR /app


# ------------------------------------------------------------
# DEPENDENCIES
# ------------------------------------------------------------
#
# Copiamos primeiro requirements.txt.
#
# Isso permite que o Docker aproveite o cache dessa camada
# caso apenas o código Python seja alterado.
#
COPY docker/ingestion/requirements.txt ./requirements.txt


# Instala as dependências Python.
#
# --no-cache-dir evita armazenar o cache do pip dentro da
# imagem.
#
RUN pip install --no-cache-dir -r requirements.txt


# ------------------------------------------------------------
# SOURCE CODE
# ------------------------------------------------------------
#
# Copiamos o código Python para dentro da imagem.
#
COPY src ./src


# ------------------------------------------------------------
# DEFAULT COMMAND
# ------------------------------------------------------------
#
# O Compose sobrescreve esse comando.
#
# Deixamos um comando simples para que o container permaneça
# ativo durante desenvolvimento.
#
CMD ["tail", "-f", "/dev/null"]