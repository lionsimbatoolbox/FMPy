import unittest
from fmpy.sundials import *
import numpy as np


class CVodeTest(unittest.TestCase):

    def test_bouncing_ball(self):
        """ Test CVode with a simple bouncing ball equation """

        # arrays to collect the samples
        time = []
        value = []

        cvode_mem = CVodeCreate(CV_BDF, CV_NEWTON)

        T0 = 0.0
        nx = 2  # number of states (height, velocity)
        nz = 1  # number of event indicators

        def rhsf(t, y, ydot, user_data):
            x  = np.ctypeslib.as_array(NV_DATA_S(y), (2,))
            dx = np.ctypeslib.as_array(NV_DATA_S(ydot), (2,))
            dx[0] = x[1]   # velocity
            dx[1] = -9.81  # gravity
            time.append(t)
            value.append(x[0])
            return 0

        f = CVRhsFn(rhsf)

        def rootf(t, y, gout, user_data):
            x  = np.ctypeslib.as_array(NV_DATA_S(y), (nz,))
            gout_ = np.ctypeslib.as_array(gout, (nz,))
            gout_[0] = x[0]
            return 0

        g = CVRootFn(rootf)

        RTOL = 1e-5

        y = N_VNew_Serial(nx)

        abstol = N_VNew_Serial(nx)
        abstol_array = np.ctypeslib.as_array(NV_DATA_S(abstol), (nx,))
        abstol_array[:] = RTOL

        x = NV_DATA_S(y)
        x_ = np.ctypeslib.as_array(x, (nx,))
        x_[0] = 1
        x_[1] = 5

        flag = CVodeInit(cvode_mem, f, T0, y)

        flag = CVodeRootInit(cvode_mem, nz, g)

        flag = CVodeSVtolerances(cvode_mem, RTOL, abstol)

        flag = CVDense(cvode_mem, nx)

        tNext = 2.0
        tret = realtype(0.0)

        while tret.value < 2.0:
            flag = CVode(cvode_mem, tNext, y, byref(tret), CV_NORMAL)
            if flag > 0:
                if x_[1] < 0:
                    x_[1] = -x_[1] * 0.5
                # reset solver
                flag = CVodeReInit(cvode_mem, tret, y)

        # clean up
        CVodeFree(byref(c_void_p(cvode_mem)))
        N_VDestroy_Serial(y)

        # import matplotlib.pyplot as plt
        #
        # plt.plot(time, value, '.-')
        # plt.show()

if __name__ == '__main__':
    unittest.main()
