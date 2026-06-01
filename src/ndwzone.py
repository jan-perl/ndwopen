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
#start tools voor zone in/uit per uur
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

myname='ndwzone'
suprtests= myname in rdwbas.suprtests 
suprdata= myname in rdwbas.suprdata
#suprtests=True
print ('Suprtests',suprtests)

rdwbas.suprtests = rdwbas.suprtests+['ndwimport']
import ndwimport



# +
#houten in en uit
# -

xlshtns2list= (glob.glob("../data/intensiteit-snelheid-htn-20??-s2.xlsx"))
xlshtns2list

# +
some_string="""Fecode,Drglpt,Volledige naam,Traject,GPSX,GPSY
623,Utln,Utrecht Lunetten,Ut-Ht,5.1441664696,52.0655555725
340,Htn,Houten,Ut-Gdm,5.16821,52.03402
335,Htnc,Houten Castellum,Ut-Gdm,5.17949,52.01701
991,Lek,pont bij Culemborg,Ut-Gdm,5.208283,51.965951"""
#154,Cl,Culemborg,Ut-Gdm,5.2269444466,51.9466667175
df= pd.read_csv(io.StringIO(some_string), sep=",")
stationplc = geopandas.GeoDataFrame(
      df, geometry=geopandas.points_from_xy(df.GPSX, df.GPSY), crs="EPSG:4326")

stationplc

# +
#todo visualisatie:
#geo stations Houten
#geo punt odijk
#geo punt A12
#visualisatie A27 NZ
# -

if (not suprtests):
    odfhtn= ndwimport.ndw_od_read_overzicht(xlshtns2list[0],"testseq12","testcoll20260522")
    fig, ax = plt.subplots()
    pland= odfhtn.plot(alpha=0.4,color='blue',ax=ax)
    pland= ndwimport.odf.plot(alpha=0.4,color='yellow',ax=ax)
    pland= ndwimport.odf12.plot(alpha=0.4,color='red',ax=ax)
    pland= stationplc.plot(alpha=0.4,color='green',ax=ax)
    cx.add_basemap(pland, source= ndwimport.prov0,crs=ndwimport.odf.crs)
    figname = "../output/htnmeetptov.png";
    fig.savefig(figname,dpi=300)

idfhtnmy =[ ndwimport.ndw_od_read_overzicht_en_intensiteiten(testfil,"htnmy",testfil) for testfil in xlshtns2list ]
idfhtnmy=pd.concat(idfhtnmy)

idfa27my = ndwimport.idfa27my
a27prevrawborrow=['GEO1A_A_RWS_359850','RWS01_MONIBAS_0271hrr0680ra']
idfhtnmyc= pd.concat([idfhtnmy, idfa27my[idfa27my['ID'].isin(a27prevrawborrow)] ] )

# +
#methode A
#eens kijken waar we uitkomen met schattingen EST uit de s2 data
# -

rdata27hmy=ndwimport.merge_initest(idfhtnmyc,ndwimport.a27id_config)
#rdata27my

#nee dat lukt niet, GEO1A_A_RWS_359850 mist in s2
ndwimport.summstr_normprep(rdata27hmy[rdata27hmy["perend"]>ndwimport.calendafter],
                             'a27','Intensiteit',[],['ID']).reset_index()   

usefactsa27hmy=ndwimport.summstr_normprep(rdata27hmy[rdata27hmy["perend"]>ndwimport.calendafter],
                             'a27','Intensiteit',[],[]).reset_index()    
if (not suprtests):
    display(usefactsa27hmy)
cdata27hmy=ndwimport.corrcol(rdata27hmy,'a27','Intensiteit',usefactsa27hmy,'IntensiteitCorr')  
ndwimport.ilowhihmplt(cdata27hmy,'a27','IntensiteitCorr',['perstart'])      

edata27hmy=ndwimport.estcol(cdata27hmy,'a27',ndwimport.calendafter,'IntensiteitCorr','IntensiteitEst') 

ndwimport.plttimesest(edata27hmy,'IntensiteitEst')  


# +
#methode B, pak EST van eerdere A27 data
# -

def addestasraw(measdf,estdf,nabefore,ccol,addlids):
    estdf2=estdf[(estdf['ID'].str[0:3] == 'EST') | (estdf['ID'].isin(addlids))]
    estdfrecs=estdf2[estdf2['perstart']>=(measdf['perstart'].min())].copy(deep=False)
#    print(estdfrecs.sum())
    estdfrecs= estdfrecs.drop(ccol,axis=1).rename(columns={(ccol+"Est"):ccol}) 
