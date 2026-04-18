clearmetrics
============

Python BI platform for ingesting, transforming, validating, and visualizing financial data.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   domain
   ports
   adapters
   application

Domain
------

.. toctree::
   :maxdepth: 1

   domain/models
   domain/services
   domain/rules
   domain/exceptions

.. automodule:: clearmetrics.domain.models.transaction
   :members:

.. automodule:: clearmetrics.domain.models.metric
   :members:

.. automodule:: clearmetrics.domain.models.user
   :members:

.. automodule:: clearmetrics.domain.models.report
   :members:

.. automodule:: clearmetrics.domain.models.quality_result
   :members:

.. automodule:: clearmetrics.domain.services.etl_service
   :members:

.. automodule:: clearmetrics.domain.services.quality_service
   :members:

.. automodule:: clearmetrics.domain.services.auth_service
   :members:

.. automodule:: clearmetrics.domain.rules.not_null_rule
   :members:

.. automodule:: clearmetrics.domain.rules.positive_amount_rule
   :members:

.. automodule:: clearmetrics.domain.rules.valid_currency_rule
   :members:

.. automodule:: clearmetrics.domain.rules.no_duplicate_rule
   :members:

.. automodule:: clearmetrics.domain.rules.date_range_rule
   :members:

Ports
-----

.. automodule:: clearmetrics.ports.outbound.i_transaction_source_port
   :members:

.. automodule:: clearmetrics.ports.outbound.i_metric_source_port
   :members:

.. automodule:: clearmetrics.ports.outbound.i_transaction_storage_port
   :members:

.. automodule:: clearmetrics.ports.outbound.i_metric_storage_port
   :members:

.. automodule:: clearmetrics.ports.outbound.i_token_generator_port
   :members:

.. automodule:: clearmetrics.ports.outbound.i_token_verifier_port
   :members:

.. automodule:: clearmetrics.ports.outbound.i_quality_rule_port
   :members:

Application
-----------

.. automodule:: clearmetrics.application.ingest_data
   :members:

.. automodule:: clearmetrics.application.validate_data
   :members:

.. automodule:: clearmetrics.application.export_metrics
   :members:

Adapters
--------

.. automodule:: clearmetrics.adapters.outbound.postgresql_transaction_source_adapter
   :members:

.. automodule:: clearmetrics.adapters.outbound.postgresql_transaction_storage_adapter
   :members:

.. automodule:: clearmetrics.adapters.outbound.csv_transaction_source_adapter
   :members:

.. automodule:: clearmetrics.adapters.outbound.external_api_transaction_source_adapter
   :members:

.. automodule:: clearmetrics.adapters.outbound.jwt_token_generator_adapter
   :members:

.. automodule:: clearmetrics.adapters.outbound.jwt_token_verifier_adapter
   :members:

.. automodule:: clearmetrics.adapters.inbound.fastapi_api
   :members:

Indices
-------

* :ref:`genindex`
* :ref:`modindex`
