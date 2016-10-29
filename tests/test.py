#!/usr/bin/env python
"""
Python test script
"""
__author__ = "Alex Drlica-Wagner"

import logging
import subprocess


params = dict(
    input = 'data/example_author_list.csv',
    csv= 'test_author_list.csv'
)
params['tex'] = params['csv'].replace('.csv','.tex')
params['aux'] = params['csv'].replace('.csv','.aux')
params['log'] = params['csv'].replace('.csv','.log')
params['bib'] = params['csv'].replace('.csv','*.bib')
params['pdf'] = params['csv'].replace('.csv','.pdf')
params['clean'] = [params['csv'],params['tex'],params['aux'],params['log'],params['bib'],params['pdf']]

def setup_func():
    "set up test fixtures"
    cmd = "cp %(input)s %(csv)s"%params
    print(cmd)
    subprocess.check_call(cmd,shell=True)

def teardown_func():
    "tear down test fixtures"
    cmd = "rm -f "+' '.join(params['clean'])
    print(cmd)
    subprocess.check_call(cmd,shell=True)

def test_mkauthlist():
    cmd = "mkauthlist -f --doc --sort -j emulateapj %(csv)s %(tex)s"%params
    print(cmd)
    subprocess.check_call(cmd,shell=True)

test_mkauthlist.setup = setup_func
test_mkauthlist.teardown = teardown_func

#def test_emulateapj():

#def test_latex()
#    latex = "pdflatex -interaction=nonstopmode %(tex)s"
#    cmd = latex%params
#    print cmd
#    subprocess.check_call(cmd,shell=True)
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()

    test_mkauthlist.setup()
    test_mkauthlist()
    test_mkauthlist.teardown()
