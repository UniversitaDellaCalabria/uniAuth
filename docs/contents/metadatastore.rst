MetadataStore definitions
^^^^^^^^^^^^^^^^^^^^^^^^^

.. thumbnail:: mdstore.png

  Defining a Metadata Store, everytime you save the entrie will be validated to avoid faulty configurations in Production Environment.


------------


.. thumbnail:: validate_md.png

  On save: if MetadataStore type is ``remote`` or ``mdq`` it will be validated upon the reachablility of its endpoint and the validity of its https certificate. If type is ``local`` instead, the validation will check the existence of the file path and the validity of the XML syntax. If one of the previous checks will fail the resource will be automatically disactivated.
