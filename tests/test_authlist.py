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

class TestAuthlist(unittest.TestCase):

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
        """Remove intermediate files."""
        self.clean = [self.csv,self.tex,self.aux,self.out,self.log,self.bib,
                      self.pdf,self.order,self.cntrb]
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
        """Run 'vanilla' mkauthlist."""
        cmd = "mkauthlist -f --doc %(csv)s %(tex)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)
        self.latex(pdf='test_mkauthlist.pdf')

    def test_order(self):
        """Explicitly order some authors."""
        cmd = "mkauthlist -f --doc %(csv)s %(tex)s -a %(order)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)

        # Shouldn't be any need to build the file
        #self.latex(pdf='test_order.pdf')

        with open(self.tex,'r') as f:
            authors = [l for l in f.readlines() if l.startswith('\\author')]
            self.assertEqual(authors[1],'\\author{E.~Sheldon}\n')
            self.assertEqual(authors[4],'\\author{A.~A.~Plazas}\n')
            self.assertEqual(authors[5],'\\author{Y.~Zhang}\n')
            self.assertEqual(authors[-1],'\\author{T.~M.~C.~Abbott}\n')

    def test_contribution(self):
        """Write author contributions."""
        cmd = "mkauthlist -f --doc %(csv)s %(tex)s --cntrb %(cntrb)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)

        # Shouldn't be any need to build the file
        #self.latex(pdf='test_contrib.pdf')

        with open(self.cntrb,'r') as f:
            lines = f.readlines()
            self.assertEqual(lines[0],'Author contributions are listed below. \\\\\n')
            self.assertEqual(lines[1],'P.~Melchior: Lead designer and author \\\\\n')
            self.assertEqual(lines[-1],'T.~M.~C.~Abbott:  \\\\\n')

    def test_sort(self):
        """Sort all authors alphabetically."""
        cmd = "mkauthlist -f --doc %(csv)s %(tex)s --sort"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)

        with open(self.tex,'r') as f:
            authors = [l for l in f.readlines() if l.startswith('\\author')]
            self.assertEqual(authors[0],'\\author{T.~M.~C.~Abbott}\n')
            self.assertEqual(authors[-1],'\\author{Y.~Zhang}\n')

    def test_sort_order(self):
        """Order some authors, sort the rest."""
        cmd = "mkauthlist -f --doc %(csv)s %(tex)s --sort -a %(order)s"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)

        with open(self.tex,'r') as f:
            authors = [l for l in f.readlines() if l.startswith('\\author')]
            self.assertEqual(authors[1],'\\author{E.~Sheldon}\n')
            self.assertEqual(authors[-1],'\\author{Y.~Zhang}\n')

    def test_sort_builder(self):
        """Sort builders, but leave other authors unchanged."""
        cmd = "mkauthlist -f --doc %(csv)s %(tex)s -sb"%self.files
        print(cmd)
        subprocess.check_output(cmd,shell=True)

        with open(self.tex,'r') as f:
            authors = [l for l in f.readlines() if l.startswith('\\author')]
            self.assertEqual(authors[3],'\\author{E.~Sheldon}\n')
            self.assertEqual(authors[4],'\\author{T.~M.~C.~Abbott}\n')
            self.assertEqual(authors[-1],'\\author{Y.~Zhang}\n')
            
if __name__ == "__main__":
    unittest.main()
