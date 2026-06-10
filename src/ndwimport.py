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
#a27 data several years
#noot: veel lagere waarde voor 2012 voor: RWS01_MONIBAS_0271hrl0669ra_1 	35158.9 	57263.6 
# -

xlsa27s2list= (glob.glob("../data/intensiteit-snelheid-a27-20??-s2.xlsx"))
xlsa27s2list

idfa27my =[ ndw_od_read_overzicht_en_intensiteiten(testfil,"a27my",testfil) for testfil in xlsa27s2list ]
idfa27my=pd.concat(idfa27my)
#idfhmy.dtypes

# +
#de 2 punten bij 687 worden niet gebruikt
#let op: lijkt deels spitsstrook RWS01_MONIBAS_0270vwa0678ra	a27	678	r	af
#67.5 = zoutopslag na oprit 28 , 69.1 = Euretco, r = richting hogere getallen : noord (Euretco vanaf afslag 28)
#deze 2 waren in gebruik tot dat in 2019 de tellers bij de aansluiting startten

#PUT01_PUVIS_N409.07_0_2	n409	7	r	t
#PUT01_PUVIS_N409.07_1_2	n409	7	l	t

some_string="""ID	stroom	hm	ri	afop	estfrID	IDsinds
GEO1A_A_RWS_359819	a27	681	l	op		2018-11-23
GEO1A_A_RWS_359850	a27	680	r	op		2019-03-01
GEO1A_A_RWS_359853	a27	681	l	af		2018-11-23
EST1A_A_EST_359850	a27	680	r	af	GEO1A_A_RWS_359819	2018-11-23
RWS01_MONIBAS_0270vwa0678ra	a27d	678	r	d
RWS01_MONIBAS_0271hrl0675ra	a27d	675	l	t		2017-10-24
RWS01_MONIBAS_0271hrl0681ra	a27	681	l	d
RWS01_MONIBAS_0271hrl0691ra	a27	691	l	t
RWS01_MONIBAS_0271hrr0674ra	a27	674	r	t
RWS01_MONIBAS_0271hrr0678ra	a27d	678	r	d
RWS01_MONIBAS_0271hrr0680ra	a27	680	r	d
RWS01_MONIBAS_0271hrr0691ra	a27	691	r	t
RWS01_MONIBAS_0271hrr0671ra_1	a27	671	r	t
RWS01_MONIBAS_0271hrl0669ra_1	a27	669	l	t
RWS01_MONIBAS_0271hrl0695ra	a27	695	l	t
RWS01_MONIBAS_0271hrr0697ra	a27	697	r	t
RWS01_MONIBAS_0271hrr0685ra	a27o	685	r	t
RWS01_MONIBAS_0271hrl0685ra	a27o	685	l	t"""
#read CSV string into pandas DataFrame
a27id_config= pd.read_csv(io.StringIO(some_string), sep="\t")
display(a27id_config)


# -

#koppelt config aan data
#maakt extra records aan voor estfrID records en kopieert records naar voor de meetperiode
def merge_initest(df,cfg,addestrecs=True):
    cfg['IDsinds'].fillna("2000-01-01",inplace=True)
    cfg['IDsinds']=cfg['IDsinds'].mask(cfg['IDsinds']=="","2000-01-01")
    cfg['IDsinds']=pd.to_datetime(cfg['IDsinds'],format="%Y-%m-%d")
    rv=df.merge(cfg,how='left')    

    cfg['estfrID'].fillna("",inplace=True)
    estrecm = cfg[cfg['estfrID'] != ""] [['ID','estfrID']]
    if addestrecs & (len(estrecm)>0):
        print ('adding placeholder for estimates' ,estrecm)
        estv=df.rename(columns={'ID':'estfrID'}).merge(estrecm,how='right')
        estv=estv.merge(cfg,how='left') 
        rv=pd.concat([rv,estv])

    foundpers=rv.groupby(['perstart','perend'])['Intensiteit'].agg('count').reset_index()
