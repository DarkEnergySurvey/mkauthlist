#!/usr/bin/env python
"""A simple script for making latex author lists from the csv file
produced by the DES Publication Database (PubDB).

Some usage notes:
(1) By default, the script does not tier or sort the author list. The
'--sort' option does not respect tiers.
(2) An exact match is required to group affiliations. This should not
be a problem for affiliations provided by the PubDB; however, be
careful if you are editing affiliations by hand.
(3) The script parses quoted CSV format. Latex umlauts cause a problem
(i.e., the Munich affiliation) and must be escaped in the CSV
file. The PubDB should do this by default.
(4) There are some authors in the database with blank
affiliations. These need to be corrected by hand in the CSV file.

"""
__author__ = "Alex Drlica-Wagner"
__email__ = "kadrlica@fnal.gov"
__version__ = "0.2.0"

import csv
import numpy as np
import os,sys
from collections import OrderedDict as odict
import copy

#MUNICH HACK (shouldn't be necessary any more)
HACK = odict([
    #('Ludwig-Maximilians-Universit',r'Department of Physics, Ludwig-Maximilians-Universit\"at, Scheinerstr.\ 1, 81679 M\"unchen, Germany')
])

def hack_alphabetic(data,name='da Costa'):
    """ 
    Hack the alphabetic ordering to deal with lowercase 'da Costa'
    This should be fixed at the DB level.
    """
    idx = data['Lastname'] == name
    hack  = np.sum(idx) > 0
    hack &= (idx[-1] == True)
    hack &= (data['JoinedAsBuilder'][idx] == 'True').all()
    if hack:
        print "%% WARNING: Hacking alphabetic order for '%s'"%name

        # Older versions of numpy have problems inserting multiple rows...
        if int(np.__version__.replace('.','')) <= 161:
            msg = "% WARNING: Alphabetic hack only works with numpy > 1.6.1"
            print msg
            #raise Exception(msg)

        entry = data[idx]
        new = np.delete(data,np.where(idx))
        # Count backward to try to be robust against resorted lists...
        for i,d in enumerate(new[::-1]):
            if d['JoinedAsBuilder'].lower() != 'true': continue
            if d['Lastname'].upper() < name.upper():
                new = np.insert(new,len(new)-i,entry)
                break

        if len(new) != len(data):
            msg = "%% ERROR: Failed to hack '%s'"%name
            raise Exception(msg)

        return new
    return data

journal2class = odict([
    #('aastex','aastex'),
    #('revtex','revtex'),
    ('apj','aastex'),
    ('emulateapj','emulateapj'),
    ('aj','aastex'),
    ('prl','revtex'),
    ('prd','revtex'),
    ('mnras','mnras'),
    ('elsevier','elsevier'),
])

defaults = dict(
    title = "DES Publication Title",
    abstract=r"This is a sample document created by \texttt{authlist.py v%s}."%__version__,
    collaboration="The DES Collaboration"
)

### REVTEX ###
revtex_authlist = r"""
%(authors)s

\collaboration{%(collaboration)s}
"""

revtex_document = r"""
\documentclass[reprint,superscriptaddress]{revtex4-1}
\pagestyle{empty}
\begin{document}
\title{%(title)s}
 
%(authlist)s

\begin{abstract}
%(abstract)s
\end{abstract}
\maketitle
\end{document}
"""

### AASTEX ###
aastex_authlist = r"""
\def\andname{}

\author{
%(authors)s
\\ \vspace{0.2cm} (%(collaboration)s) \\
}
 
%(affiliations)s
"""

aastex_document = r"""
\documentclass[preprint]{aastex}

\begin{document}
\title{%(title)s}
 
%(authlist)s
 
\begin{abstract}
%(abstract)s
\end{abstract}
\maketitle
\end{document}
"""

### EMULATEAPJ ###
emulateapj_document = r"""
\documentclass[iop]{emulateapj}

\begin{document}
\title{%(title)s}
 
%(authlist)s
 
\begin{abstract}
%(abstract)s
\end{abstract}
\maketitle
\end{document}
"""

### MNRAS ###
mnras_authlist = r"""
\author[%(collaboration)s]{
\parbox{\textwidth}{
\Large
%(authors)s
\begin{center} (%(collaboration)s) \end{center}
}
\vspace{0.4cm}
\\
\parbox{\textwidth}{
%%\scriptsize
%(affiliations)s
}
}
"""

mnras_document = r"""
\documentclass{mnras}
\pagestyle{empty}
\begin{document}
\title{%(title)s}
 
%(authlist)s
 
\maketitle
\begin{abstract}
%(abstract)s
\end{abstract}

\end{document}
"""

