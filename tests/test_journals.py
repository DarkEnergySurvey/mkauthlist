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

class TestJournal(unittest.TestCase):

    def setUp(self):
        self.csv = 'example_author_list.csv'
        self.cls = ['emulateapj.cls','mnras.cls','aastex.cls','aastex61.cls','aastex63.cls']
        self.tex = self.csv.replace('.csv','.tex')
        self.aux = self.csv.replace('.csv','.aux')
        self.out = self.csv.replace('.csv','.out')
        self.log = self.csv.replace('.csv','.log')
        self.bib = self.csv.replace('.csv','*.bib')
        self.pdf = self.csv.replace('.csv','.pdf')

        self.files = dict(self.__dict__)

        cmd = "cp " + ' '.join(['data/'+f for f in [self.csv]+self.cls]) + ' .'
        print(cmd)
        out = subprocess.check_output(cmd,shell=True)

        #for filename in [self.csv]+self.cls:
        #    shutil.copy(os.path.join('data',filename),'.')

    def tearDown(self):
        self.clean = [self.csv,self.tex,self.aux,self.out,self.log,self.bib,self.pdf]
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

    def test_aastex61(self):
        cmd = "mkauthlist -f --doc -j aastex61 %(csv)s %(tex)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)
        self.latex(pdf='test_aastex61.pdf')

    def test_aastex63(self):
        cmd = "mkauthlist -f --doc -j aastex63 %(csv)s %(tex)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)
        self.latex(pdf='test_aastex63.pdf')

    def test_revtex(self):
        cmd = "mkauthlist -f --doc -j revtex %(csv)s %(tex)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)
        self.latex(pdf='test_revtex.pdf')

    def test_elsevier(self):
        cmd = "mkauthlist -f --doc -j elsevier %(csv)s %(tex)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)
        self.latex(pdf='test_elsevier.pdf')

    def test_arxiv(self):
        cmd = "mkauthlist -f -j arxiv %(csv)s %(tex)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)
        shutil.copy(self.tex,'test_arxiv.txt')

if __name__ == "__main__":
    unittest.main()