#    display(foundpers.iloc[-1,])
    refper=foundpers.iloc[-1,]
    for idx,row in foundpers.iterrows():
        replids=cfg[ (row['perend'] <= cfg['IDsinds'])  ]['ID'].to_list()
        if len(replids):
            print ('replacing' ,replids, row['perend'])
            estv=rv[ (rv['ID'].isin(replids)) & (rv['perstart'] == refper['perstart'] )& (rv['perend'] == refper['perend'] )].copy()
            estv['perstart'] =row['perstart'] 
            estv['perend'] =row['perend'] 
            kv=rv[ (rv['ID'].isin(replids) ==False) | (rv['perstart'] != row['perstart'] )| (rv['perend'] != row['perend'] )]
            display (estv[['ID','Intensiteit']])
            rv=pd.concat([kv,estv])
    #hier staan evenveel waarden als het originieel, met een schatting van het totaal
    #print(estv)
    return rv
#a27dta=merge_initest(idfh,a27id_config)
rdata27my=merge_initest(idfa27my,a27id_config)
a27dta=rdata27my[rdata27my['perstart'].dt.year.isin((2017,2025))]


def calendafter(datdf):
    return datdf['IDsinds'].max()


# +
#rdata27my=merge_initest(idfa27my,a27id_config)
#rdata27my
# -

rd1=rdata27my[rdata27my['perstart'].dt.year<=2099].groupby(["stroom","ID","perstart"])[["Intensiteit"]].sum().reset_index()
rd2=rd1.pivot(index='ID', columns='perstart', values='Intensiteit')
rd2

#to get ID list:
if (not suprtests):
    print(a27id_config[['ID']].to_csv(index=False))

# +
#a27dta.dtypes
# -



# +
iafopmap={'op':1,'af':-1,'t':0,'d':0}
isignmap={'r':1,'l':-1 }
debugCorrD=False
def cumsumavg0(ser):
    st = pd.Series.cumsum(ser)
    st = st-st.mean()
    if (debugCorrD):
        print ('cumsumavg0',ser.to_list(),"->",st.to_list(),'=',st.sum())
    return  st

#cmpdiff is intensiteit lagere hm  - intensiteit deze hm , waarbij aftakkend verkeer wordt meegeteld in goede richting
#berekent CorrDoor factoren op basis van data na nabefore, of 
#split2 is subest vak ['afop','ID']: alleen voor debugging gebruiken anders altijd []
def summstr_normprep(strdfi,strval,ccol,split1,split2,keepearly):
    nabefore=strdfi['IDsinds'].max()
    strdfr= strdfi[(strdfi['stroom']==strval) & 
                   ((strdfi['perend']>nabefore) | keepearly)].copy()
    #sommeer over periodes etc, maar niet over IDS
    agrps=['stroom','ri','hm']
    grps=split1+agrps
    strdf = strdfr.groupby(grps+['afop','ID']).agg('sum')[ccol].reset_index()
    strdf['isign'] =strdf['ri'].map(isignmap) 
    strdf['iafop'] =strdf['afop'].map(iafopmap) 
    strdf['Ilow'] = np.where(strdf['iafop'],strdf['isign'] ==strdf['iafop'] ,1) * strdf[ccol]
    strdf['Ihigh'] = np.where(strdf['iafop'],strdf['isign'] == -strdf['iafop'] ,1) * strdf[ccol]        
    strdf['Idoor'] = np.where(strdf['iafop'] ==0 ,strdf[ccol],0)
    summs = strdf.groupby(grps+split2).agg('sum')[['isign','iafop','Ilow','Ihigh','Idoor']].reset_index()
    #nu per hm/ri
    grpsexhm=split1+['stroom','ri']    
    sshift1=summs.groupby(grpsexhm).shift(1,fill_value=np.nan)
    summs['cmpdiff'] = np.where(summs['isign'] >0 ,
           sshift1['Ihigh']- summs['Ilow'],
           sshift1['Ilow']- summs['Ihigh'])
    summs['cmpdiff'].fillna(0.0,inplace=True)     
    #vaklabels
    summs['hmstr']=summs['hm'].astype(str)+" "
    sshift1=summs.groupby(grpsexhm).shift(1,fill_value=np.nan)
    summs['cmpvak'] = np.where(summs['isign'] >0 ,
           sshift1['hmstr']+'-'+ summs['hmstr'],
           sshift1['hmstr']+'-'+ summs['hmstr'])    
