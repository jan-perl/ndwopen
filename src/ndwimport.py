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

myname='ndwimport'
suprtests= myname in rdwbas.suprtests 
suprdata= myname in rdwbas.suprdata
#suprtests=True
print ('Suprtests',suprtests)

#testfil="../data/intensiteit-snelheid-a27htn-2025.xlsx"
testfil="../data/intensiteit-snelheid-a27-2025-s2.xlsx"


def ndw_od_read_overzicht(fn,setuid,collid):
    sh='Overzicht'
    df=pd.read_excel(fn,sheet_name=sh,skiprows=5)
    dfd=pd.read_excel(fn,sheet_name=sh,nrows=3,header=None).T
    dfd.columns = dfd.iloc[0,]
    dfd=dfd[1:2]
    dfd['setuid']=setuid
    dfd['perstart'] = pd.to_datetime(dfd['Periode'].str[0:10],format="%d-%m-%Y")
    dfd['perend'] = pd.to_datetime(dfd['Periode'].str[-10:],format="%d-%m-%Y")+pd.DateOffset(days=1)
    #print(dfd)
    #print(dfd.dtypes)
    gdf = geopandas.GeoDataFrame(
      df, geometry=geopandas.points_from_xy(df.Lengtegraad, df.Breedtegraad), crs="EPSG:4326")
    gdf['setuid']=setuid
    gdf['collid']=collid
    gdf=gdf.merge(dfd,how='left')
    return gdf
odf= ndw_od_read_overzicht(testfil,"testseq1","testcoll20260521")
odf

prov0=cx.providers.nlmaps.grijs.copy()
print( odf.crs)
plot_crs=3857
#data_crs="epsg:28992"
if 1==1:
#    prov0['url']='https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/{variant}/EPSG:28992/{z}/{x}/{y}.png'
    prov0['url']='https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/{variant}/EPSG:3857/{z}/{x}/{y}.png'    
#    prov0['bounds']=  [[48.040502, -1.657292 ],[56.110590 ,12.431727 ]]  
#    prov0['bounds']=  [[48.040502, -1.657292 ],[56.110590 ,12.431727 ]]  
    prov0['min_zoom']= 0
    prov0['max_zoom'] =12
    print (prov0)

if (not suprtests):
    pland= odf.plot(alpha=0.4)
    cx.add_basemap(pland, source= prov0,crs=odf.crs)


# +
def ndw_od_read_intensiteiten(fn,odfin):
    sh='Intensiteit'
    olen=len(odfin)
#    print(olen)
    headercol="Inheader"
    dfdd=[ pd.read_excel(fn,sheet_name=sh,skiprows = i*44+4,nrows=25).assign(iread=i) for i in range(0,olen)] 
    dfdi=[ pd.read_excel(fn,sheet_name=sh,skiprows = i*44+3,nrows=1,header=None,
                         names=[headercol],  usecols=[0]) .assign(iread=i) for i in range(0,olen)] 
    dfdc= [ d.merge(i,how='left') for d,i in zip ( dfdd,dfdi) ]
    
    dfd=pd.concat(dfdc).reset_index().drop(columns=['index'])
#    print(len(dfdi))
    dfd['ID']=dfd['Inheader'].str.replace('^.*\(','').str.replace('. op .*$','')
    dfd=dfd.merge(odfin,how='left')
    dfd['uur']=pd.to_numeric(dfd["uur op de dag"].str[0:2],errors='coerce')
    if 1==1:
        dfdc=dfd.copy(deep=True)
        dfdc['sperstart']=dfdc['perstart'].dt.strftime('%Y-%m-%d %H:%M:%S')
        dfdc['sperend']=(dfdc['perend'] - pd.to_timedelta(1, unit='s') ).dt.strftime('%Y-%m-%d %H:%M:%S')

        dfdc['exphdr']= 'Gemiddelde voertuigverdeling per uur van '+ dfdc['sperstart'] + ' tot ' + dfdc['sperend'] + ' voor ' + dfd['Naam'] + \
           ' ('+dfd['ID']+') op '+dfd['Dagen van de week']
        dfdc['dfdexpok']= dfdc['exphdr'] == dfdc['Inheader']
#        dfdc.to_excel('../intermediate/ndw_od_read_intensiteiten_test.xlsx')
    return dfd                        

