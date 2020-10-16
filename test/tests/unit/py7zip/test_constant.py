# System imports
import unittest
from pytest import raises

# Project imports
import py7zip.constant as const

class TestComplyConst(unittest.TestCase):

    def test_setting_constant(self):
        const.TEST_VARIABLE = 'this is a test'
        assert const.TEST_VARIABLE == 'this is a test'


    def test_setting_existing_value(self):
        const.SET_VARIABLE_TEST = 'this is a test'

        with raises(TypeError) as exc_info:
            const.SET_VARIABLE_TEST = 'this is a test'

        assert exc_info.value.args[0] == "Can't rebind const(SET_VARIABLE_TEST)"


    def test_removing_existing_value(self):
        const.REMOVE_VARIABLE_TEST = 'this is a test'

        with raises(TypeError) as exc_info:
            del const.REMOVE_VARIABLE_TEST

        assert exc_info.value.args[0] == "Can't unbind const(REMOVE_VARIABLE_TEST)" 

        with raises(NameError) as exc_info:
            del const.REMOVE_UNDEF_VARIABLE_TEST

        assert exc_info.type == NameError
