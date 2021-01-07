
PATH_TO_CIL = /home/zephaniah/Documents/Zephaniahs_Research/cil#/home/zephaniah/.opam/4.10.0/lib/cil #/home/weimerw/src/cil
PATH_TO_CIL_LIBS	= $(PATH_TO_CIL)/lib/cil
PATH_TO_FRONTC_LIBS	= $(PATH_TO_CIL)/_build/src/frontc
PATH_TO_OCAMLUTIL_LIBS	= $(PATH_TO_CIL)/_build/src/ocamlutil
PATH_TO_EXT_LIBS_1	= $(PATH_TO_CIL)/_build/src/ext
PATH_TO_EXT_LIBS_2	= $(PATH_TO_CIL)/_build/src/ext/simplify
PATH_TO_OCAML = /home/zeph/ocml/bin
OCAMLOPT  = $(PATH_TO_OCAML)/ocamlopt -I $(PATH_TO_CIL_LIBS) -I $(PATH_TO_FRONTC_LIBS) -I $(PATH_TO_OCAMLUTIL_LIBS) -I $(PATH_TO_EXT_LIBS_1) -I $(PATH_TO_EXT_LIBS_2)

all: cilcfgformula

cilcfgformula: cilcfgformula.ml
	$(OCAMLOPT) -o cilcfgformula str.cmxa unix.cmxa nums.cmxa /home/zephaniah/.opam/4.10.0/lib/findlib/findlib.cmxa dynlink.cmxa cil.cmxa simplify.cmxa cilcfgformula.ml

	#$(OCAMLOPT) -o cilcfgformula str.cmxa unix.cmxa nums.cmxa findlib/findlib.cmxa dynlink.cmxa cil.cmxa simplify.cmxa cilcfgformula.ml

clean:
	$(RM) cilcfgformula *.cm? *.o a.out
