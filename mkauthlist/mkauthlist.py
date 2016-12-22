#!/usr/bin/env python
"""A simple script for making latex author lists from the csv file
produced by the DES Publication Database (PubDB).

Some usage notes:
(1) By default, the script preserves the order of the input file. The
'--sort' option does not respect tiers (use '--sort-builder' instead).
(2) An exact match is required to group affiliations. This should not
be a problem for affiliations provided by the DES PubDB; however, be
careful if you are editing affiliations by hand.
(3) The script parses quoted CSV format. LaTeX umlauts cause problems
(i.e., '\"') and must be escaped in the CSV file. The PubDB should do
this by default.
(4) There are some authors in the database with blank
affiliations. These need to be corrected by hand in the CSV file.
(5) Auxiliary author ordering (i.e, '-a, --aux') preserves the rest
of the author list. For example, the author list will become:
Ordered authors - Tier 1 authors - Tier 2 authors
"""

__author__  = "Alex Drlica-Wagner"
__email__   = "kadrlica@fnal.gov"
try: 
    # Module is in the python path
    from mkauthlist import __version__
except ImportError:
    # This file still lives in the source directory
    from _version import get_versions
    __version__ = get_versions()['version']
except:
    # This file is alone
    __version__ = "UNKNOWN"

import csv
import numpy as np
import os,sys
from collections import OrderedDict as odict
import copy
import logging

#MUNICH HACK (shouldn't be necessary any more)
HACK = odict([
    #('Ludwig-Maximilians-Universit',r'Department of Physics, Ludwig-Maximilians-Universit\"at, Scheinerstr.\ 1, 81679 M\"unchen, Germany')
])

def hack_umlaut(lines):
    """
    This hack was to avoid having the csv reader was reading umlauts
    as escaped quote characters.
    """
    hacked = False
    out = []
    for l in lines:
        if r'\"' in l: hacked = True
        # Replace the bad CSV formatting in old files
        l = l.replace(r'\"',r'\""')
        # Now fix the new files that we just broke with the previous line
        l = l.replace(r'\"""',r'\""')

        out += [l]

    if hacked:
        logging.warn("Hacking umlaut escape sequence")

    return out

def hack_alphabetic(data,name='da Costa'):
    """ 
    Hack the alphabetic ordering to deal with lowercase 'da Costa'
    This should be fixed at the DB level.
    """
    idx = data['Lastname'] == name
    hack  = np.sum(idx) > 0
    hack &= (idx[-1] == True)
    hack &= (get_builders(data)).all()
    if hack:
        logging.warn("Hacking alphabetic order for '%s'"%name)

        # Older versions of numpy have problems inserting multiple rows...
        if int(np.__version__.replace('.','')) <= 161:
            msg = "Alphabetic hack only works with numpy > 1.6.1"
            logging.warn(msg)
            #raise Exception(msg)

        entry = data[idx]
        new = np.delete(data,np.where(idx))
        # Count backward to try to be robust against resorted lists...
        for i,d in enumerate(new[::-1]):
            if get_builders(d): continue
            if d['Lastname'].upper() < name.upper():
                new = np.insert(new,len(new)-i,entry)
                break

        if len(new) != len(data):
            msg = "Failed to hack '%s'"%name
            logging.error(msg)
            raise Exception(msg)

        return new
    return data

def get_builders(data):
    """ Get a boolean array of the authors that are builders. """
    if 'AuthorType' in data.dtype.names:
        builders = (np.char.lower(data['AuthorType']) == 'builder')
    elif 'JoinedAsBuilder' in data.dtype.names:
        builders = (np.char.lower(data['JoinedAsBuilder']) == 'true')
    else:
        msg = "No builder column found."
        raise ValueError(msg)

    return builders

def write_contributions(filename,data):
    """ Write a file of author contributions. """
    logging.info("Creating contribution list...")
    if 'Contribution' not in data.dtype.names:
        logging.error("No 'Contribution' field.")
        raise Exception()

    cntrbdict = odict()
    for i,d in enumerate(data):
        if cntrbdict.get(d['Authorname'],d['Contribution']) != d['Contribution']:
            logging.warn("Non-unique contribution for '%(Authorname)s'"%d)

        cntrbdict[d['Authorname']]=d['Contribution']

    output = r'Author contributions are listed below. \\'+'\n'
    for i,(name,cntrb) in enumerate(cntrbdict.items()):
        if cntrb == '':
            logging.warn("Blank contribution for '%s'"%name)

        output += r'%s: %s \\'%(name,cntrb.capitalize()) + '\n'

    logging.info('Writing contribution file: %s'%filename)

    out = open(filename,'wb')
    out.write(output)
    out.close()