#    print(estdfrecs.columns)
    gdf=estdfrecs[measdf.columns].copy(deep=True)    
    gdf['setuid']=measdf.iloc[0]['setuid']
    gdf['collid']='est'
#    print(gdf.sum())
    rv2=pd.concat([measdf,gdf])
    rv=rv2[rv2["perend"]>nabefore]
    return rv
idfhtnemyB= addestasraw(idfhtnmy,ndwimport.edata27my,ndwimport.calendafter,'Intensiteit',['GEO1A_A_RWS_359850'])
#idfhtnemy

#now compare results
def cmprawests(df1,df2r,ccol):
    estdf1=df1[(df1['ID'].str[0:3] == 'EST') ]
    estdf2=df2r[(df2r['ID'].str[0:3] == 'EST') ]
    jfields=['ID','perstart','uur']
    estj=estdf1[jfields + [ccol+'Est']] .merge(estdf2[jfields + [ ccol]])
    sns.scatterplot(data=estj,x=ccol,y=ccol+'Est')
    sns.lineplot(data=estj,x=ccol,y=ccol)
    return estj                                                
cmprawests(edata27hmy, idfhtnemyB,'Intensiteit').sum()


def renameestfields(measdf,estdf,nabefore,ccol):
    estdfrecs=estdf[estdf['perstart']>=(measdf['perstart'].min())].copy(deep=False)
#    print(estdfrecs.sum())
    estdfrecs= estdfrecs.drop(ccol,axis=1).rename(columns={(ccol+"Est"):ccol}) 
#    print(estdfrecs.columns)
    rv2=estdfrecs[measdf.columns].copy(deep=True)    
    rv=rv2[rv2["perend"]>nabefore]
    return rv
idfhtnemyA=  renameestfields(idfhtnmy,edata27hmy,ndwimport.calendafter,'Intensiteit')

idfhtnemy=idfhtnemyA
idfhtnemy.dtypes

#houten data, oude versie
htn25fil="../data/intensiteit-snelheid-export(2).xlsx"
idf=ndwimport.ndw_od_read_overzicht_en_intensiteiten(htn25fil,"testseq1","testcoll20260521")
h25ih=idf[idf['uur'].isna() == False] 
#h25ih

# +
#let op: lijkt deels spitsstrook RWS01_MONIBAS_0270vwa0678ra	a27	678	r	af
#67.5 = zoutopslag na oprit 28 , 69.1 = Euretco, r = richting noord (Euretco vanaf afslag 28)

#PUT01_PUVIS_N409.07_0_2	n409	7	r	t
#PUT01_PUVIS_N409.07_1_2	n409	7	l	t

some_string="""ID	centrum	richting	Zoneinuit
GEO1A_A_RWS_359819	Houten	A27Zuid	uit
EST1A_A_EST_359850	Houten	A27Zuid	in
GEO1A_A_RWS_359850	Houten	A27Noord	uit
GEO1A_A_RWS_359853	Houten	A27Noord	in
PUT01_N410.03_0	Houten	Odijk	uit
PUT01_N410.03_1	Houten	Odijk	in
PUT01_N421.01_0	Houten	A12west	uit
PUT01_N421.01_1	Houten	A12west	in
PUT01_PUVIS_N409.07_0_2	Houten	Laagraven	in
PUT01_PUVIS_N409.07_1_2	Houten	Laagraven	uit
RWS01_MONIBAS_0270vwa0678ra	deelsdoor	A27Zuid	in
"""
#read CSV string into pandas DataFrame
htncor_config= pd.read_csv(io.StringIO(some_string), sep="\t")
display(htncor_config)
#merge_initest alleen als EST veld berekend moet worden
if 1==1:
    htncordta=idfhtnemy.merge(htncor_config,how='left')
else:    
    htncordta = ndwimport.merge_initest(idfhtnemy,htncor_config)
htncordta=htncordta[htncordta['centrum']=='Houten']
htncordta['Balans']=htncordta ['Zoneinuit'].map( {'in':1,'uit':-1 }) * htncordta['Intensiteit']

# +
#htncordta.groupby(["ID"]).agg('sum')
# -

summs = htncordta.groupby(['centrum','richting','Zoneinuit','ID','perstart']).agg('sum')[['Intensiteit']]
summs

nacorona=pd.to_datetime("2021-06-01")
htncordtanc = htncordta[ (htncordta['perstart'] > nacorona) ]
summsud = htncordtanc.groupby(['uur','Zoneinuit','perstart'])['Intensiteit'].agg('sum').reset_index()
sns.lineplot(data=summsud,x='uur',y='Intensiteit',hue='Zoneinuit')

