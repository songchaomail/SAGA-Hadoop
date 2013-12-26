'''
Command Line Util for using BigJob (via the Pilot-API)
'''
import argparse
import sys
import os
import pdb
import pickle
import hadoop1, hadoop2
import saga
import logging
import time
 
SAGA_HADOOP_DIRECTORY="~/.hadoop"  
  
class SAGAHadoopCLI(object):
    
    def __init__(self):
        self.pilots = []
        self.__restore()
        
    def submit_hadoop_job(self,                            
                          resource_url="fork://localhost",
                          working_directory=os.getcwd(),
                          number_cores=1,
                          cores_per_node=1,
                     ):
        
        try:
            # create a job service for Futuregrid's 'india' PBS cluster
            js = saga.job.Service(resource_url)
                    # describe our job
            jd = saga.job.Description()
            # resource requirements
            jd.total_cpu_count = int(number_cores)
            # environment, executable & arguments
            executable = "python"
            arguments = ["-m", "hadoop2.bootstrap_hadoop2"] 
            logging.debug("Run %s Args: %s"%(executable, str(arguments)))
            jd.executable  = executable
            jd.arguments   = []
            # output options
            jd.output = "hadoop_job.stdout"
            jd.error  = "hadoop_job.stderr"
            jd.working_directory=working_directory
            # create the job (state: New)
            myjob = js.create_job(jd)
    
            print "Starting Hadoop bootstrap job...\n"
            # run the job (submit the job to PBS)
            myjob.run()
            id = myjob.get_id()
            #id = id[id.index("]-[")+3: len(id)-1]
            print "**** Job: " + str(id) + " State : %s" % (myjob.get_state())
    
            while True:
                state = myjob.get_state()
                if state=="Running":
                    if os.path.exists("work/started"):
                        get_hadoop_config_data(id)
                        break
                time.sleep(3)
        except Exception as ex:
            print "An error occured: %s" % (str(ex))
        
                

    def cancel(self, pilot_url):
        pass
    
    
    def list(self):
        print "\SAGA Hadoop Job\t\t\t\t\t\t\t\t\tState"
        print "-----------------------------------------------------------------------------------------------------"
        
    ###########################################################################
    # auxiliary methods

    def version(self):
        print "SAGA Hadoop Version: " + bigjob.version
    
    def clean(self):
        os.remove(self.__get_save_filename())
    
    ###########################################################################
    # private and protected methods
    
    def __persist(self):
        f = open(self.__get_save_filename(), 'wb')
        pickle.dump(self.pilots, f)
        f.close()
    
    def __restore(self):
        if os.path.exists(self.__get_save_filename()):
            try:
                f = open(self.__get_save_filename(), 'rb')
                self.pilots = pickle.load(f)
                f.close()
            except:
                pass

    def __get_save_filename(self):
        return os.path.join(os.path.expanduser(SAGA_HADOOP_DIRECTORY), 'pilot-cli.p')


def main():
    app = SAGAHadoopCLI()
    parser = argparse.ArgumentParser(add_help=True, description="""SAGA Hadoop Command Line Utility""")
    
    parser.add_argument('--clean', action="store_true", default=False)
    parser.add_argument('--version', action="store_true", default=False)    
    
    saga_hadoop_group = parser.add_argument_group('Manage SAGA Hadoop clusters')
    saga_hadoop_group.add_argument('--resource', action="store", nargs=1, metavar="RESOURCE_URL", 
                              help="submit a job to specified resource, e.g. fork://localhost",
                              default="fork://localhost")
    saga_hadoop_group.add_argument('--working_directory', action="store", nargs="?", metavar="WORKING_DIRECTORY", 
                              help="submit a job to specified resource, e.g. fork://localhost",
                              default=os.getcwd())    
        
    saga_hadoop_group.add_argument('--number_cores', default="1", nargs="?")
    saga_hadoop_group.add_argument('--cores_per_node',  default="1", nargs="?")    
        
    parsed_arguments = parser.parse_args()    
    
    
    
    if parsed_arguments.version==True:
        app.version()
    else:
        app.submit_hadoop_job(resource_url=parsed_arguments.resource, 
                              working_directory=parsed_arguments.working_directory, 
                              number_cores=parsed_arguments.number_cores, 
                              cores_per_node=parsed_arguments.cores_per_node)
        
if __name__ == '__main__':
    main()
    
    