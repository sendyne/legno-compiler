import os
from enum import Enum
import util.config as config
import util.util as util
import parse as parselib

class PlotType(Enum):
    SIMULATION = "sim"
    MEASUREMENT = "meas"

class DeviceStatePathHandler:
    DEVICE_STATE_DIR = "device-state"

    def __init__(self,board,model,make_dirs=True):
        self.board = board
        self.model = model
        self.set_root_dir(DeviceStatePathHandler.DEVICE_STATE_DIR + "/%s/%s"  \
                          % (board,model))
        for path in [
                self.ROOT_DIR,
                self.MODEL_DIR,
                self.SRC_DIR,
                self.VISUALIZATIONS
        ]:
            if make_dirs:
                util.mkdir_if_dne(path)


    def get_model_file(self,block,output,loc,static_cfg,hidden_cfg,label):
        rel_path = "%s/%s/%s/" % (self.MODEL_DIR,block,static_cfg)
        util.mkdir_if_dne(rel_path)
        util.mkdir_if_dne(rel_path)
        if label.value == 'none':
            return "%s/mdl-%s-%s-%s.txt" % (rel_path,loc,output,hidden_cfg)
        else:
            return "%s/mdl-%s-%s-%s.txt" % (rel_path,loc,output,label.value)



    def get_histogram_vis(self,name,block,output,static_cfg,label):
        rel_path = "%s/%s/%s/" % (self.VISUALIZATIONS,block,static_cfg)
        util.mkdir_if_dne(rel_path)
        if label.value == 'none':
            return "%s/hist-%s-%s.png" \
                % (rel_path,name,output)
        else:
            return "%s/hist-%s-%s-%s.png" \
                % (rel_path,name,output,label.value)


    def get_correctable_delta_vis(self,block,output,loc,static_cfg,hidden_cfg,label):
        rel_path = "%s/%s/%s/" % (self.VISUALIZATIONS,block,static_cfg)
        util.mkdir_if_dne(rel_path)
        if label.value == 'none':
            return "%s/%s-%s-%s-corr.png" % (rel_path,loc,output,hidden_cfg)
        else:
            return "%s/%s-%s-%s-corr.png" % (rel_path,loc,output,label.value)


    def get_delta_vis(self,block,output,loc,static_cfg,hidden_cfg,label):
        rel_path = "%s/%s/%s/" % (self.VISUALIZATIONS,block,static_cfg)
        util.mkdir_if_dne(rel_path)
        if label.value == 'none':
            return "%s/%s-%s-%s-mdl.png" % (rel_path,loc,output,hidden_cfg)
        else:
            return "%s/%s-%s-%s-mdl.png" % (rel_path,loc,output,label.value)

    def set_root_dir(self,root):
        self.ROOT_DIR = root
        self.DATABASE = self.ROOT_DIR + "/%s-%s.db" % (self.board,self.model)
        self.MODEL_DIR = self.ROOT_DIR + "/models"
        self.SRC_DIR = self.ROOT_DIR + "/models-src"
        self.VISUALIZATIONS = self.ROOT_DIR + "/viz"