idf= ndw_od_read_intensiteiten(testfil,odf)
#(idf)
# +
#idfh.dtypes
# -

def ndw_od_read_overzicht_en_intensiteiten(fn,setuid,collid):
    lodf= ndw_od_read_overzicht(fn,setuid,collid)
    df= ndw_od_read_intensiteiten(fn,lodf)
    df=df[df['uur'].isna() == False] 
    return df
idfh=ndw_od_read_overzicht_en_intensiteiten(testfil,"testseq1","testcoll20260521")
idfh

sns.lineplot(data=idfh,x="uur",y="Intensiteit",hue="ID")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)


# +
#let op: lijkt deels spitsstrook RWS01_MONIBAS_0270vwa0678ra	a27	678	r	af
#67.5 = zoutopslag na oprit 28 , 69.1 = Euretco, r = richting hogere getallen : noord (Euretco vanaf afslag 28)

#PUT01_PUVIS_N409.07_0_2	n409	7	r	t
#PUT01_PUVIS_N409.07_1_2	n409	7	l	t

some_string="""ID	stroom	hm	ri	afop	estfrID	IDsinds
GEO1A_A_RWS_359819	a27	681	l	op		2018-11-23
GEO1A_A_RWS_359850	a27	680	r	op		2019-03-01
GEO1A_A_RWS_359853	a27	681	l	af		2018-11-23
EST1A_A_EST_359850	a27	680	r	af	GEO1A_A_RWS_359819	2018-11-23
RWS01_MONIBAS_0270vwa0678ra	a27d	678	r	d
RWS01_MONIBAS_0271hrl0675ra	a27	675	l	t
RWS01_MONIBAS_0271hrl0681ra	a27	681	l	d
RWS01_MONIBAS_0271hrl0691ra	a27	691	l	t
RWS01_MONIBAS_0271hrr0674ra	a27	674	r	t
RWS01_MONIBAS_0271hrr0678ra	a27d	678	r	d
RWS01_MONIBAS_0271hrr0680ra	a27	680	r	d
RWS01_MONIBAS_0271hrr0691ra	a27	691	r	t
RWS01_MONIBAS_0271hrr0671ra_1	a27	671	r	t
RWS01_MONIBAS_0271hrl0669ra_1	a27	669	l	t
RWS01_MONIBAS_0271hrl0695ra	a27	695	l	t
RWS01_MONIBAS_0271hrr0697ra	a27	697	r	t"""
#read CSV string into pandas DataFrame
a27id_config= pd.read_csv(io.StringIO(some_string), sep="\t")
def merge_initest(df,cfg,addestrecs=True):
    cfg['IDsinds']=cfg['IDsinds'].mask(pd.isna(cfg['IDsinds']),"2000-01-01")
    cfg['IDsinds']=cfg['IDsinds'].mask(cfg['IDsinds']=="","2000-01-01")
    cfg['IDsinds']=pd.to_datetime(cfg['IDsinds'],format="%Y-%m-%d")
    rv=df.merge(cfg,how='left')    
    estrecm = cfg[cfg['ID'].str[0:3] == 'EST'].copy().rename(columns={'ID':'estID','estfrID':'ID'})
    if addestrecs & (len(estrecm)>0):
        estv=df.merge(estrecm,how='right').rename(columns={'ID':'estfrID','estID':'ID'})
        rv=pd.concat([rv,estv])
    #hier staan evenveel waarden als het originieel, met een schatting van het totaal
    #print(estv)
    return rv
a27dta=merge_initest(idfh,a27id_config)
display(a27id_config)
# -

calendafter=a27id_config['IDsinds'].max()

#to get ID list:
if (not suprtests):
    print(a27id_config[['ID']].to_csv(index=False))

# +
#a27dta.dtypes
# -



# +
iafopmap={'op':1,'af':-1,'t':0,'d':0}
def cumsumavg0(ser):
    st = pd.Series.cumsum(ser)
    st = st-st.mean()
    return  st

