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
GEO1A_A_RWS_359850	a27	680	r	op		2019-01-03
GEO1A_A_RWS_359853	a27	681	l	af		2018-11-23
EST1A_A_EST_359850	a27	680	r	af	GEO1A_A_RWS_359819
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
display(a27id_config)
def merge_initest(df,cfg):
    estrecm = cfg[cfg['ID'].str[0:3] == 'EST'].copy().rename(columns={'ID':'estID','estfrID':'ID'})
    estv=df.merge(estrecm,how='right').rename(columns={'ID':'estfrID','estID':'ID'})
    #hier staan evenveel waarden als het originieel, met een schatting van het totaal
    #print(estv)
    rv=df.merge(cfg,how='left')    
    return pd.concat([rv,estv])
a27dta=merge_initest(idfh,a27id_config)
# -

#to get ID list:
if (not suprtests):
    print(a27id_config[['ID']].to_csv(index=False))


# +
#a27dta.dtypes

# +
#old experiments

# +
def summstr_old(strdf,strval,ccol,split1,split2):
    strdf= strdf[strdf['stroom']==strval].copy()
    strdf['isign'] =strdf['ri'].map( {'r':1,'l':-1 }) 
    strdf['iafop'] =strdf['afop'].map({'op':1,'af':-1,'t':0,'d':0}) 
    strdf['Ilow'] = np.where(strdf['iafop'],strdf['isign'] ==strdf['iafop'] ,1) * strdf[ccol]
    strdf['Ihigh'] = np.where(strdf['iafop'],strdf['isign'] == -strdf['iafop'] ,1) * strdf[ccol]    
    grps=split1+['stroom','ri','hm']+split2
    summs = strdf.groupby(grps).agg('sum')[['isign','iafop','Ilow','Ihigh']].reset_index()
    grpsexhm=split1+['stroom','ri']
    summs['cmpdiff'] = np.where(summs['isign'] >0 ,
                                summs.groupby(grpsexhm).shift(1,fill_value=np.nan)['Ihigh']- summs['Ilow'],
                                summs.groupby(grpsexhm).shift(1,fill_value=np.nan)['Ilow']- summs['Ihigh'])        
    summs['hmstr']=summs['hm'].astype(str)+" "
    summs['cmpvak'] = np.where(summs['isign'] >0 ,
                                summs.groupby(grpsexhm).shift(1,fill_value=np.nan)['hmstr']+'-'+ summs['hmstr'],
                                summs.groupby(grpsexhm).shift(1,fill_value=np.nan)['hmstr']+'-'+ summs['hmstr'])
    return summs
    
summstr_old(a27dta,'a27','Intensiteit',[],['afop','ID'])    
#summstr(a27dta,'a27','Intensiteit',[],[])    

# +
def crossmerge(self,f2):
#    return f1.merge(f2,how='cross')
    tk='_tmpkey'
    return self.assign(key=1).merge(f2.assign(key=1), how='outer', on='key').drop(columns=['key'])

#conventie: vaknaam is stroom + ri + hm, waarbij hm de laagste waarde van het vak is
#daardoor de laatste vakken op 0 zetten
def summstr(strdf,strval,ccol,split1):
    strdf= strdf[strdf['stroom']==strval].copy()
    grpsexhm=split1+['stroom','ri']
    ccnorm=ccol+"_norm"
