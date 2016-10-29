#!/usr/bin/env python
"""
Python test script
"""
__author__ = "Alex Drlica-Wagner"

import logging
import subprocess
import unittest


class TestAuthlistFunc(unittest.TestCase):

    def setUp(self):
        input = 'data/example_author_list.csv'

        self.csv = 'test_author_list.csv'
        self.tex = self.csv.replace('.csv','.tex')
        self.aux = self.csv.replace('.csv','.aux')
        self.log = self.csv.replace('.csv','.log')
        self.bib = self.csv.replace('.csv','*.bib')
        self.pdf = self.csv.replace('.csv','.pdf')
        self.cls = ['emulateapj.cls','mnras.cls','aastex.cls']

        self.files = dict(self.__dict__)

        cmd = "cp %s %s"%(input,self.csv)
        print(cmd)
        subprocess.check_output(cmd,shell=True)
         
        cmd = "cp %s ."%(' '.join(['data/%s'%c for c in self.cls]))
        print(cmd)
        subprocess.check_output(cmd,shell=True)

    def tearDown(self):
        self.clean = [self.csv,self.tex,self.aux,self.log,self.bib,self.pdf] 
        self.clean += self.cls

        cmd = "rm -f "+' '.join(self.clean)
        print(cmd)
        subprocess.check_output(cmd,shell=True)

    def latex(self, tex=None):
        if tex is None: tex = self.tex

        cmd = "pdflatex -interaction=nonstopmode %s"%(tex)
        print(cmd)
        subprocess.check_output(cmd,shell=True)

    def test_mkauthlist(self):
        cmd = "mkauthlist -f --doc %(csv)s %(tex)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)
        
        self.latex()

        cmd = 'cp %s %s'%(self.pdf,'test_mkauthlist.pdf')
        print(cmd)
        subprocess.check_output(cmd,shell=True)

    def test_emulateapj(self):
        cmd = "mkauthlist -f --doc -j emulateapj %(csv)s %(tex)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)

        self.latex()

        cmd = 'cp %s %s'%(self.pdf,'test_emulateapj.pdf')
        print(cmd)
        subprocess.check_output(cmd,shell=True)
     
    def test_mnras(self):
        cmd = "mkauthlist -f --doc -j mnras %(csv)s %(tex)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)

        self.latex()

        cmd = 'cp %s %s'%(self.pdf,'test_mnras.pdf')
        print(cmd)
        subprocess.check_output(cmd,shell=True)
     
    def test_aastex(self):
        cmd = "mkauthlist -f --doc -j aastex %(csv)s %(tex)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)

        self.latex()

        cmd = 'cp %s %s'%(self.pdf,'test_aastex.pdf')
        print(cmd)
        subprocess.check_output(cmd,shell=True)

    def test_revtex(self):
        cmd = "mkauthlist -f --doc -j revtex %(csv)s %(tex)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)

        self.latex()

        cmd = 'cp %s %s'%(self.pdf,'test_revtex.pdf')
        print(cmd)
        subprocess.check_output(cmd,shell=True)
    
if __name__ == "__main__":
    unittest.main()
