# app_skel
A bare bones simulation application skeleton which comes with ipyrad
style-params file creation and parsing, a base conda package meta.yaml,
serial simulations and integration with an ipyparallel backend off the
shelf, base rtfd documentation skel, and some other useful stuff like
`app_skel.save()` and `app_skel.load()`, which might need _some_
customization depending on how complicated your model is.

The default module name is app_skel (recommend changing) and the central
class that does the work is called Core (change if you like).

Any very particular changes that need to be addressed in the code are labeled
with a `FIXME` tag and hopefully sufficient explanation.

## Usage
__Pro Tip:__ Run the `egrep` _before_ you do the `git init`.

* Clone this repo
* Replace app_skel with your chosen new package name:

    egrep -lRZ 'app_skel' . | xargs -0 -l sed -i -e 's/app_skel/foo/g'

* If you choose, you can rename the `Core` class to something more meaningful

    egrep -lRZ 'Core' . | xargs -0 -l sed -i -e 's/Core/Bar/g'

* You are probably 95% there, but there will probably be some things to clean
up. Better than doing it all from scratch.


## Where the work is done
Inside app_skel.__main__ around line 159 is a call to `data.simulate()`. This
will call the workhorse function of the primary class, and so app_skel.Core
should have a `simulate()` function which does the work and accepts and
handles well the following arguments:
* nsims     The number of simulations to run 
* ipyclient The ipyparallel client to use
* quiet     Don't print anything to standard out
* verbose   Print more stuff to standard out
* force     Overwrite previous simulations if necessary

## Default CLI args
The default CLI will parse a handful of universally useful arguments:
* `-n`  This is the flag to create a new params file
* `-p`  The flag to specify a params file for a new run of the app
* `-s`  How many simulations to run (if it's a simulation based model)
* `-c`  How many cores to spin up with the ipyparallel backend
* `-f`  Force the operation (overwrite anything that already exists)
* `-v`  Print out more progress info
* `-q`  Don't print anythin to standard out
* `-d`  Turn on debug mode to log debug info to a file
* `-V`  Print version info and exit

Long form arguments:

* `--ipcluster <cluster_id>`    Pass in a cluster ID for a running up ipcluster
    parser.add_argument("--ipcluster", metavar="ipcluster", dest="ipcluster",