#    strdft= strdf[strdf['afop']=='t']
#    perlst = strdft.groupby(grpsexhm).agg('mean')[[ccol]].reset_index().rename (
#        columns={ccol: 'tavg'})
#    print(perlst)
    
    strdf['iafop'] =strdf['afop'].map({'op':1,'af':-1,'t': 0 ,'d': 0 }) 
    vaklst = strdf.groupby(grpsexhm+['hm']).agg('sum')[[ccol]].reset_index().rename (
        columns={ccol: ccnorm})
    vaklst['hmi'] = vaklst.groupby(grpsexhm).shift(-1,fill_value=0)['hm']
    vaklst['hmi2'] = vaklst.groupby(grpsexhm).shift(1,fill_value=0)['hm']
    vaklst['isign'] =vaklst['ri'].map( {'r':1,'l':-1 }) 
    some_string="""dtag
1
-1"""
    hwmerge= pd.read_csv(io.StringIO(some_string), sep="\t")
    #iafop moet 1 zijn
    #display (vaklst)
    strdf1= crossmerge(strdf.merge(vaklst,how='left'),hwmerge)
#    strdf2=strdf1.copy(deep=True)
    #display (strdf)
    #eerst voor de tellers met laagste hms   
    strdf1['vak']   =np.where(strdf1['dtag'] <0, strdf1['hm'],strdf1['hmi'] )
    strdf1['idoor'] =(strdf1['iafop'] ==0) *strdf1['dtag'] *strdf1['isign'] 
    strdf1['isecb'] =strdf1['idoor'] +strdf1['iafop']*(  strdf1['iafop']== strdf1['dtag'] *strdf1['isign']  )  
    strdf1['isecm'] =np.where(strdf1['dtag'] <0, strdf1['hmi2'],strdf1['hmi'] )!=0
    toopt= strdf1
    #toopt['iafop'] = np.where ( toopt['hmi']!=0, toopt['iafop'] ,0).astype(int)
    toopt[ccol] = toopt[ccol] *toopt['isecb'] *strdf1['isecm']
    return toopt


optd=summstr(a27dta,'a27','Intensiteit',['uur']) .sort_values(['stroom','ri','vak','hm']) 
optd[optd['uur']==12][['Intensiteit','stroom','ri','vak','hm','hmi','hmi2','dtag','ID','idoor','iafop','isecb','Intensiteit']]
#summstr(a27dta,'a27','Intensiteit',[],[])    

# +
#print(optd.dtypes)
def matchpervak(strdf,strval,ccol,split1):
    optdl=summstr(strdf,strval,ccol,split1)
    optdl['nvar']=1
    matchgrps=split1+['stroom','ri','vak']
    inisum=optdl.groupby(split1+['stroom','ri','vak']).agg('sum')[['Intensiteit']]
    #display(inisum)
    fitdatin=optdl.pivot_table(values=ccol, index=matchgrps, columns='ID', aggfunc='sum', fill_value=0)
    yvars=fitdatin.columns.to_list()
    display(yvars)
    fitdatin= fitdatin.reset_index()
    fitdatin['target']=0
    vak0sli=fitdatin['vak']==0
    np.sum(np.abs(fitdatin[yvars]),axis=1)
    fitdatin.loc[vak0sli,yvars]=1
    fitdatin.loc[vak0sli,'target']=np.sum(fitdatin.loc[vak0sli,yvars],axis=1)
    fit1=nnls(fitdatin[yvars],fitdatin['target'])
    rv=pd.DataFrame(fit1[0],index=yvars).T  
    diff= np.sum(np.array(fitdatin[yvars]),axis=1).astype(float)
    fitdatin['orig']=diff.T
    diff= np.sum(np.array(rv)*np.array(fitdatin[yvars]),axis=1).astype(float)
    fitdatin['result']=diff.T
    if (not suprtests):
        display(fitdatin)
    #mism=rv * fitdatin['target']
    if (not suprtests):
        display(rv)
    return fitdatin
    
optd=matchpervak(a27dta,'a27','Intensiteit',[]) 
# -

optd['dirhr']=  optd['stroom'] + optd['ri'] #+ (optdu['vak'].astype(str))
sns.lineplot(data=optd[optd['vak'] !=0],x="vak",y="orig",label='Ilow',hue="ri")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

optdu=matchpervak(a27dta,'a27','Intensiteit',['uur'])

