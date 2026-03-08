
import os
import logging
from fastapi import FastAPI
from datamodels.variables import Variables
from datamodels.infrastructure import Infrastructure
from sqlalchemy import create_engine
from datamodels.db import Base

logger = logging.getLogger(__name__)

def initialize_db(var: Variables):
    """ Initialize the DB """
    db_path = var.db.db_path
    db_host = var.db.db_host
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    engine = create_engine(db_host)
    var.db.engine = engine
    logger.info(f"Created the DB engine for host : {db_host}")
    Base.metadata.create_all(engine)
    return True

def initialize_logger(var: Variables):
    """ Initialize the logger """
    log_path = var.utils.log_path
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(format=log_format, level=logging.DEBUG, filename=log_path, filemode='w')
    return True

def initialize_server(app: FastAPI):
    """ Initialize the Server & all variables"""

    var = Variables()
    infra = Infrastructure()
    initialize_logger(var)  # initialize logge
    initialize_db(var)   #intialize db
    logger.info("Server Initialized")
    app.state.var = var
    app.state.infra = infra


# Shutdown Functions

def shutdown_db(var: Variables):
    """ Close the engine"""
    if var.db.engine:
        var.db.engine.dispose()
    logger.info("DB Engine disposed")

def shutdown_server(var):
    """ Shutdown all the server related components"""

    shutdown_db(var)
    logger.info("Shutdown Complete")

    return True