#    summs['tocorr'] =summs.groupby(grpsexhm)['cmpdiff'].cumsum()
    sshift1=summs.groupby(grpsexhm).shift(0,fill_value=np.nan).reset_index()
    summs['CorrDoorAbs'] =sshift1['cmpdiff']
#    display(summs)
    summs['CorrDoorAbs'] =summs.groupby(grpsexhm)['CorrDoorAbs'].transform(cumsumavg0)
#    print (summs['tocorr'].sum() )
    summs['CorrDoor'] =1+summs['CorrDoorAbs'] /summs['Idoor']
    if (debugCorrD):
        summs['ResDoor'] =summs['CorrDoor'] *summs['Idoor'] 
    else:
        summs=summs.drop(['CorrDoorAbs'],axis=1)
    return summs
    
#summstr_normprep(a27dta,'a27','Intensiteit',[],['ID'],False)    
summstr_normprep(a27dta,'a27','Intensiteit',[],[],False)    
#summstr(a27dta,'a27','Intensiteit',[],[])    
# -

def ilowhihmplt(strdfi,strval,ccol,split1):
    a27dtas=summstr_normprep(strdfi,strval,ccol,split1,[],False).reset_index()
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
#maak een nieuwe kolom aan waarbij de meetdata DOORgaande stromen gecorrigeerd zijn voor CorrDoor
#en plot deze om te zien dat ervoor en erna inderdaad vlakke stukken ontstaan
def corrcol(strdfi,strval,ccol,facts,ccol2):
    factscols=['stroom','ri','hm','CorrDoor']
    udf= strdfi.merge(facts[factscols],how='left')
    iafop = udf['afop'].map(iafopmap) 
    docorr = np.where(np.isnan (iafop),0,iafop==0)
    udf[ccol2] = udf[ccol] * np.where(docorr,udf['CorrDoor'],1)
#    display(udf[docorr==0])
    rv=udf.drop(['CorrDoor'],axis=1)
    return rv
    
usefacts1=summstr_normprep(a27dta,'a27','Intensiteit',[],[],False).reset_index()    
cdata27=corrcol(a27dta,'a27','Intensiteit',usefacts1,'IntensiteitCorr')  
ilowhihmplt(cdata27,'a27','IntensiteitCorr',[])              


# -

#op de te corrigeren waarden zou voor de hele periode een volgende correctie nul worden
#controleer dat cmpdiff van die gecorrigeerde waarden inderdaad rekenruis wordt
def dlowhihmplt(strdfi,strval,ccol,split1):
    a27dtas=summstr_normprep(strdfi,strval,ccol,split1,[],False).reset_index()
    a27dtas['opdel']=  a27dtas['stroom'] + a27dtas['ri'] 
    if len(split1)==1:
        a27dtas['opdel']=a27dtas['opdel'] + (a27dtas[split1[0]].astype(str))
    #display(a27dtas)    
    sns.lineplot(data=a27dtas,x="hm",y="cmpdiff",hue="opdel")
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    assert(a27dtas['cmpdiff'].abs().max() < 1e-6)
#dlowhihmplt(a27dta,'a27','Intensiteit',[])   
dlowhihmplt(cdata27,'a27','IntensiteitCorr',[])  


# +
#heel veel lijntjes
#dlowhihmplt(a27dta,'a27','Intensiteit',['uur'])  

# +
#heel veel lijntjes
#dlowhihmplt(cdata27,'a27','IntensiteitCorr',['uur'])         
# -

