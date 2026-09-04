# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
#basic import excel files from pandas tools for viewer tools https://dexter.ndw.nu/opendata
#berekent ook op/af uit door-stromen bij missende data
# -

import rdwbas

import pandas as pd
import numpy as np
import seaborn as sns

import re
import io
import time
import glob

import geopandas
import contextily as cx
import xyzservices.providers as xyz
import matplotlib.pyplot as plt
from matplotlib import colors 
import matplotlib.ticker as ticker

from sklearn.linear_model import LinearRegression
from scipy.optimize import nnls
from sklearn import linear_model
import seaborn

myname='ndwconsischk'
suprtests= myname in rdwbas.suprtests 
suprdata= myname in rdwbas.suprdata
#suprtests=True
print ('Suprtests',suprtests)

rdwbas.suprtests = rdwbas.suprtests+['ndwimport']
import ndwimport



# +
#nu houten IO
# -

xlslist= (glob.glob("../data/intensiteit-snelheid-*.xlsx"))
xlslist

allsumf1= [ ndwimport.ndw_od_read_overzicht(t,t,"datadatalog") for t in xlslist ]
allsumdf = pd.concat(allsumf1)
allsumdf

allsumdf.to_excel("../intermediate/xlscatalog.xlsx")

# +
#zelfde verhaal. A12 check over Houten Oost en Bunnik heen
# -

xlsa12s1list= (glob.glob("../data/intensiteit-snelheid-a12-20??-s1.xlsx"))
xlsa12s1list

testfil12=xlsa12s1list[1]

idfa12=ndwimport.ndw_od_read_overzicht_en_intensiteiten(testfil12,"testseq12","testcoll20260522")
#display(idfa12)

odf12= ndwimport.ndw_od_read_overzicht(testfil12,"testseq12","testcoll20260522")
if (not suprtests):
    pland= odf12.plot(alpha=0.4)
    cx.add_basemap(pland, source= ndwimport.prov0,crs=odf12.crs)

idfa12my =[ ndwimport.ndw_od_read_overzicht_en_intensiteiten(testfil,"a12my",testfil) for testfil in xlsa12s1list ]
idfa12my=pd.concat(idfa12my)

# +
some_string="""ID	stroom	hm	ri	afop	estfrID	IDsinds
PUT01_N421.01_0	a12	658	l	op		
PUT01_N421.01_1	a12	662	r	af		
RWS01_MONIBAS_0121hrl0638ra	a12	638	l	t		
RWS01_MONIBAS_0121hrl0638rb	a12	638	l	t		
RWS01_MONIBAS_0121hrl0647ra	a12	647	l	t		
RWS01_MONIBAS_0121hrl0658ra	a12	658	l	d		
RWS01_MONIBAS_0121hrl0664ra	a12	664	l	t		
RWS01_MONIBAS_0121hrl0672ra	a12d	672	l	t		
RWS01_MONIBAS_0121hrr0640ra	a12	640	r	t		
RWS01_MONIBAS_0121hrr0647ra	a12	647	r	t		
RWS01_MONIBAS_0121hrr0660ra	a12	660	r	t		
RWS01_MONIBAS_0121hrr0662ra	a12	662	r	d		
RWS01_MONIBAS_0121hrr0672ra	a12	672	r	t		
RWS01_MONICA_00D00C0A500FD0070307	a12u	660	r	d		
RWS01_MONICA_00D00C0A541400200007	a12u	660	r	d		
RWS01_MONICA_00D00C0A585FD0070007	a12u	662	r	d		
RWS01_MONICA_00D00C0A585FD007000B	a12u	662	r	d		
RWS01_MONICA_00D00C0A585FD007000F	a12u	662	r	d		
RWS01_MONICA_00D00C0A585FD0070013	a12u	662	r	d		"""
#read CSV string into pandas DataFrame
a12id_config= pd.read_csv(io.StringIO(some_string), sep="\t")
display(a12id_config)

rdata12my=ndwimport.merge_initest(idfa12my,a12id_config)
# -

ndwimport.summstr_normprep(rdata12my,'a12','Intensiteit',[],['ID'],False)    

ndwimport.ilowhihmplt(rdata12my,'a12','Intensiteit',['perstart'])    

# +

#rdata27my
usefacts12my=ndwimport.summstr_normprep(rdata12my,
                             'a12','Intensiteit',[],[],False).reset_index()    
#display(usefacts12my)
cdata12my=ndwimport.corrcol(rdata12my,'a12','Intensiteit',usefacts12my,'IntensiteitCorr')  
ndwimport.ilowhihmplt(cdata12my,'a12','IntensiteitCorr',['perstart'])   
# -

ndwimport.dlowhiaxplt(cdata12my,'a12','IntensiteitCorr',['uur'],False,True)  


def _scaledr12(x):
            return x *0.05
