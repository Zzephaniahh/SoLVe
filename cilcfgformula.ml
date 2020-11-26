open Cil


(*****************************************************************************
 * A transformation to make every function call end its statement. So
 * { x=1; Foo(); y=1; }
 * becomes at least:
 * { { x=1; Foo(); }
 *   { y=1; } }
 * But probably more like:
 * { { x=1; } { Foo(); } { y=1; } }
 ****************************************************************************)
let rec contains_call il =
  match il with
      [] -> false
    | Call _ :: tl -> true
    | _ :: tl -> contains_call tl

class callBBVisitor =
object
  inherit nopCilVisitor

  method vstmt s =
    match s.skind with
        Instr il when contains_call il ->
          begin
            let list_of_stmts =
              Util.list_map (fun one_inst -> mkStmtOneInstr one_inst) il in
            let block = mkBlock list_of_stmts in
              ChangeDoChildrenPost
                (s, (fun _ -> s.skind <- Block block; s))
          end
      | _ -> DoChildren

  method vvdec _ = SkipChildren
  method vexpr _ = SkipChildren
  method vlval _ = SkipChildren
  method vtype _ = SkipChildren
end

let calls_end_basic_blocks f =
  let thisVisitor = new callBBVisitor in
    visitCilFileSameGlobals thisVisitor f


let get_control_flow stmt = begin
    match stmt.skind with
    | If(predicate,then_block, else_block,_) ->
      assert(List.length stmt.succs = 2);
      let then_stmt :: else_stmt :: [] = stmt.succs in
      let predicate_str = Pretty.sprint ~width:80 (dn_exp () predicate) in
      Printf.printf "(%d, %d, %s)\n" stmt.sid
        then_stmt.sid predicate_str ;
      Printf.printf "(%d, %d, !%s)\n" stmt.sid
        else_stmt.sid predicate_str
    | _ ->
      List.iter (fun succ ->
        Printf.printf "(%d, %d, True)\n" stmt.sid succ.sid
      ) stmt.succs;
    end

let get_data_flow lhs rhs loc stmt = begin
  match lhs with
  | Var(v),NoOffset ->
    let rhs_str = Pretty.sprint ~width:80 (dn_exp () rhs) in
    let type_str = Pretty.sprint ~width:80 (dn_type () v.vtype) in
    Printf.printf "[%s %s, %s, %d]\n"
    type_str v.vname rhs_str stmt.sid
  | _ -> () (* more complicated assignments not handled here *)
end

(*
   This procedure returns the "Cil.fundec" associated with the callee
   (i.e., the destination procedure) if possible, or None if the
   callee cannot be resolved.

   FIXME: add in alias analysis for function pointer resolution later, etc.
 *)
let process_function_call calling_context_fundec
                          func_hash lhs func_name arg_list stmt
                          : (Cil.fundec option) (* <- return type *)
                          =
  match func_name with
  | Lval(Var(func_var_info), _) -> begin
      let func_str = Pretty.sprint ~width:80 (dn_exp () func_name) in
      Printf.printf "FUNCTION CALL BEGIN: ";
      let type_str = Pretty.sprint ~width:80 (dn_type () func_var_info.vtype) in
      Printf.printf "[Name: %s] [Call Line: %d] [Return Type: %s]" func_str stmt.sid type_str; (*lhs_str;*)
      begin match lhs with
        | None -> ()
        | Some(actual_lhs) ->
          let lhs_str = Pretty.sprint ~width:80 (dn_lval () actual_lhs) in
          Printf.printf " [LHS: %s] \n" lhs_str;
      end;
      if Hashtbl.mem func_hash func_var_info then begin
        (* let func_str = Pretty.sprint ~width:80 (dn_exp () func_name) in *)
        let callee_func_obj:fundec = Hashtbl.find func_hash func_var_info in
        (* Printf.printf "FUNCTION CALL: RESOLVED\n"; (*statement_str*) *)
        (* let process_block statement = begin *)
        Printf.printf "Param_assign: ";
        List.iter2 (fun actual_param formal_param ->
          let actual_str = Pretty.sprint ~width:80 (dn_exp () actual_param) in
          Printf.printf "(%s %s) " actual_str formal_param.vname;
        ) arg_list callee_func_obj.sformals;
        Printf.printf "\n";
        Some(callee_func_obj)
      end else begin
        (* Printf.printf "FUNCTION CALL: NOT RESOLVED: function not found\n" ; *)
        None
      end
  end

  | _ ->
      (* Printf.printf "FUNCTION CALL: NOT RESOLVED: function call form not understood\n"; *)
      None


