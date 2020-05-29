import hwlib2.hcdc.llstructs as llstructs
import hwlib2.hcdc.llenums as llenums
import lab_bench.grendel_util as grendel_util


def make_block_loc(blk,loc):
  assert(len(loc) == 4)
  addr = loc.address
  loc = {
    'block':llenums.BlockType(blk.name).name,
    'chip':addr[0],
    'tile':addr[1],
    'slice':addr[2],
    'idx':addr[3]
  }
  return llstructs.block_loc_t(),loc

def make_port_loc(blk,loc,port):
  assert(isinstance(ctx,BuildContext))
  assert(len(loc) == 4)
  loc = { \
          'inst':build_block_loc(blk,loc), \
          'port':PortType(port).name}

  return port_loc_t(),loc


def make_circ_cmd(cmdtype,cmddata):
    assert(isinstance(cmdtype,llenums.CircCmdType))
    cmd_d = {
        "cmd_type": llenums.CmdType.CIRC_CMD.name,
        "cmd_data":{
            "circ_cmd": {
                'circ_cmd_type': cmdtype.name,
                'circ_cmd_data': {cmdtype.value:cmddata}
            }
        }
    }
    return llstructs.cmd_t(),cmd_d

def _unpack_response(resp):
  if isinstance(resp,grendel_util.HeaderArduinoResponse):
    if resp.num_args == 1:
      return _unpack_response(resp.data(0))
    elif resp.num_args == 0:
      return resp.message
    else:
      raise Exception("only can handle responses with one or zero data segments")

  elif isinstance(resp,grendel_util.DataArduinoResponse):
    assert(isinstance(resp.value,grendel_util.PayloadArduinoResponse))
    return _unpack_response(resp.value)

  elif isinstance(resp,grendel_util.PayloadArduinoResponse):
    payload_type = llstructs.parse(llstructs.response_type_t(), \
                                   bytes([resp.payload_type]))
    payload_result = None
    if payload_type == llenums.ResponseType.BLOCK_STATE.value:
      payload_result = llstructs.parse(llstructs.state_t(), \
                                       resp.values)
    elif payload_type == llenums.ResponseType.PROFILE_RESULT.value:
      payload_result = llstructs.parse(llstructs.profile_result_t(), \
                                       resp.array)

    return payload_result


def profile(runtime,blk,loc,cfg,output_port,in0=0.0,in1=0.0):
    state_t = {blk.name:blk.state.concretize(cfg,loc)}
    loc_t,loc_d = make_block_loc(blk,loc)
    values = [0.0]*2
    values[llenums.PortType.IN0.to_code()] = in0
    values[llenums.PortType.IN1.to_code()] = in1
    profile_data = {"method": llenums.ProfileOpType.INPUT_OUTPUT.name, \
                    "inst": loc_d,
                    "in_vals": values, \
                    "state":state_t,
                    "output":output_port.name}

    cmd_t, cmd_data = make_circ_cmd(llenums.CircCmdType.PROFILE,
                             profile_data)
    cmd = cmd_t.build(cmd_data,debug=True)

    runtime.execute(cmd)
    resp = _unpack_response(runtime.result())
    return resp

def set_state(runtime,blk,loc,cfg):
    state_t = {blk.name:blk.state.concretize(cfg,loc)}
    loc_t,loc_d = make_block_loc(blk,loc)
    state_data = {'inst':loc_d, 'state':state_t}
    cmd_t,cmd_data = make_circ_cmd(llenums.CircCmdType.SET_STATE, \
                                       state_data)
    cmd = cmd_t.build(cmd_data,debug=True)
    runtime.execute(cmd)
    return _unpack_response(runtime.result())

def disable(runtime,blk,loc):
    loc_t,loc_d = make_block_loc(blk,loc)
    cmd_t,cmd_d = make_circ_cmd(llenums.CircCmdType.DISABLE,  \
                                          {'inst':loc_d})
    cmd = cmd_t.build(cmd_d,debug=True)
    runtime.execute(cmd)
    return _unpack_response(runtime.result())
