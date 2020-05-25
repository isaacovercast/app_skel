
""" functions to auto-launch an ipcluster instance """

## imports for running ipcluster

import ipyparallel as ipp
import subprocess
import socket
import shlex
import time
import sys
import os

from app_skel.util import app_skelError


import logging
LOGGER = logging.getLogger(__name__)

def start_ipcluster(data):
    """ Start ipcluster """

    ## TODO: MPI support is totally untested right now.
    ## if MPI argument then use --ip arg to view all sockets
    iparg = ""
    if "MPI" in data._ipcluster["engines"]:
        iparg = "--ip=*"

    ## make ipcluster arg call
    standard = """
        ipcluster start 
                  --daemonize 
                  --cluster-id={}
                  --engines={} 
                  --profile={}
                  --n={}
                  {}"""\
        .format(data._ipcluster["cluster_id"], 
                data._ipcluster["engines"], 
                data._ipcluster["profile"],
                data._ipcluster["cores"],
                iparg)
                   
    ## wrap ipcluster start
    try: 
        LOGGER.info(shlex.split(standard))
        subprocess.check_call(shlex.split(standard), 
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE)

    except subprocess.CalledProcessError as inst:
        LOGGER.debug("  ipcontroller already running.")
        raise

    except Exception as inst:
        sys.exit("  Error launching ipcluster for parallelization:\n({})\n".\
                 format(inst))


## Currently unused, we are still doing it the "nice" way inside main, but
## leaving this here in case it becomes necessary.
def stop_ipcluster(data):
    """ Shut down the ipcluster."""

    standard = """
        ipcluster stop --clulster-id={}""".format(data._ipcluster["profile"])
    ## wrap ipcluster start
    try:
        LOGGER.info(shlex.split(standard))
        subprocess.check_call(shlex.split(standard),
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE)

    except Exception as inst:
        sys.exit("  Error launching ipcluster for parallelization:\n({})\n".\
                 format(inst))


def register_ipcluster(data):
    """
    The name is a unique id that keeps this __init__ distinct
    from interfering with other ipcontrollers. Run statements are wrapped
    so that ipcluster will be killed on exit.
    """
    ## check if this pid already has a running cluster
    data._ipcluster["cluster_id"] = "app_skel-cli-"+str(os.getpid())
    start_ipcluster(data)
    return data


def get_client(cluster_id, profile, engines, timeout, cores, quiet, **kwargs):
    """ 
    Creates a client to view ipcluster engines for a given profile and 
    returns it with at least one engine spun up and ready to go. If no 
    engines are found after nwait amount of time then an error is raised.
    If engines==MPI it waits a bit longer to find engines. If the number
    of engines is set then it waits even longer to try to find that number
    of engines.
    """

    ## save stds for later, we're gonna hide them to prevent external printing 
    devnull = open(os.devnull, 'w')
    save_stdout = sys.stdout 
    save_stderr = sys.stderr
    sys.stdout = devnull
    sys.stderr = devnull

    ## get cluster_info print string
    connection_string = "  establishing parallel connection:"

    ## wrapped search for ipcluster
    try: 
        ## are we looking for a running ipcluster instance?
        if profile not in [None, "default"]:
            args = {'profile': profile, "timeout": timeout}
        else:
            clusterargs = [cluster_id, profile, timeout]
            argnames = ["cluster_id", "profile", "timeout"]
            args = {key:value for key, value in zip(argnames, clusterargs)}

        ## get connection within timeout window of wait time and hide messages
        ipyclient = ipp.Client(**args)
        sys.stdout = save_stdout
        sys.stderr = save_stderr

        ## check that all engines have connected            
        if (engines == "MPI") or ("app_skel-cli-" in cluster_id):
            if not quiet:
                print(connection_string)

        for _ in range(6000):
            initid = len(ipyclient)
            time.sleep(0.01)
            ## If MPI then wait for all engines to start so we can report
            ## how many cores are on each host. If Local then only wait for
            ## one engine to be ready and then just go.
            if (engines == "MPI") or ("app_skel-cli-" in cluster_id):
                ## wait for cores to be connected
                if cores:
                    time.sleep(0.1)
                    if initid == cores:
                        break
                if initid:
                    time.sleep(3)
                    if len(ipyclient) == initid:
                        break
            else:
                if cores:
                    if initid == cores:
                        break
                else:
                    if initid:
                        break

    except KeyboardInterrupt as inst:
        raise inst

    ## This is raised if ipcluster is not running ------------
    except IOError as inst:
        if "app_skel-cli-" in cluster_id:
            raise app_skelError(NO_IPCLUSTER_CLI)
        else:
            raise app_skelError(NO_IPCLUSTER_API)

    except (ipp.TimeoutError, ipp.NoEnginesRegistered) as inst:
        raise inst

    except Exception as inst:
        raise inst

    finally:
        ## ensure that no matter what we reset the stds
        sys.stdout = save_stdout
        sys.stderr = save_stderr

    return ipyclient

def cluster_info(ipyclient):
    """
    Reports host and engine info for an ipyclient
    """
    ## get engine data, skips busy engines.    
    hosts = []
    for eid in ipyclient.ids:
        engine = ipyclient[eid]
        if not engine.outstanding:
            hosts.append(engine.apply(socket.gethostname))

    ## report it
    hosts = [i.get() for i in hosts]
    result = []
    for hostname in set(hosts):
        result.append("  host compute node: [{} cores] on {}"\
            .format(hosts.count(hostname), hostname))
    return "\n".join(result)


## GLOBALS
NO_IPCLUSTER_CLI = """\
    No ipcluster instance found. This may be a problem with your installation
    setup, or it could be that the cluster instance isn't firing up fast enough.
    This most often happens on cluster nodes. One solution is to launch
    ipcluster by hand and then pass the `--ipcluster` flag. See
    the docs for more info.
    """
NO_IPCLUSTER_API = """
    No ipcluster instance found. See documentation for the proper way to set 
    up an ipcluster instance when running the Python API. In short, 
    you must run 'ipcluster start' to initiate a local or remote cluster. 
    Also, if you changed the 'profile' or 'cluster_id' setting from their 
    default values you must enter these into the Region._ipcluster dictionary.
    """