let main () = begin
  let func_hash = Hashtbl.create 255 in

  Cil.initCIL () ;

  let input_filename = "in.i" in

  let (ast : Cil.file) = Frontc.parse input_filename () in
  (* let (ast : Cil.file) = calls_end_basic_blocks ast_x in  *)

  (* Simplify memory operations *)
  ignore (calls_end_basic_blocks ast) ;
  List.iter Simplify.doGlobal ast.globals;
  Cfg.computeFileCFG ast ;


  let rec process_stmt fundec stmt = begin

    (* given a single statement, extract the control flow *)
    get_control_flow stmt;

    match stmt.skind with
    | Return(None, loc) -> begin
      let type_str = Pretty.sprint ~width:80 (dn_type () fundec.vtype) in
      Printf.printf "Return: [%s %s, None, %d] \n" type_str fundec.vname stmt.sid ;
    end
      (* Printf.printf "Return: [%s, None, %d] \n" fundec.vname, stmt.sid; *)

    | Return(Some(exp), loc) -> begin
      let exp_str = Pretty.sprint ~width:80 (dn_exp () exp) in
      let type_str = Pretty.sprint ~width:80 (dn_type () fundec.vtype) in
      Printf.printf "Return: [%s %s, %s, %d] \n" type_str fundec.vname exp_str stmt.sid;
    end
      (*dn exp*)
    | Instr(instr_list) ->
      List.iter (fun instr -> match instr with
      | Set(lhs, rhs, loc) -> begin
        (* for an instruction get the data flow *)
        get_data_flow lhs rhs loc stmt;
      end

      | Call(lhs, func_name, arg_list,  _ ) -> begin (*exp_list,*)
        let func_name_str = Pretty.sprint ~width:80 (dn_exp () func_name) in

        match process_function_call fundec func_hash lhs func_name arg_list stmt with
        | Some(resolved_called_fundec) ->
          (* Printf.printf "Recursively handling call: %s\n" func_name_str ; *)
          process_fundec resolved_called_fundec;
        Printf.printf "Call ends: %s\n" func_name_str ;



        | None ->
          ()
          (* Printf.printf "Warning: could not resolve call: %s\n" func_name_str *)

      end

      | Asm _ -> ()
      ) instr_list ;

    | _ -> (); (* only instructions have side effects in CIL *)

    (* Printf.printf "\n\nFirst Function Ends\n"; (*statement_str*) *)

  end and process_fundec fundec = begin
    (* not sure if this is correct, trying to pass in the function declaration fundec, and iterate over each statement*)
    List.iter (fun stmt -> process_stmt fundec.svar stmt) fundec.sallstmts;
  end

  (* and process_fundec fundec = begin (* don't need this as fundec needs to be passed*)
    process_stmt_list fundec.sallstmts ;
  end *)
    in

  (* first pass to collect all functions *)
  List.iter (fun glob -> match glob with
  | GFun(fundec, loc) ->
    begin
      Hashtbl.add func_hash fundec.svar fundec
    end
  | _ -> ()
  ) ast.globals;

  List.iter (fun glob -> match glob with
  | GFun(fundec, loc) -> begin
    if fundec.svar.vname = "main" then begin
      Printf.printf "FUNCTION CALL BEGIN: [Name: main] [Call Line: 1] \n";

      (* let bbfun = calls_end_basic_blocks fundec in *)
      process_fundec fundec;(* only process main()*)
      Printf.printf "Call ends: main\n";
  end end

  (* | GVarDecl(varinfo, loc) -> begin (*prob don't need this*)
    if loc.line > 0 then begin (* Does nothing, find a fix for garbage functions.*)
      let type_str = Pretty.sprint ~width:80 (dn_type () varinfo.vtype) in
      Printf.printf "Function dec: %s\nType: %s\n" varinfo.vname type_str;  (*(isFunctionType(varinfo.vtype))*)
      end
    end *)
  | _ -> ()
  ) ast.globals;

  let out_channel = open_out "out.i" in
  Cil.dumpFile Cil.defaultCilPrinter out_channel "out.i" ast ;
  close_out out_channel ;

  ()


end ;;
main () ;;

(* let process_el(single_arg:Cil.exp) =
  let el_str = Pretty.sprint ~width:80 (dn_exp () single_arg) in
  Printf.printf "%s " el_str;
in
List.iter
process_el
arg_list;
Printf.printf ")\n"; *)
