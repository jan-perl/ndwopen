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



allgem_CBSsum=pd.read_pickle ("../data/gem1sum_GM0321.pkl")

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
ndwimport.summstr_normprep(rdata27hmy[rdata27hmy["perend"]>ndwimport.calendafter],
                             'a27','Intensiteit',[],['ID']).reset_index()   

usefactsa27hmy=ndwimport.summstr_normprep(rdata27hmy[rdata27hmy["perend"]>ndwimport.calendafter],
                             'a27','Intensiteit',[],[]).reset_index()    
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

xlshtns2list= (glob.glob("../data/intensiteit-snelheid-htn-20?[57]-s2.xlsx"))
xlshtns2list


