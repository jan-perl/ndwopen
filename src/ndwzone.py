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
some_string="""Fecode,ID,Volledige naam,Traject,GPSX,GPSY
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
    odfbnk= ndwimport.ndw_od_read_overzicht("../data/intensiteit-snelheid-a12bnk-2025-s2.xlsx","locbnk","testcoll20260522")    
    #odfbnk=odfbnk[odfbnk['Lengtegraad']>5]
#    display(odfbnk)
    fig, ax = plt.subplots()
    pland= odfhtn.plot(alpha=0.4,color='blue',ax=ax)
    pland= ndwimport.odf.plot(alpha=0.4,color='yellow',ax=ax)
    pland= odfbnk.plot(alpha=0.4,color='grey',ax=ax)
    pland= ndwimport.odf12.plot(alpha=0.4,color='red',ax=ax)
    pland= stationplc.plot(alpha=0.4,color='green',ax=ax)
    cx.add_basemap(pland, source= ndwimport.prov0,crs=ndwimport.odf.crs)
    figname = "../output/htnmeetptov.png";
    fig.savefig(figname,dpi=300)

targgem =321
#targgemcode = 'GM%04.0f'%targgem

def selgemyrs(targgem):
    targgemcode = 'GM%04.0f'%targgem
    targgem_CBSsum=pd.read_pickle ("../intermediate/gemdata/gem1sum_"+targgemcode+".pkl")
    ODindta =pd.read_pickle ("../intermediate/gemdata/gem1odin_"+targgemcode+".pkl")
    rv =(targgem_CBSsum,ODindta)
    return rv
(allgem_CBSsum,summ1gemdatahtn)=selgemyrs(targgem)

# +
plot_crs=3857
plot_crs="epsg:28992"
gdc=[]
def add_geodict(gdf,gd2,ax,colv,labelv):
    gdfrds= gdf.to_crs(crs=plot_crs)
    gd2.append(gdfrds)
    return gdfrds.plot(ax=ax,alpha=0.4,color=colv,label=labelv)

if (not suprtests):   
    fig, ax = plt.subplots()
    allgem_CBSsum.set_crs(crs="epsg:28992")
    pland=allgem_CBSsum.boundary.plot(color='green',alpha=0.1,ax=ax)
    pland.set_ylim(bottom=441000,top=453000)
    #pland.set_xlim(left=137000,right=149000)
    cx.add_basemap(pland, source= ndwimport.prov0,crs=plot_crs)
    pland= add_geodict(ndwimport.odf,gdc,ax,'yellow','overig a27')
    pland= add_geodict( odfbnk,gdc,ax,'grey','overig bnk')
    pland= add_geodict( ndwimport.odf12,gdc,ax,'red','overig a12')
    pland= add_geodict(  stationplc,gdc,ax,'green','OV, pont')
    pland= add_geodict( odfhtn,gdc,ax,'blue','Gebruikt htn')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    figname = "../output/htnmeetptovgg.png";
    fig.savefig(figname,dpi=300)
    namesptsx=(pd.concat(gdc).copy().set_index('ID')['geometry'].x.to_dict())
    namesptsy=(pd.concat(gdc).copy().set_index('ID')['geometry'].y.to_dict())
    #display(namespts)

# +
#namesptsx

# +
#odfhtn
# -

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
ndwimport.summstr_normprep(rdata27hmy[rdata27hmy["perend"]>ndwimport.calendafter(rdata27hmy)],
                             'a27','Intensiteit',[],['ID'],False).reset_index()   

usefactsa27hmy=ndwimport.summstr_normprep(rdata27hmy[rdata27hmy["perend"]>ndwimport.calendafter(rdata27hmy)],
                             'a27','Intensiteit',[],[],False).reset_index()    
if (not suprtests):
    display(usefactsa27hmy)
cdata27hmy=ndwimport.corrcol(rdata27hmy,'a27','Intensiteit',usefactsa27hmy,'IntensiteitCorr')  
ndwimport.ilowhihmplt(cdata27hmy,'a27','IntensiteitCorr',['perstart'])      

edata27hmy=ndwimport.estcol(cdata27hmy,'a27','IntensiteitCorr','IntensiteitEst') 

ndwimport.plttimesestmy(edata27hmy,'IntensiteitEst')  


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
idfhtnemyB= addestasraw(idfhtnmy,ndwimport.edata27my,ndwimport.calendafter(ndwimport.edata27my),'Intensiteit',['GEO1A_A_RWS_359850'])
#idfhtnemy

#now compare results
def cmprawests(df1,df2r,ccol):
    estdf1=df1[(df1['ID'].str[0:3] == 'EST') ]
    estdf2=df2r[(df2r['ID'].str[0:3] == 'EST') ]
    jfields=['ID','perstart','uur']
    estj=estdf1[jfields + [ccol+'Est']] .merge(estdf2[jfields + [ ccol]])
    estj['EstDiff'] = estj[ccol]- estj[ccol+'Est'] 
    p=sns.scatterplot(data=estj,x=ccol,y='EstDiff',hue='perstart')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    p.set_ylabel('schatting beperkt aantal punten Htn - schatting full a27')
    p.set_xlabel('schatting full a27')
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
idfhtnemyA=  renameestfields(idfhtnmy,edata27hmy,ndwimport.calendafter(edata27hmy),'Intensiteit')

# +
#methode C: gebruik edata27mycln alsof het ruwe data is
# -

#print (edata27mycln.columns)
rd1=idfhtnmy [idfhtnmy ['perstart'].dt.year<=2099].groupby(["ID","perstart"])[["Intensiteit"]].sum().reset_index()
rd2=rd1.pivot(index='ID', columns='perstart', values='Intensiteit')
rd2

edata27mycln = ndwimport.edata27mycln
#print (edata27mycln.columns)
rd1=edata27mycln [edata27mycln ['perstart'].dt.year<=2099].groupby(["ID","perstart"])[["Intensiteit"]].sum().reset_index()
rd2=rd1.pivot(index='ID', columns='perstart', values='Intensiteit')
rd2


def combine_cleaned(dfhtn,dfpr):
    newids=dfpr["ID"].unique()
    print (newids)
    minph=dfhtn['perstart'].min()
    minpr=dfpr['perstart'].min()    
    dfhkeep=dfhtn[(dfhtn["ID"].isin(newids)==False) & (dfhtn["perstart"]>= minpr) ]
    dfpkeep=dfpr[(dfpr["perstart"]>= minph) ]
    rv= pd.concat([dfhkeep,dfpkeep])
    return rv
idfhtnemyC=combine_cleaned(idfhtnmy,edata27mycln)

# +
#kies methode
# -

idfhtnemy=idfhtnemyC
idfhtnemy.dtypes

#houten data, oude versie
htn25fil="../data/intensiteit-snelheid-export(2).xlsx"
idf=ndwimport.ndw_od_read_overzicht_en_intensiteiten(htn25fil,"testseq1","testcoll20260521")
h25ih=idf[idf['uur'].isna() == False] 
#h25ih

# +
#let op: lijkt deels spitsstrook RWS01_MONIBAS_0270vwa0678ra	a27	678	r	af
#67.5 = zoutopslag na oprit 28 , 69.1 = Euretco, r = richting noord (Euretco vanaf afslag 28)

some_string="""ID	centrum	richting	Zoneinuit	estfrID	IDsinds	PlotPt	Drlov
GEO1A_A_RWS_359819	Houten	A27Zuid	uit		2019-03-01	RWS01_MONIBAS_0271hrl0675ra	RWS01_MONIBAS_0271hrl0681ra
EST1A_A_EST_359850	Houten	A27Zuid	in		2019-03-01	RWS01_MONIBAS_0271hrl0675ra	Htnc
GEO1A_A_RWS_359850	Houten	A27Noord	uit		2019-03-01	RWS01_MONIBAS_0271hrr0680ra	RWS01_MONIBAS_0271hrr0678ra
GEO1A_A_RWS_359853	Houten	A27Noord	in		2019-03-01	RWS01_MONIBAS_0271hrr0680ra	Htn
PUT01_N410.03_0	Houten	Odijk	uit			PUT01_N410.03_0	Htn
PUT01_N410.03_1	Houten	Odijk	in			PUT01_N410.03_0	Htn
PUT01_N421.01_0	Houten	A12west	uit			PUT01_N421.01_0	PUT01_N410.03_0
PUT01_N421.01_1	Houten	A12west	in			PUT01_N421.01_0	Htn
PUT01_N409.01_0	Houten	Laagraven	in			PUT01_N409.01_0	PUT01_PUVIS_N409.07_0_2
PUT01_N409.01_2	Houten	Laagraven	uit			PUT01_N409.01_0	PUT01_PUVIS_N409.07_0_2
RWS01_MONIBAS_0270vwa0678ra	deelsdoor	A27Zuid	in"""
#read CSV string into pandas DataFrame
htncor_config= pd.read_csv(io.StringIO(some_string), sep="\t")
display(htncor_config)
htncordta = ndwimport.merge_initest(idfhtnemy,htncor_config,False)
htncordta=htncordta[htncordta['centrum']=='Houten']
htncordta['Balans']=htncordta ['Zoneinuit'].map( {'in':1,'uit':-1 }) * htncordta['Intensiteit']

# +
#htncordta.groupby(["ID"]).agg('sum')
# -

summs = htncordta.groupby(['centrum','richting','Zoneinuit','ID','perstart','PlotPt','Drlov']).agg('sum')[['Intensiteit']].reset_index()
summs25=summs[summs['perstart'].dt.year.isin([2025])]
summs25



# +
plot_crs=3857
plot_crs="epsg:28992"
pltparahtn={'scleft':134000, 'scright':147000,
            'sctop':453000, 'scbottom':441000,
            'minttxsp':1000,
            'geodx':namesptsx,'geody':namesptsy,
           'totalpos':[136000,443000]}
def plaxkm(x, pos=None):
    return '%.0f'%(x/1000.)
def show_numbers(summsi,ifield,ascale,tit,fn,pltpa):
    totalar=[0,0,0]
    geodictx =pltpa['geodx']
    geodicty =pltpa['geody']
    summs=summsi.copy()
    summs['PlotPtx']= summs['PlotPt'].map(geodictx)
    summs['PlotPty']= summs['PlotPt'].map(geodicty)
    summs['Drlovx']= summs['Drlov'].map(geodictx)
    summs['Drlovy']= summs['Drlov'].map(geodicty)
    #display(summs)
    fig, ax = plt.subplots()
    pland=allgem_CBSsum.boundary.plot(color='green',alpha=0.05,ax=ax)
    for index, row in summs.iterrows(): 
        (lx,ly)=(row['PlotPtx'] , row['PlotPty'] )
        (ldx,ldy)=(row['Drlovx'] , row['Drlovy'] )
        (ldx,ldy)=(lx- ldx,ly- ldy)
        lori= np.sqrt(ldx*ldx + ldy*ldy)
        f= -1 if (row['Zoneinuit'] =='uit') else 1
        totalar[1] +=f*row[ifield]
        totalar[1-f] +=f*row[ifield]
        fs=f*ascale*row[ifield]/lori        
        (ex,ey)=(lx-ldx*fs,ly-ldy*fs)
        #print ( (lx, ly, ldx, ldy) )
        #ax.arrow(lx, ly, ldx, ldy)        
        ax.annotate("",xytext=(ex,ey),xy=(lx, ly), 
                    arrowprops=dict(arrowstyle="<-"))
        ax.set_xlim(left=pltpa['scleft'], right=pltpa['scright'])
        ax.set_ylim(top=pltpa['sctop'], bottom=pltpa['scbottom'])
        ft = f*max( abs(fs*1.1), pltpa['minttxsp']/lori  )
        (ext,eyt)=(lx-ldx*ft,ly-ldy*ft)
        ax.annotate("%5.0f"%(row[ifield]),xy=(ext,eyt),
                   horizontalalignment='center',
                   verticalalignment='center',alpha=0.5)
    ax.annotate("in  %6.0f\n%6.0f\nuit %6.0f"%(totalar[0],totalar[1],totalar[2]),xy=pltpa['totalpos'])
    cx.add_basemap(pland, source= ndwimport.prov0,crs=plot_crs)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(plaxkm))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(plaxkm))

    #ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    ax.set_title(tit)
    figname = "../output/"+fn+".png";
    fig.savefig(figname,dpi=300)


show_numbers(summs25,'Intensiteit',0.15,
             'Werkdagen 2025 0-24 hrs','htnmeetptovar',pltparahtn)
# -

oshrs=[7,8]
htncordtao= htncordta[htncordta['uur'].isin(oshrs)]
summso = htncordtao.groupby(['centrum','richting','Zoneinuit','ID','perstart','PlotPt','Drlov']).agg('sum')[['Intensiteit']].reset_index()
summs25o=summso[summso['perstart'].dt.year.isin([2025])]
summs25o
show_numbers(summs25o,'Intensiteit',1,
             'Werkdagen 2025 7:00-9:00 hrs','htnmeetptovaro',pltparahtn)

mshrs=[16,17]
htncordtam= htncordta[htncordta['uur'].isin(mshrs)]
summsm = htncordtam.groupby(['centrum','richting','Zoneinuit','ID','perstart','PlotPt','Drlov']).agg('sum')[['Intensiteit']].reset_index()
summs25m=summsm[summsm['perstart'].dt.year.isin([2025])]
summs25m
show_numbers(summs25m,'Intensiteit',1,
             'Werkdagen 2025 16:00-18:00 hrs','htnmeetptovarm',pltparahtn)

excorona=[2016,2017,2020,2021]
htncordtanc = htncordta[ (htncordta['perstart'].dt.year.isin(excorona)==False) ]
summsud = htncordtanc.groupby(['uur','Zoneinuit','perstart'])['Intensiteit'].agg('sum').reset_index()
sns.lineplot(data=summsud,x='uur',y='Intensiteit',hue='Zoneinuit',style='perstart')
plt.title('''Totaal per uur en richting op werkdagen 
excl 2020,2021''')

summsur= htncordtanc.groupby(['uur','richting','perstart']).agg('sum')[['Intensiteit']].reset_index()
sns.lineplot(data=summsur,x='uur',y='Intensiteit',hue='richting',style='perstart')
plt.title('''Totaal per uur en richting op werkdagen 
2018-2025 ex corona''')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

summsur= htncordtanc.groupby(['uur','richting','perstart']).agg('sum')[['Balans']].reset_index()
sns.lineplot(data=summsur,x='uur',y='Balans',hue='richting',style='perstart')
plt.title('''Balans per uur en richting op werkdagen + is Houten in
spreiding 2022-2025 aangegeven''')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

summsur= htncordta.groupby(['richting','perstart'])['Intensiteit'].agg('sum').reset_index()
sns.lineplot(data=summsur,x='perstart',y='Intensiteit',hue='richting')
plt.title('Bijdragen per werkdag van verschillende richtingen per jaar')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

summsud = htncordta.groupby(['Zoneinuit','perstart'])['Intensiteit'].agg('sum').reset_index()
sns.lineplot(data=summsud,x='perstart',y='Intensiteit',hue='Zoneinuit')
plt.title("""Totaalplot in en uit (moet 0 zijn voor balans):
    Verschillen over de dag meetfouten en via niet gemeten wegen""")

ndiv=603
summsud = (htncordta.groupby(['perstart'])['Intensiteit'].agg('sum')/ndiv).reset_index()
#display(summsud)
sns.lineplot(data=summsud,x='perstart',y='Intensiteit')
plt.title('groei auto bewegingen in/uit houten per werkdag: 2022 =100')

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

ochturen=(5,6,7,8,9)
miduren=(15,16,17,18,19)
def adduuriucat(dfin):
    df=dfin.copy()
    df['pendelcat'] = 'buitensp'
    df['pendelcat'] = df['pendelcat'] .where(False== ((df['uur'].isin(ochturen) ) & (df['Zoneinuit']=="in")),'bezoekersp')
    df['pendelcat'] = df['pendelcat'] .where(False==( (df['uur'].isin(ochturen) ) & (df['Zoneinuit']=="uit")),'bewonersp')
    df['pendelcat'] = df['pendelcat'] .where(False== ((df['uur'].isin(miduren) ) & (df['Zoneinuit']=="uit")),'bezoekersp')
    df['pendelcat'] = df['pendelcat'] .where(False==( (df['uur'].isin(miduren) ) & (df['Zoneinuit']=="in")),'bewonersp')
    return df
htncordtap= adduuriucat( htncordta)

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

xlshtns2list= (glob.glob("../data/intensiteit-snelheid-htn-20?[57]-s2.xlsx"))
xlshtns2list

# +
#ODIN data
# -

summ1=summ1gemdatahtn.groupby(['Jaar','AankGem','Weekdag'])['FactorV'].agg('sum').reset_index()
sns.lineplot(data=summ1,x='Jaar',y='FactorV',hue='Weekdag',style='AankGem', marker= 'o')

summ1gemdatawerkd= summ1gemdatahtn[summ1gemdatahtn['Weekdag'].isin([2,3,4,5,6])]

# +
rscalea={'in':7/5/365,'uit':7/5/365, 'binnen': 7/5/365, 'buiten' : 20000000*7/5 / 18000000000/365}
def pltjr4gra(dat,xfield,field,txt,rscale,normfactorV):
    fieldexpl= {"FactorVActive":{False:"aantal loop+fiets (buiten rel)",True:"deel loop+fiets"},
                "FactorV":{False:"aantal ritten (buiten rel)",True:"een"},
                "FactorKm":{False:"totale reisafstand (km) (buiten rel)",True:"gemiddelde afstand (km)"}
               }
    #['VertGem','AankGem','WoGem']
    gemfield=min(dat['VertGem'])
    addfv=[] if (field=='FactorV') or not normfactorV else ['FactorV']
    inuittot=dat.groupby(['verplricht',xfield])[[field]+addfv].agg('sum').reset_index()
    
    if normfactorV:
        inuittot['FactorVs'] = inuittot[field] / inuittot['FactorV'] 
    else:
        inuittot['FactorVs'] = inuittot[field] * (inuittot['verplricht'].map(rscale)) 
    #display(inuittot)
    inuittot['richting'] = inuittot['verplricht'] + " " + ("%.0f" %gemfield)
    p=sns.lineplot(data=inuittot,x=xfield,y='FactorVs',hue='richting',marker='o')
    if normfactorV & (field =="FactorVActive"):
        p.set_ylim(bottom=0,top=1)
    else:
        p.set_ylim(bottom=0)
    ylab=fieldexpl[field][normfactorV]
    p.set_ylabel(ylab)     
    p.set_title(txt)
    return p

pltjr4gra(summ1gemdatawerkd,"Jaar",'FactorVActive',
          'ODIN aantal verplaatsingen actieve modes werkdagen',rscalea,False)  

# +
#Verelijkingen ODiN

# +
lokaallabel='lokaal'
def pendelcODIN(gemdat):
    df= gemdat[(gemdat['Weekdag'].isin([2,3,4,5,6]) ) & (gemdat['verplricht'] !='buiten')].copy();
    rscalea={'in':7/5/365,'uit':7/5/365, 'binnen': 7/5/365, 'buiten' : 20000000*7/5 / 18000000000/365}
    gemfield=min(df['VertGem'])
    df['Uur'] = df['AankUur']
    df['Uur'] = df['Uur'] .where(False== (df['verplricht']=="uit"), df['VertUur'] )
    df['pendelcat'] = 'buitensp'
    df['pendelcat'] = df['pendelcat'] .where(False== ((df['AankUur'].isin(ochturen) ) & (df['verplricht']=="in")),'bezoekersp')
    df['pendelcat'] = df['pendelcat'] .where(False==( (df['VertUur'].isin(ochturen) ) & (df['verplricht']=="uit")),'bewonersp')
    df['pendelcat'] = df['pendelcat'] .where(False== ((df['VertUur'].isin(miduren) ) & (df['verplricht']=="uit")),'bezoekersp')
    df['pendelcat'] = df['pendelcat'] .where(False==( (df['AankUur'].isin(miduren) ) & (df['verplricht']=="in")),'bewonersp')
    df['pendelcat'] = df['pendelcat'] .where(False==( df['verplricht'].isin( ["binnen"]  )),lokaallabel)
    df['pendelcat'] = df['pendelcat'] .where(False==( df['verplricht'].isin( ["buiten"]  )),"niet-gem" )
    return df

pc2htn=pendelcODIN(summ1gemdatahtn)   


# +
def datplotcumcatwo(dat, fieldsplit,valfield,mult):
    dagg = dat.groupby (['pendelcat',fieldsplit] )[[valfield]].agg('sum')
    dagg = dagg*mult
    dagg= dagg.reset_index().sort_values(fieldsplit)
    dagg[valfield]=dagg.groupby(['pendelcat'])[valfield].cumsum()
    dagg[valfield] = dagg[valfield].where(dagg['pendelcat']  !=lokaallabel,0.5 * dagg[valfield])
    dagg['opdeling'] =fieldsplit
    return dagg
    
def modplotopdcatwo(fig,ax,dat, fieldsplit,title,valfield,jaarnorm):
    mult=7/5/365;
    if jaarnorm:
        jaren=dat['Jaar'].unique()
        mult /= len(jaren)
    dagg=datplotcumcatwo(dat, fieldsplit,valfield,mult ) 
    dagg=dagg.sort_values([fieldsplit,'pendelcat'],ascending=[True,True])
    
#    dagg['Jaar'] += dagg['opdeling'] .map(fieldsplit)

    hues=dagg[fieldsplit].unique()
#    print(hues[::-1])
    sns.barplot(ax=ax,data=dagg,x='pendelcat', y= valfield , 
                hue=fieldsplit,dodge=0,hue_order=hues[::-1])
    leglabels= {'WoGem':'Woongemeente','KHvm_expl' : 'Hoofdvervoermiddel'}
    ax.legend(title=leglabels[fieldsplit], bbox_to_anchor=(1.01, 0.95), loc=2, borderaxespad=0.,framealpha=0)
    ax.set_title(title )
    #return daggcum
fig, axs = plt.subplots(1, 1)    
modplotopdcatwo(fig,axs,pc2htn,'WoGem', 'Alle verplaatsingen per werkdag','FactorV',True)


# +
def ODINkeygrph(pc2,legloc,locabbr):
    fig, axs = plt.subplots(2, 2,figsize=(12,12))
    fig.subplots_adjust(hspace=0.3,wspace=0.4)
    modplotopdcatwo(fig,axs[0,0],pc2,'WoGem', 'Alle verplaatsingen per werkdag '+legloc,'FactorV',True)
    modplotopdcatwo(fig,axs[0,1],pc2,'KHvm_expl', 'Alle verplaatsingen per werkdag '+legloc,'FactorV',True)
    modplotopdcatwo(fig,axs[1,0], pc2[pc2['KHvm']==1],'WoGem', 'Verplaatsingen Autobestuurders per werkdag '+legloc,'FactorV',True)
    modplotopdcatwo(fig,axs[1,1], pc2[pc2['KHvm']==1],'WoGem', 'Kilometers Autobestuurders per werkdag '+legloc,'FactorKm',True)
    fig.savefig("../output/"+locabbr+"_pendODINWOgem.svg",dpi=300, bbox_inches='tight')   
    
ODINkeygrph(pc2htn,"Houten","htn") 


# -

def ODINuurcheck(pc2,legloc,locabbr):
    p2uur= pc2[(pc2['KHvm']==1) & (pc2['verplricht']!="binnen")].groupby (['pendelcat','WoGem','Uur'] )[['FactorV']].agg('sum').reset_index()
    sns.lineplot(data=p2uur ,x='Uur', y='FactorV',hue='pendelcat',style='WoGem',marker= 'o')
    plt.title('''Indeling controleren: bewoners/bezoekers sterk contrast op WoGem''')
    plt.savefig("../output/"+locabbr+"_penduurchk.svg",dpi=300, bbox_inches='tight')   
ODINuurcheck(pc2htn,"Houten","htn") 


# +
def jrODINpendel(pc2, fieldsplit,title,valfield,teldat,legloc,locabbr):
    dat = pc2[(pc2['KHvm']==1) & (pc2['pendelcat'] !=lokaallabel)]
    mult=7/5/365;
    dagg= dat.groupby (['pendelcat',fieldsplit] )[[valfield]].agg('sum').reset_index()
    dagg['pendeldata'] = dagg['pendelcat']
    dagg['Intensiteit'] = dagg[valfield] *mult
    dagg['bron']= 'enquetes'
    summsur= teldat.groupby(['pendelcat','perstart']).agg('sum')[['Intensiteit']].reset_index()
    summsur['bron']= 'tellingen'
    summsur['pendeldata'] = 'tellingen '+summsur['pendelcat']
    summsur['Jaar'] = summsur['perstart'].dt.year
    cframe=pd.concat([dagg,summsur])
#    print(cframe)
    p=sns.lineplot(data=cframe,x='Jaar',y='Intensiteit',hue='pendelcat',style='bron',marker='o')
    p.set_ylim(bottom=0)
    plt.title('Pendel aantallen '+legloc+' per werkdag')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    fig.savefig("../output/"+locabbr+"_pendjrvg1.svg",dpi=300, bbox_inches='tight')    
    
jrODINpendel(pc2htn ,'Jaar', 'Autobestuurders','FactorV',htncordtap,"Houten","htn") 
# -





pltjr4gra(summ1gemdatawerkd,"VertUur",'FactorVActive',
          'ODIN aantal verplaatsingen actieve modes werkdagen',rscalea,False)  

allyr=range(2000,2050)
def telvsodin(teldatainuit, ODINdta,xfield,jaarsel,tit,savf):
    rscalew={'in':1/(5*52),'uit':1/(5*52), 'binnen': 1/(5*52), 'buiten' : 20000000 / 18000000000/365}
    #auto bestuurders
    ODINdta['uur']=ODINdta['VertUur'].where(ODINdta['verplricht'].str[0:2] !="in", ODINdta['AankUur'])
    datawerkd= ODINdta[ODINdta['Weekdag'].isin([2,3,4,5,6])]
    datawerkd= datawerkd[datawerkd['Jaar'].isin(jaarsel) ]
    teldatainuit['Jaar']=teldatainuit['perstart'].dt.year
    teldatainuit= teldatainuit[teldatainuit['Jaar'].isin(jaarsel) ]
    summsud = teldatainuit.groupby(['Zoneinuit',xfield])['Intensiteit'].agg('sum').reset_index()
    p=sns.lineplot(data=summsud,x=xfield,y='Intensiteit',hue='Zoneinuit',marker='x')
    p=pltjr4gra(datawerkd[datawerkd['KHvm']==1],xfield,'FactorV',
             'ODIN: aantal verplaatsingen als auto bestuurder per werkdag',     rscalew,False)
    p.set_title(tit)
    return p
telvsodin(htncordta, summ1gemdatahtn,'Jaar',allyr,"""Teldata lussen in/uit Houten vs ODIN aut bestuurder 2018-2022:
        data werkdagen: ODIN sterker Corona effect dan verkeerswegen""","htniuODINcmp")  

yrboth=(2018,2019,2021,2022,2023)
telvsodin(htncordta, summ1gemdatahtn,'uur',
          yrboth,"""Teldata lussen in/uit Houten vs ODIN aut bestuurder 2018-2022:
        data werkdagen: ODIN sterker Corona effect dan verkeerswegen""","htniuODINcmp") 

# +
#wijk bij duurstede
# -

wijklst= (glob.glob("../data/intensiteit-snelheid-wijk-20??-s2.xlsx"))
wijklst

idfwijkmy =[ ndwimport.ndw_od_read_overzicht_en_intensiteiten(testfil,"a12bijmy",testfil) for testfil in wijklst ]
idfwijkmy=pd.concat(idfwijkmy)

targgem =352
#targgemcode = 'GM%04.0f'%targgem
(allgem_CBSsum,summ1gemdatawijk)=selgemyrs(targgem)
#summ1gemdata =pd.read_pickle ("../data/gem1odin_"+targgemcode+".pkl")

if (not suprtests):   
    fig, ax = plt.subplots()
    allgem_CBSsum.set_crs(crs="epsg:28992")
    pland=allgem_CBSsum.boundary.plot(color='green',alpha=0.1,ax=ax)
    cx.add_basemap(pland, source= ndwimport.prov0,crs=plot_crs)
    odfwijk= ndwimport.ndw_od_read_overzicht(wijklst[0],"testseq12","testcoll20260522")
    pland= add_geodict(odfwijk,gdc,ax,'blue','meetpt')
#    pland= add_geodict( odfbnk,gdc,ax,'grey','overig bnk')
#    pland= add_geodict( ndwimport.odf12,gdc,ax,'red','overig a12')
#    pland= add_geodict(  stationplc,gdc,ax,'green','OV, pont')
#    pland= add_geodict( odfhtn,gdc,ax,'blue','Gebruikt htn')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    figname = "../output/wijkmeetptovgg.png";
    fig.savefig(figname,dpi=300)
    namesptsx=(pd.concat(gdc).copy().set_index('ID')['geometry'].x.to_dict())
    namesptsy=(pd.concat(gdc).copy().set_index('ID')['geometry'].y.to_dict())
    #display(namespts)

some_string="""ID	centrum	richting	Zoneinuit	estfrID	IDsinds	PlotPt	Drlov
PUT01_PUVIS_N229.13_0_2	WijkbD	Odijk	in			PUT01_PUVIS_N229.13_0_2	PUT01_N229.19_0
PUT01_PUVIS_N229.13_1_2	WijkbD	Odijk	uit			PUT01_PUVIS_N229.13_1_2	PUT01_N229.19_0
PUT01_N227.11_0	WijkbD	Doorn	in			PUT01_N227.11_0	PUT01_N229.19_0
PUT01_N227.11_1	WijkbD	Doorn	uit			PUT01_N227.11_1	PUT01_N229.19_0"""
#read CSV string into pandas DataFrame
wijkri_config= pd.read_csv(io.StringIO(some_string), sep="\t")
display(wijkri_config)
wijkcordta=ndwimport.merge_initest(idfwijkmy,wijkri_config)
wijkcordta=wijkcordta[wijkcordta['centrum']=='WijkbD']
wijkcordta['Balans']=wijkcordta ['Zoneinuit'].map( {'in':1,'uit':-1 }) * wijkcordta['Intensiteit']

# +
excorona=[2016,2017,2020,2021]
wijkcordtanc = wijkcordta[ (wijkcordta['perstart'].dt.year.isin(excorona)==False) ]

summsur= wijkcordtanc.groupby(['uur','richting','perstart']).agg('sum')[['Intensiteit']].reset_index()
sns.lineplot(data=summsur,x='uur',y='Intensiteit',hue='richting',style='perstart')
plt.title('''Totaal per uur en richting op werkdagen 2018-2025''')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
fig.savefig("../output/wijkrichttot.svg",dpi=300, bbox_inches='tight')
# -

summsur= wijkcordtanc.groupby(['uur','richting','perstart']).agg('sum')[['Balans']].reset_index()
sns.lineplot(data=summsur,x='uur',y='Balans',hue='richting',style='perstart')
plt.title('''Balans per uur en richting op werkdagen 2018-2025''')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
fig.savefig("../output/wijkrichtbal.svg",dpi=300, bbox_inches='tight')

#    pland.set_ylim(bottom=435000,top=444000)
#    pland.set_xlim(left=137000,right=149000)
pltparawijk={'scleft':145000, 'scright':157000,
            'scbottom':440000,'sctop':450000,
            'minttxsp':1000,
            'geodx':namesptsx,'geody':namesptsy,
           'totalpos':[148000,443000]}
summswijk = wijkcordta.groupby(['centrum','richting','Zoneinuit','ID','perstart','PlotPt','Drlov']).agg('sum')[['Intensiteit']].reset_index()
summswijk25=summswijk[summswijk['perstart'].dt.year.isin([2025])]
print(summswijk25)
show_numbers(summswijk25,'Intensiteit',0.15,
             'Werkdagen 2025 0-24 hrs','wijkmeetptovar',pltparawijk)

wijkcordtap= adduuriucat(wijkcordta)
#wijkcordtap

summsur= wijkcordtap.groupby(['pendelcat','perstart']).agg('sum')[['Intensiteit']].reset_index()
summsur['pendeldata'] = 'tellingen '+summsur['pendelcat']
p=sns.lineplot(data=summsur,x='perstart',y='Intensiteit',hue='pendeldata',marker='o')
p.set_ylim(bottom=0)
plt.title('''Pendel aantallen op werkdagen 2018-2025''')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
fig.savefig("../output/wijkpendtelcat.svg",dpi=300, bbox_inches='tight')

# +
#nu vergelijkingen ODiN
# -

pc2wijk=pendelcODIN(summ1gemdatawijk)    

ODINkeygrph(pc2wijk,"Wijk bij Duurstede","wijk") 

ODINuurcheck(pc2wijk,"Wijk bij Duurstede","wijk") 

jrODINpendel( pc2wijk,'Jaar', 'Autobestuurders','FactorV',wijkcordtap,"Wijk bij Duurstede","wijk")     

telvsodin(wijkcordta, summ1gemdatawijk,'Jaar',allyr,"""Teldata lussen in/uit Wijk bij Duurstede vs ODIN aut bestuurder 2018-2022:
        data werkdagen: ODIN sterker Corona effect dan verkeerswegen""","cliuODINcmp")  

yrboth=(2019,2021)
telvsodin(wijkcordta, summ1gemdatawijk,'uur',
          yrboth,"""Teldata lussen in/uit Wijk bij Duurstede vs ODIN aut bestuurder 2018-2022:
        data werkdagen: ODIN sterker Corona effect dan verkeerswegen""","htniuODINcmp") 

# +
#Culemborg
# -

targgem =216
(allgem_CBSsum,summ1gemdatacl)=selgemyrs(targgem)
#summ1gemdata =pd.read_pickle ("../data/gem1odin_"+targgemcode+".pkl")

# +
some_string="""Fecode,ID,Volledige naam,Traject,GPSX,GPSY
991,Lek,pont bij Culemborg,Ut-Gdm,5.208283,51.965951
154,Cl,Culemborg,Ut-Gdm,5.2269444466,51.9466667175"""
df= pd.read_csv(io.StringIO(some_string), sep=",")
stationplccl = geopandas.GeoDataFrame(
      df, geometry=geopandas.points_from_xy(df.GPSX, df.GPSY), crs="EPSG:4326")

stationplccl
# -

if (not suprtests):   
    fig, ax = plt.subplots()
    allgem_CBSsum.set_crs(crs="epsg:28992")
    pland=allgem_CBSsum.boundary.plot(color='green',alpha=0.1,ax=ax)
    pland.set_ylim(bottom=435000,top=444000)
    pland.set_xlim(left=137000,right=149000)
    ax.set_aspect(aspect=1.0)
    cx.add_basemap(pland, source= ndwimport.prov0,crs=plot_crs)
    odfwijk= ndwimport.ndw_od_read_overzicht(wijklst[1],"testseq12","testcoll20260522")
#    print(odfwijk)
    pland= add_geodict(odfwijk,gdc,ax,'blue','meetpt')    
#    pland= add_geodict( odfbnk,gdc,ax,'grey','overig bnk')
#    pland= add_geodict( ndwimport.odf12,gdc,ax,'red','overig a12')
    pland= add_geodict(  stationplccl,gdc,ax,'green','OV, pont')
#    pland= add_geodict( odfhtn,gdc,ax,'blue','Gebruikt htn')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#    ax.set_aspect(aspect=1.0)
    figname = "../output/clmeetptovgg.png";
    fig.savefig(figname,dpi=300)
    namesptsx=(pd.concat(gdc).copy().set_index('ID')['geometry'].x.to_dict())
    namesptsy=(pd.concat(gdc).copy().set_index('ID')['geometry'].y.to_dict())
    #display(namespts)

some_string="""ID	centrum	richting	Zoneinuit	estfrID	IDsinds	PlotPt	Drlov
PGL10_N320-01_hmp_1.16_Li_HTN2589	Culemborg	A2	uit			PGL10_N320-01_hmp_1.16_Li_HTN2589	Cl
PGL10_N320-01_hmp_1.16_Re_HTN2589	Culemborg	A2	in			PGL10_N320-01_hmp_1.16_Re_HTN2589	Cl
PGL10_N320-04_hmp_8.30_Li_HTN2593	Culemborg	Maurik	in			PGL10_N320-04_hmp_8.30_Li_HTN2593	Cl
PGL10_N320-04_hmp_8.30_Re_HTN2593	Culemborg	Maurik	uit			PGL10_N320-04_hmp_8.30_Re_HTN2593	Cl
PGL10_N833-01_hmp_6.94_Li_HTN2699	Culemborg	Geldermalsen	in			PGL10_N833-01_hmp_6.94_Li_HTN2699	Cl
PGL10_N833-01_hmp_6.94_Re_HTN2699	Culemborg	Geldermalsen	uit			PGL10_N833-01_hmp_6.94_Re_HTN2699	Cl"""
#read CSV string into pandas DataFrame
clri_config= pd.read_csv(io.StringIO(some_string), sep="\t")
display(clri_config)
clcordta=ndwimport.merge_initest(idfwijkmy,clri_config)
clcordta=clcordta[clcordta['centrum']=='Culemborg']
clcordta['Balans']=clcordta ['Zoneinuit'].map( {'in':1,'uit':-1 }) * clcordta['Intensiteit']

summsur= clcordta.groupby(['uur','richting','perstart']).agg('sum')[['Intensiteit']].reset_index()
sns.lineplot(data=summsur,x='uur',y='Intensiteit',hue='richting',style='perstart')
plt.title('''Totaal per uur en richting op werkdagen 
2018-2025 ex corona''')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

fig, ax = plt.subplots()
summsur= clcordta.groupby(['uur','richting','perstart']).agg('sum')[['Balans']].reset_index()
sns.lineplot(ax=ax,data=summsur,x='uur',y='Balans',hue='richting',style='perstart')
plt.title('''Balans per uur en richting op werkdagen 
2018-2025 ex corona''')
ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
fig.savefig("../output/clrichtbal.svg",dpi=300, bbox_inches='tight')

#    pland.set_ylim(bottom=435000,top=444000)
#    pland.set_xlim(left=137000,right=149000)
pltparacl={'scleft':137000, 'scright':149000,
            'scbottom':435000,'sctop':444000,
            'minttxsp':1000,
            'geodx':namesptsx,'geody':namesptsy,
           'totalpos':[138000,441000]}
summscl = clcordta.groupby(['centrum','richting','Zoneinuit','ID','perstart','PlotPt','Drlov']).agg('sum')[['Intensiteit']].reset_index()
summscl25=summscl[summscl['perstart'].dt.year.isin([2025])]
summscl25
show_numbers(summscl25,'Intensiteit',0.15,
             'Werkdagen 2025 0-24 hrs','cl_meetptovar',pltparacl)

clcordtap= adduuriucat(clcordta)

# +
#nu vergelijkingen ODiN
# -

pc2cl=pendelcODIN(summ1gemdatacl)    

ODINkeygrph(pc2cl,"Culemborg","cl") 

ODINuurcheck(pc2cl,"Culemborg","cl") 

jrODINpendel( pc2cl,'Jaar', 'Autobestuurders','FactorV',clcordtap,"Culemborg","cl") 





telvsodin(clcordta, summ1gemdatacl,'Jaar',allyr,"""Teldata lussen in/uit Cl vs ODIN aut bestuurder 2018-2022:
        data werkdagen: ODIN hoger dan verkeerswegen""","cliuODINcmp")  

telvsodin(clcordta, summ1gemdatacl,'uur',
          yrboth,"""Teldata lussen in/uit Culemborg vs ODIN aut bestuurder 2018-2022:
        data werkdagen: ODIN sterker Corona effect dan verkeerswegen""","htniuODINcmp") 



# +
#ijsselstein
# -

ijstlst= (glob.glob("../data/intensiteit-snelheid-ijsst-20??-s1.xlsx"))
ijstlst

idfijstmy =[ ndwimport.ndw_od_read_overzicht_en_intensiteiten(testfil,"a12bijmy",testfil) for testfil in ijstlst ]
idfijstmy=pd.concat(idfijstmy)

targgem =353
(allgem_CBSsum,summ1gemdata)=selgemyrs(targgem)

some_string="""ID	centrum	richting	Zoneinuit	estfrID	IDsinds	PlotPt	Drlov
GEO1A_A_RWS_359612	Ijsselstein	A2R	in			GEO1A_A_RWS_359612	PUT01_PUVIS_N210.37_0_2
GEO1A_A_RWS_359616	Ijsselstein	A2R	uit			GEO1A_A_RWS_359616	PUT01_PUVIS_N210.37_0_2
PUT01_N210.29_0	Ijsselstein	A2Ngein	uit			PUT01_N210.29_0	PUT01_PUVIS_N210.37_0_2
PUT01_N210.29_3	Ijsselstein	A2Ngein	in			PUT01_N210.29_3	PUT01_PUVIS_N210.37_0_2
PUT01_N210.31_0	Ijsselstein	Benschop	in			PUT01_N210.31_0	PUT01_PUVIS_N210.37_0_2
PUT01_N210.31_1	Ijsselstein	Benschop	uit			PUT01_N210.31_1	PUT01_PUVIS_N210.37_0_2"""
#read CSV string into pandas DataFrame
ijstri_config= pd.read_csv(io.StringIO(some_string), sep="\t")
display(ijstri_config)
ijstcordta=ndwimport.merge_initest(idfijstmy,ijstri_config)
ijstcordta=ijstcordta[ijstcordta['centrum']=='Ijsselstein']
ijstcordta['Balans']=ijstcordta ['Zoneinuit'].map( {'in':1,'uit':-1 }) * ijstcordta['Intensiteit']

if (not suprtests):   
    fig, ax = plt.subplots()
    allgem_CBSsum.set_crs(crs="epsg:28992")
    pland=allgem_CBSsum.boundary.plot(color='green',alpha=0.1,ax=ax)
    cx.add_basemap(pland, source= ndwimport.prov0,crs=plot_crs)
    odfijst= ndwimport.ndw_od_read_overzicht(ijstlst[0],"testseq12","testcoll20260522")
    pland= add_geodict(odfijst,gdc,ax,'blue','meetpt')
#    pland= add_geodict( odfbnk,gdc,ax,'grey','overig bnk')
#    pland= add_geodict( ndwimport.odf12,gdc,ax,'red','overig a12')
#    pland= add_geodict(  stationplc,gdc,ax,'green','OV, pont')
#    pland= add_geodict( odfhtn,gdc,ax,'blue','Gebruikt htn')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    figname = "../output/ijstmeetptovgg.png";
    fig.savefig(figname,dpi=300)
    namesptsx=(pd.concat(gdc).copy().set_index('ID')['geometry'].x.to_dict())
    namesptsy=(pd.concat(gdc).copy().set_index('ID')['geometry'].y.to_dict())
    #display(namespts)

summsur= ijstcordta.groupby(['uur','richting','perstart']).agg('sum')[['Intensiteit']].reset_index()
sns.lineplot(data=summsur,x='uur',y='Intensiteit',hue='richting',style='perstart')
plt.title('''Totaal per uur en richting op werkdagen 
2018-2025 ex corona''')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

summsur= ijstcordta.groupby(['uur','richting','perstart']).agg('sum')[['Balans']].reset_index()
sns.lineplot(data=summsur,x='uur',y='Balans',hue='richting',style='perstart')
plt.title('''Totaal per uur en richting op werkdagen 
2018-2025 ex corona''')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)


