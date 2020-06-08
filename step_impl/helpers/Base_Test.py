import os

from step_impl.helpers.API import API

from getgauge.python import before_spec
from getgauge.python import data_store as ds


class Base_Test:

    @before_spec("<service>")
    def before_spec_setup(self):
        token = os.environ['app-token']
        ds.spec.api = API("http://127.0.0.1:8080/api", auth=token)