#de afwijkingen na correctie per uur
#per uur zou dit ook soort of uit moeten middelen, behalve voor estfrID en waarden van voor de periode
def dlowhiaxplt(strdfi,strval,ccol,split1,keepearly,plotooknietoprit):
    a27dtas=summstr_normprep(strdfi,strval,ccol,split1,[],keepearly).reset_index()
    a27dtas['opdel']=  a27dtas['stroom'] + a27dtas['ri'] 
    if len(split1)==1:
        a27dtas['opdel']=a27dtas['opdel'] + (a27dtas['hm'].astype(str))
    #display(a27dtas)    
    print(("Gemmiddeld verschil (rekenruis) : ",a27dtas['cmpdiff'].sum() / (a27dtas['Ihigh'] +a27dtas['Ilow'] ).sum() ))
    a27dtas['cmprel'] = a27dtas['cmpdiff'] / (a27dtas['Ihigh'] +a27dtas['Ilow'] )
    a27dtas['s2']  = plotooknietoprit | (np.abs(a27dtas['Ihigh'] -a27dtas['Ilow'] ) >1e-6) | \
        (np.abs(a27dtas.shift(1,fill_value=np.nan)['Ihigh'] -a27dtas.shift(1,fill_value=np.nan)['Ilow'] ) >1e-6)
    sns.lineplot(data=a27dtas[a27dtas['s2']],x=split1[0],y="cmprel",hue="opdel")
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
dlowhiaxplt(cdata27,'a27','IntensiteitCorr',['uur'],False,False)            

#ter informatie: de waarden die het zouden zijn zonder correctie: daar zitten nog trendmatige waarden  in
# die weg gecorrigeerd zijn in IntensiteitCorr
dlowhiaxplt(cdata27,'a27','Intensiteit',['uur'],False,False)      


# +
#cdata27.dtypes

# +
#nu de EST_xx IDs
def estcolonlye(strdfi,strval,ccol,ccol2):
    nabefore=strdfi['IDsinds'].max()
    split0=['perstart','perend']
    split1=split0+['uur']
#    strdfs= strdfi[strdfi['perstart']>nabefore]
#    strdfs= strdfi[strdfi['perend']>nabefore]
    strdfs= strdfi
    factsag=summstr_normprep(strdfs,strval,ccol,split1,[],True).reset_index()    
    agrps=['stroom','ri','hm']
    factsagsel=factsag[split1+agrps+["cmpdiff"]].rename(columns={"cmpdiff":"cmpdiffsec"})
    factsai=summstr_normprep(strdfs,strval,ccol,split1,['ID'],True).reset_index()    
    factse=factsai[factsai['ID'].str[0:3] == 'EST'].merge(factsagsel,how='left')    
    factsechk=factse.groupby(split0+agrps+['ID'])["cmpdiffsec"].agg("sum")
    factse=factse[split1+['ID',"cmpdiffsec"]]
    display(factsechk)    
    udf= strdfi.merge(factse,how='left')
    udf[ccol2] = np.where(udf['perend']<=nabefore,np.nan,
                          udf[ccol]+np.where(np.isnan(udf['cmpdiffsec']),0, udf['cmpdiffsec'])  )         
#    display(udf[docorr==0])
    rv=udf.drop(['cmpdiffsec'],axis=1)
    return rv

edata27=estcolonlye(cdata27,'a27','IntensiteitCorr','IntensiteitEst') 
#edata27.sum()

# +
#nu de EST_xx IDs, debug met 2 jaren, zonder uur
def estcol(strdfi,strval,ccol,ccol2):
    #nabefore=strdfi['IDsinds'].max()
    split0=['perstart','perend']
    split1=split0     +['uur']