summsur= htncordtanc.groupby(['uur','richting','perstart']).agg('sum')[['Intensiteit']].reset_index()
sns.lineplot(data=summsur,x='uur',y='Intensiteit',hue='richting')
plt.title('''Totaal per uur en richting op werkdagen 
spreiding 2022-2025 aangegeven''')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

summsur= htncordtanc.groupby(['uur','richting','perstart']).agg('sum')[['Balans']].reset_index()
sns.lineplot(data=summsur,x='uur',y='Balans',hue='richting')
plt.title('''Balans per uur en richting op werkdagen + is Houten in
spreiding 2022-2025 aangegeven''')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

summsur= htncordta.groupby(['richting','perstart'])['Intensiteit'].agg('sum').reset_index()
sns.lineplot(data=summsur,x='perstart',y='Intensiteit',hue='richting')
plt.title('Bijdragen per werkdag van verschillende richtingen per jaar')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

summsud = htncordta.groupby(['Zoneinuit','perstart'])['Intensiteit'].agg('sum').reset_index()
sns.lineplot(data=summsud,x='perstart',y='Intensiteit',hue='Zoneinuit')
plt.title("""Totaalplot voor balans:
    Verschillen over de dag meetfouten en via niet gemeten wegen""")

ndiv=603
summsud = (htncordta.groupby(['perstart'])['Intensiteit'].agg('sum')/ndiv).reset_index()
#display(summsud)
sns.lineplot(data=summsud,x='perstart',y='Intensiteit')
plt.title('auto bewegingen in/uit houten per werkdag: 2022 =100')

summsur= htncordtanc.groupby(['uur','perstart']).agg('sum')[['Balans']].reset_index()
sns.lineplot(data=summsur,x='uur',y='Balans',hue='perstart')
plt.title('''Balans per uur werkdagen + is Houten in
ochtend iets uit, middag iets in Houten heeft meer wonen dan werken''')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

summsur= htncordtanc.groupby(['uur','perstart']).agg('sum')[['Intensiteit','Balans']].reset_index()
summsur['Relbalans'] = 2*summsur['Balans'] / summsur['Intensiteit']
sns.lineplot(data=summsur,x='uur',y='Relbalans',hue='perstart')
plt.title('''Balans per uur werkdagen + is Houten in
ochtend iets uit, middag iets in Houten heeft meer wonen dan werken''')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

# +
summsur= htncordtanc.groupby(['uur','perstart']).agg('sum')[['Balans']].reset_index()
ouhrs=[3,4,5,6,7,8,9,10,11,12]

summsur= htncordtanc.groupby(['uur','perstart']).agg('sum')[['Intensiteit','Balans']].reset_index()
summsur['Pendelhr'] = np.where(summsur['uur'].isin (ouhrs),-1,1)
summsur['Pendel'] = summsur['Pendelhr'] * summsur['Balans'] 
summsurs= summsur.groupby(['perstart','Pendelhr']).agg('sum')[['Intensiteit','Pendel']].reset_index()
display(summsurs)
sns.lineplot(data=summsur,x='uur',y='Pendel',hue='perstart')
plt.title('''Balans per uur werkdagen + is Houten in
ochtend iets uit, middag iets in Houten heeft meer wonen dan werken''')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
# -

vooravsp=[15,16]
htncordtancd= htncordtanc[htncordtanc['uur'].isin(vooravsp)]
summsur= htncordtancd.groupby(['perstart','richting','Zoneinuit'])['Intensiteit'].agg('sum').reset_index()
#display(summsur)
sns.lineplot(data=summsur,x='perstart',y='Intensiteit',hue='richting',style='Zoneinuit')
plt.title('''Aantallen per stroom werkdagen 15-17 uur
meer voertuigen verlaten Houten via A27 voor avondspits''')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

summsur= htncordtancd.groupby(['perstart','richting','Zoneinuit'])['Intensiteit'].agg('max').reset_index()
#display(summsur)
sns.lineplot(data=summsur,x='perstart',y='Intensiteit',hue='richting',style='Zoneinuit')
plt.title('''Drukste uur werkdagen''')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)



# +
#vergelijkingen
#ODIN data gemeente houten andere gemeenten per uur per jaar per modaliteit
# let op: ODIN is reizigers -> alleen eigen bestuurder meetellen
# en vergelijken ODIN binnen gemeente
# en en beide per afstandsklasse

# +
#vergelijking bevolkingsgroei Houten, NL

# +
#vergelijking tellussen VRI; ook autogebruik binnen gemeente
# -




