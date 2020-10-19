open Cil


module Edge_map = Map.Make(String);;
let m = Edge_map.empty;;

let main () = begin
  let func_hash = Hashtbl.create 255 in


  Cil.initCIL () ;

  let input_filename = "in.i" in
  let (ast : Cil.file) = Frontc.parse input_filename () in

  (* Simplify memory operations *)
  List.iter Simplify.doGlobal ast.globals;
  Cfg.computeFileCFG ast ;

  (* Example function to process a function and print out some information
   * that might be used to make predicates about data and control flow. *)
  let process fundec = begin

    (* General debugging for reader convenience *)
    (* Printf.printf "Processing %s()\n" fundec.svar.vname ; *)
    (* ( match fundec.smaxstmtid with
    | Some(i) -> Printf.printf "max stmt id = %d\n" i
    | None -> () ) ; *)
    (* List.iter (fun stmt ->
      let stmt_str = Pretty.sprint ~width:80 (dn_stmt () stmt) in
      (* Printf.printf "\nstmt %d = %s\n" stmt.sid stmt_str ; *)

      List.iter (fun succ ->
        (* if stmt.sid = 1 then
              print_endline "THEN"; *)
        Printf.printf "  Edge: %d -> %d\n" stmt.sid succ.sid
      ) stmt.succs ;
      List.iter (fun pred ->
        Printf.printf "  Edge: %d -> %d\n" pred.sid stmt.sid
      ) stmt.preds ;
    ) fundec.sallstmts ; *)
    (* Printf.printf "\n\n" ; *)

    (* A rough cut at control-flow predicates *)
    List.iter (fun stmt ->
      match stmt.skind with
      | If(predicate,then_block,else_block,_) ->
        assert(List.length stmt.succs = 2);
        let then_stmt :: else_stmt :: [] = stmt.succs in
        let predicate_str = Pretty.sprint ~width:80 (dn_exp () predicate) in
        Printf.printf "(%d, %d, %s)\n" stmt.sid
          then_stmt.sid predicate_str ;
        Printf.printf "(%d, %d, !(%s))\n" stmt.sid
          else_stmt.sid predicate_str
      | _ ->
        List.iter (fun succ ->
          Printf.printf "(%d, %d, True)\n" stmt.sid succ.sid
        ) stmt.succs

    ) fundec.sallstmts ;

    (* A rough cut at data-flow predicates *)
    List.iter (fun stmt ->
      match stmt.skind with
      | Instr(instr_list) ->
        List.iter (fun instr -> match instr with
        | Set(lhs, rhs, loc) -> begin
          match lhs with
          | Var(v),NoOffset ->
            let rhs_str = Pretty.sprint ~width:80 (dn_exp () rhs) in
            Printf.printf "[%s, %s, %d]\n"
              v.vname rhs_str stmt.sid
          | _ -> () (* more complicated assignments not handled here *)
        end


          (*match loc with
          | Var(v),NoOffset ->
            let loc_str = Pretty.sprint ~width:80 (dn_exp () loc) in
            Printf.printf "Data Transfers %s <- %s on PC = %d\n"
              loc_str
          | _ -> () (* more complicated assignments not handled here *)
        end*)
        | Call(lhs, func_name, arg_list,  _ ) -> begin (*exp_list,*)
        match func_name with
          | Lval(Var(func_var_info), _) -> begin

          let func_str = Pretty.sprint ~width:80 (dn_exp () func_name) in
          Printf.printf "Name: %s\nCall Line: %d\n" func_str stmt.sid; (*lhs_str;*)
          begin match lhs with
            | None -> ()
            | Some(actual_lhs) -> let lhs_str = Pretty.sprint ~width:80 (dn_lval () actual_lhs) in
          Printf.printf "LHS: %s \n" lhs_str;
        end;

          Printf.printf "Actual args: (";

          let process_el(single_arg:Cil.exp) =
            let el_str = Pretty.sprint ~width:80 (dn_exp () single_arg) in
            Printf.printf "%s " el_str;
          in
          List.iter
          process_el
          arg_list;
          Printf.printf ")\n";

          if Hashtbl.mem func_hash func_var_info then
            (* let func_str = Pretty.sprint ~width:80 (dn_exp () func_name) in *)
            let func_obj:fundec = Hashtbl.find func_hash func_var_info in
            (* let process_block statement = begin *)
            Printf.printf "Param_assign: ";
            List.iter2 (fun actual_param formal_param ->
              let actual_str = Pretty.sprint ~width:80 (dn_exp () actual_param) in

            Printf.printf "(%s %s) " actual_str formal_param.vname;
          ) arg_list func_obj.sformals;
          Printf.printf "\n";

              List.iter (fun stmt ->
                match stmt.skind with
                | If(predicate,then_block,else_block,_) ->
                  assert(List.length stmt.succs = 2);
                  let then_stmt :: else_stmt :: [] = stmt.succs in
                  let predicate_str = Pretty.sprint ~width:80 (dn_exp () predicate) in
                  Printf.printf "(%d, %d, %s)\n" stmt.sid
                    then_stmt.sid predicate_str ;
                  Printf.printf "(%d, %d, !(%s))\n" stmt.sid
                    else_stmt.sid predicate_str
                | _ ->
                  List.iter (fun succ ->
                    Printf.printf "(%d, %d, True)\n" stmt.sid succ.sid
                  ) stmt.succs

                ) func_obj.sallstmts ;

                List.iter (fun stmt ->
                  match stmt.skind with
                  | Instr(instr_list) ->
                    List.iter (fun instr -> match instr with
                    | Set(lhs, rhs, loc) -> begin
                      match lhs with
                      | Var(v),NoOffset ->
                        let rhs_str = Pretty.sprint ~width:80 (dn_exp () rhs) in
                        Printf.printf "[%s, %s, %d]\n"
                          v.vname rhs_str stmt.sid
                      | _ -> () (* more complicated assignments not handled here *)
                    end

                  (* | Asm _ -> () *)
                  ) instr_list ;
                | _ -> () (* only instructions have side effects in CIL *)
              ) func_obj.sallstmts ;


              (* let statement_str = Pretty.sprint ~width:80 (dn_stmt () statement) in *)
            (* Printf.printf "FUNCTION END line %\n" statement.sid  statement_str; (*statement_str*) *)

              (* Printf.printf "return statement id: %d \n" statement.sid; *)
          (* end
            in
            List.iter process_block func_obj.sbody.bstmts; *)


          Printf.printf "FUNCTION CALL END\n"; (*statement_str*)

          end

          (* | FE(Var(_), _) -> begin
          let func_str = Pretty.sprint ~width:80 (dn_exp () func_name) in
          Printf.printf "Our natural function call is %s, at location: %d \n" func_str stmt.sid
        end *)
          | Lval(Mem(_), _) -> begin (*not currently used*)
          let func_str = Pretty.sprint ~width:80 (dn_exp () func_name) in Printf.printf "This is a pointer call %s\n" func_str
        end
        end

        | Asm _ -> ()
        ) instr_list ;
        Printf.printf "FUNCTION CALL END\n"; (*statement_str*)

      | _ -> () (* only instructions have side effects in CIL *)
    ) fundec.sallstmts ;

  end in
  List.iter (fun glob -> match glob with
  | GFun(fundec, loc) ->
    begin
      Hashtbl.add func_hash fundec.svar fundec
    end
  | _ -> ()
  ) ast.globals;

  (* let fun_head = List.hd ast.globals in *)
  List.iter (fun glob -> match glob with
  | GFun(fundec, loc) -> process fundec

  | GVarDecl(varinfo, loc) -> begin
    if loc.line > 0 then begin (* Does nothing, find a fix for garbage functions.*)
      let type_str = Pretty.sprint ~width:80 (dn_type () varinfo.vtype) in
      Printf.printf "Function dec: %s\nType: %s\n" varinfo.vname type_str;  (*(isFunctionType(varinfo.vtype))*)
      end
    end
  | _ -> ()
  ) ast.globals;

  let out_channel = open_out "out.i" in
  Cil.dumpFile Cil.defaultCilPrinter out_channel "out.i" ast ;
  close_out out_channel ;

  ()


end ;;
main () ;;
