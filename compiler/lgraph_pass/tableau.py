import hwlib.block as blocklib
import compiler.lgraph_pass.unify as unifylib
import ops.base_op as oplib
from compiler.lgraph_pass.vadp import * 

class DSVar:
  def __init__(self,var):
    self.var = var

  def __repr__(self):
    return self.var


class Goal:

  def __init__(self,var,typ,expr):
    assert(isinstance(var,PortVar) or \
           isinstance(var,LawVar) or \
           isinstance(var,DSVar))
    assert(isinstance(expr, oplib.Op))
    self.variable = var
    self.type = typ
    self.expr = expr

  def equals(self,g2):
    return str(self) == str(g2)

  def __repr__(self):
    return "goal %s : %s = %s" % (self.variable,self.type,self.expr)

class PortRelation:

  def __init__(self,block,idx,modes,port,expr):
    self.block = block
    self.ident = idx
    self.modes = modes
    self.port = port
    self.expr = expr
    self.cstrs = dict(map(lambda v: (v,unifylib.UnifyConstraint.NONE), \
                          self.expr.vars()))
    for var in self.cstrs.keys():
      if self.block.inputs.has(var):
        self.cstrs[var] = unifylib.UnifyConstraint.NOT_CONSTANT

      if self.block.data.has(var) and \
         self.block.data[var].type == blocklib.BlockDataType.CONST:
        self.cstrs[var] = unifylib.UnifyConstraint.CONSTANT

      elif self.block.data.has(var) and \
         self.block.data[var].type == blocklib.BlockDataType.EXPR:
        self.cstrs[var] = unifylib.UnifyConstraint.FUNCTION

  def equals(self,g2):
    return str(self) == str(g2)

  def copy(self):
    rel = PortRelation(self.block, \
                       self.ident, \
                       self.modes, \
                       self.port, \
                       self.expr)
    rel.cstrs = dict(self.cstrs)
    return rel

  def same_block(self,rel):
    if not isinstance(rel,PortRelation):
      return False

    return self.block.name == rel.block.name and \
      self.ident == rel.ident

  def typecheck(self,goal):
    assert(isinstance(goal,Goal))
    if goal.type is None:
      return True
    output_type = self.port.type
    return goal.type == output_type

  def __repr__(self):
    output_type = self.port.type
    cstrs = ",".join(map(lambda tup: "%s=%s" % (tup[0],tup[1].value), \
                                      self.cstrs.items()))
    return "rel %s(%d,%s) : %s = %s [%s]" % (self.block.name,self.ident, \
                                             self.port.name, \
                                             self.port.type,self.expr, \
                                             cstrs)


class PhysicsLawRelation:

  def __init__(self,law,lawvar,mode,expr):
    assert(isinstance(lawvar, LawVar))
    assert(lawvar.law == law.name)
    self.law = law
    self.target = lawvar
    self.mode = mode
    self.expr = expr


  def same_usage(self,v):
    assert(isinstance(v,PhysicsLawRelation))
    return self.target.same_usage(v.target)

  @property
  def name(self):
    return self.law

  def equals(self,g2):
    return str(self) == str(g2)

  def copy(self):
    rel = PhysicsLawRelation(self.law, \
                             self.target.copy(),
                             self.mode, \
                             self.expr)
    return rel
  def typecheck(self,goal):
    assert(isinstance(goal,Goal))
    if goal.type is None:
      return True
    return self.law.virt.typecheck(goal.type)

  def decl_var(self,var_name,typ):
    assert(var_name in self.variables)
    if not self.var_types[var_name] is None:
      assert(self.var_types[var_name] == typ)
    self.var_types[var_name] = typ

  def __repr__(self):
    return "%s = %s @ %s" % (self.target,self.mode,self.expr)

class Tableau:

  def __init__(self):
    self.goals = []
    self.relations = []
    self.vadp = []

  def add_stmt(self,vadp_st):
    assert(isinstance(vadp_st,VADPStmt))
    self.vadp.append(vadp_st)

  def copy(self):
    tab = Tableau()
    tab.goals = list(self.goals)
    tab.relations = list(map(lambda rel: rel.copy(), \
                             self.relations))
    tab.vadp = list(self.vadp)
    return tab

  def success(self):
    return len(self.goals) == 0

  def remove_relation(self,relation):
    assert(isinstance(relation,PortRelation) or \
           isinstance(relation,LawRelation))
    g = list(filter(lambda g: not relation.equals(g), \
                    self.relations))
    assert(len(g) >= len(self.relations)-1)
    self.relations = g


  def remove_goal(self,goal):
    assert(isinstance(goal,Goal))
    g = list(filter(lambda g: not goal.equals(g), \
                    self.goals))
    assert(len(g) >= len(self.goals)-1)
    self.goals = g


  def add_goal(self,goal):
    assert(isinstance(goal,Goal))
    self.goals.append(goal)

  def add_relation(self,rel):
    assert(isinstance(rel,PortRelation) or \
           isinstance(rel,PhysicsLawRelation))
    self.relations.append(rel)

  def typecheck(self,goal):
    if goal.typ is None:
      return True
    return goal.type == self.type

  def __repr__(self):
    st = "<<< GOALS >>>\n"
    for goal in self.goals:
      st += "%s\n" % goal

    st += "<<< RELATIONS >>>\n"
    for rel in self.relations:
      st += "%s\n" % rel

    st += "<<< VADP >>>\n"
    for stmt in self.vadp:
      st += "%s\n" % stmt


    return st



