from unittest import TestCase
from hamcrest import *
from configuration import get_factory


conf = """factory: textil
production_units:
    - name: typeA
      rate: 5
    - name: typeB
"""

class TestConfiguration(TestCase):

    def test_simple_configuration(self):
        factory = get_factory(conf)
        assert_that(factory.name, "textil")
        assert_that(len(factory.production_units), is_(2))

        pu = factory.production_units[0]
        assert_that(pu.rate, is_(5))