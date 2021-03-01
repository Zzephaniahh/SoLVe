from pysmt.smtlib.parser import SmtLibParser
from six.moves import cStringIO # Py2-Py3 Compatibility



F = open('locks_test.vmt','r') 
# print(=F.read())

# DEMO_SMTLIB=\
# """
# (set-logic QF_LIA)
# (declare-fun p () Int)
# (declare-fun q () Int)
# (declare-fun x () Bool)
# (declare-fun y () Bool)
# (define-fun .def_1 () Bool (! (and x y) :cost 1))
# (assert (=> x (> p q)))
# (check-sat)
# (push)
# (assert (=> y (> q p)))
# (check-sat)
# (assert .def_1)
# (check-sat)
# (pop)
# (check-sat)
# """

parser = SmtLibParser()

script = parser.get_script(cStringIO(F.read()))
fomr = script.get_last_formula()
# print(script)
ann = script.annotations
for form in script:
    print(form.annotations)





class PDR(object):
    def __init__(self, system):
        self.system = system
        self.frames = [system.init]
        self.solver = Solver()
        self.prime_map = dict([(v, next_var(v)) for v in self.system.variables])

    def check_property(self, prop):
        """Property Directed Reachability approach without optimizations."""
        print("Checking property %s..." % prop)

        while True:
            cube = self.get_bad_state(prop)
            if cube is not None:
                # Blocking phase of a bad state
                if self.recursive_block(cube):
                    print("--> Bug found at step %d" % (len(self.frames)))
                    break
                else:
                    print("   [PDR] Cube blocked '%s'" % str(cube))
            else:
                # Checking if the last two frames are equivalent i.e., are inductive
                if self.inductive():
                    print("--> The system is safe!")
                    break
                else:
                    print("   [PDR] Adding frame %d..." % (len(self.frames)))
                    self.frames.append(TRUE())

    def get_bad_state(self, prop):
        """Extracts a reachable state that intersects the negation
        of the property and the last current frame"""
        return self.solve(And(self.frames[-1], Not(prop)))

    def solve(self, formula):
        """Provides a satisfiable assignment to the state variables that are consistent with the input formula"""
        if self.solver.solve([formula]):
            return And([EqualsOrIff(v, self.solver.get_value(v)) for v in self.system.variables])
        return None

    def recursive_block(self, cube):
        """Blocks the cube at each frame, if possible.
        Returns True if the cube cannot be blocked.
        """
        for i in range(len(self.frames)-1, 0, -1):
            cubeprime = cube.substitute(dict([(v, next_var(v)) for v in self.system.variables]))
            cubepre = self.solve(And(self.frames[i-1], self.system.trans, Not(cube), cubeprime))
            if cubepre is None:
                for j in range(1, i+1):
                    self.frames[j] = And(self.frames[j], Not(cube))
                return False
            cube = cubepre
        return True

    def inductive(self):
        """Checks if last two frames are equivalent """
        if len(self.frames) > 1 and \
           self.solve(Not(EqualsOrIff(self.frames[-1], self.frames[-2]))) is None:
            return True
        return False


def main():
    pass
    # example = counter(4)

    # pdr = PDR(example[0])

    # for prop in example[1]:
    #     pdr.check_property(prop)
    #     print("")

if __name__ == "__main__":
    main()