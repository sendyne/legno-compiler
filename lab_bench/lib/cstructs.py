from lab_bench.lib.enums import BlockType,ExpCmdType,CircCmdType,CmdType
from hwlib.hcdc import enums as specdata
import lab_bench.lib.chipcmd.data as chipdata
import construct as cstruct


def experiment_cmd_type_t():
    kwargs = {
        ExpCmdType.RESET.name:0,
        ExpCmdType.USE_ANALOG_CHIP.name:1,
        ExpCmdType.SET_SIM_TIME.name:2,
        ExpCmdType.USE_OSC.name:3,
        ExpCmdType.RUN.name:4,
    }
    return cstruct.Enum(cstruct.Int16ul,**kwargs)


def circ_cmd_type():
    kwargs = {
        CircCmdType.USE_DAC.name:0,
        CircCmdType.USE_MULT.name:1,
        CircCmdType.USE_FANOUT.name:2,
        CircCmdType.USE_INTEG.name:3,
        CircCmdType.USE_LUT.name:4,
        CircCmdType.USE_ADC.name:5,
        CircCmdType.DISABLE_DAC.name:6,
        CircCmdType.DISABLE_MULT.name:7,
        CircCmdType.DISABLE_INTEG.name:8,
        CircCmdType.DISABLE_FANOUT.name:9,
        CircCmdType.DISABLE_LUT.name:10,
        CircCmdType.DISABLE_ADC.name:11,
        CircCmdType.CONNECT.name:12,
        CircCmdType.BREAK.name:13,
        CircCmdType.GET_INTEG_STATUS.name:14,
        CircCmdType.GET_ADC_STATUS.name:15,
        CircCmdType.WRITE_LUT.name:16,
        CircCmdType.CALIBRATE.name:17,
        CircCmdType.TUNE.name:18,
        CircCmdType.GET_STATE.name:19,
        CircCmdType.SET_STATE.name:20,
        CircCmdType.DEFAULTS.name:21,
        CircCmdType.PROFILE.name:22
    }
    return cstruct.Enum(cstruct.Int24ul,
                        **kwargs)

'''


def circ_use_integ_t():
    return cstruct.Struct(
        "loc" / circ_loc_t(),
        "inv" / cstruct.Int8ul,
        'in_range' / cstruct.Int8ul,
        'out_range' / cstruct.Int8ul,
        'debug' / cstruct.Int8ul,
        cstruct.Padding(1),
        "value" / cstruct.Float32l
    )

def circ_use_dac_t():
    return cstruct.Struct(
        "loc" / circ_loc_t(),
        "source" / cstruct.Int8ul,
        "inv" / cstruct.Int8ul,
        "out_range" / cstruct.Int8ul,
        cstruct.Padding(2),
        "value" / cstruct.Float32l
    )

def circ_use_mult_t():
    return cstruct.Struct(
        "loc" / circ_loc_idx1_t(),
        "use_coeff" / bool_t(),
        cstruct.Padding(1),
        "in0_range" / cstruct.Int8ul,
        "in1_range" / cstruct.Int8ul,
        "out_range" / cstruct.Int8ul,
        cstruct.Padding(3),
        "coeff" / cstruct.Float32l
    )

def circ_write_lut_t():
    return cstruct.Struct(
        "loc" / circ_loc_t(),
        "offset" / cstruct.Int8ul,
        "n" / cstruct.Int8ul
    )


def circ_use_lut_t():
    return cstruct.Struct(
        "loc" / circ_loc_t(),
        "source" / cstruct.Int8ul
    )

def circ_use_adc_t():
    return cstruct.Struct(
        "loc" / circ_loc_t(),
        "in_range" / cstruct.Int8ul
    )

def circ_use_fanout_t():
    return cstruct.Struct(
        "loc" / circ_loc_idx1_t(),
        "inv" / cstruct.Array(3,cstruct.Int8ul),
        "in_range" / cstruct.Int8ul,
        "third" / cstruct.Int8ul
    )
'''

def circ_connection_t():
    return cstruct.Struct(
        "src_blk" / block_type_t(),
        "src_loc" / circ_loc_idx2_t(),
        cstruct.Padding(1),
        "dst_blk" / block_type_t(),
        "dst_loc" / circ_loc_idx2_t()
    )


def circ_state_t():
    return cstruct.Struct(
        "blk" / block_type_t(),
        "loc" / circ_loc_idx1_t(),
        "data" / cstruct.Array(64,cstruct.Int8ul)
    )


def circ_calib_t():
    return cstruct.Struct(
        "calib_obj" / cstruct.Int8ul,
        cstruct.Padding(1),
        "blk" / block_type_t(),
        "loc" / circ_loc_idx1_t()
    )

def circ_prof_t():
    return cstruct.Struct(
        "mode" / cstruct.Int8ul,
        cstruct.Padding(1),
        "blk" / block_type_t(),
        "loc" / circ_loc_idx1_t(),
        "in0" / cstruct.Float32l,
        "in1" / cstruct.Float32l
    )

def circ_cmd_data():
    return cstruct.Union(None,
                         fanout=circ_use_fanout_t(),
                         integ=circ_use_integ_t(),
                         mult=circ_use_mult_t(),
                         dac=circ_use_dac_t(),
                         lut=circ_use_lut_t(),
                         write_lut=circ_write_lut_t(),
                         adc=circ_use_adc_t(),
                         conn=circ_connection_t(),
                         circ_loc=circ_loc_t(),
                         circ_loc_idx1=circ_loc_idx1_t(),
                         state=circ_state_t(),
                         calib=circ_calib_t(),
                         prof=circ_prof_t()
    )

def circ_cmd_t():
        return cstruct.Struct(
            "type" / circ_cmd_type(),
            cstruct.Padding(1),
            "data" / circ_cmd_data()
        )

def exp_cmd_args_t():
    return cstruct.Union(None,
        floats=cstruct.Array(3,cstruct.Float32l),
        ints=cstruct.Array(3,cstruct.Int32ul)
    )

def experiment_cmd_t():
        typ = experiment_cmd_type_t()
        return cstruct.AlignedStruct(4,
            "type" / typ,
            "args" / exp_cmd_args_t()
        )

def cmd_type_t():
    kwargs = {
        CmdType.CIRC_CMD.name:0,
        CmdType.EXPERIMENT_CMD.name:1,
        CmdType.FLUSH_CMD.name:2
    }
    return cstruct.Enum(cstruct.Int8ul,**kwargs)

def cmd_data_t():
    return cstruct.Union(None,
        "exp_cmd"/ experiment_cmd_t(),
        "circ_cmd" / circ_cmd_t(),
        "flush_cmd" / cstruct.Int8ul
    )


def cmd_t():
    return cstruct.Struct(
        "test" / cstruct.Int8ul,
        "type" / cmd_type_t(),
        cstruct.Padding(2),
        "data" / cmd_data_t(),
    )



def profile_t():
    return cstruct.Struct(
        "bias" / cstruct.Float32l,
        "noise" / cstruct.Float32l,
        "output" / cstruct.Float32l,
        "input0" / cstruct.Float32l,
        "input1" / cstruct.Float32l,
        "port" / cstruct.Int8ul,
        "mode" / cstruct.Int8ul
    )