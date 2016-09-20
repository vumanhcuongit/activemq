#!/usr/bin/python

import fileinput
import sys
import os
import shutil
import re


ACTIVEMQ_HOME = "/opt/activemq"
ACTIVEMQ_CONF = ACTIVEMQ_HOME + '/conf.tmp'


class ServiceRun():


    def replace_all(self, file, searchRegex, replaceExp):
      """ Replace String in file with regex
      :param file: The file name where you should to modify the string
      :param searchRegex: The pattern witch must match to replace the string
      :param replaceExp: The string replacement
      :return:
      """

      regex = re.compile(searchRegex, re.IGNORECASE)

      f = open(file,'r')
      out = f.readlines()
      f.close()

      f = open(file,'w')

      for line in out:
          if regex.search(line) is not None:
            line = regex.sub(replaceExp, line)

          f.write(line)

      f.close()


    def add_end_file(self, file, line):
        """ Add line at the end of file

        :param file: The file where you should to add line to the end
        :param line: The line to add in file
        :return:
        """
        with open(file, "a") as myFile:
            myFile.write("\n" + line + "\n")



    def do_setting_activemq_users(self, login, password):
        global ACTIVEMQ_HOME

        if login is None or login == "" :
            raise KeyError("You must set the login")
        if password is None or password == "":
            raise KeyError("You must set the password")

        self.add_end_file(ACTIVEMQ_CONF + "/users.properties", login + "=" + password)

    def do_remove_default_account(self):
        global ACTIVEMQ_HOME


        self.replace_all(ACTIVEMQ_CONF + "/users.properties","admin=admin", "")
        self.replace_all(ACTIVEMQ_CONF + "/jetty-realm.properties", "admin: admin, admin", "")
        self.replace_all(ACTIVEMQ_CONF + "/jetty-realm.properties", "user: user, user", "")
        self.replace_all(ACTIVEMQ_CONF + "/groups.properties", "admins=admin", "")
        self.replace_all(ACTIVEMQ_CONF + "/jmx.access", "admin readwrite", "")
        self.replace_all(ACTIVEMQ_CONF + "/jmx.password", "admin activemq", "")
        self.replace_all(ACTIVEMQ_CONF + "/credentials.properties", "activemq\.username=system", "")
        self.replace_all(ACTIVEMQ_CONF + "/credentials.properties", "activemq\.password=manager", "")
        self.replace_all(ACTIVEMQ_CONF + "/credentials.properties", "guest\.password=password", "")



    def do_setting_activemq_credential(self, user, password):
        global ACTIVEMQ_HOME

        if user is None or user == "" :
    	       raise KeyError("You must set the user")

        if password is None or password == "" :
    	       raise KeyError("You must set the password")

        self.add_end_file(ACTIVEMQ_CONF + "/credentials.properties", "activemq.username=" + user)
        self.add_end_file(ACTIVEMQ_CONF + "/credentials.properties", "activemq.password=" + password)



    def do_setting_activemq_groups(self, group, users):
        global ACTIVEMQ_HOME

        if group is None or group == "" :
            raise KeyError("You must set the group")

        if users is None:
            self.add_end_file(ACTIVEMQ_CONF + "/groups.properties", group + "=")
        else:
            self.add_end_file(ACTIVEMQ_CONF + "/groups.properties", group + "=" + users)


    def do_setting_activemq_web_access(self, role, user, password):
        global ACTIVEMQ_HOME

        if role is None or role == "":
            raise KeyError("You must set the role")

        if user is None or user == "":
            raise KeyError("You must set the username")

        if password is None or password == "":
            raise KeyError("You must set the password")


        self.add_end_file(ACTIVEMQ_CONF + "/jetty-realm.properties", user + ": " + password + ", " +role);


    def do_setting_activemq_jmx_access(self, role, user, password):
        global ACTIVEMQ_HOME

        if role is None or role == "":
            raise KeyError("You must set role")

        if user is None or user == "":
            raise KeyError("You must set user")

        if password is None or password == "":
            raise KeyError("You must set password")

        self.add_end_file(ACTIVEMQ_CONF + "/jmx.access", user + " " + role)
        self.add_end_file(ACTIVEMQ_CONF + "/jmx.password", user + " " + password)


    def do_setting_activemq_log4j(self, loglevel):
        global ACTIVEMQ_HOME

        if loglevel is None or loglevel == "":
            raise KeyError("You must set loglevel")

        self.replace_all(ACTIVEMQ_CONF + "/log4j.properties", "log4j\.rootLogger=[^,]+", "log4j.rootLogger=" + loglevel)
        self.replace_all(ACTIVEMQ_CONF + "/log4j.properties", "log4j\.logger\.org\.apache\.activemq\.audit=[^,]+", "log4j.logger.org.apache.activemq.audit=" + loglevel)


    def do_setting_activemq_main(self, name, messageLimit, storageUsage, tempUsage, maxConnection, frameSize, topics, queues, enabledScheduler, enabledAuth, zkAddress="", zkPassword="", replicas="3", zkPath ="/activemq/leveldb-stores", hostname="" ):

        if name is None or name == "":
            raise KeyError("You must set the name")

        if messageLimit is None or messageLimit < 0:
            raise KeyError("You must set the messageLimit")

        if storageUsage is None or storageUsage == "":
            raise KeyError("You must set the storageUsage")

        if tempUsage is None or tempUsage == "":
            raise KeyError("You must set the tempStorage")

        if maxConnection is None or maxConnection < 0:
            raise KeyError("You must set the maxConnection")

        if frameSize is None or frameSize < 0:
            raise KeyError("You must set the frameSize")

        self.replace_all(ACTIVEMQ_CONF + "/activemq.xml", 'brokerName="[^"]*"', 'brokerName="' + name + '"')
        self.replace_all(ACTIVEMQ_CONF + "/activemq.xml", '<constantPendingMessageLimitStrategy limit="\d+"/>', '<constantPendingMessageLimitStrategy limit="' + str(messageLimit) + '"/>')
        self.replace_all(ACTIVEMQ_CONF + "/activemq.xml", '<storeUsage limit="[^"]+"/>', '<storeUsage limit="' + storageUsage + '"/>')
        self.replace_all(ACTIVEMQ_CONF + "/activemq.xml", '<tempUsage limit="[^"]+"/>', '<tempUsage limit="' + tempUsage + '"/>')
        self.replace_all(ACTIVEMQ_CONF + "/activemq.xml", '\?maximumConnections=1000', "?maximumConnections=" + str(maxConnection))
        self.replace_all(ACTIVEMQ_CONF + "/activemq.xml", 'wireFormat\.maxFrameSize=104857600', "wireFormat.maxFrameSize=" + str(frameSize))

        # Look for enabled scheduler
        if enabledScheduler == "true" :
        	self.replace_all(ACTIVEMQ_CONF + "/activemq.xml", '<broker', '<broker schedulerSupport="true"')

        # We inject the setting to manage right on topic and queue if needed
        if enabledAuth == "true":
            rightManagement = """<plugins>
              		             <!--  use JAAS to authenticate using the login.config file on the classpath to configure JAAS -->
              		             <jaasAuthenticationPlugin configuration="activemq" />
        		                 <authorizationPlugin>
                		            <map>
                  			            <authorizationMap>
                    				        <authorizationEntries>
                      					        <authorizationEntry queue=">" read="admins,reads,writes,owners" write="admins,writes,owners" admin="admins,owners" />
                      					        <authorizationEntry topic=">" read="admins,reads,writes,owners" write="admins,writes,owners" admin="admins,owners" />
                      					        <authorizationEntry topic="ActiveMQ.Advisory.>" read="admins,reads,writes,owners" write="admins,reads,writes,owners" admin="admins,reads,writes,owners"/>
                    				        </authorizationEntries>

                    				        <!-- let's assign roles to temporary destinations. comment this entry if we don't want any roles assigned to temp destinations  -->
                    				        <tempDestinationAuthorizationEntry>
                      					        <tempDestinationAuthorizationEntry read="tempDestinationAdmins" write="tempDestinationAdmins" admin="tempDestinationAdmins"/>
                   				            </tempDestinationAuthorizationEntry>
                  			            </authorizationMap>
                		            </map>
              		             </authorizationPlugin>
        	                     </plugins>\n"""
            self.replace_all(ACTIVEMQ_CONF + "/activemq.xml", '</broker>', rightManagement + '</broker>')



        if (topics is not None and topics != "") or (queues is not None and queues != ""):
            staticRoute = "<destinations>\n"
            if topics is not None and topics != "" :
                topicList = topics.split(';')
                for topic in topicList:
                    staticRoute += '<topic physicalName="' + topic + '" />' + "\n"

            if queues is not None and queues != "":
                queueList = queues.split(';')
                for queue in queueList:
                    staticRoute += '<queue physicalName="' + queue + '" />' + "\n"

            staticRoute += "</destinations>\n"

            self.replace_all(ACTIVEMQ_CONF + "/activemq.xml", '</broker>', staticRoute + '</broker>')
            
        # process Replicated LevelDB persistenceAdapter
        if zkAddress != "":
            # <kahaDB directory="${activemq.data}/kahadb"/>
            xml_string = """<replicatedLevelDB
                  directory="${{activemq.data}}"
                  replicas="{0}"
                  zkAddress="{1}"
                  bind="tcp://0.0.0.0:0"
                  zkPassword="{2}"
                  zkPath="{3}"
                  hostname="{4}"
                  securityToken="same_securityToken"
                  sync="quorum_mem"
                  />\n"""
            replicatedLevelDB = xml_string.format(replicas, 
                zkAddress, zkPassword, zkPath, hostname)
            self.replace_all(ACTIVEMQ_CONF + "/activemq.xml", '<kahaDB directory=".*/>', replicatedLevelDB)

    def do_setting_activemq_ip(self):
        line_ip = 'MQ_HOST_IP=`wget -q -O - http://169.254.169.250/2015-12-19/self/container/primary_ip`'
        line_options = 'ACTIVEMQ_OPTS="$ACTIVEMQ_OPTS -Dactivemq.host_ip=${MQ_HOST_IP} $ACTIVEMQ_OTHER_OPTS"'
          
        self.add_end_file(ACTIVEMQ_HOME + "/bin/env",
            line_ip + '\n' + line_options)
        self.replace_all(ACTIVEMQ_CONF + "/activemq.xml",
            '0\.0\.0\.0', '${activemq.host_ip}')
        
    
    def do_setting_activemq_mem(self, memString):
        self.replace_all(ACTIVEMQ_HOME + "/bin/env",
            'ACTIVEMQ_OPTS_MEMORY=".*"',
            'ACTIVEMQ_OPTS_MEMORY="{0}"'.format(memString) )

    def do_setting_activemq_wrapper(self, minMemoryInMB, maxMemoryInMb):

        if minMemoryInMB is None or minMemoryInMB < 0:
            raise KeyError("You must set the minMemory")

        if maxMemoryInMb is None or maxMemoryInMb < 0:
            raise KeyError("You must set the maxMemory")
            
        # -Xms64M -Xmx1024M        
        self.do_setting_activemq_mem('-Xms{0}M -Xmx{1}M'.
            format(minMemoryInMB,maxMemoryInMb))


    def do_init_activemq(self):

        # We change the activemq launcher to start activemq with activmq user
        self.replace_all(ACTIVEMQ_HOME + "/bin/env", 'ACTIVEMQ_USER=""', 'ACTIVEMQ_USER="activemq"')

        # We change some macro on wrapper.conf to move data
        # has set in docker env ACTIVEMQ_DATA
        # self.replace_all(ACTIVEMQ_HOME + "/bin/linux-x86-64/wrapper.conf" ,"set\.default\.ACTIVEMQ_DATA=%ACTIVEMQ_BASE%\/data", "set.default.ACTIVEMQ_DATA=/data/activemq")

        # Fix bug #4 "Cannot mount a custom activemq.xml"
        # has set in docker env ACTIVEMQ_CONF
        # self.replace_all(ACTIVEMQ_HOME + "/bin/linux-x86-64/wrapper.conf" ,"set\.default\.ACTIVEMQ_CONF=%ACTIVEMQ_BASE%/conf$", "set.default.ACTIVEMQ_CONF=%ACTIVEMQ_BASE%/conf.tmp")

        # We replace the log output
        self.replace_all(ACTIVEMQ_CONF + "/log4j.properties", "\$\{activemq\.base\}\/data\/", "/var/log/activemq/")
        # wrapper will not used
        # self.replace_all(ACTIVEMQ_HOME + "/bin/linux-x86-64/wrapper.conf" ,"wrapper\.logfile=%ACTIVEMQ_DATA%\/wrapper\.log", "wrapper.logfile=/var/log/activemq/wrapper.log")


