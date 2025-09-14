#!/usr/bin/env python3
"""crispresso_abe_efficiency.py

Command-line tool to compute A->G editing efficiencies from CRISPResso2 outputs.
"""
import argparse, pandas as pd, sys
def read_base_edits(path):
    df = pd.read_csv(path, sep=None, engine='python')
    df.columns = [c.strip() for c in df.columns]
    return df
def main():
    parser = argparse.ArgumentParser(description='Compute A->G efficiencies from CRISPResso2 base edits.')
    parser.add_argument('-i','--input', required=True)
    parser.add_argument('-p','--protospacer', required=True)
    parser.add_argument('-s','--position', type=int, default=6)
    parser.add_argument('-o','--out', default='crispresso_base_summary.tsv')
    args = parser.parse_args()
    df = read_base_edits(args.input)
    # naive summarization: pivot Frequency per Sample x Position
    cols = {c.lower(): c for c in df.columns}
    pos_col = cols.get('position') or 'Position'
    sub_col = cols.get('substitution') or 'Substitution'
    freq_col = cols.get('frequency') or 'Frequency'
    sample_col = cols.get('sample') or 'Sample'
    if freq_col not in df.columns:
        print('Frequency column not found; ensure CRISPResso2_base_edits.txt has Frequency column', file=sys.stderr)
    df['Subst'] = df[sub_col].astype(str).str.replace('->','>').str.replace(' ','')
    df_a2g = df[df['Subst'].str.contains('A>G', regex=True)]
    if df_a2g.empty:
        print('No A>G substitutions found in input file', file=sys.stderr)
    pivot = df_a2g.pivot_table(index=sample_col, columns=pos_col, values=freq_col, aggfunc='sum', fill_value=0)
    pivot.reset_index().to_csv(args.out, sep='\t', index=False)
    print('Wrote', args.out)
if __name__ == '__main__':
    main()