def _scaledrinv12(x):
            return x * 20
if (not suprtests):    
    ndwimport.pltjaaropaf(cdata12my,'a12','IntensiteitCorr',[658,662],_scaledr12, _scaledrinv12,
            "A12 afrit Houten Oost opaf en door/4 :  l: westwaarts, r : oostwaards" )

# +
#htn wegverloop
# -

testhtn25s2="../data/intensiteit-snelheid-htn-2025-s2.xlsx"

odfhtn25s2= ndwimport.ndw_od_read_overzicht(testhtn25s2,"lochtn","testcoll20260522")  

odfhtn25s2

idfhtn25s2= ndwimport.ndw_od_read_overzicht_en_intensiteiten(testhtn25s2,"lochtn","testcoll20260522") 

# +
#N409 van Nieuwegein naar Houten 10.4 bij Down under naar Essenkade

some_string="""ID	stroom	hm	ri	afop	estfrID	IDsinds
PUT01_N409.01_0	n409	104	r	t
PUT01_N409.01_2	n409	104	l	t
PUT01_PUVIS_N409.07_0_2	n409	123	r	t
PUT01_PUVIS_N409.07_1_2	n409	123	l	t
PUT01_N229.05_0	n229	673	r	t		
PUT01_N229.05_1	n229	673	l	t		
PUT01_N410.03_0	n410	14	r	t		
PUT01_N410.03_1	n410	14	r	t		
PUT01_N410.12_0	n410	40	r	t		
PUT01_N410.12_1	n410	40	l	t		
PUT01_PUVIS_N229.13_0_2	n229	1484	r	t		
PUT01_PUVIS_N229.13_1_2	n229	1484	l	t		"""
#read CSV string into pandas DataFrame
htn25put_config= pd.read_csv(io.StringIO(some_string), sep="\t")
#display(a12bnk_config)
rdathtn25s2=ndwimport.merge_initest(idfhtn25s2,htn25put_config)
# -

ndwimport.summstr_normprep(rdathtn25s2,'n409','Intensiteit',[],['ID'],False)    

ndwimport.ilowhihmplt(rdathtn25s2,'n409','Intensiteit',['perstart'])   

ndwimport.dlowhiaxplt(rdathtn25s2,'n409','Intensiteit',['uur'],False,True)   

ndwimport.ilowhihmplt(rdathtn25s2,'n410','Intensiteit',['perstart'])   



# +
#nu wat A12 rond bunnik
# -

testbnk="../data/intensiteit-snelheid-a12bnk-2025-s2.xlsx"
odfbnk= ndwimport.ndw_od_read_overzicht(testbnk,"locbnk","testcoll20260522")    
#odfbnk=odfbnk[odfbnk['Lengtegraad']>5]
#odfbnk=odfbnk[odfbnk['Breedtegraad']>52.05]

if (not suprtests):
    pland= odfbnk.plot(alpha=0.4)
    cx.add_basemap(pland, source= ndwimport.prov0,crs=odfbnk.crs)

odfbnk

idfbnk=ndwimport.ndw_od_read_overzicht_en_intensiteiten(testbnk,"testseq1","testcoll20260521")
idfbnk


# +
def sel3let(cfg,sel):
    return cfg[cfg['ID'].str[0:3] == sel]

sns.lineplot(data=sel3let(idfbnk,'PUT'),x="uur",y="Intensiteit",hue="ID")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
# -

if (not suprtests):
    fig, ax = plt.subplots()
    pland= sel3let(odfbnk,'GEO').plot(alpha=0.4,color='red',ax=ax)
    pland= sel3let(odfbnk,'RWS').plot(alpha=0.4,color='blue',ax=ax)
    cx.add_basemap(pland, source= ndwimport.prov0,crs=odfbnk.crs)

some_string="""ID	stroom	hm	ri	afop	estfrID	IDsinds
GEO1A_A_RWS_360159	a12	678	r	af		
GEO1A_A_RWS_360160	a12	677	l	op		
GEO1A_A_RWS_360181	a12	677	l	af		
GEO1A_A_RWS_360183	a12	678	r	op		
PUT01_N229.03_0	n229	600	r	t		2016-04-06
PUT01_N229.03_2	n229	600	l	t		2016-04-06
PUT01_N229.05_0	n229	673	r	t		
PUT01_N229.05_1	n229	673	l	t		
PUT01_N410.12_0	n410	401	r	t		
PUT01_N410.12_1	n410	401	l	t		
PUT01_PUVIS_N229.13_0_2	n229	1484	r	t		
PUT01_PUVIS_N229.13_1_2	n229	1484	l	t		
RWS01_MONIBAS_0121hrl0677ra	a12	677	l	d		
RWS01_MONIBAS_0121hrl0680ra	a12d	680	l	d		
RWS01_MONIBAS_0121hrl0696ra	a12	696	l	t		
RWS01_MONIBAS_0121hrr0677ra	a12	678	r	d		
RWS01_MONIBAS_0121hrr0682ra	a12	682	r	t		
RWS01_MONIBAS_0121hrr0696ra	a12	696	r	t		
RWS01_MONICA_00D00C0A9437D0070007	a12u	660	r	d		
RWS01_MONICA_00D00C0A9437D007000B	a12u	662	r	d		
RWS01_MONICA_00D00C0A9437D007000F	a12u	662	r	d		
RWS01_MONICA_00D00C0A9437D0070013	a12u	662	r	d		"""
#read CSV string into pandas DataFrame
a12bnk_config= pd.read_csv(io.StringIO(some_string), sep="\t")
display(a12bnk_config)
rdata12bnki=ndwimport.merge_initest(idfbnk,a12bnk_config)

