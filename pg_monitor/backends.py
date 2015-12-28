#!/usr/bin/python

import sys
import checkStatus as st
import sql
import factors as fac

# var=val;warn;crit;min;max
# check_mk output format 
# status 	item_name	perfdata	output


def getBackends( param=None ) :
	item_name = 'POSTGRES_BACKENDS'
	status = []
	perfdata = '-'
	output = ''
	if param != None :
		

                query = "SELECT \
			      dbs.datname, \
                              ( current_setting('max_connections')::int - current_setting('superuser_reserved_connections')::int ) as max_allowed_connect,\
                              coalesce( nullif((numbackends -1 ),-1), 0 ) as connect_count,\
                              ( coalesce( nullif((numbackends -1 ),-1), 0 ) * 100 ) / current_setting('max_connections')::int as percent_connect \
                         FROM \
				pg_stat_database dbs \
                         JOIN \
				pg_database db on db.datname = dbs.datname \
                         WHERE \
				db.datistemplate IS FALSE "
				
		results = sql.getSQLResult ( {'host': param['host'] , 'port' : param['port'], 'dbname': 'postgres', 'user' : param['user'] ,'password' : param['password'] } ,query ) 
		connect_sum = 0

		if results[0] == None :
			return '2' + ' ' + item_name  + ' ' + '-' + ' ' + str(results[1])

		rows = results[1]
		if len(rows[1]) > 0  :
			max_connect = rows[0][1]
			warning = fac.getNumberPercentLimits(  param['warning'] , max_connect )
			critical = fac.getNumberPercentLimits(  param['critical'] , max_connect )
			for row in rows :
				if int(row[2]) != 0 :
					if perfdata == '-' :
						perfdata = row[0] + '=' + str(row[2]) + ';' +  str(warning) + ';' + str(critical) + ';' + '1' + ';' + str(row[1]) 
						output =  '{0:s} has {1:d}% of the total connections used'.format(row[0],row[3])
					elif perfdata != '-'  :
						perfdata = perfdata + '|' + row[0] + '=' + str(row[2]) + ';' +  str(warning) + ';' + str(critical) + ';' + '1' + ';' + str(row[1])
						output =  output + ';{0:s} has {1:d}% of the total connections used'.format(row[0],row[3])
					connect_sum += int(row[2])		
				else :
					if perfdata == '-' :
                                        	perfdata = row[0] + '=' + str(row[2]) + ';' +  str(warning) + ';' + str(critical) + ';' + '1' + ';' + str(row[1])
                                        	output =  'No backend currenlty exists for {0:s} database - which might implies that the Application connected to the database might be down or the database currently refuses connections to it '.format(row[0])
                                	elif perfdata != '-'  :
                                        	perfdata = perfdata + '|' + row[0] + '=' + str(row[2]) + ';' +  str(warning) + ';' + str(critical) + ';' + '1' + ';' + str(row[1])
                                        	output =  output + ';No backend currenlty exists for {0:s} database - which might implies that the Application connected to the database might be down or the database currently refuses connections to it '.format(row[0])
					status.append(2)
			status.append( st.getStatus( int(connect_sum),int(warning) , int(critical), int('0') , int(max_connect)  ) )
			
			status.sort( reverse=True )
			return str(status[0]) + ' ' + item_name + ' ' + str(perfdata) + ' ' + output
	else :
		return '2' + ' ' + 'POSTGRES_BACKENDS' + ' ' + '-' + ' ' + 'Invalid parameters passed to check'
## testing the function 
if __name__ == '__main__' :
	print ( getBackends( {'host' : 'localhost', 'port' : '5432' ,'user' : 'postgres' , 'password' : '',\
                         'warning' : '30'  , 'critical' : '45%'  } )  ) 

