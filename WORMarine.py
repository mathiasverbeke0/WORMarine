####################
## IMPORT MODULES ##
####################

import requests, string, time, sys, argparse, itertools
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


######################
## DEFINE FUNCTIONS ##
######################

def get_species(prefix, incomplete, pid, retries, sleep_duration):

    # Initialize rSkips (the number of species to skip) and the list of species names
    rSkips = 0
    species_names = []

    # Initialize the number of trials
    trials = 0

    while True: 
        
        # If the number of trials exceeds the maximum number of retries, raise an error
        if trials == retries:
            raise ValueError(f'Failed to establish a connection with WORMS after {retries} attempts for prefix {prefix} (Status code: {status_code})')
        
        # Send a request to WORMS
        url = f'http://www.marinespecies.org/aphia.php?p=taxlist&searchpar=0&tComp=begins&tName={prefix}&rSkips={rSkips}&vOnly=1&marine=1&fossil=4&&pid={pid}&rComp=%3D&tRank=220'
        response = requests.get(url)

        # If the status code is not 200...
        if response.status_code != 200:
            # Save the response status code
            status_code = response.status_code
            
            # Wait for the specified duration (with exponential backoff)
            time.sleep(sleep_duration**(trials + 1))
            
            # Increment the number of trials
            trials += 1
            continue

        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the element containing the species information (for the listed species page)
        species_element = soup.find('ul', class_='list-group aphia_core_list_group_hover')

        # Find the element containing the species information (for the single species page)
        species_element2 = soup.find('ol', class_='aphia_core_breadcrumb-classification')
        
        # If a single species page is reached, extract the species name and return
        if species_element2 != None:
            species_placeholder = [species_element2.find_all('i')[-1].get_text(strip=True)]

            species_names.extend(species_placeholder)

            return species_names, incomplete

        # If the species element is None and the list of species names is empty, return an empty list
        elif species_element == None and len(species_names) == 0:
            return [], incomplete
        
        # If the species element is None and the list of species names is not empty, return the list of species names
        elif species_element == None and len(species_names) != 0:
            return species_names, incomplete
        
        # If the species element is not None and the number of species to skip exceeds 4900, add the prefix to the list of prefixes with too many species to extract and return the current list of species names
        elif species_element != None and rSkips > 4900:
            incomplete.append(prefix)
            return species_names, incomplete

        # In any other case, extract the species names and increment the number of species to skip by 100
        else:
            # Extract the species names
            species_placeholder = [item.get_text(strip=True) for item in species_element.find_all('i')]
            species_placeholder = [item for item in species_placeholder if len(item.split()) >= 1]
            
            # Add the species names to the list of species names
            species_names.extend(species_placeholder)
            
            # Increment the number of species to skip by 100
            rSkips += 100
            
            # Reset the number of trials
            trials = 0

def generate_prefixes(levelOfDetail):
    if levelOfDetail <= 0:
        sys.exit('Ensure that the level of detail is set to a value greater than or equal to 1.')

    prefixes = [''.join(prefix) for prefix in itertools.product(string.ascii_lowercase, repeat=levelOfDetail)]
    
    return prefixes


#####################
## PARSE ARGUMENTS ##
#####################

parser = argparse.ArgumentParser(description='Extract species names from WORMS')

parser.add_argument('-p', '--pid', type=int, help='The PID of the organism cluster', required=True)
parser.add_argument('-d', '--directory', type=str, help='The directory to write the species names file to', required=True)
parser.add_argument('-l', '--level', type=int, help='The level of detail', default=1)
parser.add_argument('-t', '--threads', type=int, help='The number of threads to use', default=4)
parser.add_argument('-r', '--retries', type=int, help='Maximum number of retries for requesting 1 page', default=3)
parser.add_argument('-s', '--sleep', type=float, help='Sleep duration between retries (in seconds) with exponential backoff', default=2)

args = parser.parse_args()

