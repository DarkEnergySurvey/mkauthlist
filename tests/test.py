#!/usr/bin/env python
"""
Python test script
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
        self.cls = ['emulateapj.cls','mnras.cls','aastex.cls']
        self.tex = self.csv.replace('.csv','.tex')
        self.aux = self.csv.replace('.csv','.aux')
        self.out = self.csv.replace('.csv','.out')
        self.log = self.csv.replace('.csv','.log')
        self.bib = self.csv.replace('.csv','*.bib')
        self.pdf = self.csv.replace('.csv','.pdf')

        self.files = dict(self.__dict__)

        for filename in [self.csv]+self.cls:
            shutil.copy(os.path.join('data',filename),'.')

    def tearDown(self):
        self.clean = [self.csv,self.tex,self.aux,self.log,self.bib,self.pdf] 
        self.clean += self.cls

        cmd = "rm -f "+' '.join(self.clean)
        print(cmd)
        subprocess.check_output(cmd,shell=True)

    def latex(self, tex=None, pdf=None):
        if tex is None: tex = self.tex
        if pdf is None: pdf = self.pdf

        cmd = "pdflatex -interaction=nonstopmode %s"%(tex)
        print(cmd)
        subprocess.check_call(cmd,shell=True)
        shutil.copy(tex.replace('.tex','.pdf'),pdf)
        
    def test_mkauthlist(self):
        cmd = "mkauthlist -f --doc %(csv)s %(tex)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)
        self.latex(pdf='test_mkauthlist.pdf')

    def test_emulateapj(self):
        cmd = "mkauthlist -f --doc -j emulateapj %(csv)s %(tex)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)
        self.latex(pdf='test_emulateapj.pdf')
     
    def test_mnras(self):
        cmd = "mkauthlist -f --doc -j mnras %(csv)s %(tex)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)
        self.latex(pdf='test_mnras.pdf')
     
    def test_aastex(self):
        cmd = "mkauthlist -f --doc -j aastex %(csv)s %(tex)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)
        self.latex(pdf='test_aastex.pdf')

    def test_revtex(self):
        cmd = "mkauthlist -f --doc -j revtex %(csv)s %(tex)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)
        self.latex(pdf='test_revtex.pdf')
    
if __name__ == "__main__":
    unittest.main()