#    strdfs= strdfi[strdfi['perstart']>nabefore]
#    strdfs= strdfi[strdfi['perend']>nabefore]
    strdfs= strdfi
    strdfs['estfrID'].fillna("",inplace=True)
    factsag=summstr_normprep(strdfs,strval,ccol,split1,[],True).reset_index()    
    agrps=['stroom','ri','hm']
    factsagsel=factsag[split1+agrps+["cmpdiff","cmpvak"]].\
         rename(columns={"cmpdiff":"cmpdiffsec","cmpvak":"cmpvaksec"})
    grpsexhm=split1+['stroom','ri']    
    sshift1=factsagsel.groupby(grpsexhm).shift(-1,fill_value=np.nan)
    factsagsel['cmpdiffoth'] =sshift1['cmpdiffsec']
    factsagsel['cmpvakoth'] =sshift1['cmpvaksec']
    #vergelijk met eigen hm (voorwaards) of met vorige
    factsai=summstr_normprep(strdfs,strval,ccol,split1,['ID'],True).reset_index()    
    #nu bij ieder ID ook het verschil voor het vak
    factse=factsai.merge(factsagsel)
    factse['Afopoffset']= factse['iafop'] * np.where(factse['iafop'] <0,
                              factse[ 'cmpdiffoth'] ,factse[ 'cmpdiffsec']  )    
    display(factse[factse['iafop']!=0])
    factsef=factse[split1+['ID',"Afopoffset"]]
    udf= strdfi.merge(factse,how='left')
    udf["Afopoffset"].fillna(0,inplace=True)    
    udf['usemask'] = (udf['perstart']<= udf['IDsinds'] )  | (udf['estfrID'] != "") 
    udf[ccol2] = udf[ccol]+ udf['Afopoffset'].where(udf['usemask'] ,0)
#    udf=udf.drop(['Afopoffset'],axis=1)
    rv= udf

    return rv

edata27=estcol(cdata27,'a27','IntensiteitCorr','IntensiteitEst') 
edata27.to_excel("../intermediate/test-2.xlsx")
#edata27.sum()

# +
#cdata27['estfrID'].to_list()

# +
def estcolchk(strdfi,strval,ccol,ccol2):
    strdfs=strdfi.copy()
    #check 1: same number of NAs
    c1 = strdfs.groupby(['perstart'])[[ccol,ccol2]].agg('count')
    display (c1)
    #check 2: changed
    strdfs['isadj']= (strdfs[ccol] - strdfs[ccol2]).abs() > 1e-6
    strdfs['dc']=(strdfs['perstart']<= strdfs['IDsinds'] )
    strdfs['dc']=(strdfs['estfrID'] != "" )
    c2 = strdfs.groupby(['perstart','ID','IDsinds','dc'])[['isadj']].agg('sum').reset_index()
    display (c2[c2['isadj'] !=0 ])
    strdfsch=strdfs[strdfs['isadj']]
    sns.scatterplot(data=strdfsch,x=ccol,y=ccol2,hue="ID",style="perstart")    

estcolchk(edata27,'a27','IntensiteitCorr','IntensiteitEst') 


# -

def estcolvchk(strdfi,strval,ccol,ccol2):
    strdfs=strdfi.copy()
    split0=['perstart','perend']
    split1=split0     +['uur']
    agrps=['stroom','ri','hm']
    #check 1: same number of NAs
    cvak=["cmpdiff"]
    factsag2=summstr_normprep(strdfs,strval,ccol2,split1,[],True)[split1+agrps+cvak] 
    factsag1=summstr_normprep(strdfs,strval,ccol, split1,[],True)[split1+agrps+cvak] 
    factsag1= factsag1.rename(columns={"cmpdiff":"cmpdiff_"+ccol})
    factsag2= factsag2.rename(columns={"cmpdiff":"cmpdiff_"+ccol2})
    #display(factsag1.dtypes)
    factsag=factsag1.merge(factsag2)
    
    c1 = factsag.groupby(['perstart'])[["cmpdiff_"+ccol,"cmpdiff_"+ccol2]].agg('count')
    display (c1)
    #check 2: changed
    factsag['isadj']= (factsag["cmpdiff_"+ccol] - factsag["cmpdiff_"+ccol2]).abs() > 1e-6
    factsag['opdel']=     factsag['ri'] + (factsag['hm'].astype(str))
    c2 = factsag.groupby(['perstart','ri','hm'])[['isadj']].agg('sum').reset_index()
    display (c2[c2['isadj'] !=0 ])
    factsagch=factsag[factsag['isadj']]    
    sns.scatterplot(data=factsagch,x="cmpdiff_"+ccol,y="cmpdiff_"+ccol2,hue="opdel",style="perstart")
    assert(factsagch["cmpdiff_"+ccol2].abs().max() < 1e-6) 
estcolvchk(edata27,'a27','IntensiteitCorr','IntensiteitEst')     

