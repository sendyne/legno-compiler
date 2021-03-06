import runtime.models.exp_delta_model as exp_delta_model_lib
import util.paths as pathlib
import hwlib.adp as adplib
import os
import json

def get_base_name(board,blk,loc,cfg):
    addr = "_".join(map(lambda i: str(i), loc.address))
    mode = "_".join(map(lambda m: str(m), cfg.mode))
    return "%s-%s-%s-%s" % (board.model_number,blk.name,addr,mode)

def get_model(board,blk,loc,cfg):
    return '%s' % (get_base_name(board,blk,loc,cfg))

def get_adp(board,blk,loc,cfg):
    return '%s.adp' % (get_base_name(board,blk,loc,cfg))

def run_command(cmd):
    code = os.system(cmd)
    if code != 0:
        raise Exception("command failed. <code=%s>" % code)

def generate_adp(board,blk,loc,cfg):
    adp_file = get_adp(board,blk,loc,cfg)

    new_adp = adplib.ADP()
    new_adp.add_instance(blk,loc)
    blkcfg = new_adp.configs.get(blk.name,loc)
    blkcfg.set_config(cfg)

    with open(adp_file,'w') as fh:
        text = json.dumps(new_adp.to_json())
        fh.write(text)

    return adp_file

def database_is_homogenous(board):
    modes = []
    locs = []
    outputs = []
    blocks = []
    for model in exp_delta_model_lib.get_all(board):
        modes.append(model.config.mode)
        locs.append(model.loc)
        outputs.append(model.output.name)
        blocks.append(model.block.name)

    # test that the data is homogenous
    if len(set(locs)) != 1:
        print("[not homogenous] # locs=%d" % (len(set(locs))))
        return False

    # test that the data is homogenous
    if len(set(modes)) != 1:
        print("[not homogenous] # modes=%d" % (len(set(modes))))
        return False

    if len(set(outputs)) != 1:
        print("[not homogenous] # outputs=%d" % (len(set(outputs))))
        return False

    if len(set(blocks)) != 1:
        print("[not homogenous] # blocks=%d" % (len(set(blocks))))
        return False

    return True



def homogenous_database_get_block_info(board):
    assert(database_is_homogenous(board))
    for model in exp_delta_model_lib.get_all(board):
        return model.block,model.loc,model.output,model.config


def profile(board,char_board,calib_obj):
    CMD = "python3 grendel.py prof --grid-size 15 --model-number {model} {adp} {calib_obj}"

    block,loc,_,config = homogenous_database_get_block_info(char_board)

    filename = generate_adp(char_board,block,loc,config)

    cmd = CMD.format(model=board.model_number, \
                     adp=filename, \
                     calib_obj=calib_obj.value)
    run_command(cmd)

def fit_delta_models(board):
    CMD = "python3 grendel.py mkdeltas --model-number {model}"
    cmd = CMD.format(model=board.model_number)
    run_command(cmd)


def get_block_databases(model_number):
    for root,dirs,files in os.walk(pathlib.DeviceStatePathHandler.DEVICE_STATE_DIR):
        for filename in files:
            if not filename.endswith('.db'):
                continue
            if filename.startswith('hcdcv2-%s-' % model_number):
                dbname = filename.split('hcdcv2-')[1].split('.db')[0]
                yield dbname