#split2 is subest vab ['afop','ID']: alleen voor debugging gebruiken
def summstr_normprep(strdfi,strval,ccol,split1,split2):
    nabefore=strdfi['IDsinds'].max()
    strdfr= strdfi[(strdfi['stroom']==strval) & (strdfi['perstart']>nabefore)].copy()
    #sommeer over periodes etc, maar niet over IDS
    agrps=['stroom','ri','hm']
    grps=split1+agrps
    strdf = strdfr.groupby(grps+['afop','ID']).agg('sum')[ccol].reset_index()
    strdf['isign'] =strdf['ri'].map( {'r':1,'l':-1 }) 
    strdf['iafop'] =strdf['afop'].map(iafopmap) 
    strdf['Ilow'] = np.where(strdf['iafop'],strdf['isign'] ==strdf['iafop'] ,1) * strdf[ccol]
    strdf['Ihigh'] = np.where(strdf['iafop'],strdf['isign'] == -strdf['iafop'] ,1) * strdf[ccol]        
    strdf['Idoor'] = np.where(strdf['iafop'] ==0 ,strdf[ccol],0)
    summs = strdf.groupby(grps+split2).agg('sum')[['isign','iafop','Ilow','Ihigh','Idoor']].reset_index()
    #nu per hm/ri
    grpsexhm=split1+['stroom','ri']    
    summs['cmpdiff'] = np.where(summs['isign'] >0 ,
                                summs.groupby(grpsexhm).shift(1,fill_value=np.nan)['Ihigh']- summs['Ilow'],
                                summs.groupby(grpsexhm).shift(1,fill_value=np.nan)['Ilow']- summs['Ihigh'])
    summs['cmpdiff'].fillna(0.0,inplace=True)     
    #vaklabels
    summs['hmstr']=summs['hm'].astype(str)+" "
    summs['cmpvak'] = np.where(summs['isign'] >0 ,
                                summs.groupby(grpsexhm).shift(1,fill_value=np.nan)['hmstr']+'-'+ summs['hmstr'],
                                summs.groupby(grpsexhm).shift(1,fill_value=np.nan)['hmstr']+'-'+ summs['hmstr'])    
#    summs['tocorr'] =summs.groupby(grpsexhm)['cmpdiff'].cumsum()
    summs['CorrDoor'] =summs.groupby(grpsexhm)['cmpdiff'].transform(cumsumavg0)
#    print (summs['tocorr'].sum() )
    summs['CorrDoor'] =1+summs['CorrDoor'] /summs['Idoor'] 
    return summs
    
summstr_normprep(a27dta,'a27','Intensiteit',[],['ID'])    
#summstr_normprep(a27dta,'a27','Intensiteit',[],[])    
#summstr(a27dta,'a27','Intensiteit',[],[])    
# -

def ilowhihmplt(strdfi,strval,ccol,split1):
    a27dtas=summstr_normprep(strdfi,strval,ccol,split1,[]).reset_index()
    a27dtas['opdel']=  a27dtas['stroom'] + a27dtas['ri'] 
    if len(split1)==1:
        a27dtas['opdel']=a27dtas['opdel'] + (a27dtas[split1[0]].astype(str))
#    display(a27dtas)
    fig, ax = plt.subplots()
    sns.lineplot(data=a27dtas,x="hm",y="Ilow",hue="opdel",ax=ax)
    sns.lineplot(data=a27dtas,x="hm",y="Ihigh",hue="opdel",ax=ax)
    ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
ilowhihmplt(a27dta,'a27','Intensiteit',['perstart'])              


# +
def corrcol(strdfi,strval,ccol,facts,ccol2):
    factscols=['stroom','ri','hm','CorrDoor']
    udf= strdfi.merge(facts[factscols],how='left')
    iafop = udf['afop'].map(iafopmap) 
    docorr = np.where(np.isnan (iafop),0,iafop==0)
    udf[ccol2] = udf[ccol] * np.where(docorr,udf['CorrDoor'],1)
#    display(udf[docorr==0])
    rv=udf.drop(['CorrDoor'],axis=1)
    return rv
    
usefacts1=summstr_normprep(a27dta,'a27','Intensiteit',[],[]).reset_index()    
cdata27=corrcol(a27dta,'a27','Intensiteit',usefacts1,'IntensiteitCorr')  
ilowhihmplt(cdata27,'a27','IntensiteitCorr',[])              


# -

