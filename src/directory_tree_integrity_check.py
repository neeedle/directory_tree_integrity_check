import hashlib
import os
import sys

# hashlist[0] = (SHA1_HASH, PARTIAL_FILE_PATH)
# Partial file path is used in order to keep the script
# cross platform; every time the full file path is
# needed, the current working directory gets added to
# the partial file path

# parameters: filename (full path)
# reads it in 4096 bytes chunks and feeds them to the sha1 function
# returns the sha1 hash
# PS literally copypasted this from Stack Overflow

def sha1(fname):
    hash_sha1 = hashlib.sha1()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest()

# parameters: a path, verbose flag (false if message is not needed)
# walks the directory tree generated by the os.walk method, creates
# a hashlist
# returns the created hashlist

def create_hashlist_from_path(path, verbose=False):
    total_number_of_files = count_files_in_directory_tree(path)
    file_counter = 0
    hashlist = []
    for root, dirs, files in os.walk(path):
        # taken from Stack Overflow, excludes directories in ignored_directories from dirs
        dirs[:] = [d for d in dirs if d not in ignored_directories]
        files.sort() # preventing unexpected results by sorting the file names first
        for name in files:
            if (name not in ignored_files):
                path_to_be_written = os.path.relpath(root, start=path)
                hashlist.append(((sha1(os.path.join(root, name)), os.path.join(path_to_be_written, name)))) # appends a new sha1 digest - file path tuple to the list
                file_counter += 1
                if not verbose:
                    print("Progress: {:.1f}%".format((file_counter/total_number_of_files)*100), end='\r')
                elif verbose:
                    print(name + " Done")
    print('')
    print("Hashed {} files".format(file_counter))
    return hashlist

# parameters: a hashlist
# writes the sha1 hash of the file and the partial file path itself to file, in this order
# and one per line
# function is void

def write_hashlist_to_file(hashlist):
    with open('directory.sha1', 'w+') as f:
        for couple in hashlist:
            f.write(couple[0] + ' ' + couple[1] + '\n')

# parameters: none
# reads file line by line, strips the trailing newline from it
# splicing is used to separate sha1 hash from partial file path
# returns the parsed hashlist

def parse_hashlist_file():
    hashlist = []
    with open('directory.sha1', 'r') as f:
        for line in f:
            line = line.strip()
            sha1_hash = line[:40]
            file_path = line[41:]
            hashlist.append((sha1_hash, file_path))
    hashlist = add_cwd_to_hashlist(hashlist)
    return hashlist

# parameters: a hashlist
# adds the cwd to the partial file path
# returns the fixed hashlist

def add_cwd_to_hashlist(hashlist):
    return [(hash, os.path.join(cwd, relpath)) for hash, relpath in hashlist]


def create_and_write_hashlist_to_file():
    print("Calculating hashes...")
    hashlist = create_hashlist_from_path(cwd)
    print("Writing hashes to file...")
    write_hashlist_to_file(hashlist)
    print("Done")


def print_menu():
    print("1. Calculate and write SHA1 hashes to file")
    print("2. Calculate SHA1 hashes and check them against file")
    print("3. Exit")


def count_files_in_directory_tree(path):
    file_counter = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in ignored_directories]
        for name in files:
            if (name not in ignored_files):
                file_counter += 1
    return file_counter


if __name__ == '__main__':

    ignored_files = ['directory_tree_integrity_check.py', 'directory.sha1'] # add here the files you want to exclude from the integrity check
    ignored_directories = []
    cwd = os.getcwd()
    menu_choice = 0
    print_menu()

    while menu_choice != 3:
        print("\nType in your choice:")

        # check if the menu_choice is different from the 3 allowed
        while True:
            try:
                menu_choice = int(input('>'))
            except ValueError:
                pass
            if (menu_choice > 0 or menu_choice < 4):
                break

        if menu_choice == 1:
            # check if 'directory.sha1' exists first
            if os.path.isfile('directory.sha1'):
                print("SHA1 hashes file exists already")
                print("Do you want to overwrite it? y/n")
                response = input()
                if response == 'y':
                    create_and_write_hashlist_to_file()
            else:
                create_and_write_hashlist_to_file()

        elif menu_choice == 2:
            # check if 'directory.sha1' does not exist
            if not os.path.isfile('directory.sha1'):
                print("SHA1 hashes file has not been found")
                print("Do you want to create it? y/n")
                response = input()
                # basically do what menu_choice 1 does
                if response == 'y':
                    create_and_write_hashlist_to_file()
            # 'directory.sha1' exist
            else:
                # parse it
                parsed_hashlist = parse_hashlist_file()
                mismatch_number, num_of_checked_files = 0, 0
                # check parsed data against what we calculate in every iteration
                for couple in parsed_hashlist:
                    try:
                        if couple[0] != sha1(couple[1]):
                            # print("MISMATCH " + '"' + couple[1][ ( (couple[1].rfind('\\') ) + 1) : ] + '"')
                            print("MISMATCH " + '"' + couple[1] + '"')
                            mismatch_number += 1
                        num_of_checked_files += 1
                        print("Checking: {:.1f}%".format((num_of_checked_files/len(parsed_hashlist))*100), end='\r')
                    except FileNotFoundError:
                        print("File" + ' " ' + couple[1] + ' " ' + "has not been found" )
                        num_of_checked_files += 1
                        mismatch_number += 1
                print('')
                if mismatch_number == 0:
                    print("All files match")
            print("Checked {} files".format(num_of_checked_files))
            
        elif menu_choice == 3:
            pass

    print("Exiting...")
    sys.exit(0)
