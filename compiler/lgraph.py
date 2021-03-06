import itertools

import ops.opparse as parser
import random
import math
import logging
#import compiler.lgraph_pass.route as lgraph_route
#from compiler.lgraph_pass.rules import get_rules
#import compiler.lgraph_pass.to_abs_op as lgraphlib_aop
#import compiler.lgraph_pass.to_abs_circ as lgraphlib_acirc
#import compiler.lgraph_pass.make_fanouts as lgraphlib_mkfan
#import compiler.lgraph_pass.util as lgraphlib_util
#import hwlib.abs as acirc
#import hwlib.props as prop
#from hwlib.config import Labels
#import ops.aop as aop

import hwlib.block as blocklib
import compiler.lgraph_pass.route as routelib
import compiler.lgraph_pass.assemble as asmlib
import compiler.lgraph_pass.synth as synthlib
import compiler.lgraph_pass.rule as rulelib
import compiler.lgraph_pass.vadp as vadplib
from compiler.lgraph_pass.rules.kirch import KirchhoffRule
from compiler.lgraph_pass.rules.lutfuse import FuseLUTRule
from compiler.lgraph_pass.rules.flip import FlipSignRule
import numpy as np


def get_laws(dev):
    return [KirchhoffRule(), FuseLUTRule(dev), FlipSignRule()]

# TODO, always choose minimal fragment combination

def score_fragment(frag):
    score = 0
    for stmt in frag:
        if isinstance(stmt,vadplib.VADPConfig):
            score += 1
    return score

# combines the fragments, returns circuits from best to worst
def combine_fragments(frags):
    def mkfrag(fs,indices):
        # make a set of fragment selections from the selected indices
        print(indices)
        return dict(map(lambda tup: (tup[0], tup[1][indices[tup[0]]]), \
                 fs.items()))

    variables = list(frags.keys())
    sorted_frags = {}
    curr_frags = {}
    for v,frags in frags.items():
        indices = np.argsort(list(map(lambda f: score_fragment(f), frags)))
        sorted_frags[v] = list(map(lambda idx: frags[idx], indices)) 
        curr_frags[v] = 0

    has_frag = True
    while has_frag:
        yield mkfrag(sorted_frags,curr_frags)
        best_score_diff = None
        best_frag = None
        for v,idx in curr_frags.items():
            frags = sorted_frags[v]
            # if we can select the next fragment
            if idx+1 < len(frags):
                # if the score increase is better than what we have now
                score_diff = score_fragment(frags[idx+1]) - score_fragment(frags[idx])
                if best_score_diff is None or \
                   best_score_diff > score_diff:
                    best_score_diff = score_diff
                    best_frag = v

        if best_score_diff is None:
            has_frag = False
        else:
            curr_frags[best_frag] += 1




def compile(board,prob,
            vadp_fragments=100, \
            synth_depth=12, \
            asm_frags=10, \
            vadps=1, \
            adps=1, \
            routes=1):

    fragments = dict(map(lambda v: (v,[]), prob.variables()))
    compute_blocks = list(filter(lambda blk: \
                              blk.type == blocklib.BlockType.COMPUTE, \
                              board.blocks))

    # perform synthesis
    laws = get_laws(board)
    fragments = {}
    for variable in prob.variables():
        fragments[variable] = []
        expr = prob.binding(variable)
        print("> SYNTH %s = %s" % (variable,expr))
        for vadp in synthlib.search(board, \
                                    compute_blocks,laws,variable,expr, \
                                    depth=synth_depth):
            if len(fragments[variable]) >= vadp_fragments:
                break
            fragments[variable].append(vadp)

        print("VAR %s: %d fragments"  \
              % (variable,len(fragments[variable])))
        if len(fragments[variable]) == 0:
            raise Exception("could not synthesize any fragments for <%s>" % variable)

    print("> assembling circuit")
    # insert copier blocks when necessary
    assemble_blocks = list(filter(lambda blk: \
                                  blk.type == blocklib.BlockType.ASSEMBLE, \
                                  board.blocks))

    circuit = {}
    block_counts = {}
    vadp_circuits = []

    for circuit in combine_fragments(fragments):
        if len(vadp_circuits) >= vadps:
            break

        for circ in asmlib.assemble(assemble_blocks,circuit, \
                                    n_asm_frags=asm_frags):
            vadp_circuits.append(circ)
            if len(vadp_circuits) >= vadps:
                break


    print("> routing circuit")
    adp_circuits = []
    for circ in vadp_circuits:
        for vadp in routelib.route(board,circ):
            adp = vadplib.to_adp(vadp)
            adp_circuits.append(adp)
            yield adp
            if len(adp_circuits) > adps:
                break
