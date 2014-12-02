#    Copyright 2011 VMware, Inc.
#    All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# Copied from Neutron
from cue.db import models

from oslo.config import cfg
from oslo.db import options as db_options
from oslo.db.sqlalchemy import session

CONF = cfg.CONF

CONF.register_opt(cfg.StrOpt('sqlite_db', default='cue.sqlite'))

db_options.set_defaults(
    cfg.CONF, connection='sqlite:///$state_path/$sqlite_db')

_FACADE = None


def _create_facade_lazily():
    global _FACADE

    if _FACADE is None:
        _FACADE = session.EngineFacade.from_config(cfg.CONF, sqlite_fk=True)

    return _FACADE


def get_engine():
    """Helper method to grab engine."""
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(autocommit=True, expire_on_commit=False):
    """Helper method to grab session."""
    facade = _create_facade_lazily()
    return facade.get_session(autocommit=autocommit,
                              expire_on_commit=expire_on_commit)


def create_cluster(project_id, name, nic, vol_size, flavor, num_of_nodes):
    session = get_session()

    cluster_ref = models.Cluster.add(session, project_id, name, nic, vol_size)

    for i in range(num_of_nodes):
        models.Node.add(session, cluster_ref.id, flavor, vol_size)

    return cluster_ref


def get_cluster_nodes(cluster_id):
    session = get_session()

    return models.Node.get_all(session, cluster_id=cluster_id)