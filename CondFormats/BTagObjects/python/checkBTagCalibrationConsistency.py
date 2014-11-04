import itertools
import unittest
import sys
from dataLoader import *


data = None
check_flavor = True
check_op = True
check_sys = True


class BtagCalibConsistencyChecker(unittest.TestCase):
    def __init__(self, *args, **kws):
        super(BtagCalibConsistencyChecker, self).__init__(*args, **kws)

    def test_ops_tight(self):
        if check_op:
            self.assertIn(0, data.ops, "OP_TIGHT is missing")

    def test_ops_medium(self):
        if check_op:
            self.assertIn(1, data.ops, "OP_MEDIUM is missing")

    def test_ops_loose(self):
        if check_op:
            self.assertIn(2, data.ops, "OP_LOOSE is missing")

    def test_flavs_b(self):
        if check_flavor:
            self.assertIn(0, data.flavs, "FLAV_B is missing")

    def test_flavs_c(self):
        if check_flavor:
            self.assertIn(1, data.flavs, "FLAV_C is missing")

    def test_flavs_udsg(self):
        if check_flavor:
            self.assertIn(2, data.flavs, "FLAV_UDSG is missing")

    def test_systematics_central(self):
        if check_sys:
            self.assertIn("central", data.syss,
                          "'central' sys. uncert. is missing")

    def test_systematics_up(self):
        if check_sys:
            self.assertIn("up", data.syss, "'up' sys. uncert. is missing")

    def test_systematics_down(self):
        if check_sys:
            self.assertIn("down", data.syss, "'down' sys. uncert. is missing")

    def test_systematics_doublesidedness(self):
        if check_sys:
            for sys in data.syss:
                if "up" in sys:
                    other = sys.replace("up", "down")
                    self.assertIn(other, data.syss,
                                  "'%s' sys. uncert. is missing" % other)
                elif "down" in sys:
                    other = sys.replace("down", "up")
                    self.assertIn(other, data.syss,
                                  "'%s' sys. uncert. is missing" % other)

    def test_eta_ranges(self):
        for a, b in data.etas:
            self.assertLess(a, b)
            self.assertGreater(a, ETA_MIN - 1e-7)
            self.assertLess(b, ETA_MAX + 1e-7)

    def test_pt_ranges(self):
        for a, b in data.pts:
            self.assertLess(a, b)
            self.assertGreater(a, PT_MIN - 1e-7)
            self.assertLess(b, PT_MAX + 1e-7)

    def test_discr_ranges(self):
        for a, b in data.discrs:
            self.assertLess(a, b)
            self.assertGreater(a, DISCR_MIN - 1e-7)
            self.assertLess(b, DISCR_MAX + 1e-7)

    def test_coverage(self):
        res = list(itertools.chain.from_iterable(
            self._check_coverage(op, meas, sys, flav)
            for flav in data.flavs
            for sys in data.syss
            for meas in data.meass
            for op in data.ops
        ))
        self.assertFalse(bool(res), "\n"+"\n".join(res))

    def _check_coverage(self, op, meas, sys, flav):
        region = "op=%d, %s, %s, flav=%d" % (op, meas, sys, flav)
        print "Checking coverage for", region

        # load relevant entries
        ens = filter(
            lambda e:
            e.params.operatingPoint == op and
            e.params.measurementType == meas and
            e.params.sysType == sys and
            e.params.jetFlavor == flav,
            data.entries
        )

        # use full or half eta range?
        if any(e.params.etaMin < 0. for e in ens):
            eta_test_points = data.eta_test_points
        else:
            eta_test_points = data.abseta_test_points

        # walk over all testpoints
        res = []
        for eta in eta_test_points:
            for pt in data.pt_test_points:
                tmp_eta_pt = filter(
                    lambda e:
                    e.params.etaMin < eta < e.params.etaMax and
                    e.params.ptMin < pt < e.params.ptMax,
                    ens
                )
                if op == 3:
                    for discr in data.discr_test_points:
                        tmp_eta_pt_discr = filter(
                            lambda e:
                            e.params.discrMin < discr < e.params.discrMax,
                            tmp_eta_pt
                        )
                        size = len(tmp_eta_pt_discr)
                        if size == 0:
                            res.append(
                                "Region not covered: %s eta=%f, pt=%f, "
                                "discr=%f" % (region, eta, pt, discr)
                            )
                        elif size > 1:
                            res.append(
                                "Region covered %d times: %s eta=%f, pt=%f, "
                                "discr=%f" % (size, region, eta, pt, discr)
                            )
                else:
                    size = len(tmp_eta_pt)
                    if size == 0:
                        res.append(
                            "Region not covered: "
                            "%s eta=%f, pt=%f" % (region, eta, pt)
                        )
                    elif size > 1:
                        res.append(
                            "Region covered %d times: "
                            "%s eta=%f, pt=%f" % (size, region, eta, pt)
                        )
        return res


def run_check(filename, op=True, sys=True, flavor=True, print_data=True):
    with open(filename) as f:
        lines = f.readlines()
    if not (lines and "OperatingPoint" in lines[0]):
        print "Data file does not contain typical header."
        return False
    lines.pop(0)  # remove header
    run_check_csv(lines, op, sys, flavor, print_data)


def run_check_csv(csv_data, op=True, sys=True, flavor=True, print_data=True):
    global data, check_op, check_sys, check_flavor
    check_op, check_sys, check_flavor = op, sys, flavor
    data = DataLoader(csv_data)
    if print_data:
        data.print_data()
    testsuite = unittest.TestLoader().loadTestsFromTestCase(
        BtagCalibConsistencyChecker)
    res = unittest.TextTestRunner().run(testsuite)
    return not bool(res.failures)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Need csv data file as first argument. Exit."
        exit(-1)
    light = not '--light' in sys.argv
    if not run_check(sys.argv[1], light, light, light):
        exit(-1)

