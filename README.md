# huggingface-model-scorer

## Authors
- Daniel Wu
- Evan Zhang
- Bryan Chiang
- Parin Timbadia

# Why

To score HuggingFace models based on riskiness associated with the model, based on the following metrics.

## Repository Structure

### src 
a root level directory that contains the source code, which has the following modules
- Parsing -> Class defintions of UrlParser, which parses the URL file into a group of the model assets.
- Metrics -> Class definition of metrics type, which enables calculation of latency and actual implemented metrics.
- Output  -> Contains NDJSON output formatting.
- Parallel-> N/A

### tests 
a root level directory containing system module tests, primarily the metrics.

## Metrics
  - Bus Factor          -> Risk associated with knowledge distribution by the creators of a creation, like Github repo contributors or Model contributors.
  - Code Quality        -> Risk associated with how good code is, judged by an LLM.
  - Dataset Quality     -> Risk associated with how good dataset quality is, calculated by various factors like consistency and missing value coverage.
  - Documentation Score -> Risk associated with how thorough a repository's documentation quality is.
  - License             -> Risk associated with whether a license exists.
  - Performance Claims  -> Risk associated with whether the performance claims made are backed by real evidence.
  - Ramp Up Score       -> Risk associated with how quickly a new person could learn the asset based on whether or not it has proper documentation or such.
  - Size                -> Risk associated with how large a dataset is, which matters for different hardware that is being used.
  - Net Score           -> Weighted sum of all the scores that summarizes how risky a model is.
  - Code or Dataset     -> Whether code or dataset exists.

## System Diagram

<img width="1981" height="881" alt="dLLBRnCn4Bxlhx1wIXHjuBoggfPMI4XK5AgU45fDl9F4gXyhsmi4w7zdx7MztYHSE6maVpFppNjoxJnOFoXPkMUXUx2W69VWt8ttLcm6Zn-uqO_Y5xAtLTK3VuOTCj9pGk_Oxuens3XlWVlHZ3qAZn5dh6Q3bGqZSNgQ7nfj2P01-bPq4xPYq8iMTTSReVrYcK0xw5OXHSHTn5xe6_tT" src="https://github.com/user-attachments/assets/d7294861-7016-48c5-92b0-785f46b3f1de" />


# Setup Instructions

To build the program you can use it in one of two ways:

1. run.py
In the CLI, use

'''
python run.py --install
'''

2. executable
In the CLI, use

'''
./run --install
'''

# Test Instructions
You can run either the whole test automated test, or you can run manual tests of each metric module.

## Automated Test
'''
python run.py --test
'''
OR
'''
./run --test
'''

## Manual Tests

'''
python tests/test_<metric>.py
'''

# Run Instructions

To actually return a full NDJSON file on models and their asset groups, you will perform a run by inputting a URL file containing links to the model assets.

'''
python $URLFILE
'''
OR

'''
./run $URLFILE
'''
# Known Issues

- There might be issues with the setup process, in which case, try installing the requirements.txt packages first.
- There is no sharing of datasets across models, so there may be inaccuracies in the final score of a certain model if they use a dataset but dont store the url in the url file.