optdu['dirhr']=  optdu['stroom'] + optdu['ri'] + (optdu['vak'].astype(str))
sns.lineplot(data=optdu[optdu['vak'] !=0],x="uur",y="orig",label='Ilow',hue="dirhr")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

# +
#end of old experiments

# +
iafopmap={'op':1,'af':-1,'t':0,'d':0}
def cumsumavg0(ser):
    st = pd.Series.cumsum(ser)
    st = st-st.mean()
    return  st

#split2 is subest vab ['afop','ID']: alleen voor debugging gebruiken
def summstr_normprep(strdfi,strval,ccol,split1,split2):
    strdfr= strdfi[strdfi['stroom']==strval].copy()
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

calendafter=pd.to_datetime("2019-03-01")
#nu de EST_xx IDs
def estcol(strdfi,strval,nabefore,ccol,ccol2):
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
    udf[ccol2] = udf[ccol]+np.where(np.isnan(udf['cmpdiffsec']),0,
                     np.where(udf['perstart']>nabefore, udf['cmpdiffsec'],np.nan)  )         
#    display(udf[docorr==0])
    rv=udf.drop(['cmpdiffsec'],axis=1)
    return rv
edata27=estcol(cdata27,'a27',calendafter,'IntensiteitCorr','IntensiteitEst') 
#edata27.sum()

dlowhiaxplt(edata27,'a27','IntensiteitCorr',['uur'])  

dlowhiaxplt(edata27,'a27','IntensiteitEst',['uur'])  


def plttimesest(dfin):
    dfplt=dfin[dfin['ID'].str[0:3] == 'EST']
    sns.lineplot(data=dfplt,x='uur',y='Intensiteit',label='Tegenrichting')
    sns.lineplot(data=dfplt,x='uur',y='IntensiteitCorr',label='TegenrichtingCorr')
    sns.lineplot(data=dfplt,x='uur',y='IntensiteitEst',label='IntensiteitEst')
plttimesest(edata27)    



# +
#nu houten IO
# -

xlslist= (glob.glob("../data/intensiteit-snelheid-*.xlsx"))
xlslist

allsumf1= [ ndw_od_read_overzicht(t,t,"datadatalog") for t in xlslist ]
allsumdf = pd.concat(allsumf1)
allsumdf

allsumdf.to_excel("../intermediate/xlscatalog.xlsx")

# +
#a27 data sevral years
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

edata27my=estcol(cdata27my,'a27',calendafter,'IntensiteitCorr','IntensiteitEst') 
#edata27.sum()

ilowhihmplt(edata27my,'a27','IntensiteitEst',['perstart']) 


def plttimesest(dfin,col):
    dfplt=dfin[dfin['ID'].str[0:3] == 'EST']
    sns.lineplot(data=dfplt,x='uur',y=col,hue='perstart')
plttimesest(edata27my,'Intensiteit')  

plttimesest(edata27my,'IntensiteitEst')  

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

testfil12=xlsa12s1list[0]

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

summstr_normprep(rdata12my,'a12','Intensiteit',[],['ID'])    

ilowhihmplt(rdata12my,'a12','Intensiteit',['perstart'])    

# +

#rdata27my
usefacts12my=summstr_normprep(rdata12my,
                             'a12','Intensiteit',[],[]).reset_index()    
#display(usefacts12my)
cdata12my=corrcol(rdata12my,'a12','Intensiteit',usefacts12my,'IntensiteitCorr')  
ilowhihmplt(cdata12my,'a12','IntensiteitCorr',['perstart'])   
# -

dlowhiaxplt(cdata12my,'a12','IntensiteitCorr',['uur'])  


def _scaledr12(x):
            return x *0.05
def _scaledrinv12(x):
            return x * 20
pltjaaropaf(cdata12my,'a12','IntensiteitCorr',[658,662],_scaledr12, _scaledrinv12,
            "A12 afrit Houten Oost opaf en door/4 :  l: westwaarts, r : oostwaards" )