# Extract arguments
pid = args.pid
levelOfDetail = args.level
directory = args.directory
threads = args.threads
retries = args.retries
sleep_duration = args.sleep

#######################
## GENERATE PREFIXES ##
#######################

prefixes = generate_prefixes(levelOfDetail)


#################################
## FETCH ORGANISM CLUSTER NAME ##
#################################

# Send a request to WORMS with the specified PID
url = f'https://www.marinespecies.org/aphia.php?p=taxdetails&id={pid}'
response = requests.get(url)

# If the status code is not 200, raise an error
if response.status_code != 200:
    raise ValueError(f'Failed to establish a connection with WORMS for PID {pid} (Status code: {response.status_code})')

else:
    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the <h3> tag with specific class
    cluster = soup.find('h3', class_='aphia_core_header-inline')

    # Extract the text
    cluster = cluster.get_text().strip() if cluster else "Missing Cluster Name"


##############
## MESSAGES ##
##############

# Title message
print(" _    _  ______________  ___           _            \n\
| |  | ||  _  | ___ \  \/  |          (_)           \n\
| |  | || | | | |_/ / .  . | __ _ _ __ _ _ __   ___ \n\
| |/\| || | | |    /| |\/| |/ _` | '__| | '_ \ / _ \\\n\
\  /\  /\ \_/ / |\ \| |  | | (_| | |  | | | | |  __/\n\
 \/  \/  \___/\_| \_\_|  |_/\__,_|_|  |_|_| |_|\___|\n")

# Overview message
print('\033[1mDETAILS\n-------\033[0m')
print(f'\033[1mOrganism Cluster:\033[0m {cluster}')
print(f'\033[1mPID:\033[0m {pid}')
print(f'\033[1mLevel of Detail:\033[0m {levelOfDetail}')
print(f'\033[1mMaximum Retries:\033[0m {retries}')
print(f'\033[1mSleep Range:\033[0m {sleep_duration} seconds - {sleep_duration ** retries} seconds\n')

# Progress message
print('\033[1mPROGRESS\n--------\033[0m')


#########################
## FETCH SPECIES NAMES ##
#########################

# Create a list to store all the species names and a list to store the prefixes that have too many species to extract
all_species_names = []
incomplete = []

with open(f'{directory}/marine{"".join(cluster.split())}.txt', 'w') as file:

    # Use multithreading to send multiple requests to WORMS at the same time 
    with ThreadPoolExecutor(max_workers=threads) as executor:
        # Submit tasks to the executor and store the future objects in a list
        futures = [executor.submit(get_species, prefix, incomplete, pid, retries, sleep_duration) for prefix in prefixes]

        # Wait for all the tasks to complete and print the results
        for future in tqdm(as_completed(futures), total = len(prefixes)):
            try:
                species_names, incomplete = future.result()
                all_species_names.extend(species_names)
                
            except Exception as e:

                # Display the error
                print(f"An error occurred: {e}\nHalting all subsequent executions. This might take some time.")

                # Cancel all remaining futures
                for remaining_future in futures:
                    if not remaining_future.done():
                        remaining_future.cancel()
                
                sys.exit()

    # Remove all values that say et al.
    all_species_names = [name for name in all_species_names if name != 'et al.']

    # Count all organism names before removing duplicates
    species_names_amount_with_duplicates = len(all_species_names)

    # Convert the list to a set to remove duplicates
    all_species_names = list(set(all_species_names))

    # Sort the list
    all_species_names = sorted(all_species_names)

    # Print summary messages
    print('\033[1m\nSUMMARY\n-------\033[0m')
    print(f'\033[1mAmount:\033[0m {species_names_amount_with_duplicates} names extracted\n\033[1mAmount:\033[0m {len(all_species_names)} unique species\n\033[1mFile:\033[0m {directory}/marine{"".join(cluster.split())}.txt')
    
    if len(incomplete) != 0:
        print(f'\033[1mPrefixes with too many species to extract:\033[0m {incomplete}')

    file.writelines(name + '\n' for name in all_species_names)