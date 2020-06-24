import hwlib.device as devlib
import hwlib.block as blocklib
import hwlib.adp as adplib
import hwlib.physdb as physdb
import hwlib.hcdc.llenums as llenums

import phys_model.phys_util as phys_util
import ops.generic_op as genoplib
import ops.lambda_op as lambdoplib
import itertools

PROG = '''
from scipy.optimize import curve_fit
import numpy as np

def func(x,{free_vars}):
  return {expr}


xdata = {x_dataset}


ydata = {y_dataset}


popt,pcov = curve_fit(func,xdata,ydata)
lbls = [{free_var_array}]
assigns = dict(zip(lbls,popt))
perr = np.sqrt(np.diag(pcov))
'''

def fit_delta_model(phys,data):
  inputs = data['inputs']
  meas_output = data['meas_mean']
  n_inputs = len(inputs.keys())
  #if phys.model.complete:
  #  return False

  model = phys.model.delta_model
  # for building expression
  repl = {}
  dataset = [None]*n_inputs
  for idx,bound_var in enumerate(inputs.keys()):
    assert(len(inputs[bound_var]) == len(meas_output))
    dataset[idx] = inputs[bound_var]
    repl[bound_var] = genoplib.Var("x[%d]" % idx)

  expr = model.relation.substitute(repl)
  _,pyexpr = lambdoplib.to_python(expr)
  fields = {
    'free_vars':",".join(model.params),
    'free_var_array':",".join(map(lambda p: '"%s"' % p, model.params)),
    'x_dataset': str(dataset),
    'y_dataset': str(meas_output),
    'expr':pyexpr
  }
  snippet = PROG.format(**fields)
  loc = {}
  exec(snippet,globals(),loc)
  parameters = loc['lbls']
  parameter_values = loc['popt']
  parameter_stdevs = loc['perr']
  phys.model.clear()
  for idx,par in enumerate(parameters):
    val = parameter_values[idx]
    phys.model.bind(par,val)

  sumsq = phys.model.error(inputs,meas_output)
  phys.model.cost = sumsq
  phys.update()

def analyze_physical_output(phys_output):
  def valid_data_point(dataset,method,idx):
    return dataset.meas_status[idx] == llenums.ProfileStatus.SUCCESS \
      and dataset.meas_method[idx] == method

  delta_model = phys_output.model.delta_model
  dataset = phys_output.dataset
  indices = list(filter(lambda idx: valid_data_point(dataset, \
                                                  llenums.ProfileOpType.INPUT_OUTPUT, \
                                                  idx), range(0,dataset.size)))

  meas = phys_util.get_subarray(dataset.meas_mean,indices)
  meas_stdev = phys_util.get_subarray(dataset.meas_stdev,indices)
  ref = phys_util.get_subarray(dataset.output, indices)
  fit_delta_model(phys_output,dataset.get_data(llenums.ProfileStatus.SUCCESS, \
                                               llenums.ProfileOpType.INPUT_OUTPUT))