#hethaal vorig plaatje
dlowhiaxplt(edata27,'a27','IntensiteitCorr',['uur'],True,False)  

dlowhiaxplt(edata27,'a27','IntensiteitEst',['uur'],True,False)  


def plttimesest3c(dfin):
    dfplt=dfin[dfin['ID'].str[0:3] == 'EST']
    sns.lineplot(data=dfplt,x='uur',y='Intensiteit',label='Tegenrichting',alpha=0.6,style="perstart")
    sns.lineplot(data=dfplt,x='uur',y='IntensiteitCorr',label='TegenrichtingCorr',alpha=0.6,style="perstart")
    sns.lineplot(data=dfplt,x='uur',y='IntensiteitEst',label='IntensiteitEst',alpha=0.6,style="perstart")
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.title('Vergelijking 2 richtingen op/af: Est = geschat, Corr= tegenrichting (gemiddelde gebruikt als schatting volume)')
plttimesest3c(edata27)    



usefacts1my=summstr_normprep(rdata27my[rdata27my["perend"]>calendafter(rdata27my)],
                             'a27','Intensiteit',[],[],False).reset_index()    
#display(usefacts1my)
cdata27my=corrcol(rdata27my,'a27','Intensiteit',usefacts1my,'IntensiteitCorr')  
ilowhihmplt(cdata27my,'a27','IntensiteitCorr',['perstart'])              

edata27my=estcol(cdata27my,'a27','IntensiteitCorr','IntensiteitEst') 
edata27my.groupby(['perstart'])[['Intensiteit','IntensiteitCorr','IntensiteitEst']].agg('count')



ilowhihmplt(edata27my,'a27','IntensiteitEst',['perstart']) 


def plttimesestmy(dfin,col):
    dfplt=dfin[dfin['ID'].str[0:3] == 'EST']
    sns.lineplot(data=dfplt,x='uur',y=col,hue='perstart')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plttimesestmy(edata27my,'Intensiteit')  
plt.title('Intensiteit tegenrichting est')

plttimesestmy(edata27my,'IntensiteitEst')  
plt.title('Instensiteit est')

edata27myd = edata27my.copy();
edata27myd['IntensiteitEstDiff'] = edata27myd['IntensiteitEst']  - edata27myd['Intensiteit'] 
plttimesestmy(edata27myd,'IntensiteitEstDiff')  
plt.title('Intensiteit est - Instensiteit tegenrichting')


def plttimeshmmy(dfin,hmval,col):
    fig, ax = plt.subplots()
    dfplt=dfin[dfin['hm'] == hmval]
    sns.lineplot(data=dfplt,x='perstart',y=col,hue='uur',style='ID',alpha=0.6,ax=ax)
    ax.set_ylim(bottom=0)
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plttimeshmmy(edata27my[edata27my['uur'].isin([14,15,16])],680,'IntensiteitEst') 
plt.title('middagspits zuid voor verhoudingen')

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
            "A27 afrit Houten opaf en door/4 werkdagen :  l: zuidwaarts, r : noordwaards" )
# -

pltjaaropaf(edata27my[edata27my["uur"].isin((16,17))],'a27','IntensiteitEst',[680,681],_scaledr27, _scaledrinv27,
            "A27 afrit Houten opaf en door/4 aspits werkdagen :  l: zuidwaarts, r : noordwaards" )

pltjaaropaf(edata27my[edata27my["uur"].isin((7,8))],'a27','IntensiteitEst',[680,681],_scaledr27, _scaledrinv27,
            "A27 afrit Houten opaf en door/4 ospits werkdagen :  l: zuidwaarts, r : noordwaards" )


# +
#hiertussen evt stap om percentage kolommen ook om te rekenen
# -

def unmerge_initest(df,cfg):
    torem = cfg.columns[1:].to_list()+["Intensiteit","IntensiteitCorr"]
#    print (torem)
    df2= df.drop(torem,axis=1)
    rv=df2.rename(columns={"IntensiteitEst":"Intensiteit"})
    return rv
edata27mycln = unmerge_initest(edata27my,a27id_config)
print (edata27mycln.columns)



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