if __name__ == '__main__':

    # We move all config file on temporary folder (Fix bug # 4)
    shutil.rmtree(ACTIVEMQ_CONF, ignore_errors=True);
    shutil.copytree(ACTIVEMQ_HOME + "/conf/", ACTIVEMQ_CONF);

    # We fix right on volume
    os.system("chown -R activemq:activemq /data/activemq")
    os.system("chown -R activemq:activemq " + ACTIVEMQ_CONF)
    os.system("chown -R activemq:activemq /var/log/activemq")

    serviceRun = ServiceRun()

    # We look if we must remove default account
    if os.getenv('ACTIVEMQ_REMOVE_DEFAULT_ACCOUNT') == "true":
        serviceRun.do_remove_default_account()

    # We init some fix parameter
    serviceRun.do_init_activemq()

    # We setting the admin account
    if os.getenv('ACTIVEMQ_ADMIN_LOGIN') is not None and os.getenv('ACTIVEMQ_ADMIN_PASSWORD') is not None:
        serviceRun.do_setting_activemq_users(os.getenv('ACTIVEMQ_ADMIN_LOGIN'), os.getenv('ACTIVEMQ_ADMIN_PASSWORD'))
        serviceRun.do_setting_activemq_web_access("admin", os.getenv('ACTIVEMQ_ADMIN_LOGIN'), os.getenv('ACTIVEMQ_ADMIN_PASSWORD'))
        serviceRun.do_setting_activemq_groups("admins", os.getenv('ACTIVEMQ_ADMIN_LOGIN'))
        serviceRun.do_setting_activemq_credential(os.getenv('ACTIVEMQ_ADMIN_LOGIN'), os.getenv('ACTIVEMQ_ADMIN_PASSWORD'))


    # We setting the user account
    if os.getenv('ACTIVEMQ_USER_LOGIN') is not None and os.getenv('ACTIVEMQ_USER_PASSWORD') is not None:
        serviceRun.do_setting_activemq_users(os.getenv('ACTIVEMQ_USER_LOGIN'), os.getenv('ACTIVEMQ_USER_PASSWORD'))
        serviceRun.do_setting_activemq_web_access("user", os.getenv('ACTIVEMQ_USER_LOGIN'), os.getenv('ACTIVEMQ_USER_PASSWORD'))


    # We setting the owner account
    if os.getenv('ACTIVEMQ_OWNER_LOGIN') is not None and os.getenv('ACTIVEMQ_OWNER_PASSWORD') is not None:
        serviceRun.do_setting_activemq_users(os.getenv('ACTIVEMQ_OWNER_LOGIN'), os.getenv('ACTIVEMQ_OWNER_PASSWORD'))
        serviceRun.do_setting_activemq_groups("owners", os.getenv('ACTIVEMQ_OWNER_LOGIN'))

    # We setting the writer account
    if os.getenv('ACTIVEMQ_WRITE_LOGIN') is not None and os.getenv('ACTIVEMQ_WRITE_PASSWORD') is not None:
        serviceRun.do_setting_activemq_users(os.getenv('ACTIVEMQ_WRITE_LOGIN'), os.getenv('ACTIVEMQ_WRITE_PASSWORD'))
        serviceRun.do_setting_activemq_groups("writes", os.getenv('ACTIVEMQ_WRITE_LOGIN'))

    # We setting the reader account
    if os.getenv('ACTIVEMQ_READ_LOGIN') is not None and os.getenv('ACTIVEMQ_READ_PASSWORD') is not None:
        serviceRun.do_setting_activemq_users(os.getenv('ACTIVEMQ_READ_LOGIN'), os.getenv('ACTIVEMQ_READ_PASSWORD'))
        if os.getenv('ACTIVEMQ_USER_LOGIN') is not None and os.getenv('ACTIVEMQ_USER_PASSWORD') is not None:
            serviceRun.do_setting_activemq_groups("reads", os.getenv('ACTIVEMQ_READ_LOGIN') + "," + os.getenv('ACTIVEMQ_USER_LOGIN'))
        else :
            serviceRun.do_setting_activemq_groups("reads", os.getenv('ACTIVEMQ_READ_LOGIN'))

    # We setting the JMX access
    if os.getenv('ACTIVEMQ_JMX_LOGIN') is not None and os.getenv('ACTIVEMQ_JMX_PASSWORD') is not None:
        serviceRun.do_setting_activemq_jmx_access("readwrite", os.getenv('ACTIVEMQ_JMX_LOGIN'), os.getenv('ACTIVEMQ_JMX_PASSWORD'))

    # We setting the log level
    if os.getenv('ACTIVEMQ_LOGLEVEL') is not None:
        serviceRun.do_setting_activemq_log4j(os.getenv('ACTIVEMQ_LOGLEVEL'))

    # We set the main parameters
    serviceRun.do_setting_activemq_main(os.getenv('ACTIVEMQ_NAME', 'localhost'), os.getenv('ACTIVEMQ_PENDING_MESSAGE_LIMIT', '1000'), os.getenv('ACTIVEMQ_STORAGE_USAGE', '100 gb'), os.getenv('ACTIVEMQ_TEMP_USAGE', '50 gb'), os.getenv('ACTIVEMQ_MAX_CONNECTION', '1000'), os.getenv('ACTIVEMQ_FRAME_SIZE', '104857600'), os.getenv('ACTIVEMQ_STATIC_TOPICS'), os.getenv('ACTIVEMQ_STATIC_QUEUES'), os.getenv('ACTIVEMQ_ENABLED_SCHEDULER', 'true'), os.getenv('ACTIVEMQ_ENABLED_AUTH', 'true'),
        os.getenv('ACTIVEMQ_ZKADDRESS', ''),
        os.getenv('ACTIVEMQ_ZKPASSWORD', ''),
        os.getenv('ACTIVEMQ_REPLICAS', '3'),
        os.getenv('ACTIVEMQ_ZKPATH', '/activemq/leveldb-stores'),
        os.getenv('ACTIVEMQ_HOSTNAME', ''))

    # We setting mem
    mem = os.getenv('ACTIVEMQ_OPTS_MEMORY', '')
    if mem != "":
        serviceRun.do_setting_activemq_mem(mem)
    else:
        serviceRun.do_setting_activemq_wrapper(os.getenv('ACTIVEMQ_MIN_MEMORY', '128'), os.getenv('ACTIVEMQ_MAX_MEMORY', '1024'))

        
    
    # We set host ip, and support other options
    serviceRun.do_setting_activemq_ip()