def dlowhihmplt(strdfi,strval,ccol,split1):
    a27dtas=summstr_normprep(strdfi,strval,ccol,split1,[]).reset_index()
    a27dtas['opdel']=  a27dtas['stroom'] + a27dtas['ri'] 
    if len(split1)==1:
        a27dtas['opdel']=a27dtas['opdel'] + (a27dtas[split1[0]].astype(str))
    #display(a27dtas)    
    sns.lineplot(data=a27dtas,x="hm",y="cmpdiff",hue="opdel")
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#dlowhihmplt(a27dta,'a27','Intensiteit',[])   
dlowhihmplt(cdata27,'a27','IntensiteitCorr',[])  


# +
#heel veel lijntjes
#dlowhihmplt(a27dta,'a27','Intensiteit',['uur'])  

# +
#heel veel lijntjes
#dlowhihmplt(cdata27,'a27','IntensiteitCorr',['uur'])         
# -

def dlowhiaxplt(strdfi,strval,ccol,split1):
    a27dtas=summstr_normprep(strdfi,strval,ccol,split1,[]).reset_index()
    a27dtas['opdel']=  a27dtas['stroom'] + a27dtas['ri'] 
    if len(split1)==1:
        a27dtas['opdel']=a27dtas['opdel'] + (a27dtas['hm'].astype(str))
    #display(a27dtas)    
    a27dtas['cmprel'] = a27dtas['cmpdiff'] / (a27dtas['Ihigh'] +a27dtas['Ilow'] )
    sns.lineplot(data=a27dtas,x=split1[0],y="cmprel",hue="opdel")
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
dlowhiaxplt(cdata27,'a27','IntensiteitCorr',['uur'])            

dlowhiaxplt(cdata27,'a27','Intensiteit',['uur'])      


# +
#cdata27.dtypes
# -

#nu de EST_xx IDs
def estcol(strdfi,strval,ccol,ccol2):
    nabefore=strdfi['IDsinds'].max()
    split0=['perstart','perend']
    split1=split0+['uur']
#    strdfs= strdfi[strdfi['perstart']>nabefore]
    strdfs= strdfi[strdfi['perstart']>nabefore]
    factsag=summstr_normprep(strdfs,strval,ccol,split1,[]).reset_index()    
    agrps=['stroom','ri','hm']
    factsagsel=factsag[split1+agrps+["cmpdiff"]].rename(columns={"cmpdiff":"cmpdiffsec"})
    factsai=summstr_normprep(strdfs,strval,ccol,split1,['ID']).reset_index()    
    factse=factsai[factsai['ID'].str[0:3] == 'EST'].merge(factsagsel,how='left')    
    factsechk=factse.groupby(split0+agrps+['ID'])["cmpdiffsec"].agg("sum")
    factse=factse[split1+['ID',"cmpdiffsec"]]
    display(factsechk)    
    udf= strdfi.merge(factse,how='left')
    udf[ccol2] = np.where(udf['perstart']<=nabefore,np.nan,
                          udf[ccol]+np.where(np.isnan(udf['cmpdiffsec']),0, udf['cmpdiffsec'])  )         
#    display(udf[docorr==0])
    rv=udf.drop(['cmpdiffsec'],axis=1)
    return rv
edata27=estcol(cdata27,'a27','IntensiteitCorr','IntensiteitEst') 
#edata27.sum()

dlowhiaxplt(edata27,'a27','IntensiteitCorr',['uur'])  

dlowhiaxplt(edata27,'a27','IntensiteitEst',['uur'])  


def plttimesest3c(dfin):
    dfplt=dfin[dfin['ID'].str[0:3] == 'EST']
    sns.lineplot(data=dfplt,x='uur',y='Intensiteit',label='Tegenrichting',alpha=0.6)
    sns.lineplot(data=dfplt,x='uur',y='IntensiteitCorr',label='TegenrichtingCorr',alpha=0.6)
    sns.lineplot(data=dfplt,x='uur',y='IntensiteitEst',label='IntensiteitEst',alpha=0.6)
plttimesest3c(edata27)    



# +
#a27 data several years
# -

xlsa27s2list= (glob.glob("../data/intensiteit-snelheid-a27-20??-s2.xlsx"))
xlsa27s2list

idfa27my =[ ndw_od_read_overzicht_en_intensiteiten(testfil,"a27my",testfil) for testfil in xlsa27s2list ]
idfa27my=pd.concat(idfa27my)
#idfhmy.dtypes

rdata27my=merge_initest(idfa27my,a27id_config)
#rdata27my

