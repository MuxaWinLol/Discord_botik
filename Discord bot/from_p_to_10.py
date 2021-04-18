def from_p_to_10(inp, cc):
    if '.' in inp:
        inp = inp.split('.')
        whole = float(int(inp[0], cc))
        dr = inp[1]
        if '(' in dr:
            dr = dr.split('(')
            pred = dr[0]
            per = dr[1][:-1]
            chisl = int(pred + per, cc) - (int(pred, cc) if pred else 0)
            zn = (cc ** len(pred + per) - (cc ** len(pred)))
            return str(chisl / zn + whole)
        else:
            return str(whole + int(dr, cc) / (cc ** len(dr)))
    else:
        return str(int(inp, cc))