class PathHandler:

    def __init__(self,subset,prog,make_dirs=True):
        self.set_root_dir(subset,prog)
        for path in [
                self.ROOT_DIR,
                self.PROG_DIR,
                self.LGRAPH_ADP_DIR,
                self.LGRAPH_ADP_DIAG_DIR,
                self.LSCALE_ADP_DIR,
                self.LSCALE_ADP_DIAG_DIR,
                self.MEAS_WAVEFORM_FILE_DIR,
                self.PLOT_DIR,
                self.TIME_DIR
        ]:
          if make_dirs:
              util.mkdir_if_dne(path)

        self._subset = subset
        self._prog = prog

    @property
    def subset(self):
        return self._subset

    @staticmethod
    def path_to_args(dirname):
        paths =[ "%s/legno/{subset:w}/{prog:w}" \
                % config.OUTPUT_PATH, \
                 "%s/legno/{subset:w}/{prog:w}/{dir:w}" \
                % config.OUTPUT_PATH \
        ]
        for path in paths:
            args = parselib.parse(path,dirname)
            if not args is None:
                return dict(args.named.items())

        raise Exception("cannot parse path: %s" % dirname)

    def set_root_dir(self,name,bmark):
        self.ROOT_DIR = "%s/legno/%s" % (config.OUTPUT_PATH,name)
        self.PROG_DIR = self.ROOT_DIR + ("/%s" % bmark)
        self.LGRAPH_ADP_DIR = self.PROG_DIR + "/lgraph-adp"
        self.LGRAPH_ADP_DIAG_DIR = self.PROG_DIR + "/lgraph-diag"
        self.LSCALE_ADP_DIR = self.PROG_DIR + "/lscale-adp"
        self.LSCALE_ADP_DIAG_DIR = self.PROG_DIR + "/lscale-diag"
        self.GRENDEL_FILE_DIR = self.PROG_DIR + "/grendel"
        self.PLOT_DIR = self.PROG_DIR + "/plots"
        self.MEAS_WAVEFORM_FILE_DIR = self.PROG_DIR + "/out-waveform"
        self.TIME_DIR = self.PROG_DIR + "/times"
        self.REF_SIM_DIR = self.PROG_DIR + "/sim/ref"
        self.ADP_SIM_DIR = self.PROG_DIR + "/sim/adp"

    def adp_sim_plot(self,plot_type,prog,lgraph,lscale,opt,model):
        assert(isinstance(plot_type,PlotType))
        filepath = "{path}/{plot_type}"
        cdir = filepath.format(path=self.PLOT_DIR, \
                               plot_type=plot_type.value)
        util.mkdir_if_dne(cdir)
        filepat = "{path}/{prog}_{lgraph}_{lscale}_{opt}_{model}.png"
        cfilename = filepat.format(path=cdir, \
                                   prog=prog, \
                                   lgraph=lgraph, \
                                   lscale=lscale, \
                                   opt=opt, model=model)
        return cfilename

    def time_file(self,name):
        path = "{path}/{name}.txt"
        return path.format(path=self.TIME_DIR, \
                           name=name)



    def lgraph_adp_diagram_file(self,graph_index):
        path = "{path}/{prog}_g{lgraph}.gv"
        return path.format(path=self.LGRAPH_ADP_DIAG_DIR,
                           prog=self._prog,
                           lgraph=graph_index)


    def lgraph_adp_file(self,graph_index):
        path = "{path}/{prog}_g{lgraph}.adp"
        return path.format(path=self.LGRAPH_ADP_DIR,
                           prog=self._prog,
                           lgraph=graph_index)


    def lscale_adp_diagram_file(self,graph_index,scale_index,model,opt,calib_obj=None):
        model_tag = model
        if not calib_obj is None:
            model_tag += "_%s" % calib_obj
        path ="{path}/{prog}_g{lgraph}_s{lscale}_{model}_{opt}.gv"
        filepath = path.format(path=self.LSCALE_ADP_DIAG_DIR, \
                               prog=self._prog, \
                               lgraph=graph_index, \
                               lscale=scale_index, \
                               model=model_tag, \
                               opt=opt)

 
    def lscale_adp_file(self,graph_index,scale_index,model,opt,calib_obj,phys_db):
        path ="{path}/{prog}_g{lgraph}_s{lscale}_{model}_{opt}_{calib_obj}_{physdb}.adp"
        filepath = path.format(path=self.LSCALE_ADP_DIR, \
                               prog=self._prog, \
                               lgraph=graph_index, \
                               lscale=scale_index, \
                               model=model, \
                               calib_obj=calib_obj, \
                               physdb=phys_db, \
                               opt=opt)

        return filepath

    def lscale_adp_diagram_file(self,graph_index,scale_index,model,opt,calib_obj,phys_db):
        path = "{path}/{prog}_g{lgraph}_s{lscale}_{model}_{opt}_{calib_obj}_{physdb}.dot"
        return path.format(path=self.LSCALE_ADP_DIAG_DIR,
                           prog=self._prog, \
                           lgraph=graph_index, \
                           lscale=scale_index, \
                           model=model, \
                           calib_obj=calib_obj, \
                           physdb=phys_db, \
                           opt=opt)



    def measured_waveform_file(self,graph_index,scale_index, \
                               model,opt,\
                               calib_obj, phys_db, \
                               variable,trial):
        path = "{path}/{prog}_g{lgraph}_s{lscale}_{model}_{calib_obj}_{opt}"
        path += "_{var}_{trial}.json"

        return path.format(path=self.MEAS_WAVEFORM_FILE_DIR,
                           prog=self._prog,
                           lgraph=graph_index,
                           lscale=scale_index,
                           model=model,
                           calib_obj=calib_obj, \
                           physdb=phys_db, \
                           opt=opt,
                           var=variable,
                           trial=trial)

    def waveform_plot_file(self,graph_index,scale_index, \
                           model,opt,\
                           calib_obj, phys_db, \
                           variable,trial, \
                           plot):
        filepath = "{path}/{plot_type}"
        cdir = filepath.format(path=self.PLOT_DIR, \
                               plot_type='wave')
        util.mkdir_if_dne(cdir)

        path = "{path}/{prog}_g{lgraph}_s{lscale}_{model}_{calib_obj}_{opt}"
        path += "_{var}_{trial}_{plot}.pdf"

        return path.format(path=cdir,
                           prog=self._prog,
                           lgraph=graph_index,
                           lscale=scale_index,
                           model=model,
                           calib_obj=calib_obj, \
                           physdb=phys_db, \
                           opt=opt,
                           var=variable,
                           trial=trial, \
                           plot=plot)




    def measured_waveform_dir(self):
      return self.MEAS_WAVEFORM_FILE_DIR

    def grendel_file_dir(self):
        return self.GRENDEL_FILE_DIR


    def lscale_adp_dir(self):
        return self.LSCALE_ADP_DIR


    def lgraph_adp_dir(self):
        return self.LGRAPH_ADP_DIR

    def has_file(self,filepath):
        if not os.path.exists(filepath):
          return False

        directory,filename = os.path.split(filepath)
        return filename in os.listdir(directory)
