# Credits

This is an adapted version of https://github.com/pinae/Sacred-MNIST

# Sacred-MNIST Example
This example of sacred assumes that we have all experiments in subfolders with unique experiment names.
The simplest way to achieve this would be by simply adding a number to the experimnt.

The queue manager is adjusted to only search for experiments that were run from the same folder the queue manger resides in.
This allows one to setup multiple queues and run them in parallel without conflicts.

The queues are run from the same mongodb dtabase though

## Installation using conda

Install environment

```
conda create --name sacred_mnist python=3.6
source activate sacred_mnist
conda install --yes --file requirements.txt
```

## Minimal example to run the queue manager

```
# start mongodb somewhere
mongod -dbpath sacred --port 27017

# start omniboard
omniboard -m localhost:27017:sacred

source activate sacred_mnist # activate environment
cd Sacred-MNIST/01_experiment

## Schedule 2 jobs into queue
python train_convnet.py -q with batch_size=64
python train_convnet.py -q with batch_size=128

## list the queued jobs. You should see 2 jobs
python queue_manager.py -l

# go to experiment 2
cd ../02_experiment
## list queue for experiment 02. This should be empty, whereas for experiment 01 we have 2 jobs
python queue_manager.py -l

## schedule new job for experiment 2
python train_convnet.py -q with batch_size=128 config_file=config1.yaml

## check queue again, should give 1 job
python queue_manager.py -l

## clear queue again
python queue_manager.py -c

## observe that this leaves experiment 01 queue unchanged
cd ../01_experiment; python queue_manager.py -l

## Now finally run the queue
python queue_manager.py

```

## How does it work?

The queue manager uses a simple regex filter for the path of the script that shall be executed
```
def get_exname():
    ex_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    return ex_name

regx = re.compile(".*{}".format(get_exname()), re.IGNORECASE)

find_filter = {'status': status, "experiment.name" : regx}
for ex in db.runs.find(find_filter):
    # print ex
```