rdata12y25=rdata12my[rdata12my['perstart'].dt.year.isin([2025]) ]
#display(rdata12y25)
rdata12bnk= pd.concat([rdata12bnki,rdata12y25])

rdata12bnk['lbl']=rdata12bnk['stroom']+rdata12bnk['ri']+((rdata12bnk['hm'].astype(str)))+ rdata12bnk['afop']
#display(rdata12bnk)
sns.lineplot(data=sel3let(rdata12bnk,'RWS'),x="uur",y="Intensiteit",hue="lbl",style="ri")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

sns.lineplot(data=sel3let(rdata12bnk,'GEO'),x="uur",y="Intensiteit",hue="lbl",style="afop")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

ndwimport.summstr_normprep(rdata12bnk,'a12','Intensiteit',[],['ID'],False) 

ndwimport.ilowhihmplt(rdata12bnk,'a12','Intensiteit',['perstart'])    

ndwimport.ilowhihmplt(rdata12bnk,'n229','Intensiteit',['perstart'])   

rdathtn25s2=rdathtn25s2[rdathtn25s2['perstart'].dt.year.isin([2025]) ]
#display(rdata12y25)
rdatnodijk= pd.concat([rdata12bnki,rdathtn25s2])

ndwimport.summstr_normprep(rdatnodijk,'n410','Intensiteit',[],['ID'],False)  

ndwimport.ilowhihmplt(rdatnodijk,'n410','Intensiteit',['perstart'])  

sns.lineplot(data=rdatnodijk[rdatnodijk['stroom']=='n410'],x="uur",y="Intensiteit",hue="perstart",style="ID")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

# +
#A12 noordelijke en zuidelijke lokale rijbanen
# -

a12bijlst= (glob.glob("../data/intensiteit-snelheid-a12?bij-20??-s1.xlsx"))
a12bijlst

idfa12bijmy =[ ndwimport.ndw_od_read_overzicht_en_intensiteiten(testfil,"a12bijmy",testfil) for testfil in a12bijlst ]
idfa12bijmy=pd.concat(idfa12bijmy)

if (not suprtests):
    odf120= ndwimport.ndw_od_read_overzicht(a12bijlst[0],"testseq120","testcoll20260522")
    odf121= ndwimport.ndw_od_read_overzicht(a12bijlst[1],"testseq121","testcoll20260522")
    odf12=pd.concat([odf121,odf120])
    odf12=odf12[odf12["ID"].str[0:3] != "PUT"]
    pland= odf12.plot(alpha=0.4)
    cx.add_basemap(pland, source= ndwimport.prov0,crs=odf12.crs)

