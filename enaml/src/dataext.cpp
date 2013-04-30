/*-----------------------------------------------------------------------------
| Copyright (c) 2013, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/
#include "inttypes.h"
#include <iostream>
#include "pythonhelpers.h"

using namespace PythonHelpers;

extern "C" {

double
sum(double array[], Py_ssize_t start, Py_ssize_t end)
{
    double sum = 0.;
    for (Py_ssize_t idx = start; idx <= end; idx++) {
        sum += array[idx];
    }
    return sum;
}


double
normAspect(double big, double small, double accum, double factor)
{
    double x = (big * factor) / (small * accum / factor);
    if (x < 1) return 1/x;
    else return x;
}


/* Slice layout

*/
void
slice_layout(double array[], PyListPtr& rects,
    Py_ssize_t start, Py_ssize_t end, 
    double x, double y, double width, double height)
{
    double accum = 0, total = sum(array, start, end);

    double newx, newy, newwidth, newheight;

    for (Py_ssize_t idx=start; idx<=end; idx++) {

        double factor = array[idx] / total;

        if (width <= height) {
            newx = x;
            newwidth = width;
            newy = y + height * accum;
            newheight = height * factor;

        } else {
            newx = x + width * accum;
            newwidth = width * factor;
            newy = y;
            newheight = height;
        }
        accum += factor;

        PyObjectPtr x(PyFloat_FromDouble(newx));
        PyObjectPtr y(PyFloat_FromDouble(newy));
        PyObjectPtr w(PyFloat_FromDouble(newwidth));
        PyObjectPtr h(PyFloat_FromDouble(newheight));

        PyObjectPtr bounds(PyTuple_Pack(4, x.get(), y.get(), w.get(), h.get()));
        rects.set_item(idx, bounds);
    }
}

void
squarify_layout(double array[], PyListPtr& rects, 
    Py_ssize_t start, Py_ssize_t end,
    double x, double y, double width, double height)
{
    if (start > end) return;

    if (end - start < 2) {
        slice_layout(array, rects, start, end, x, y, width, height);
        return;
    }

    double total = sum(array, start, end);
    int mid = start;
    double accum = array[start] / total;
    double factor = accum;

    if (width < height) {
        while (mid <= end) {
            double aspect = normAspect(height, width, accum, factor);
            double q = array[mid] / total;
            if (normAspect(height, width, accum, factor+q) > aspect) {
                break;
            }
            mid++;
            factor += q;
        }

        slice_layout(array, rects, start, mid, x, y, width, height*factor);
        squarify_layout(array, rects, mid+1, end, x, y+height*factor, width, height * (1 - factor));
    } else {
        while (mid <= end) {
            double aspect = normAspect(width, height, accum, factor);
            double q = array[mid] / total;
            if (normAspect(width, height, accum, factor+q) > aspect) {
                break;
            }
            mid++;
            factor += q;
        }

        slice_layout(array, rects, start, mid, x, y, width * factor, height);
        squarify_layout(array, rects, mid+1, end, x+width*factor, y, width * (1 - factor), height);
    }
}


/* Fast squarified layout of an array of values.

*/
static PyObject*
fast_layout(PyObject* dummy, PyObject* args)
{
    PyObject* tmp;
    Py_buffer array;
    double x, y, width, height;
    if( !PyArg_ParseTuple(args, "Odddd", &tmp, &x, &y, &width, &height) ) {
        return 0;
    }

    if (tmp == NULL) {
        return py_type_fail("tmp is NULL");
    }

    if ( PyObject_GetBuffer(tmp, &array, PyBUF_ND) ) {
        return py_type_fail("First argument of fast_layout should support buffer protocol");
    }

    if (array.shape == NULL)
        return py_type_fail("shape is NULL");

    Py_ssize_t size = array.shape[0];
    PyListPtr rects( PyList_New(size) );

    squarify_layout((double*)array.buf, rects, 0, size-1, x, y, width, height);

    rects.incref();
    return rects.release();
}


static PyMethodDef
dataext_methods[] = {
    { "fast_layout", (PyCFunction )fast_layout, METH_VARARGS,
      "fast_layout(array, x, y, w, h)" },
    { 0 } // Sentinel
};


PyMODINIT_FUNC
initdataext( void )
{
    PyObject* mod = Py_InitModule( "dataext", dataext_methods );
}

} // extern "C"