### ELSEVIER ###
elsevier_authlist = r"""
%(authors)s

%(affiliations)s
"""

elsevier_document = r"""
\documentclass{elsarticle}
\begin{document}
\title{%(title)s}
 
%(authlist)s
 
\maketitle
\begin{abstract}
%(abstract)s
\end{abstract}

\end{document}
"""

if __name__ == "__main__":
    import argparse
    description = __doc__
    formatter=argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=formatter)
    parser.add_argument('infile',metavar='DES-XXXX-XXXX_author_list.csv',
                        help="Input csv file from DES PubDB")
    parser.add_argument('outfile',metavar='DES-XXXX-XXXX_author_list.tex',
                        nargs='?',default=None,help="Output latex file (optional).")
    parser.add_argument('-a','--aux',metavar='order.csv',
                        help="Auxiliary author ordering file (one lastname per line).")
    parser.add_argument('-d','--doc',action='store_true',
                        help="Create standalone latex document.")
    parser.add_argument('-f','--force',action='store_true',
                        help="Force overwrite of output.")
    parser.add_argument('-i','--idx',default=1,type=int,
                        help="Starting index for aastex author list \
                        (useful for multi-collaboration papers).")
    parser.add_argument('-j','--journal',default='apj',
                        choices=sorted(journal2class.keys()),
                        help="Journal name or latex document class.")
    parser.add_argument('-s','--sort',action='store_true',
                        help="Alphabetize the author list (you know you want to...).")
    parser.add_argument('-sb','--sort-builder',action='store_true',
                        help="Alphabetize the builder list.")

    parser.add_argument('-V','--version',action='version',
                        version='%(prog)s '+__version__,
                        help="Print version number and exit.")
    opts = parser.parse_args()

    # FIXME: Replace umlauts to make valid CSV file
    # Things are fixed now... but we need to deal with old files.
    print "% WARNING: Hacking umlaut escape sequence"
    # Replace the bad CSV formatting in old files
    lines = [l.replace(r'\"',r'\""') for l in open(opts.infile).readlines()]
    # Now fix the new files that we just broke with the previous line
    lines = [l.replace(r'\"""',r'\""') for l in lines] 
    rows = [r for r in csv.reader(lines,skipinitialspace=True) if not r[0].startswith('#')]
    data = np.rec.fromrecords(rows[1:],names=rows[0])

    if opts.sort_builder:
        build = (np.char.lower(data['JoinedAsBuilder']) == 'true')
        builder = data[build]
        #idx = np.argsort(np.char.upper(builder['Lastname']))
        idx = np.lexsort((np.char.upper(builder['Firstname']),
                          np.char.upper(builder['Lastname'])))
        builder = builder[idx]
        nonbuilder = data[~build]
        data = np.hstack([nonbuilder,builder])
    if opts.sort: 
        data = data[np.argsort(np.char.upper(data['Lastname']))]

    # FIXME: Is this still necessary?
    data = hack_alphabetic(data, 'da Costa')

    cls = journal2class[opts.journal.lower()]
    affidict = odict()
    authdict = odict()

    # Hack for Munich affiliation...
    for k,v in HACK.items():
        print "%% WARNING: Hacking '%s' ..."%k
        select = (np.char.count(data['Affiliation'],k) > 0)
        data['Affiliation'][select] = v

    # Pre-sort the csv file by the auxiliary file
    if opts.aux is not None:
        aux = [r for r in csv.DictReader(open(opts.aux),['Lastname','Firstname'])]
        if len(np.unique(aux)) != len(aux):
            print '% ERROR: Non-unique names in aux file.'
            print open(opts.aux).read()
            raise Exception()
            
        raw = np.array(zip(data['Lastname'],range(len(data))))
        order = np.empty((0,2),dtype=raw.dtype)
        for r in aux:
            lastname = r['Lastname']
            match = (raw[:,0] == lastname)
            if not np.any(match):
                print "%% WARNING: Auxiliary name %s not found"%lastname
                continue

            # Eventually deal with duplicate names... but for now throw an error.
            firstnames = np.unique(data['Firstname'][data['Lastname']==lastname])
            if not len(firstnames) == 1:
                print '%% ERROR: Non-unique last name; order by hand.'
                for f in firstnames:
                    print f, n
                raise Exception()
            order = np.vstack([order,raw[match]])
            raw = raw[~match]
        order = np.vstack([order,raw])
        data = data[order[:,1].astype(int)]
                    
    ### REVTEX ###
    if cls in ['revtex']:
        document = revtex_document
        authlist = revtex_authlist

        for i,d in enumerate(data):
            if d['Affiliation'] == '': 
                print "%% WARNING: Blank affiliation for '%s'"%d['Authorname']
            if d['Authorname'] == '': 
                print "%% WARNING: Blank authorname for '%s %s'"%(d['Firstname'],d['Lastname'])

            if d['Authorname'] not in authdict.keys():
                authdict[d['Authorname']] = [d['Affiliation']]
            else:
                authdict[d['Authorname']].append(d['Affiliation'])

        authors = []
        for key,val in authdict.items():
            author = r'\author{%s}'%key+'\n'
            for v in val:
                author += r'\affiliation{%s}'%v+'\n'
            authors.append(author)
        params = dict(defaults,authors=''.join(authors))

    ### AASTEX ###
    if cls in ['aastex','mnras','emulateapj']:
        if cls == 'aastex':
            document = aastex_document
            authlist = aastex_authlist
            affilmark = r'\altaffilmark{%s},'
            affiltext = r'\altaffiltext{%i}{%s}'
        elif cls == 'emulateapj':
            document = emulateapj_document
            authlist = aastex_authlist
            affilmark = r'\altaffilmark{%s},'
            affiltext = r'\affil{$^{%i}$ %s}'
        elif cls == 'mnras':
            document = mnras_document
            authlist = mnras_authlist
            affilmark = r'$^{%s}$,'
            affiltext = r'$^{%i}$ %s\\'
        else:
            msg = "Unrecognized LaTex class: %s"%cls
            raise Exception(msg)
            
        for i,d in enumerate(data):
            if d['Affiliation'] == '': 
                print "%% WARNING: Blank affiliation for '%s'"%d['Authorname']
            if d['Authorname'] == '': 
                print "%% WARNING: Blank authorname for '%s %s'"%(d['Firstname'],d['Lastname'])

            if (d['Affiliation'] not in affidict.keys()):
                affidict[d['Affiliation']] = len(affidict.keys())
            affidx = affidict[d['Affiliation']]
            
            if d['Authorname'] not in authdict.keys():
                authdict[d['Authorname']] = [affidx]
            else:
                authdict[d['Authorname']].append(affidx)
         
        affiliations = []
        authors=[]
        for k,v in authdict.items():
            author = k+affilmark%(','.join([str(_v+opts.idx) for _v in v]))
            authors.append(author)
         
        for k,v in affidict.items():
            affiliation = affiltext%(v+opts.idx,k)
            affiliations.append(affiliation)
            
        params = dict(defaults,authors='\n'.join(authors).strip(','),affiliations='\n'.join(affiliations))

    ### ELSEVIER ###
    if cls in ['elsevier']:
        document = elsevier_document
        authlist = elsevier_authlist
        affilmark = r'%i,'
        affiltext = r'\address[%i]{%s}'
        for i,d in enumerate(data):
            if d['Affiliation'] == '': 
                print "%% WARNING: Blank affiliation for '%s'"%d['Authorname']
            if d['Authorname'] == '': 
                print "%% WARNING: Blank authorname for '%s %s'"%(d['Firstname'],d['Lastname'])

            if (d['Affiliation'] not in affidict.keys()):
                affidict[d['Affiliation']] = len(affidict.keys())
            affidx = affidict[d['Affiliation']]
            
            if d['Authorname'] not in authdict.keys():
                authdict[d['Authorname']] = [affidx]
            else:
                authdict[d['Authorname']].append(affidx)
         
        affiliations = []
        authors=[]
        for k,v in authdict.items():
            author = r'\author[%s]{%s}'%(','.join([str(_v+opts.idx) for _v in v]),k)
            authors.append(author)
         
        for k,v in affidict.items():
            affiliation = affiltext%(v+opts.idx,k)
            affiliations.append(affiliation)
            
        params = dict(defaults,authors='\n'.join(authors).strip(','),affiliations='\n'.join(affiliations))

    output  = "%% Author list file generated with: authlist.py %s \n"%(__version__ )
    output += "%% %s \n"%(' '.join(sys.argv))
    if opts.doc:
        params['authlist'] = authlist%params
        output += document%params
    else:
        output += authlist%params
         
    if opts.outfile is None:
        print output
    else:
        outfile = opts.outfile
        if os.path.exists(outfile) and not opts.force:
            print "Found %s; skipping..."%outfile
        out = open(outfile,'w')
        out.write(output)
