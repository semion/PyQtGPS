'''
Created on 24/10/2009

@author: Boris
'''
import sqlite3 
import os
import sys

airports = [
            (636,'Arad',None ,'Arad',31.228619,35.190900), 
            (636,'Bar Yehuda' ,'LLMZ',null,31.328169,35.388608),
            (636,'Ben Gurion' , 'LLBG','LOD',32.011389,34.886667),
            (636,'Eilat','LLET' ,'Eilat',29.561281,34.960081),
            (636,'En Yahav' ,'LLEY',None,30.621656,35.203325),
            (636,'Eyn Shemer' ,'LLES',None,32.440814,35.007661),
            (636,'Haifa' ,'LLHA' ,'Haifa',32.809444,35.043056),
            (636,'Hatserim' ,None,None,31.233358,34.662558),
            (636,'Hatserim NorthWest' ,None,None,31.260744,34.640381),
            (636,'Hatzor' ,'LLHS',None,31.762500,34.727222),
            (636,'Mahanaim' ,'LLIB','Rosh Pina',32.981047,35.571908),
            (636,'Megido' ,'LLMG',None,32.597139,35.228803),
            (636,'Nevatim' ,'LLNV',None,31.208347,35.012300),
            (636,'Nizzana West' ,None,None,30.859444,34.443054),
            (636,'Ovda' ,'LLOV',None,29.940250,34.935850),
            (636,'Palmahim' ,None,None,31.897925,34.690769),
            (636,'Ramat David' ,'LLRD',None,32.665142,35.179458),
            (636,'Ramon' ,'LLRM',None,30.776061,34.666769),
            (636,'SDe Dov' ,'LLSD','Tel Aviv',32.114661,34.782239),
            (636,'Tel Nof' ,'LLEK',None,31.839472,34.821844),
            (636,'Teyman' ,'LLBS','Beer Sheba',31.287003,34.722953),
            (636,'Yotvata' ,None,None,29.906172,35.066650)]

conn = sqlite3.connect("testDB5") #'mainDB')
c = conn.cursor()

conn.execute(''' create table country (country_id  INTEGER primary key not null, country_name TEXT unique)''')
#c.execute(''' drop table country1''')
#c.execute("""insert into country values('636','Israel')""")

#conn.execute(''' create table port(port_id INTEGER PRIMARY KEY , country_id INTEGER not null, port_name TEXT unique not null, icao_id TEXT, city TEXT, lat REAL not null, lng REAL not null,FOREIGN KEY(country_id) REFERENCES country(country_id))''')


#c.executemany("insert into port (country_id, port_name, icao_id, city, lat, lng ) values(?,?,?,?,?,?)",airports)

#print c.lastrowid
c.execute("insert into port (port_id, country_id, port_name, icao_id, city, lat, lng )  values(null,'636','TEST','null','null','25.333333','43.444444')")
conn.commit()

for row in c.execute("select port_id, country_id, port_name, icao_id, city, lat, lng from port"):
    print row


for row in c.execute("select port_name from port where(country_id = 636 and port_id < 3)"):
    print row 
c.close()


        