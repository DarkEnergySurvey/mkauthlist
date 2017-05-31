#!/usr/bin/env python
"""
Generic python script.
"""
__author__ = "Alex Drlica-Wagner"
import os
import shutil
import logging
import subprocess
import unittest

class TestAuthlistFunc(unittest.TestCase):

    def setUp(self):
        self.csv = 'example_author_list.csv'
        self.order = 'author_order.csv'
        self.cntrb = 'contributions.tex'
        self.cls = ['aastex61.cls']
        self.tex = self.csv.replace('.csv','.tex')
        self.aux = self.csv.replace('.csv','.aux')
        self.out = self.csv.replace('.csv','.out')
        self.log = self.csv.replace('.csv','.log')
        self.bib = self.csv.replace('.csv','*.bib')
        self.pdf = self.csv.replace('.csv','.pdf')
        self.files = dict(self.__dict__)

        cmd = "cp " + ' '.join(['data/'+f for f in [self.csv,self.order]+self.cls]) + ' .'
        print(cmd)
        out = subprocess.check_output(cmd,shell=True)

        #for filename in [self.csv]+self.cls:
        #    shutil.copy(os.path.join('data',filename),'.')

    def tearDown(self):
        self.clean = [self.csv,self.tex,self.aux,self.out,self.log,self.bib,self.pdf,self.order]
        self.clean += self.cls

        cmd = "rm -f "+' '.join(self.clean)
        print(cmd)
        subprocess.check_output(cmd,shell=True)

    def latex(self, tex=None, pdf=None):
        if tex is None: tex = self.tex
        if pdf is None: pdf = self.pdf

        cmd = "pdflatex -interaction=nonstopmode %s"%(tex)
        print(cmd)
        out = subprocess.check_output(cmd,shell=True)
        shutil.copy(tex.replace('.tex','.pdf'),pdf)
        
    def test_mkauthlist(self):
        cmd = "mkauthlist -f --doc %(csv)s %(tex)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)
        self.latex(pdf='test_mkauthlist.pdf')

    def test_author_order(self):
        cmd = "mkauthlist -f --doc %(csv)s %(tex)s -a %(order)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)
        self.latex(pdf='test_order.pdf')

    def test_contribution(self):
        cmd = "mkauthlist -f --doc %(csv)s %(tex)s --cntrb %(cntrb)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)
        self.latex(pdf='test_contrib.pdf')

        if not os.path.exists(self.cntrb): 
            msg = "No contributions found"
            raise Exception(msg)
        
        with open(self.cntrb) as cntrb:
            lines = cntrb.readlines()
            msg = "Unexpected author contributions: "
            if not lines[0].split()[0] == 'Author':
                raise Exception(msg+'\n'+lines[0])
                msg = "Unexpected author contributions"
            if not lines[1].split()[0] == 'P.~Melchior:':
                raise Exception(msg+'\n'+lines[1])
            
if __name__ == "__main__":
    unittest.main()