usefacts1my=summstr_normprep(rdata27my[rdata27my["perend"]>calendafter],
                             'a27','Intensiteit',[],[]).reset_index()    
#display(usefacts1my)
cdata27my=corrcol(rdata27my,'a27','Intensiteit',usefacts1my,'IntensiteitCorr')  
ilowhihmplt(cdata27my,'a27','IntensiteitCorr',['perstart'])              

edata27my=estcol(cdata27my,'a27','IntensiteitCorr','IntensiteitEst') 
#edata27.sum()

ilowhihmplt(edata27my,'a27','IntensiteitEst',['perstart']) 


def plttimesestmy(dfin,col):
    dfplt=dfin[dfin['ID'].str[0:3] == 'EST']
    sns.lineplot(data=dfplt,x='uur',y=col,hue='perstart')
plttimesestmy(edata27my,'Intensiteit')  

plttimesestmy(edata27my,'IntensiteitEst')  

edata27myd = edata27my.copy();
edata27myd['IntensiteitEstDiff'] = edata27myd['IntensiteitEst']  - edata27myd['Intensiteit'] 
plttimesestmy(edata27myd,'IntensiteitEstDiff')  


def plttimeshmmy(dfin,hmval,col):
    fig, ax = plt.subplots()
    dfplt=dfin[dfin['hm'] == hmval]
    sns.lineplot(data=dfplt,x='perstart',y=col,hue='uur',style='ID',alpha=0.6,ax=ax)
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plttimeshmmy(edata27my[edata27my['uur'].isin([14,15,16])],680,'IntensiteitEst') 

edata27my.dtypes



# +
def _scaledr27(x):
            return x *0.25
def _scaledrinv27(x):
            return x * 4

def pltjaaropaf(dfin,strval,col,hmset, _scaledr,_scaledrinv,titletxt):
    strdfi=dfin[dfin['hm'].isin(hmset)]
    dfplt= strdfi[strdfi['stroom']==strval]
    a27dtas=dfplt.groupby(['ri','hm','afop','ID','perstart'])[col].agg('sum').reset_index()
    a27dtas['opdel']=   a27dtas['ri'] + (a27dtas['hm'].astype(str))+ " " +a27dtas['afop'] +\
          " " + a27dtas['ID'].str[0:3]  
    a27dtas[col] *= np.where(a27dtas['afop'].isin(['d']),_scaledr(1),1)
    fig, ax1 = plt.subplots()
    if 1==1:
        lp=sns.lineplot(data=a27dtas,
                     x='perstart',y=col,hue='opdel',style="afop",ax=ax1)
        ax1.set_title(titletxt)

        secax = lp.secondary_yaxis('right', functions=(_scaledrinv, _scaledr))
        lp.set_ylabel('aantallen werkdagen op/af')
        secax.set_ylabel('aantallen werkdagen door')
    else:        
        ax2 = ax1.twinx()
        sns.lineplot(data=a27dtas[a27dtas['afop'].isin(['d'])==False],
                     x='perstart',y=col,hue='opdel',style="afop",ax=ax1)
        sns.lineplot(data=a27dtas[a27dtas['afop'].isin(['d'])],
                     x='perstart',y=col,hue='opdel',style="afop",ax=ax2)
    ax1.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=4.)
    
pltjaaropaf(edata27my,'a27','IntensiteitEst',[680,681],_scaledr27, _scaledrinv27,
            "A27 afrit Houten opaf en door/4 :  l: zuidwaarts, r : noordwaards" )

# +
#zelfde verhaal. A12 check
# -

xlsa12s1list= (glob.glob("../data/intensiteit-snelheid-a12-20??-s1.xlsx"))
xlsa12s1list

testfil12=xlsa12s1list[1]

idfa12=ndw_od_read_overzicht_en_intensiteiten(testfil12,"testseq12","testcoll20260522")
#display(idfa12)

odf12= ndw_od_read_overzicht(testfil12,"testseq12","testcoll20260522")
if (not suprtests):
    pland= odf12.plot(alpha=0.4)
    cx.add_basemap(pland, source= prov0,crs=odf.crs)

idfa12my =[ ndw_od_read_overzicht_en_intensiteiten(testfil,"a12my",testfil) for testfil in xlsa12s1list ]
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

rdata12my=merge_initest(idfa12my,a12id_config)
# -

print("Klaar")
