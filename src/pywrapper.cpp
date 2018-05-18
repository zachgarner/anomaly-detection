#include<Python.h>
#include<vector>
#include"edm-multi.h"
#include"edm-per.h"
#include"edmTail.h"
#include"edmx.h"
#include <py3c/compat.h>

std::vector<double> to_vector(PyObject *pyList) {
    Py_ssize_t list_len = PyList_Size(pyList);
    std::vector<double> valueVector;
    for(Py_ssize_t i=0; i<list_len; i++) {
        PyObject *pyItem = PyList_GetItem(pyList, i);
        double value = PyFloat_AsDouble(pyItem);
        valueVector.push_back(value);
    }
    return valueVector;
}

PyObject* to_pylist(std::vector<int> &ret) {
    int ret_len = ret.size();
    PyObject *pyRetList = PyList_New(ret_len);
    for(int i=0; i<ret_len; i++) {
        PyObject *pyRetValue = PyInt_FromSsize_t(ret[i]);
        PyList_SetItem(pyRetList, i, pyRetValue);
    }
    return pyRetList;
}

PyObject* to_pytuple(int best_loc, double best_stat) {
    PyObject *pyRetTuple = PyTuple_New(2);
    PyTuple_SetItem(pyRetTuple, 0, PyInt_FromSsize_t(best_loc));
    PyTuple_SetItem(pyRetTuple, 1, PyFloat_FromDouble(best_stat));
    return pyRetTuple;
}

static PyObject* EDM_multi_wrapper(PyObject *self, PyObject *args) {
    PyObject *pyList;
    int min_size;
    double beta;
    int degree;
    PyArg_ParseTuple(args, "Oidi", &pyList, &min_size, &beta, &degree);
    std::vector<double> Z = to_vector(pyList);
    std::vector<int> ret = EDM_multi(Z, min_size, beta, degree);
    return to_pylist(ret);
}

static PyObject* EDM_percent_wrapper(PyObject *self, PyObject *args) {
    PyObject *pyList;
    int min_size;
    double percent;
    int degree;
    PyArg_ParseTuple(args, "Oidi", &pyList, &min_size, &percent, &degree);
    std::vector<double> Z = to_vector(pyList);
    std::vector<int> ret = EDM_percent(Z, min_size, percent, degree);
    return to_pylist(ret);
}

static PyObject* EDM_tail_wrapper(PyObject *self, PyObject *args) {
    PyObject *pyList;
    int min_size;
    double alpha;
    double quant;
    PyArg_ParseTuple(args, "Oidd", &pyList, &min_size, &alpha, &quant);
    std::vector<double> Z = to_vector(pyList);
    EDMResult ret = EDM_tail(Z, min_size, alpha, quant);
    return to_pytuple(ret.best_loc, ret.best_stat);
}

static PyObject* EDM_x_wrapper(PyObject *self, PyObject *args) {
    PyObject *pyList;
    int min_size;
    double alpha;
    PyArg_ParseTuple(args, "Oid", &pyList, &min_size, &alpha);
    std::vector<double> Z = to_vector(pyList);
    EDMResult ret = EDMX(Z, min_size, alpha);
    return to_pytuple(ret.best_loc, ret.best_stat);
}

static PyMethodDef edmMethods[] = {
    {"edm_multi",  EDM_multi_wrapper, METH_VARARGS, "EDM Multi"},
    {"edm_percent",  EDM_percent_wrapper, METH_VARARGS, "EDM Percent"},
    {"edm_tail",  EDM_tail_wrapper, METH_VARARGS, "EDM Tail"},
    {"edm_x",  EDM_x_wrapper, METH_VARARGS, "EDM X"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "edm",
    NULL,
    -1,
    edmMethods,
};

PyMODINIT_FUNC PyInit_edm(void) {
    (void) PyModule_Create(&moduledef);
}
