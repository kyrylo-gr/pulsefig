# flake8: noqa: D101, D102
import unittest

from pulsefig.variables import UnsetParameter


class Obj:
    param = UnsetParameter()

    def __init__(self):

        pass


class TestUnsetParameter(unittest.TestCase):
    # def setUp(self) -> None:
    # self.obj = Obj()

    def test_simple_assign(self):
        obj = Obj()
        a = obj.param
        self.assertTrue(float(a) == 0, msg=f"{a} should be 0")
        obj.param = 2
        self.assertTrue(float(a) == 2, msg=f"{a} should be 2")

    def test_addition(self):
        obj = Obj()
        a = obj.param + 2
        obj.param = 3
        assert float(a) == 5

    def test_raddition(self):
        obj = Obj()
        a = 2 + obj.param
        obj.param = 3
        assert float(a) == 5

    def test_multiplication(self):
        obj = Obj()
        a = obj.param * 2
        obj.param = 3
        assert float(a) == 6

    def test_rmultiplication(self):
        obj = Obj()
        a = 2 * obj.param
        obj.param = 3
        assert float(a) == 6

    def test_subtraction(self):
        obj = Obj()
        a = obj.param - 2
        obj.param = 3
        assert float(a) == 1

    def test_rsubtraction(self):
        obj = Obj()
        a = 2 - obj.param
        obj.param = 3
        assert float(a) == -1

    def test_division(self):
        obj = Obj()
        a = obj.param / 2
        obj.param = 3
        assert float(a) == 1.5

    def test_multiple_operations(self):
        obj = Obj()
        a = (obj.param + 2) * 3
        obj.param = 3
        assert float(a) == 15

    def test_equals_false(self):
        obj = Obj()
        a = obj.param == 2
        obj.param = 3
        assert float(a) == 0

    def test_equals_true(self):
        obj = Obj()
        a = obj.param == 2
        obj.param = 2
        assert float(a) == 1

    def test_not_equals_false(self):
        obj = Obj()
        a = obj.param != 2
        obj.param = 2
        assert float(a) == 0

    def test_not_equals_true(self):
        obj = Obj()
        a = obj.param != 2
        obj.param = 3
        assert float(a) == 1

    def test_lt_true(self):
        obj = Obj()
        a = obj.param < 2
        obj.param = 1
        assert float(a) == 1

    def test_lt_false(self):
        obj = Obj()
        a = obj.param < 2
        obj.param = 2
        assert float(a) == 0

    def test_gt_true(self):
        obj = Obj()
        a = obj.param > 2
        obj.param = 3
        assert float(a) == 1

    def test_gt_false(self):
        obj = Obj()
        a = obj.param > 2
        obj.param = 1
        assert float(a) == 0

    def test_le_true(self):
        obj = Obj()
        a = obj.param <= 2
        obj.param = 2
        assert float(a) == 1

    def test_le_false(self):
        obj = Obj()
        a = obj.param <= 2
        obj.param = 3
        assert float(a) == 0

    def test_ge_true(self):
        obj = Obj()
        a = obj.param >= 2
        obj.param = 3
        assert float(a) == 1

    def test_ge_false(self):
        obj = Obj()
        a = obj.param >= 2
        obj.param = 1
        assert float(a) == 0

    def test_hash_true(self):
        obj = Obj()
        a = obj.param
        b = obj.param
        assert hash(a) == hash(b)

    def test_hash_false(self):
        obj = Obj()
        a = obj.param
        b = obj.param + 2
        assert hash(a) != hash(b)

    def test_hash_operation(self):
        obj = Obj()
        a = (obj.param + 2) / 2
        b = (obj.param + 2) / 2
        assert hash(a) == hash(b)


class TestParameterPostOperation(unittest.TestCase):

    def test_addition(self):
        obj = Obj()
        a = obj.param + 2
        obj.param = 3
        assert float(a + 2) == 7

    def test_multiplication(self):
        obj = Obj()
        a = obj.param * 2
        obj.param = 3
        assert float(a * 2) == 12

    def test_subtraction(self):
        obj = Obj()
        a = obj.param - 2
        obj.param = 3
        assert float(a - 2) == -1

    def test_division(self):
        obj = Obj()
        a = obj.param / 2
        obj.param = 3
        assert float(a / 2) == 0.75

    def test_multiple_operations(self):
        obj = Obj()
        a = (obj.param + 2) * 3
        obj.param = 3
        assert float(a - 5) == 10


class TestDoubleUnsetParameter(unittest.TestCase):
    def test_self_addition(self):
        obj1 = Obj()
        a = obj1.param + obj1.param
        obj1.param = 3
        assert float(a) == 6

    def test_addition(self):
        obj1 = Obj()
        obj2 = Obj()
        a = obj1.param + obj2.param
        obj1.param = 3
        obj2.param = 2
        assert float(a) == 5

    def test_multiplication(self):
        obj1 = Obj()
        obj2 = Obj()
        a = obj1.param * obj2.param
        obj1.param = 3
        obj2.param = 2
        assert float(a) == 6

    def test_subtraction(self):
        obj1 = Obj()
        obj2 = Obj()
        a = obj1.param - obj2.param
        obj1.param = 3
        obj2.param = 2
        assert float(a) == 1

    def test_division(self):
        obj1 = Obj()
        obj2 = Obj()
        a = obj1.param / obj2.param
        obj1.param = 3
        obj2.param = 2
        assert float(a) == 1.5

    def test_3_additions(self):
        obj1 = Obj()
        obj2 = Obj()
        obj3 = Obj()
        a = obj1.param + obj2.param + obj3.param * 2
        obj1.param = 3
        obj2.param = 2
        obj3.param = 1
        assert float(a) == 7


if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
