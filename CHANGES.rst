0.6.0 - Released on 2025-02-13
------------------------------
* Drop python 2 support
* Drop python 3.5, 3.6 support
* Keep support of python 3.7 and python 3.8 even if tests does not run on the CI on those version
* Remove debian packaging recipe based on python 2

0.5 2018-10-15
--------------

 * Fix Home Page

0.4 2018-10-13
--------------

 * Rename setting `prometheus.metric_path_info` to `prometheus.metrics_path_info`

0.3 2018-10-13
--------------

 * Fix python packaging

0.2 2018-10-13
--------------

 * Add security restriction based on permission prometheus:metrics:read
 * Add a setting to obfuscate the /metrics url

0.1 2018-10-10
--------------

 * Initial release with a /metrics route that expose prometheus metrics