journal2class = odict([
    ('tex','aastex61'),
    ('revtex','revtex'),
    ('prl','revtex'),
    ('prd','revtex'),
    ('aastex','aastex'),     # This is for aastex v5.*
    ('aastex61','aastex61'), # This is for aastex v6.1
    ('apj','aastex61'),
    ('apjl','aastex61'),
    ('aj','aastex61'),
    ('mnras','mnras'),
    ('elsevier','elsevier'),
    ('emulateapj','emulateapj'),
])

defaults = dict(
    title = "DES Publication Title",
    abstract=r"This is a sample document created by \texttt{%s v%s}."%(os.path.basename(__file__),__version__),
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

### AASTEX61 ###
aastex61_authlist = r"""
%(authors)s

\collaboration{(%(collaboration)s)}
"""

aastex61_document = r"""
\documentclass[twocolumn]{aastex61}

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
\documentclass[final,5p]{elsarticle}
\begin{document}

\begin{frontmatter}
\title{%(title)s}
 
%(authlist)s
 
\begin{abstract}
%(abstract)s
\end{abstract}
\end{frontmatter}

\end{document}
"""

if __name__ == "__main__":
    import argparse
    description = __doc__
    formatter=argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=formatter)
    parser.add_argument('infile',metavar='DES-XXXX-XXXX_author_list.csv',
                        help="input csv file from DES PubDB")
    parser.add_argument('outfile',metavar='DES-XXXX-XXXX_author_list.tex',
                        nargs='?',default=None,help="output latex file (optional).")
    parser.add_argument('-a','--aux',metavar='order.csv',
                        help="auxiliary author ordering file (one name per line).")
    parser.add_argument('-c','--collab','--collaboration',
                        default='DES Collaboration',help="collaboration name.")
    parser.add_argument('--cntrb','--contributions',nargs='?',
                        const='contributions.tex',help="contribution file.")
    parser.add_argument('-d','--doc',action='store_true',
                        help="create standalone latex document.")
    parser.add_argument('-f','--force',action='store_true',
                        help="force overwrite of output.")
    parser.add_argument('-i','--idx',default=1,type=int,
                        help="starting index for aastex author list \
                        (useful for multi-collaboration papers).")
    parser.add_argument('-j','--journal',default='apj',
                        choices=sorted(journal2class.keys()),
                        help="journal name or latex document class.")
    parser.add_argument('-s','--sort',action='store_true',
                        help="alphabetize the author list (you know you want to...).")
    parser.add_argument('-sb','--sort-builder',action='store_true',
                        help="alphabetize the builder list.")
    parser.add_argument('-v','--verbose',action='count',default=0,
                        help="verbose output.")
    parser.add_argument('-V','--version',action='version',
                        version='%(prog)s '+__version__,
                        help="print version number and exit.")
    args = parser.parse_args()

    if args.verbose == 1: level = logging.INFO
    elif args.verbose >= 2: level = logging.DEBUG
    else: level = logging.WARNING
    logging.basicConfig(format="%% %(levelname)s: %(message)s", level=level)

    defaults['collaboration'] = args.collab

    readlines = open(args.infile).readlines()
    # FIXME: Replace umlauts to make valid CSV file
    # Things are fixed now... but we need to deal with old files.
    lines = hack_umlaut(readlines)

    rows = [r for r in csv.reader(lines,skipinitialspace=True) if not r[0].startswith('#')]
    data = np.rec.fromrecords(rows[1:],names=rows[0])

    if args.sort_builder:
        build = get_builders(data)
        builder = data[build]
        idx = np.lexsort((np.char.upper(builder['Firstname']),
                          np.char.upper(builder['Lastname'])))
        builder = builder[idx]
        nonbuilder = data[~build]
        data = np.hstack([nonbuilder,builder])
    if args.sort: 
        data = data[np.argsort(np.char.upper(data['Lastname']))]

    # FIXME: Is this still necessary?
    data = hack_alphabetic(data, 'da Costa')

    cls = journal2class[args.journal.lower()]
    affidict = odict()
    authdict = odict()

    # Hack for Munich affiliation...
    for k,v in HACK.items():
        logging.warn("Hacking '%s' ..."%k)
        select = (np.char.count(data['Affiliation'],k) > 0)
        data['Affiliation'][select] = v

    # Pre-sort the csv file by the auxiliary file
    if args.aux is not None:
        aux = [r for r in csv.DictReader(open(args.aux),['Lastname','Firstname'])]
        if len(np.unique(aux)) != len(aux):
            logging.error('Non-unique names in aux file.')
            print(open(args.aux).read())
            raise Exception()
            
        raw = np.array(zip(data['Lastname'],range(len(data))))
        order = np.empty((0,2),dtype=raw.dtype)
        for r in aux:
            lastname = r['Lastname']
            match = (raw[:,0] == lastname)
            if not np.any(match):
                logging.warn("Auxiliary name %s not found"%lastname)
                continue

            # Eventually deal with duplicate names... but for now throw an error.
            firstnames = np.unique(data['Firstname'][data['Lastname']==lastname])
            if not len(firstnames) == 1:
                logging.error('Non-unique last name; order by hand.')
                for f in firstnames:
                    print(f)
                raise Exception()
            order = np.vstack([order,raw[match]])
            raw = raw[~match]
        order = np.vstack([order,raw])
        data = data[order[:,1].astype(int)]
                    
    ### REVTEX ###
    if cls in ['revtex','aastex61']:
        if cls == 'revtex':
            document = revtex_document
            authlist = revtex_authlist
        elif cls == 'aastex61':
            document = aastex61_document
            authlist = aastex61_authlist
        else:
            msg = "Unrecognized latex class: %s"%cls
            raise Exception(msg)

        for i,d in enumerate(data):
            if d['Affiliation'] == '': 
                logging.warn("Blank affiliation for '%s'"%d['Authorname'])
            if d['Authorname'] == '': 
                logging.warn("Blank authorname for '%s %s'"%(d['Firstname'],
                                                             d['Lastname']))

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

    ### Separate author and affiliation ###
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
            msg = "Unrecognized latex class: %s"%cls
            raise Exception(msg)
            
        for i,d in enumerate(data):
            if d['Affiliation'] == '': 
                logging.warn("Blank affiliation for '%s'"%d['Authorname'])
            if d['Authorname'] == '': 
                logging.warn("Blank authorname for '%s %s'"%(d['Firstname'],
                                                             d['Lastname']))

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
            author = k+affilmark%(','.join([str(_v+args.idx) for _v in v]))
            authors.append(author)
         
        for k,v in affidict.items():
            affiliation = affiltext%(v+args.idx,k)
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
                logging.warn("Blank affiliation for '%s'"%d['Authorname'])
            if d['Authorname'] == '':
                logging.warn("Blank authorname for '%s %s'"%(d['Firstname'],
                                                             d['Lastname']))

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
            author = r'\author[%s]{%s}'%(','.join([str(_v+args.idx) for _v in v]),k)
            authors.append(author)
         
        for k,v in affidict.items():
            affiliation = affiltext%(v+args.idx,k)
            affiliations.append(affiliation)
            
        params = dict(defaults,authors='\n'.join(authors).strip(','),affiliations='\n'.join(affiliations))

    output  = "%% Author list file generated with: %s %s \n"%(parser.prog, __version__ )
    output += "%% %s %s \n"%(os.path.basename(sys.argv[0]),' '.join(sys.argv[1:]))
    if args.doc:
        params['authlist'] = authlist%params
        output += document%params
    else:
        output += authlist%params
         
    if args.outfile is None:
        print(output)
    else:
        outfile = args.outfile
        if os.path.exists(outfile) and not args.force:
            logging.warn("Found %s; skipping..."%outfile)
        out = open(outfile,'w')
        out.write(output)
        out.close()

    if args.cntrb:
        write_contributions(args.cntrb,data)