# +
some_string="""ID	stroom	hm	ri	afop	estfrID	IDsinds
GEO1A_A_RWS_400003	a12z	604	r	t		
RWS01_MONIBAS_0120vwx0604ra	a12z27	604	r	t		
RWS01_MONIBAS_0120vwa0607ra	a12z27	608	r	a		
RWS01_MONIBAS_0120vwx0608ra	a12z27	608	r	d		
RWS01_MONIBAS_0120vwx0611ra	a12z27	611	r	t		
RWS01_MONIBAS_0120vwx0614ra	a12z27	614	r	t		
GEO1A_R_RWSTI4156	a12z27	614	r	o		
RWS01_MONIBAS_0120vwx0618ra	a12z27	617	r	t		
RWS01_MONIBAS_0120vwx0621ra	a12z27	621	r	t		
RWS01_MONIBAS_0120vwe0623ra	a12z27	623	r	t		
RWS01_MONIBAS_0120vwx0623ra	a12z27	623	r	a		
RWS01_MONIBAS_0120vwe0624ra	a12z27	624	r	t		
GEO0K_K_RWSTI359888	a12z27	629	r	t		
RWS01_MONICA_10D00C09B400B8200187	a12z2	621	r	t		
PUT01_PUVIS_N408.05_1_2	n409	4	l	t		
PUT01_PUVIS_N408.05_0_2	n409	4	r	t		
PUT01_N408.03_3	n409	9	l	t		
PUT01_N408.03_0	n409	9	r	t		
PUT01_N408.01_1	n409	26	l	t		
PUT01_N408.01_0	n409	26	r	t		
GEO0K_K_RWSTI359886	a27i	604	l	t		
GEO0K_K_RWSTI359894	a12n	623	l	o		
GEO0K_R_RWSTI4407	a12n	623	l	a		
GEO1A_R_RWSTI4155	a12n	608	l	a		
GEO1A_R_RWSTI4172	a12n	612	l	o		
RWS01_MONIBAS_0120vwy0608ra	a12n	608	l	t		
RWS01_MONIBAS_0120vwy0612ra	a12n	612	l	t		
RWS01_MONIBAS_0120vwy0619ra	a12n	619	l	t		
RWS01_MONIBAS_0120vwy0623ra	a12n	623	l	t		
RWS01_MONIBAS_0120vwy0627ra	a12n	627	l	t		
RWS01_MONIBAS_0120vwy0632ra	a12n	632	l	t		
RWS01_MONIBAS_0120vwy0632rb	a12n	632	l	t		
RWS01_MONIBAS_0270vwn0706ra	a12n	706	l	t		
RWS01_MONIBAS_0270vwq0704ra	a12n	704	l	t		
RWS01_MONIBAS_0270vwv0712ra	a12n	712	l	t		
RWS01_MONICA_00D01B0B2000A8200007	a12nx	712	l	o		
RWS01_MONICA_10D00C097037C0200011	a12nx	605	l	t		
RWS01_MONICA_10D00C097419C0200011	a12nx	605	l	t		"""
#read CSV string into pandas DataFrame
a12lcons_config= pd.read_csv(io.StringIO(some_string), sep="\t")
display(a12lcons_config)

rdata12bijmy=ndwimport.merge_initest(idfa12bijmy,a12lcons_config)
# -

ndwimport.ilowhihmplt(rdata12bijmy,'a12z27','Intensiteit',['perstart'])   

ndwimport.ilowhihmplt(rdata12bijmy,'a12n','Intensiteit',['perstart'])  

ndwimport.ilowhihmplt(rdata12bijmy,'n409','Intensiteit',['perstart'])  



# +
#ijsselstein
# -

ijstlst= (glob.glob("../data/intensiteit-snelheid-ijsst-20??-s1.xlsx"))
ijstlst

idfijstmy =[ ndwimport.ndw_od_read_overzicht_en_intensiteiten(testfil,"a12bijmy",testfil) for testfil in ijstlst ]
idfijstmy=pd.concat(idfijstmy)

if (not suprtests):
    odfijst= ndwimport.ndw_od_read_overzicht(ijstlst[0],"testseq12","testcoll20260522")
    pland= odfijst.plot(alpha=0.4)
    cx.add_basemap(pland, source= ndwimport.prov0,crs=odf12.crs)

# +
some_string="""ID	stroom	hm	ri	afop	estfrID	IDsinds
GEO1A_A_RWS_359612	a2	685	r	af		
GEO1A_A_RWS_359616	a2	685	r	op		
PUT01_N210.29_0	n210	495	r	t		
PUT01_N210.29_3	n210	495	l	t		
PUT01_N210.31_0	n210	420	r	t		
PUT01_N210.31_1	n210	420	l	t		
PUT01_N210.39_0	n210	488	r	t		
PUT01_N210.39_2	n210	488	l	t		
PUT01_N228.39_0	n228	250	r	t		
PUT01_N228.39_1	n228	250	l	t		
PUT01_PUVIS_N210.37_0_2	n210	473	r	t		
PUT01_PUVIS_N210.37_1_2	n210	473	l	t		
PUT01_PUVIS_N228.27_0_2	n228	202	r	t		
PUT01_PUVIS_N228.27_1_2	n228	202	l	t		
RWS01_MONIBAS_0021hrr0669ra	a2	669	r	t		
RWS01_MONIBAS_0021hrr0685ra	a2	685	r	d		
RWS01_MONIBAS_0021hrr0689ra	a2	689	r	t		
RWS01_MONIBAS_0021hrr0696ra	a2	696	r	t		"""
#read CSV string into pandas DataFrame
ijsta2cons_config= pd.read_csv(io.StringIO(some_string), sep="\t")
display(ijsta2cons_config)

rdataijsta2=ndwimport.merge_initest(idfijstmy,ijsta2cons_config)
# -

ndwimport.ilowhihmplt(rdataijsta2,'a2','Intensiteit',['perstart'])   

ndwimport.ilowhihmplt(rdataijsta2,'n210','Intensiteit',['perstart'])  

ndwimport.ilowhihmplt(rdataijsta2,'n228','Intensiteit',['perstart'])  


